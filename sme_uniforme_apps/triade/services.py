import json
import logging
import uuid
from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from sme_uniforme_apps.proponentes.models import Proponente

from .builders import TriadePayloadBuilder
from .client import TriadeHttpClient
from .exceptions import TriadeConfigError, TriadePermanentError, TriadeTransientError
from .models import TriadeDocumento, TriadeLote
from .persistence import queryset_update_with_alterado_em, save_with_alterado_em
from .runtime import get_triade_runtime_config
from .statuses import (
    TRIADE_LOTE_STATUSES_REPROCESSAVEIS,
    TRIADE_LOTE_TERMINAL_STATUSES,
    normalize_decisao,
    normalize_status,
)

log = logging.getLogger(__name__)


@dataclass
class TriadePreparedLote:
    lote: TriadeLote
    payload: dict
    created: bool
    reused_payload: bool


class TriadeSubmissionService:
    DEFAULT_ORIGEM_OPERACIONAL = "concluir-cadastro"
    DEFAULT_FLUXO = "mvp_conclusao_cadastro"
    STATUS_PAYLOAD_PRONTO = "payload_ready"
    STATUS_ERRO = "error"
    STATUS_PROCESSANDO = "processing"

    def __init__(self, client=None):
        runtime_config = get_triade_runtime_config()
        self.enabled = runtime_config.enabled
        self.send_only_required_documents = runtime_config.send_only_required_documents
        self.api_url = self._get_setting("TRIADE_API_URL")
        self.api_token = self._get_setting("TRIADE_API_TOKEN")
        self.source_system = self._get_setting("TRIADE_SOURCE_SYSTEM")
        self.schema_version = self._get_setting("TRIADE_SCHEMA_VERSION")
        self.timeout_seconds = self._get_setting(
            "TRIADE_TIMEOUT_SECONDS", required=False, default=30
        )

        if not self.enabled:
            raise TriadeConfigError("Integracao TRIADE desabilitada nas configuracoes.")

        self.client = client or TriadeHttpClient(
            base_url=self.api_url,
            api_token=self.api_token,
            timeout_seconds=self.timeout_seconds,
        )

    def prepare_lote_envio(
        self,
        proponente,
        origem_operacional=DEFAULT_ORIGEM_OPERACIONAL,
        fluxo=DEFAULT_FLUXO,
    ):
        external_batch_id = self.build_external_batch_id(proponente)
        lote, created = TriadeLote.objects.get_or_create(
            external_batch_id=external_batch_id,
            defaults={
                "proponente": proponente,
                "source_system": self.source_system,
                "schema_version": self.schema_version,
                "status": self.STATUS_PAYLOAD_PRONTO,
            },
        )

        update_fields = []
        if lote.proponente_id != proponente.id:
            lote.proponente = proponente
            update_fields.append("proponente")
        if not lote.source_system:
            lote.source_system = self.source_system
            update_fields.append("source_system")
        if not lote.schema_version:
            lote.schema_version = self.schema_version
            update_fields.append("schema_version")

        if lote.payload_envio and lote.batch_id:
            if update_fields:
                save_with_alterado_em(lote, update_fields)
            return TriadePreparedLote(
                lote=lote,
                payload=self._deserialize_json(lote.payload_envio, "payload_envio"),
                created=created,
                reused_payload=True,
            )

        anexos = self._get_anexos_para_envio(proponente)
        payload = TriadePayloadBuilder(
            source_system=self.source_system,
            schema_version=self.schema_version,
            origem_operacional=origem_operacional,
            fluxo=fluxo,
        ).build(
            proponente=proponente,
            external_batch_id=external_batch_id,
            anexos=anexos,
        )

        lote.payload_envio = self._serialize_json(payload)
        lote.metadata = self._serialize_json(payload.get("metadata", {}))
        lote.status = self.STATUS_PAYLOAD_PRONTO
        update_fields.extend(["payload_envio", "metadata", "status"])
        save_with_alterado_em(lote, tuple(dict.fromkeys(update_fields)))

        anexos_por_external_document_id = {str(anexo.uuid): anexo for anexo in anexos}
        self._sync_documentos_snapshot(
            lote=lote,
            documentos=payload.get("documents", []),
            anexos_por_external_document_id=anexos_por_external_document_id,
        )

        return TriadePreparedLote(
            lote=lote,
            payload=payload,
            created=created,
            reused_payload=False,
        )

    def dispatch_proponente_uuid(
        self,
        proponente_uuid,
        origem_operacional=DEFAULT_ORIGEM_OPERACIONAL,
        fluxo=DEFAULT_FLUXO,
    ):
        try:
            proponente = Proponente.objects.get(uuid=proponente_uuid)
        except Proponente.DoesNotExist:
            raise TriadePermanentError(
                "Proponente {} nao encontrado para envio ao TRIADE.".format(
                    proponente_uuid
                )
            )

        return self.dispatch_proponente(
            proponente=proponente,
            origem_operacional=origem_operacional,
            fluxo=fluxo,
        )

    def dispatch_proponente(
        self,
        proponente,
        origem_operacional=DEFAULT_ORIGEM_OPERACIONAL,
        fluxo=DEFAULT_FLUXO,
    ):
        prepared = self.prepare_lote_envio(
            proponente=proponente,
            origem_operacional=origem_operacional,
            fluxo=fluxo,
        )
        lote = prepared.lote

        if not lote.batch_id:
            self._criar_lote_externo(lote, prepared.payload)
            lote.refresh_from_db()
        else:
            log.info(
                "TRIADE: reutilizando batch_id %s do lote %s.",
                lote.batch_id,
                lote.external_batch_id,
            )

        self._iniciar_pipeline(lote)
        lote.refresh_from_db()
        return lote

    def build_external_batch_id(self, proponente):
        return "proponente-{}".format(proponente.uuid)

    def retry_lote_id(self, lote_id):
        try:
            lote = TriadeLote.objects.get(pk=lote_id)
        except TriadeLote.DoesNotExist:
            raise TriadePermanentError(
                "Lote TRIADE {} nao encontrado para retomada de processamento.".format(
                    lote_id
                )
            )

        return self.retry_lote(lote)

    def retry_lote(self, lote):
        blocker = self.get_retry_lote_blocker(lote)
        if blocker:
            raise TriadePermanentError(blocker)

        if lote.batch_id:
            self._iniciar_pipeline(lote)
            lote.refresh_from_db()
            return lote

        payload = self._deserialize_json(lote.payload_envio, "payload_envio")
        self._criar_lote_externo(lote, payload)
        lote.refresh_from_db()
        self._iniciar_pipeline(lote)
        lote.refresh_from_db()
        return lote

    def get_retry_lote_blocker(self, lote):
        status_normalized = normalize_status(lote.status)
        if status_normalized not in TRIADE_LOTE_STATUSES_REPROCESSAVEIS:
            return "Lote TRIADE {} esta com status {} e nao pode ser retomado.".format(
                lote.external_batch_id,
                lote.status,
            )

        if lote.batch_id:
            return None

        if not lote.payload_envio:
            return (
                "Lote TRIADE {} nao pode ser retomado sem batch_id ou payload_envio "
                "persistido."
            ).format(lote.external_batch_id)

        if self._can_retry_create_same_snapshot(lote):
            return None

        return (
            "Lote TRIADE {} falhou na criacao com HTTP {}. Isso indica erro "
            "permanente de payload/configuracao; nao retome o mesmo snapshot."
        ).format(lote.external_batch_id, lote.status_http_criacao)

    def _can_retry_create_same_snapshot(self, lote):
        status_code = lote.status_http_criacao
        if status_code is None:
            return True
        if 200 <= status_code < 300:
            return True
        if status_code == 429:
            return True
        if 500 <= status_code <= 599:
            return True
        return False

    def sync_lote(self, lote):
        if not lote.batch_id:
            raise TriadePermanentError(
                "Lote TRIADE {} nao possui batch_id para sincronizacao.".format(
                    lote.external_batch_id
                )
            )

        try:
            response = self.client.get_batch(str(lote.batch_id))
        except TriadeTransientError as exc:
            lote.ultimo_erro = str(exc)
            save_with_alterado_em(lote, ("ultimo_erro",))
            raise

        response_data = self._response_data_as_dict(response)
        if response.is_success:
            self._apply_batch_sync_to_lote(lote, response_data)
            self._sync_documentos_from_batch(lote, response_data.get("documents", []))
            return lote

        lote.ultimo_erro = self._build_error_message("consulta do lote", response)
        save_with_alterado_em(lote, ("ultimo_erro",))
        self._raise_for_response("consulta do lote", response)

    def _criar_lote_externo(self, lote, payload):
        response = self.client.create_batch(payload)
        lote.status_http_criacao = response.status_code
        lote.resposta_criacao = self._serialize_response(response)

        if response.is_success:
            response_data = self._response_data_as_dict(response)
            lote.batch_id = self._parse_uuid(response_data.get("batch_id"), "batch_id")
            lote.submission_id = self._parse_uuid(
                response_data.get("submission_id"), "submission_id", required=False
            )
            lote.analysis_desk_id = (
                response_data.get("analysis_desk_id") or lote.analysis_desk_id
            )
            lote.status = (
                normalize_status(response_data.get("status"))
                or lote.status
                or self.STATUS_PAYLOAD_PRONTO
            )
            lote.enviado_em = lote.enviado_em or timezone.now()
            lote.ultimo_erro = None
            save_with_alterado_em(
                lote,
                (
                    "status_http_criacao",
                    "resposta_criacao",
                    "batch_id",
                    "submission_id",
                    "analysis_desk_id",
                    "status",
                    "enviado_em",
                    "ultimo_erro",
                ),
            )
            self._sync_documentos_response(lote, response_data)
            return

        self._registrar_erro_no_lote(
            lote=lote,
            response=response,
            etapa="criacao do lote",
            update_fields=("status_http_criacao", "resposta_criacao"),
        )

    def _iniciar_pipeline(self, lote):
        if not lote.batch_id:
            raise TriadePermanentError(
                "TRIADE nao retornou batch_id para o lote {}.".format(
                    lote.external_batch_id
                )
            )

        response = self.client.start_submission(str(lote.batch_id))
        lote.status_http_inicio = response.status_code
        lote.resposta_inicio = self._serialize_response(response)

        if response.is_success or response.status_code == 409:
            response_data = self._response_data_as_dict(response)
            normalized_status = normalize_status(response_data.get("status"))
            lote.submission_id = (
                self._parse_uuid(
                    response_data.get("submission_id"),
                    "submission_id",
                    required=False,
                )
                or lote.submission_id
            )
            lote.analysis_desk_id = (
                response_data.get("analysis_desk_id") or lote.analysis_desk_id
            )
            if normalized_status:
                lote.status = normalized_status
            elif lote.status not in TRIADE_LOTE_TERMINAL_STATUSES:
                lote.status = self.STATUS_PROCESSANDO
            lote.iniciado_em = lote.iniciado_em or timezone.now()
            lote.ultimo_erro = None
            save_with_alterado_em(
                lote,
                (
                    "status_http_inicio",
                    "resposta_inicio",
                    "submission_id",
                    "analysis_desk_id",
                    "status",
                    "iniciado_em",
                    "ultimo_erro",
                ),
            )
            return

        self._registrar_erro_no_lote(
            lote=lote,
            response=response,
            etapa="inicio do pipeline",
            update_fields=("status_http_inicio", "resposta_inicio"),
        )

    def _sync_documentos_snapshot(
        self, lote, documentos, anexos_por_external_document_id
    ):
        external_document_ids = []
        for documento in documentos:
            external_document_id = documento["external_document_id"]
            external_document_ids.append(external_document_id)
            TriadeDocumento.objects.update_or_create(
                lote=lote,
                external_document_id=external_document_id,
                defaults={
                    "anexo": anexos_por_external_document_id.get(external_document_id),
                    "external_document_type": documento.get("document_type"),
                    "document_type": documento.get("document_type"),
                    "title": documento.get("title"),
                    "metadata": self._serialize_json(documento.get("metadata", {})),
                },
            )

        TriadeDocumento.objects.filter(lote=lote).exclude(
            external_document_id__in=external_document_ids
        ).delete()

    def _sync_documentos_response(self, lote, response_data):
        for documento in response_data.get("documents", []):
            external_document_id = documento.get("external_document_id")
            if not external_document_id:
                continue

            defaults = {}
            if documento.get("document_id"):
                defaults["document_id"] = self._parse_uuid(
                    documento.get("document_id"),
                    "documents[].document_id",
                    required=False,
                )
            normalized_status = normalize_status(documento.get("status"))
            normalized_decisao = normalize_decisao(documento.get("decisao"))
            if normalized_status:
                defaults["status"] = normalized_status
            if normalized_decisao:
                defaults["decisao"] = normalized_decisao
            if documento.get("justificativa"):
                defaults["justificativa"] = documento.get("justificativa")
            if documento.get("error"):
                defaults["error"] = documento.get("error")
            if documento.get("metadata"):
                defaults["metadata"] = self._serialize_json(documento.get("metadata"))

            if defaults:
                queryset_update_with_alterado_em(
                    TriadeDocumento.objects.filter(
                        lote=lote, external_document_id=external_document_id
                    ),
                    **defaults
                )

    def _apply_batch_sync_to_lote(self, lote, response_data):
        normalized_status = normalize_status(response_data.get("status"))
        if normalized_status:
            lote.status = normalized_status

        metadata = response_data.get("metadata")
        if metadata is not None:
            lote.metadata = self._serialize_json(metadata)

        lote.ultimo_erro = None
        save_with_alterado_em(lote, ("status", "metadata", "ultimo_erro"))

    def _sync_documentos_from_batch(self, lote, documents):
        for document_payload in documents:
            external_document_id = document_payload.get("external_document_id")
            if not external_document_id:
                continue

            defaults = {}
            normalized_status = normalize_status(document_payload.get("status"))
            normalized_decisao = normalize_decisao(document_payload.get("decisao"))

            if normalized_status:
                defaults["status"] = normalized_status
            if normalized_decisao:
                defaults["decisao"] = normalized_decisao

            document_id = self._parse_uuid(
                document_payload.get("document_id"),
                "documents[].document_id",
                required=False,
            )
            if document_id:
                defaults["document_id"] = document_id

            processed_at = self._parse_datetime(document_payload.get("processed_at"))
            if processed_at:
                defaults["processed_at"] = processed_at

            for field_name in (
                "external_document_type",
                "document_type",
                "title",
                "justificativa",
                "error",
            ):
                if field_name in document_payload:
                    defaults[field_name] = document_payload.get(field_name) or None

            if document_payload.get("metadata") is not None:
                defaults["metadata"] = self._serialize_json(
                    document_payload.get("metadata")
                )

            TriadeDocumento.objects.update_or_create(
                lote=lote,
                external_document_id=external_document_id,
                defaults=defaults,
            )

    def _registrar_erro_no_lote(self, lote, response, etapa, update_fields):
        lote.status = self.STATUS_ERRO
        lote.ultimo_erro = self._build_error_message(etapa, response)
        save_with_alterado_em(lote, update_fields + ("status", "ultimo_erro"))
        self._raise_for_response(etapa, response)

    def _raise_for_response(self, etapa, response):
        status_code = response.status_code
        message = self._build_error_message(etapa, response)

        if status_code == 429 or 500 <= status_code <= 599:
            raise TriadeTransientError(message)

        raise TriadePermanentError(message)

    def _build_error_message(self, etapa, response):
        response_data = self._response_data_as_dict(response)
        detalhe = response_data.get("detail") or response.text or "sem corpo"
        return "Falha na {} do TRIADE. HTTP {}. {}".format(
            etapa, response.status_code, detalhe
        )

    def _response_data_as_dict(self, response):
        if isinstance(response.data, dict):
            return response.data
        return {}

    def _parse_uuid(self, value, field_name, required=True):
        if not value:
            if required:
                raise TriadePermanentError(
                    "TRIADE nao retornou {} para o lote em processamento.".format(
                        field_name
                    )
                )
            return None

        try:
            return uuid.UUID(str(value))
        except (TypeError, ValueError, AttributeError):
            raise TriadePermanentError(
                "TRIADE retornou {} invalido: {}".format(field_name, value)
            )

    def _serialize_response(self, response):
        if response.data is not None:
            return self._serialize_json(response.data)
        return response.text

    def _serialize_json(self, value):
        return json.dumps(
            value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        )

    def _parse_datetime(self, value):
        if not value:
            return None

        parsed = parse_datetime(value)
        if not parsed:
            return None
        if timezone.is_naive(parsed):
            return timezone.make_aware(parsed, timezone.get_current_timezone())
        return parsed

    def _get_anexos_para_envio(self, proponente):
        queryset = proponente.anexos.select_related("tipo_documento").order_by("id")
        if self.send_only_required_documents:
            queryset = queryset.filter(tipo_documento__obrigatorio=True)
        return list(queryset)

    def _deserialize_json(self, value, field_name):
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            raise TriadePermanentError(
                "Nao foi possivel desserializar {} do lote TRIADE.".format(field_name)
            )

    def _get_setting(self, setting_name, required=True, default=None):
        value = getattr(settings, setting_name, default)
        if required and (value is None or value == ""):
            raise TriadeConfigError(
                "Configuracao {} obrigatoria para a integracao TRIADE.".format(
                    setting_name
                )
            )
        return value
