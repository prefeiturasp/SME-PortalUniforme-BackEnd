import hashlib
import hmac
import json
from uuid import uuid4
from unittest.mock import patch

import pytest

from sme_uniforme_apps.triade.models import TriadeCallback
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


def sign_payload(secret, payload_bytes):
    digest = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    return "sha256={}".format(digest)


def build_callback_payload(lote, anexo):
    return {
        "external_batch_id": lote.external_batch_id,
        "batch_id": str(uuid4()),
        "submission_id": str(uuid4()),
        "status": "completed",
        "documents": [
            {
                "external_document_id": str(anexo.uuid),
                "decisao": "APROVADO",
                "justificativa": "Documento validado.",
            }
        ],
    }


@patch(
    "sme_uniforme_apps.triade.views.transaction.on_commit",
    side_effect=lambda callback: callback(),
)
@patch("sme_uniforme_apps.triade.tasks.processar_callback_triade.delay")
def test_callback_endpoint_aceita_callback_assinado_e_enfileira_processamento(
    mock_delay,
    mock_on_commit,
    settings,
    client,
    proponente_triade,
    loja_primeira,
    anexo_triade,
):
    configure_triade_settings(settings)
    lote = TriadeSubmissionService().prepare_lote_envio(proponente_triade).lote
    payload = build_callback_payload(lote, anexo_triade)
    raw_payload = json.dumps(payload).encode("utf-8")
    delivery_id = uuid4()

    response = client.post(
        "/triade/callback/",
        data=raw_payload,
        content_type="application/json",
        HTTP_X_TRIADE_SIGNATURE=sign_payload(settings.TRIADE_HMAC_SECRET, raw_payload),
        HTTP_X_TRIADE_DELIVERY=str(delivery_id),
    )

    assert response.status_code == 202
    callback = TriadeCallback.objects.get(delivery_id=delivery_id)
    assert callback.status_processamento == "enfileirado"
    mock_on_commit.assert_called_once()
    mock_delay.assert_called_once_with(callback.id)


def test_callback_endpoint_rejeita_assinatura_invalida(
    settings, client, proponente_triade, loja_primeira, anexo_triade
):
    configure_triade_settings(settings)
    lote = TriadeSubmissionService().prepare_lote_envio(proponente_triade).lote
    payload = build_callback_payload(lote, anexo_triade)
    raw_payload = json.dumps(payload).encode("utf-8")

    response = client.post(
        "/triade/callback/",
        data=raw_payload,
        content_type="application/json",
        HTTP_X_TRIADE_SIGNATURE="sha256=assinatura-invalida",
        HTTP_X_TRIADE_DELIVERY=str(uuid4()),
    )

    assert response.status_code == 401


@patch(
    "sme_uniforme_apps.triade.views.transaction.on_commit",
    side_effect=lambda callback: callback(),
)
@patch("sme_uniforme_apps.triade.tasks.processar_callback_triade.delay")
def test_callback_endpoint_nao_reenfileira_delivery_duplicado(
    mock_delay,
    mock_on_commit,
    settings,
    client,
    proponente_triade,
    loja_primeira,
    anexo_triade,
):
    configure_triade_settings(settings)
    lote = TriadeSubmissionService().prepare_lote_envio(proponente_triade).lote
    payload = build_callback_payload(lote, anexo_triade)
    raw_payload = json.dumps(payload).encode("utf-8")
    delivery_id = uuid4()
    signature = sign_payload(settings.TRIADE_HMAC_SECRET, raw_payload)

    first_response = client.post(
        "/triade/callback/",
        data=raw_payload,
        content_type="application/json",
        HTTP_X_TRIADE_SIGNATURE=signature,
        HTTP_X_TRIADE_DELIVERY=str(delivery_id),
    )
    second_response = client.post(
        "/triade/callback/",
        data=raw_payload,
        content_type="application/json",
        HTTP_X_TRIADE_SIGNATURE=signature,
        HTTP_X_TRIADE_DELIVERY=str(delivery_id),
    )

    assert first_response.status_code == 202
    assert second_response.status_code == 200
    assert TriadeCallback.objects.filter(delivery_id=delivery_id).count() == 1
    mock_on_commit.assert_called_once()
    assert mock_delay.call_count == 1
