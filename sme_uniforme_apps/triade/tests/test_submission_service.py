import json
from uuid import uuid4
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from sme_uniforme_apps.triade.exceptions import (
    TriadePermanentError,
    TriadeTransientError,
)
from sme_uniforme_apps.triade.models import TriadeConfiguracao, TriadeDocumento
from sme_uniforme_apps.triade.services import TriadeSubmissionService

pytestmark = pytest.mark.django_db


class DummyResponse:
    def __init__(self, status_code, payload=None, text=None):
        self.status_code = status_code
        self._payload = payload
        self.text = text if text is not None else json.dumps(payload or {})

    def json(self):
        if self._payload is None:
            raise ValueError("response without json")
        return self._payload


def configure_triade_settings(settings):
    settings.TRIADE_ENABLED = True
    settings.TRIADE_API_URL = "https://triade.exemplo.com"
    settings.TRIADE_API_TOKEN = "token-teste"
    settings.TRIADE_SOURCE_SYSTEM = "portal_uniforme"
    settings.TRIADE_SCHEMA_VERSION = "1.0"
    settings.TRIADE_TIMEOUT_SECONDS = 15
    settings.TRIADE_SEND_ONLY_REQUIRED_DOCUMENTS = False


def test_prepare_lote_reconstroi_payload_persistido_quando_lote_ainda_nao_tem_batch_id(
    settings, proponente_triade, loja_primeira, anexo_triade
):
    configure_triade_settings(settings)
    service = TriadeSubmissionService()

    prepared = service.prepare_lote_envio(proponente_triade)
    lote = prepared.lote
    assert prepared.created is True
    assert prepared.reused_payload is False
    assert lote.external_batch_id == "proponente-{}".format(proponente_triade.uuid)

    payload_antigo = json.loads(lote.payload_envio)
    del payload_antigo["applicant"]["fields"]["ponto-venda"][0]["cidade"]
    del payload_antigo["applicant"]["fields"]["ponto-venda"][0]["uf"]
    lote.payload_envio = json.dumps(payload_antigo)
    lote.save(update_fields=("payload_envio",))

    prepared_rebuild = service.prepare_lote_envio(proponente_triade)

    assert prepared_rebuild.lote.id == lote.id
    assert prepared_rebuild.created is False
    assert prepared_rebuild.reused_payload is False
    assert (
        prepared_rebuild.payload["applicant"]["fields"]["ponto-venda"][0]["cidade"]
        == "São Paulo"
    )
    assert (
        prepared_rebuild.payload["applicant"]["fields"]["ponto-venda"][0]["uf"] == "SP"
    )


def test_prepare_lote_reusa_external_batch_id_e_payload_persistido_quando_ja_tem_batch_id(
    settings, proponente_triade, loja_primeira, anexo_triade
):
    configure_triade_settings(settings)
    service = TriadeSubmissionService()

    prepared = service.prepare_lote_envio(proponente_triade)
    lote = prepared.lote
    lote.batch_id = uuid4()
    lote.save(update_fields=("batch_id",))

    proponente_triade.razao_social = "Empresa Alterada Depois Do Primeiro Snapshot"
    proponente_triade.save(update_fields=("razao_social",))

    prepared_reuse = service.prepare_lote_envio(proponente_triade)

    assert prepared_reuse.lote.id == lote.id
    assert prepared_reuse.created is False
    assert prepared_reuse.reused_payload is True
    assert prepared_reuse.payload["applicant"]["name"] == "Empresa Teste LTDA"


def test_prepare_lote_envia_so_documentos_obrigatorios_quando_configurado_no_banco(
    settings, proponente_triade, loja_primeira, anexo_triade
):
    configure_triade_settings(settings)
    TriadeConfiguracao.objects.create(
        habilitado=True,
        enviar_apenas_documentos_obrigatorios=True,
    )
    tipo_documento_opcional = baker.make(
        "TipoDocumento",
        identificador="alvara_funcionamento",
        nome="Alvara de funcionamento",
        obrigatorio=False,
        visivel=True,
    )
    anexo_opcional = baker.make(
        "Anexo",
        proponente=proponente_triade,
        tipo_documento=tipo_documento_opcional,
        arquivo=SimpleUploadedFile(
            "alvara_funcionamento.pdf",
            b"%PDF-1.4 documento opcional",
            content_type="application/pdf",
        ),
    )

    prepared = TriadeSubmissionService().prepare_lote_envio(proponente_triade)

    external_document_ids = [
        documento["external_document_id"] for documento in prepared.payload["documents"]
    ]

    assert str(anexo_triade.uuid) in external_document_ids
    assert str(anexo_opcional.uuid) not in external_document_ids
    assert TriadeDocumento.objects.filter(lote=prepared.lote).count() == len(
        external_document_ids
    )


@patch("sme_uniforme_apps.triade.client.requests.Session.request")
def test_dispatch_proponente_envia_lote_e_inicia_pipeline(
    mock_request, settings, proponente_triade, loja_primeira, anexo_triade
):
    configure_triade_settings(settings)
    batch_id = uuid4()
    submission_id = uuid4()
    mock_request.side_effect = [
        DummyResponse(
            201,
            {
                "batch_id": str(batch_id),
                "submission_id": str(submission_id),
                "analysis_desk_id": "mesa-portal-uniforme",
                "status": "received",
            },
        ),
        DummyResponse(202, {"status": "processing"}),
    ]

    lote = TriadeSubmissionService().dispatch_proponente_uuid(
        str(proponente_triade.uuid)
    )
    lote.refresh_from_db()

    assert mock_request.call_count == 2
    assert (
        mock_request.call_args_list[0].kwargs["url"]
        == "https://triade.exemplo.com/integration/v1/batches"
    )
    assert (
        mock_request.call_args_list[0].kwargs["json"]["external_batch_id"]
        == lote.external_batch_id
    )
    assert mock_request.call_args_list[1].kwargs[
        "url"
    ] == "https://triade.exemplo.com/integration/v1/submissions/{}/start".format(
        batch_id
    )
    assert lote.batch_id == batch_id
    assert lote.submission_id == submission_id
    assert lote.status_http_criacao == 201
    assert lote.status_http_inicio == 202
    assert lote.status == "processing"
    assert lote.enviado_em is not None
    assert lote.iniciado_em is not None
    assert lote.payload_envio
    assert lote.ultimo_erro is None

    documento = TriadeDocumento.objects.get(lote=lote, anexo=anexo_triade)
    assert documento.anexo_id == anexo_triade.id
    assert documento.external_document_id == str(anexo_triade.uuid)
    assert documento.document_type == anexo_triade.tipo_documento.identificador
    assert TriadeDocumento.objects.filter(lote=lote).count() == 3


@patch("sme_uniforme_apps.triade.client.requests.Session.request")
def test_dispatch_persiste_submission_id_retornado_no_start_quando_nao_veio_na_criacao(
    mock_request, settings, proponente_triade, loja_primeira, anexo_triade
):
    configure_triade_settings(settings)
    batch_id = uuid4()
    submission_id = uuid4()
    mock_request.side_effect = [
        DummyResponse(
            201,
            {
                "batch_id": str(batch_id),
                "status": "RECEIVED",
            },
        ),
        DummyResponse(
            200,
            {
                "submission_id": str(submission_id),
                "analysis_desk_id": "mesa-retorno-start",
                "status": "PROCESSING",
            },
        ),
    ]

    lote = TriadeSubmissionService().dispatch_proponente_uuid(
        str(proponente_triade.uuid)
    )
    lote.refresh_from_db()

    assert lote.batch_id == batch_id
    assert lote.submission_id == submission_id
    assert lote.analysis_desk_id == "mesa-retorno-start"
    assert lote.status_http_inicio == 200
    assert lote.status == "processing"


@patch("sme_uniforme_apps.triade.client.requests.Session.request")
def test_dispatch_trata_409_do_start_como_sucesso_idempotente(
    mock_request, settings, proponente_triade, loja_primeira, anexo_triade
):
    configure_triade_settings(settings)
    batch_id = uuid4()
    submission_id = uuid4()
    mock_request.side_effect = [
        DummyResponse(
            201,
            {
                "batch_id": str(batch_id),
                "submission_id": str(submission_id),
                "status": "received",
            },
        ),
        DummyResponse(409, {"detail": "pipeline ja iniciado"}),
    ]

    lote = TriadeSubmissionService().dispatch_proponente_uuid(
        str(proponente_triade.uuid)
    )
    lote.refresh_from_db()

    assert lote.status_http_inicio == 409
    assert lote.status == "processing"
    assert lote.iniciado_em is not None
    assert lote.ultimo_erro is None


@patch("sme_uniforme_apps.triade.client.requests.Session.request")
def test_dispatch_com_409_no_start_preserva_status_terminal_do_lote(
    mock_request, settings, proponente_triade, loja_primeira, anexo_triade
):
    configure_triade_settings(settings)
    service = TriadeSubmissionService()
    prepared = service.prepare_lote_envio(proponente_triade)
    lote = prepared.lote
    lote.batch_id = uuid4()
    lote.status = "completed"
    lote.save(update_fields=("batch_id", "status"))
    mock_request.side_effect = [DummyResponse(409, {"detail": "pipeline ja iniciado"})]

    lote = service.dispatch_proponente_uuid(str(proponente_triade.uuid))
    lote.refresh_from_db()

    assert mock_request.call_count == 1
    assert lote.status_http_inicio == 409
    assert lote.status == "completed"
    assert lote.ultimo_erro is None


@patch("sme_uniforme_apps.triade.client.requests.Session.request")
def test_retry_lote_sem_batch_id_reusa_snapshot_persistido(
    mock_request, settings, proponente_triade, loja_primeira, anexo_triade
):
    configure_triade_settings(settings)
    service = TriadeSubmissionService()
    prepared = service.prepare_lote_envio(proponente_triade)
    lote = prepared.lote
    payload_snapshot = json.loads(lote.payload_envio)
    batch_id = uuid4()

    proponente_triade.razao_social = "Empresa Alterada Depois Do Snapshot"
    proponente_triade.save(update_fields=("razao_social",))

    mock_request.side_effect = [
        DummyResponse(201, {"batch_id": str(batch_id), "status": "received"}),
        DummyResponse(200, {"status": "processing"}),
    ]

    lote = service.retry_lote(lote)
    lote.refresh_from_db()

    assert mock_request.call_count == 2
    assert (
        mock_request.call_args_list[0].kwargs["json"]["applicant"]["name"]
        == payload_snapshot["applicant"]["name"]
    )
    assert mock_request.call_args_list[0].kwargs["json"]["applicant"]["name"] == (
        "Empresa Teste LTDA"
    )
    assert lote.batch_id == batch_id
    assert lote.status == "processing"


@patch("sme_uniforme_apps.triade.client.requests.Session.request")
def test_retry_lote_com_batch_id_apenas_reinicia_pipeline(
    mock_request, settings, proponente_triade, loja_primeira, anexo_triade
):
    configure_triade_settings(settings)
    service = TriadeSubmissionService()
    lote = service.prepare_lote_envio(proponente_triade).lote
    lote.batch_id = uuid4()
    lote.status = "error"
    lote.save(update_fields=("batch_id", "status"))
    mock_request.side_effect = [DummyResponse(409, {"detail": "pipeline ja iniciado"})]

    lote = service.retry_lote(lote)
    lote.refresh_from_db()

    assert mock_request.call_count == 1
    assert mock_request.call_args.kwargs["url"] == (
        "https://triade.exemplo.com/integration/v1/submissions/{}/start".format(
            lote.batch_id
        )
    )
    assert lote.status_http_inicio == 409


def test_retry_lote_falha_sem_batch_id_e_sem_payload_persistido(
    settings, proponente_triade, loja_primeira, anexo_triade
):
    configure_triade_settings(settings)
    service = TriadeSubmissionService()
    lote = service.prepare_lote_envio(proponente_triade).lote
    lote.status = "error"
    lote.payload_envio = None
    lote.batch_id = None
    lote.save(update_fields=("status", "payload_envio", "batch_id"))

    with pytest.raises(TriadePermanentError, match="batch_id ou payload_envio"):
        service.retry_lote(lote)


def test_retry_lote_falha_quando_criacao_anterior_foi_erro_permanente(
    settings, proponente_triade, loja_primeira, anexo_triade
):
    configure_triade_settings(settings)
    service = TriadeSubmissionService()
    lote = service.prepare_lote_envio(proponente_triade).lote
    lote.status = "error"
    lote.batch_id = None
    lote.status_http_criacao = 422
    lote.save(update_fields=("status", "batch_id", "status_http_criacao"))

    with pytest.raises(TriadePermanentError, match="erro permanente de payload"):
        service.retry_lote(lote)


def test_task_reprocessar_lote_triade_tem_autoretry_configurado():
    from sme_uniforme_apps.triade.tasks import reprocessar_lote_triade

    assert TriadeTransientError in reprocessar_lote_triade.autoretry_for
    assert reprocessar_lote_triade.retry_kwargs.get("max_retries") == 6
    assert reprocessar_lote_triade.retry_backoff == 2
