import hashlib
import hmac
import json
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.db import OperationalError

from sme_uniforme_apps.triade.callbacks import TriadeCallbackService
from sme_uniforme_apps.triade.exceptions import TriadeCallbackTransientError
from sme_uniforme_apps.triade.models import TriadeCallback, TriadeDocumento
from sme_uniforme_apps.triade.services import TriadeSubmissionService

pytestmark = pytest.mark.django_db


def configure_triade_settings(settings):
    settings.TRIADE_ENABLED = True
    settings.TRIADE_API_URL = "https://triade.exemplo.com"
    settings.TRIADE_API_TOKEN = "token-teste"
    settings.TRIADE_SOURCE_SYSTEM = "portal_uniforme"
    settings.TRIADE_SCHEMA_VERSION = "1.0"
    settings.TRIADE_TIMEOUT_SECONDS = 15
    settings.TRIADE_HMAC_SECRET = "segredo-triade"


def build_callback_payload(lote, anexo, batch_id, submission_id):
    return {
        "external_batch_id": lote.external_batch_id,
        "batch_id": str(batch_id),
        "submission_id": str(submission_id),
        "analysis_desk_id": "mesa-portal-uniforme",
        "status": "completed",
        "decisao_parecer": "REPROVADO",
        "parecer_texto": "Parecer final confirmado.",
        "confirmado_em": "2026-05-31T12:00:00Z",
        "confirmado_por": "analista.triade",
        "documents": [
            {
                "external_document_id": str(anexo.uuid),
                "document_id": str(uuid4()),
                "status": "completed",
                "decisao": "REPROVADO",
                "justificativa": "Documento divergente.",
                "processed_at": "2026-05-31T11:45:00Z",
                "error": None,
                "metadata": {"anexo_uuid": str(anexo.uuid)},
            }
        ],
    }


def sign_payload(secret, payload_bytes):
    digest = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    return "sha256={}".format(digest)


def test_process_callback_atualiza_lote_documento_e_anexo(
    settings, proponente_triade, loja_primeira, anexo_triade
):
    configure_triade_settings(settings)
    submission_service = TriadeSubmissionService()
    lote = submission_service.prepare_lote_envio(proponente_triade).lote
    batch_id = uuid4()
    submission_id = uuid4()
    payload = build_callback_payload(lote, anexo_triade, batch_id, submission_id)
    raw_payload = json.dumps(payload).encode("utf-8")

    callback = TriadeCallback.objects.create(
        delivery_id=uuid4(),
        lote=lote,
        external_batch_id=lote.external_batch_id,
        batch_id=batch_id,
        submission_id=submission_id,
        assinatura_recebida=sign_payload(settings.TRIADE_HMAC_SECRET, raw_payload),
        payload_bruto=raw_payload.decode("utf-8"),
        payload_hash=hashlib.sha256(raw_payload).hexdigest(),
        status_processamento=TriadeCallbackService.STATUS_RECEBIDO,
    )
    lote_alterado_em_original = lote.alterado_em
    callback_alterado_em_original = callback.alterado_em
    anexo_alterado_em_original = anexo_triade.alterado_em

    TriadeCallbackService().process_callback(callback.id)

    callback.refresh_from_db()
    lote.refresh_from_db()
    anexo_triade.refresh_from_db()
    documento = TriadeDocumento.objects.get(
        lote=lote, external_document_id=str(anexo_triade.uuid)
    )

    assert callback.status_processamento == TriadeCallbackService.STATUS_PROCESSADO
    assert lote.batch_id == batch_id
    assert lote.submission_id == submission_id
    assert lote.status == "completed"
    assert lote.decisao_parecer == "REPROVADO"
    assert lote.parecer_texto == "Parecer final confirmado."
    assert lote.confirmado_por == "analista.triade"
    assert lote.callback_recebido_em is not None
    assert lote.alterado_em > lote_alterado_em_original
    assert callback.alterado_em > callback_alterado_em_original
    assert documento.status == "completed"
    assert documento.decisao == "REPROVADO"
    assert documento.justificativa == "Documento divergente."
    assert documento.processed_at is not None
    assert anexo_triade.status_ia == "REPROVADO"
    assert anexo_triade.justificativa_ia == "Documento divergente."
    assert anexo_triade.alterado_em > anexo_alterado_em_original


def test_process_callback_marca_payload_duplicado_por_ids(
    settings, proponente_triade, loja_primeira, anexo_triade
):
    configure_triade_settings(settings)
    submission_service = TriadeSubmissionService()
    lote = submission_service.prepare_lote_envio(proponente_triade).lote
    batch_id = uuid4()
    submission_id = uuid4()
    payload = build_callback_payload(lote, anexo_triade, batch_id, submission_id)
    raw_payload = json.dumps(payload).encode("utf-8")
    payload_hash = hashlib.sha256(raw_payload).hexdigest()

    callback_processado = TriadeCallback.objects.create(
        delivery_id=uuid4(),
        lote=lote,
        external_batch_id=lote.external_batch_id,
        batch_id=batch_id,
        submission_id=submission_id,
        payload_bruto=raw_payload.decode("utf-8"),
        payload_hash=payload_hash,
        status_processamento=TriadeCallbackService.STATUS_PROCESSADO,
    )
    callback_duplicado = TriadeCallback.objects.create(
        delivery_id=uuid4(),
        lote=lote,
        external_batch_id=lote.external_batch_id,
        batch_id=batch_id,
        submission_id=submission_id,
        payload_bruto=raw_payload.decode("utf-8"),
        payload_hash=payload_hash,
        status_processamento=TriadeCallbackService.STATUS_RECEBIDO,
    )

    TriadeCallbackService().process_callback(callback_duplicado.id)

    callback_processado.refresh_from_db()
    callback_duplicado.refresh_from_db()
    assert (
        callback_processado.status_processamento
        == TriadeCallbackService.STATUS_PROCESSADO
    )
    assert (
        callback_duplicado.status_processamento
        == TriadeCallbackService.STATUS_DUPLICADO
    )


def test_process_callback_normaliza_status_e_decisao_recebidos_do_triade(
    settings, proponente_triade, loja_primeira, anexo_triade
):
    configure_triade_settings(settings)
    submission_service = TriadeSubmissionService()
    lote = submission_service.prepare_lote_envio(proponente_triade).lote
    batch_id = uuid4()
    submission_id = uuid4()
    payload = build_callback_payload(lote, anexo_triade, batch_id, submission_id)
    payload["status"] = "COMPLETED"
    payload["decisao_parecer"] = "pendencia"
    payload["documents"][0]["status"] = "PENDING_REVIEW"
    payload["documents"][0]["decisao"] = "pendencia"
    raw_payload = json.dumps(payload).encode("utf-8")

    callback = TriadeCallback.objects.create(
        delivery_id=uuid4(),
        lote=lote,
        external_batch_id=lote.external_batch_id,
        batch_id=batch_id,
        submission_id=submission_id,
        assinatura_recebida=sign_payload(settings.TRIADE_HMAC_SECRET, raw_payload),
        payload_bruto=raw_payload.decode("utf-8"),
        payload_hash=hashlib.sha256(raw_payload).hexdigest(),
        status_processamento=TriadeCallbackService.STATUS_RECEBIDO,
    )

    TriadeCallbackService().process_callback(callback.id)

    lote.refresh_from_db()
    anexo_triade.refresh_from_db()
    documento = TriadeDocumento.objects.get(
        lote=lote, external_document_id=str(anexo_triade.uuid)
    )

    assert lote.status == "completed"
    assert lote.decisao_parecer == "PENDENCIA"
    assert documento.status == "pending_review"
    assert documento.decisao == "PENDENCIA"
    assert anexo_triade.status_ia == "PENDENCIA"


def test_process_callback_reseta_status_e_retry_em_operational_error(
    settings, proponente_triade, loja_primeira, anexo_triade
):
    """Garante que erro transitório de banco não deixa o callback perdido:
    status volta para RECEBIDO e exceção transitória é levantada para o
    celery retentar via autoretry_for.
    """
    configure_triade_settings(settings)
    submission_service = TriadeSubmissionService()
    lote = submission_service.prepare_lote_envio(proponente_triade).lote
    batch_id = uuid4()
    submission_id = uuid4()
    payload = build_callback_payload(lote, anexo_triade, batch_id, submission_id)
    raw_payload = json.dumps(payload).encode("utf-8")

    callback = TriadeCallback.objects.create(
        delivery_id=uuid4(),
        lote=lote,
        external_batch_id=lote.external_batch_id,
        batch_id=batch_id,
        submission_id=submission_id,
        assinatura_recebida=sign_payload(settings.TRIADE_HMAC_SECRET, raw_payload),
        payload_bruto=raw_payload.decode("utf-8"),
        payload_hash=hashlib.sha256(raw_payload).hexdigest(),
        status_processamento=TriadeCallbackService.STATUS_RECEBIDO,
    )

    with patch(
        "sme_uniforme_apps.triade.callbacks.TriadeCallbackService._apply_payload_to_lote",
        side_effect=OperationalError("connection lost"),
    ):
        with pytest.raises(TriadeCallbackTransientError):
            TriadeCallbackService().process_callback(callback.id)

    callback.refresh_from_db()
    assert callback.status_processamento == TriadeCallbackService.STATUS_RECEBIDO
    assert callback.processado_em is None
    assert "Falha transitória" in callback.erro


def test_process_callback_mantem_excecao_transiente_quando_reset_status_falha(
    settings, proponente_triade, loja_primeira, anexo_triade
):
    configure_triade_settings(settings)
    submission_service = TriadeSubmissionService()
    lote = submission_service.prepare_lote_envio(proponente_triade).lote
    batch_id = uuid4()
    submission_id = uuid4()
    payload = build_callback_payload(lote, anexo_triade, batch_id, submission_id)
    raw_payload = json.dumps(payload).encode("utf-8")

    callback = TriadeCallback.objects.create(
        delivery_id=uuid4(),
        lote=lote,
        external_batch_id=lote.external_batch_id,
        batch_id=batch_id,
        submission_id=submission_id,
        assinatura_recebida=sign_payload(settings.TRIADE_HMAC_SECRET, raw_payload),
        payload_bruto=raw_payload.decode("utf-8"),
        payload_hash=hashlib.sha256(raw_payload).hexdigest(),
        status_processamento=TriadeCallbackService.STATUS_RECEBIDO,
    )

    with patch(
        "sme_uniforme_apps.triade.callbacks.TriadeCallbackService._apply_payload_to_lote",
        side_effect=OperationalError("connection lost"),
    ):
        with patch(
            "sme_uniforme_apps.triade.callbacks.queryset_update_with_alterado_em",
            side_effect=OperationalError("update failed"),
        ):
            with pytest.raises(TriadeCallbackTransientError):
                TriadeCallbackService().process_callback(callback.id)


def test_process_callback_marca_status_erro_em_excecao_permanente(
    settings, proponente_triade, loja_primeira, anexo_triade
):
    """Garante que bug de programação (exceção não transitória) NÃO é
    retentado: status vai para ERRO com processado_em preenchido.
    """
    configure_triade_settings(settings)
    submission_service = TriadeSubmissionService()
    lote = submission_service.prepare_lote_envio(proponente_triade).lote
    batch_id = uuid4()
    submission_id = uuid4()
    payload = build_callback_payload(lote, anexo_triade, batch_id, submission_id)
    raw_payload = json.dumps(payload).encode("utf-8")

    callback = TriadeCallback.objects.create(
        delivery_id=uuid4(),
        lote=lote,
        external_batch_id=lote.external_batch_id,
        batch_id=batch_id,
        submission_id=submission_id,
        assinatura_recebida=sign_payload(settings.TRIADE_HMAC_SECRET, raw_payload),
        payload_bruto=raw_payload.decode("utf-8"),
        payload_hash=hashlib.sha256(raw_payload).hexdigest(),
        status_processamento=TriadeCallbackService.STATUS_RECEBIDO,
    )

    with patch(
        "sme_uniforme_apps.triade.callbacks.TriadeCallbackService._apply_payload_to_lote",
        side_effect=KeyError("bug de programacao"),
    ):
        with pytest.raises(KeyError):
            TriadeCallbackService().process_callback(callback.id)

    callback.refresh_from_db()
    assert callback.status_processamento == TriadeCallbackService.STATUS_ERRO
    assert callback.processado_em is not None


def test_task_processar_callback_triade_tem_autoretry_configurado():
    """Garante que a task tem autoretry_for configurado para
    TriadeCallbackTransientError, com limite máximo de tentativas.
    """
    from sme_uniforme_apps.triade.tasks import processar_callback_triade

    assert TriadeCallbackTransientError in processar_callback_triade.autoretry_for
    assert processar_callback_triade.retry_kwargs.get("max_retries") == 6
    assert processar_callback_triade.retry_backoff == 2
