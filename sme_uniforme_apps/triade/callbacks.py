import hashlib
import hmac
import json
import logging
import uuid

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from sme_uniforme_apps.proponentes.models import Anexo

from .exceptions import (
    TriadeConfigError,
    TriadePermanentError,
    TriadeRequestError,
    TriadeSignatureError,
)
from .models import TriadeCallback, TriadeDocumento, TriadeLote
from .persistence import queryset_update_with_alterado_em, save_with_alterado_em
from .statuses import normalize_decisao, normalize_status

log = logging.getLogger(__name__)


class TriadeCallbackService:
    STATUS_RECEBIDO = "recebido"
    STATUS_ENFILEIRADO = "enfileirado"
    STATUS_PROCESSANDO = "processando"
    STATUS_PROCESSADO = "processado"
    STATUS_DUPLICADO = "duplicado"
    STATUS_ERRO = "erro"

    def __init__(self):
        self.hmac_secret = getattr(settings, "TRIADE_HMAC_SECRET", "")
        if not self.hmac_secret:
            raise TriadeConfigError(
                "Configuracao TRIADE_HMAC_SECRET obrigatoria para receber callback TRIADE."
            )

    def register_callback(self, raw_body, signature_header, delivery_header):
        payload = self._load_payload(raw_body)
        delivery_id = self._parse_delivery_id(delivery_header)
        self.validate_signature(raw_body, signature_header)

        payload_hash = hashlib.sha256(raw_body).hexdigest()
        external_batch_id = payload.get("external_batch_id") or None
        batch_id = self._parse_uuid(payload.get("batch_id"))
        submission_id = self._parse_uuid(payload.get("submission_id"))
        lote = self._find_lote(batch_id=batch_id, external_batch_id=external_batch_id)

        callback, created = TriadeCallback.objects.get_or_create(
            delivery_id=delivery_id,
            defaults={
                "lote": lote,
                "external_batch_id": external_batch_id,
                "batch_id": batch_id,
                "submission_id": submission_id,
                "assinatura_recebida": signature_header,
                "payload_bruto": raw_body.decode("utf-8"),
                "payload_hash": payload_hash,
                "status_processamento": self.STATUS_RECEBIDO,
            },
        )

        return callback, created

    def validate_signature(self, raw_body, signature_header):
        if not signature_header:
            raise TriadeRequestError("Header X-TRIADE-Signature obrigatorio.")

        prefix = "sha256="
        if not signature_header.startswith(prefix):
            raise TriadeSignatureError(
                "Header X-TRIADE-Signature deve usar o prefixo sha256=."
            )

        received_signature = signature_header[len(prefix):]
        expected_signature = hmac.new(
            self.hmac_secret.encode("utf-8"), raw_body, hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(received_signature, expected_signature):
            raise TriadeSignatureError("Assinatura TRIADE invalida.")

    def process_callback(self, callback_id):
        callback = TriadeCallback.objects.get(pk=callback_id)
        if callback.status_processamento in (
            self.STATUS_PROCESSADO,
            self.STATUS_DUPLICADO,
        ):
            return callback

        try:
            with transaction.atomic():
                callback = TriadeCallback.objects.select_for_update().get(
                    pk=callback_id
                )

                if callback.status_processamento in (
                    self.STATUS_PROCESSADO,
                    self.STATUS_DUPLICADO,
                ):
                    return callback

                callback.status_processamento = self.STATUS_PROCESSANDO
                callback.erro = None
                save_with_alterado_em(callback, ("status_processamento", "erro"))

                payload = self._load_payload(callback.payload_bruto.encode("utf-8"))
                lote = callback.lote or self._resolve_lote_for_payload(
                    callback, payload
                )
                callback.lote = lote

                if self._is_duplicate_payload(callback):
                    callback.status_processamento = self.STATUS_DUPLICADO
                    callback.processado_em = timezone.now()
                    save_with_alterado_em(
                        callback,
                        (
                            "lote",
                            "status_processamento",
                            "processado_em",
                        ),
                    )
                    return callback

                self._apply_payload_to_lote(lote, payload)
                self._apply_documents_to_lote(lote, payload.get("documents", []))

                callback.status_processamento = self.STATUS_PROCESSADO
                callback.processado_em = timezone.now()
                callback.erro = None
                save_with_alterado_em(
                    callback,
                    (
                        "lote",
                        "status_processamento",
                        "processado_em",
                        "erro",
                    ),
                )
                return callback
        except Exception as exc:
            log.exception("Falha ao processar callback TRIADE %s.", callback_id)
            queryset_update_with_alterado_em(
                TriadeCallback.objects.filter(pk=callback_id),
                status_processamento=self.STATUS_ERRO,
                erro=str(exc),
                processado_em=timezone.now(),
            )
            raise

    def _load_payload(self, raw_body):
        try:
            return json.loads(raw_body.decode("utf-8"))
        except (AttributeError, UnicodeDecodeError, ValueError):
            raise TriadeRequestError("Payload JSON invalido no callback TRIADE.")

    def _parse_delivery_id(self, delivery_header):
        if not delivery_header:
            raise TriadeRequestError("Header X-TRIADE-Delivery obrigatorio.")

        try:
            return uuid.UUID(str(delivery_header))
        except (TypeError, ValueError, AttributeError):
            raise TriadeRequestError("Header X-TRIADE-Delivery invalido.")

    def _parse_uuid(self, value):
        if not value:
            return None

        try:
            return uuid.UUID(str(value))
        except (TypeError, ValueError, AttributeError):
            return None

    def _find_lote(self, batch_id=None, external_batch_id=None):
        filters = Q()
        if batch_id:
            filters |= Q(batch_id=batch_id)
        if external_batch_id:
            filters |= Q(external_batch_id=external_batch_id)

        if not filters:
            return None

        return TriadeLote.objects.filter(filters).order_by("id").first()

    def _resolve_lote_for_payload(self, callback, payload):
        lote = self._find_lote(
            batch_id=self._parse_uuid(payload.get("batch_id")),
            external_batch_id=payload.get("external_batch_id"),
        )
        if lote:
            return lote

        raise TriadePermanentError(
            "Nao foi encontrado lote TRIADE para o callback {}.".format(
                callback.delivery_id
            )
        )

    def _is_duplicate_payload(self, callback):
        queryset = TriadeCallback.objects.filter(
            payload_hash=callback.payload_hash,
            status_processamento=self.STATUS_PROCESSADO,
        ).exclude(pk=callback.pk)

        if callback.batch_id:
            queryset = queryset.filter(batch_id=callback.batch_id)
        elif callback.external_batch_id:
            queryset = queryset.filter(external_batch_id=callback.external_batch_id)
        elif callback.submission_id:
            queryset = queryset.filter(submission_id=callback.submission_id)
        else:
            return False

        return queryset.exists()

    def _apply_payload_to_lote(self, lote, payload):
        confirmed_at = self._parse_datetime(payload.get("confirmado_em"))
        now = timezone.now()

        lote.batch_id = self._parse_uuid(payload.get("batch_id")) or lote.batch_id
        lote.submission_id = (
            self._parse_uuid(payload.get("submission_id")) or lote.submission_id
        )
        lote.analysis_desk_id = payload.get("analysis_desk_id") or lote.analysis_desk_id
        lote.status = normalize_status(payload.get("status")) or lote.status
        lote.decisao_parecer = (
            normalize_decisao(payload.get("decisao_parecer")) or lote.decisao_parecer
        )
        lote.parecer_texto = payload.get("parecer_texto") or lote.parecer_texto
        lote.confirmado_em = confirmed_at or lote.confirmado_em
        lote.confirmado_por = payload.get("confirmado_por") or lote.confirmado_por
        lote.callback_recebido_em = now
        lote.concluido_em = confirmed_at or lote.concluido_em or now
        save_with_alterado_em(
            lote,
            (
                "batch_id",
                "submission_id",
                "analysis_desk_id",
                "status",
                "decisao_parecer",
                "parecer_texto",
                "confirmado_em",
                "confirmado_por",
                "callback_recebido_em",
                "concluido_em",
            ),
        )

    def _apply_documents_to_lote(self, lote, documents):
        for document_payload in documents:
            self._apply_document_payload(lote, document_payload)

    def _apply_document_payload(self, lote, document_payload):
        external_document_id = document_payload.get("external_document_id")
        if not external_document_id:
            raise TriadePermanentError(
                "Callback TRIADE sem external_document_id nao pode ser reconciliado."
            )

        defaults = {
            "document_id": self._parse_uuid(document_payload.get("document_id")),
            "status": normalize_status(document_payload.get("status")),
            "decisao": normalize_decisao(document_payload.get("decisao")),
            "justificativa": document_payload.get("justificativa") or None,
            "error": document_payload.get("error") or None,
        }

        processed_at = self._parse_datetime(document_payload.get("processed_at"))
        if processed_at:
            defaults["processed_at"] = processed_at

        metadata = document_payload.get("metadata")
        if metadata is not None:
            defaults["metadata"] = json.dumps(
                metadata, ensure_ascii=False, separators=(",", ":"), sort_keys=True
            )

        anexo = self._resolve_anexo(
            external_document_id=external_document_id,
            metadata=metadata,
        )
        if anexo:
            defaults["anexo"] = anexo

        documento, _ = TriadeDocumento.objects.update_or_create(
            lote=lote,
            external_document_id=external_document_id,
            defaults=defaults,
        )

        if anexo:
            self._apply_document_result_to_anexo(anexo, document_payload)
            if documento.anexo_id != anexo.id:
                documento.anexo = anexo
                save_with_alterado_em(documento, ("anexo",))

    def _resolve_anexo(self, external_document_id, metadata=None):
        anexo_uuid = None
        if metadata and metadata.get("anexo_uuid"):
            anexo_uuid = metadata.get("anexo_uuid")
        else:
            anexo_uuid = external_document_id

        try:
            return Anexo.objects.get(uuid=anexo_uuid)
        except (Anexo.DoesNotExist, ValueError, TypeError):
            return None

    def _apply_document_result_to_anexo(self, anexo, document_payload):
        update_fields = []
        if "decisao" in document_payload:
            anexo.status_ia = normalize_decisao(document_payload.get("decisao"))
            update_fields.append("status_ia")
        if "justificativa" in document_payload:
            anexo.justificativa_ia = document_payload.get("justificativa")
            update_fields.append("justificativa_ia")

        if update_fields:
            save_with_alterado_em(anexo, update_fields)

    def _parse_datetime(self, value):
        if not value:
            return None

        parsed = parse_datetime(value)
        if not parsed:
            return None
        if timezone.is_naive(parsed):
            return timezone.make_aware(parsed, timezone.get_current_timezone())
        return parsed
