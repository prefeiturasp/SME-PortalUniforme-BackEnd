import hashlib
import hmac
import json
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from model_bakery import baker

from sme_uniforme_apps.triade.exceptions import TriadeTransientError
from sme_uniforme_apps.triade.models import (
    TriadeCallback,
    TriadeConfiguracao,
    TriadeDocumento,
    TriadeLote,
)
from sme_uniforme_apps.triade.services import TriadeSubmissionService

pytestmark = pytest.mark.django_db

User = get_user_model()


def configure_triade_settings(settings):
    settings.TRIADE_ENABLED = True
    settings.TRIADE_API_URL = "https://triade.exemplo.com"
    settings.TRIADE_API_TOKEN = "token-teste"
    settings.TRIADE_SOURCE_SYSTEM = "portal_uniforme"
    settings.TRIADE_SCHEMA_VERSION = "1.0"
    settings.TRIADE_TIMEOUT_SECONDS = 15
    settings.TRIADE_HMAC_SECRET = "segredo-triade"


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        email="gestor-triade@teste.com", password="123456"
    )


@pytest.fixture
def admin_client_logado(client, admin_user):
    client.force_login(admin_user)
    return client


def test_tela_admin_do_callback_exibe_payload_bruto_em_textarea_formatada(
    admin_client_logado, settings, proponente_triade, loja_primeira, anexo_triade
):
    configure_triade_settings(settings)
    lote = TriadeSubmissionService().prepare_lote_envio(proponente_triade).lote
    payload = {
        "external_batch_id": lote.external_batch_id,
        "status": "completed",
        "documents": [{"external_document_id": str(anexo_triade.uuid)}],
    }
    raw_payload = json.dumps(payload).encode("utf-8")

    callback = TriadeCallback.objects.create(
        delivery_id=uuid4(),
        lote=lote,
        external_batch_id=lote.external_batch_id,
        assinatura_recebida="sha256={}".format(
            hmac.new(
                settings.TRIADE_HMAC_SECRET.encode("utf-8"),
                raw_payload,
                hashlib.sha256,
            ).hexdigest()
        ),
        payload_bruto=raw_payload.decode("utf-8"),
        payload_hash=hashlib.sha256(raw_payload).hexdigest(),
        status_processamento="recebido",
    )

    response = admin_client_logado.get(
        reverse("admin:triade_triadecallback_change", args=[callback.pk])
    )

    assert response.status_code == 200
    conteudo = response.content.decode("utf-8")
    assert "Payload bruto" in conteudo
    assert "<textarea readonly" in conteudo
    assert lote.external_batch_id in conteudo


def test_tela_admin_da_configuracao_triade_exibe_flags_operacionais(
    admin_client_logado,
):
    configuracao = TriadeConfiguracao.objects.create(
        habilitado=False,
        enviar_apenas_documentos_obrigatorios=True,
    )

    response = admin_client_logado.get(
        reverse("admin:triade_triadeconfiguracao_change", args=[configuracao.pk])
    )

    assert response.status_code == 200
    conteudo = response.content.decode("utf-8")
    assert 'name="habilitado"' in conteudo
    assert 'name="enviar_apenas_documentos_obrigatorios"' in conteudo


def test_tela_admin_de_estatisticas_triade_consolida_quantitativos_e_filtra(
    admin_client_logado, proponente_triade
):
    lote_concluido = TriadeLote.objects.create(
        proponente=proponente_triade,
        external_batch_id="lote-concluido",
        status="COMPLETED",
        decisao_parecer="reprovado",
        source_system="portal_uniforme",
        schema_version="1.0",
    )
    lote_erro = TriadeLote.objects.create(
        external_batch_id="lote-erro",
        status="error",
        decisao_parecer="PENDENCIA",
        source_system="portal_uniforme",
        schema_version="1.0",
    )
    TriadeCallback.objects.create(
        lote=lote_concluido,
        delivery_id=uuid4(),
        external_batch_id=lote_concluido.external_batch_id,
        payload_hash="a" * 64,
        status_processamento="processado",
    )
    TriadeDocumento.objects.create(
        lote=lote_concluido,
        external_document_id="doc-aprovado",
        status="COMPLETED",
        decisao="aprovado",
    )
    TriadeDocumento.objects.create(
        lote=lote_erro,
        external_document_id="doc-reprovado",
        status="PENDING_REVIEW",
        decisao="REPROVADO",
    )

    response = admin_client_logado.get(
        reverse("admin:triade_triadeestatistica_changelist"),
        {
            "status_lote": "completed",
            "decisao_lote": "REPROVADO",
            "status_callback": "processado",
            "status_documento": "completed",
            "decisao_documento": "APROVADO",
        },
    )

    assert response.status_code == 200
    conteudo = response.content.decode("utf-8")
    assert "LOTES" in conteudo
    assert "CALLBACKS" in conteudo
    assert "DOCUMENTOS" in conteudo
    assert "Decisão do lote" in conteudo
    assert "Status do documento" in conteudo
    assert "triade-card--status" in conteudo
    assert "triade-card--decision" in conteudo
    assert "Visão geral" in conteudo
    assert response.context["metrics"]["lotes"]["total"] == 1
    assert response.context["metrics"]["lotes"]["status"]["completed"] == 1
    assert response.context["metrics"]["lotes"]["status"]["error"] == 0
    assert response.context["metrics"]["lotes"]["decisoes"]["REPROVADO"] == 1
    assert response.context["metrics"]["documentos"]["total"] == 1
    assert response.context["metrics"]["documentos"]["status"]["completed"] == 1
    assert response.context["metrics"]["documentos"]["decisoes"]["APROVADO"] == 1
    assert response.context["metrics"]["callbacks"]["status"]["processado"] == 1
    assert "pending_review" in [
        item["value"] for item in response.context["catalog"]["lotes"]["status"]
    ]
    assert response.context["recent_lotes"][0].external_batch_id == "lote-concluido"


def _changelist_url():
    return reverse("admin:triade_triadelote_changelist")


@patch("sme_uniforme_apps.triade.admin.reprocessar_lote_triade.delay")
def test_action_retomar_processamento_agenda_task_sem_limpar_estado(
    mock_delay, admin_client_logado, settings, proponente_triade
):
    """Retomada do lote deve apenas agendar o reprocessamento do mesmo
    snapshot local, sem limpar batch_id, payload ou documentos.
    """
    configure_triade_settings(settings)
    lote = TriadeLote.objects.create(
        proponente=proponente_triade,
        external_batch_id="proponente-{}".format(proponente_triade.uuid),
        source_system="portal_uniforme",
        schema_version="1.0",
        status="error",
        batch_id=uuid4(),
        submission_id=uuid4(),
        payload_envio='{"applicant":{"name":"antigo"}}',
        metadata='{"k":"v"}',
        status_http_criacao=201,
        resposta_criacao='{"ok":true}',
        status_http_inicio=422,
        resposta_inicio='{"detail":"erro"}',
        ultimo_erro="Falha no /start",
        enviado_em="2026-01-01 00:00:00+00:00",
        iniciado_em="2026-01-01 00:00:01+00:00",
    )
    TriadeDocumento.objects.create(
        lote=lote,
        external_document_id="doc-1",
        document_type="cartao_cnpj",
    )

    response = admin_client_logado.post(
        _changelist_url(),
        data={
            "action": "retomar_processamento_na_triade",
            "_selected_action": [str(lote.pk)],
        },
    )

    assert response.status_code == 302
    assert mock_delay.call_count == 1
    args = mock_delay.call_args.args
    assert len(args) == 1
    assert args[0] == lote.id

    lote.refresh_from_db()
    assert lote.payload_envio == '{"applicant":{"name":"antigo"}}'
    assert json.loads(lote.metadata) == {"k": "v"}
    assert lote.batch_id is not None
    assert lote.submission_id is not None
    assert lote.status_http_criacao == 201
    assert lote.status_http_inicio == 422
    assert lote.ultimo_erro == "Falha no /start"
    assert lote.enviado_em is not None
    assert lote.iniciado_em is not None
    assert TriadeDocumento.objects.filter(lote=lote).count() == 1


@patch("sme_uniforme_apps.triade.admin.reprocessar_lote_triade.delay")
def test_action_retomar_processamento_ignora_status_terminal(
    mock_delay, admin_client_logado, settings, proponente_triade
):
    """Lote em status terminal não entra na retomada do mesmo snapshot."""
    configure_triade_settings(settings)
    lote = TriadeLote.objects.create(
        proponente=proponente_triade,
        external_batch_id="lote-concluido",
        source_system="portal_uniforme",
        schema_version="1.0",
        status="completed",
        batch_id=uuid4(),
    )

    response = admin_client_logado.post(
        _changelist_url(),
        data={
            "action": "retomar_processamento_na_triade",
            "_selected_action": [str(lote.pk)],
        },
    )

    assert response.status_code == 302
    assert mock_delay.call_count == 0

    lote.refresh_from_db()
    assert lote.status == "completed"
    assert lote.batch_id is not None


@patch("sme_uniforme_apps.triade.admin.reprocessar_lote_triade.delay")
def test_action_retomar_processamento_ignora_lote_sem_batch_e_sem_snapshot(
    mock_delay, admin_client_logado, settings, proponente_triade
):
    """Sem batch_id e sem payload persistido, nao ha como retomar o
    mesmo lote na TRIADE.
    """
    configure_triade_settings(settings)
    lote = TriadeLote.objects.create(
        proponente=proponente_triade,
        external_batch_id="lote-sem-snapshot",
        source_system="portal_uniforme",
        schema_version="1.0",
        status="error",
        payload_envio=None,
        batch_id=None,
    )

    response = admin_client_logado.post(
        _changelist_url(),
        data={
            "action": "retomar_processamento_na_triade",
            "_selected_action": [str(lote.pk)],
        },
    )

    assert response.status_code == 302
    assert mock_delay.call_count == 0

    lote.refresh_from_db()
    assert lote.status == "error"


@patch("sme_uniforme_apps.triade.admin.reprocessar_lote_triade.delay")
def test_action_retomar_processamento_ignora_erro_permanente_de_criacao(
    mock_delay, admin_client_logado, settings, proponente_triade
):
    configure_triade_settings(settings)
    lote = TriadeLote.objects.create(
        proponente=proponente_triade,
        external_batch_id="lote-erro-permanente",
        source_system="portal_uniforme",
        schema_version="1.0",
        status="error",
        payload_envio='{"documents":[]}',
        batch_id=None,
        status_http_criacao=422,
    )

    response = admin_client_logado.post(
        _changelist_url(),
        data={
            "action": "retomar_processamento_na_triade",
            "_selected_action": [str(lote.pk)],
        },
    )

    assert response.status_code == 302
    assert mock_delay.call_count == 0

    lote.refresh_from_db()
    assert lote.status == "error"


@patch("sme_uniforme_apps.triade.admin.reprocessar_lote_triade.delay")
def test_action_retomar_processamento_processa_lote_misto(
    mock_delay, admin_client_logado, settings, proponente_triade
):
    """Mistura de lotes: um em error com snapshot (agenda), um em
    completed (ignora), um sem batch nem snapshot (ignora).
    """
    configure_triade_settings(settings)
    lote_reenviavel = TriadeLote.objects.create(
        proponente=proponente_triade,
        external_batch_id="proponente-{}".format(proponente_triade.uuid),
        source_system="portal_uniforme",
        schema_version="1.0",
        status="error",
        batch_id=uuid4(),
        payload_envio='{"documents":[]}',
    )
    lote_terminal = TriadeLote.objects.create(
        proponente=proponente_triade,
        external_batch_id="lote-terminal",
        source_system="portal_uniforme",
        schema_version="1.0",
        status="completed",
        batch_id=uuid4(),
    )
    lote_sem_snapshot = TriadeLote.objects.create(
        proponente=proponente_triade,
        external_batch_id="lote-sem-snapshot",
        source_system="portal_uniforme",
        schema_version="1.0",
        status="payload_ready",
        payload_envio=None,
        batch_id=None,
    )

    response = admin_client_logado.post(
        _changelist_url(),
        data={
            "action": "retomar_processamento_na_triade",
            "_selected_action": [
                str(lote_reenviavel.pk),
                str(lote_terminal.pk),
                str(lote_sem_snapshot.pk),
            ],
        },
    )

    assert response.status_code == 302
    assert mock_delay.call_count == 1
    args = mock_delay.call_args.args
    assert len(args) == 1
    assert args[0] == lote_reenviavel.id

    lote_reenviavel.refresh_from_db()
    lote_terminal.refresh_from_db()
    lote_sem_snapshot.refresh_from_db()
    assert lote_reenviavel.batch_id is not None
    assert lote_terminal.status == "completed"
    assert lote_terminal.batch_id is not None
    assert lote_sem_snapshot.status == "payload_ready"


class _DummyTriadeResponse:
    def __init__(self, status_code, data=None, text=None):
        self.status_code = status_code
        self.data = data
        self.text = text if text is not None else json.dumps(data or {})

    @property
    def is_success(self):
        return 200 <= self.status_code < 300

    def json(self):
        if self.data is None:
            raise ValueError("response without json")
        return self.data


@patch("sme_uniforme_apps.triade.services.TriadeHttpClient.get_batch")
def test_action_sincronizar_atualiza_status_metadata_e_documentos(
    mock_get_batch, admin_client_logado, settings, proponente_triade, anexo_triade
):
    """Sync bem-sucedido: status e metadata do lote sao atualizados,
    e os TriadeDocumento do lote ganham status/processed_at vindos
    do GET.
    """
    configure_triade_settings(settings)
    batch_id = uuid4()
    document_id = uuid4()
    lote = TriadeLote.objects.create(
        proponente=proponente_triade,
        external_batch_id="proponente-{}".format(proponente_triade.uuid),
        source_system="portal_uniforme",
        schema_version="1.0",
        status="processing",
        batch_id=batch_id,
        decisao_parecer="APROVADO",
        parecer_texto="Parecer original do callback",
    )
    documento_local = TriadeDocumento.objects.create(
        lote=lote,
        anexo=anexo_triade,
        external_document_id=str(anexo_triade.uuid),
        document_type="cartao_cnpj",
        status="received",
    )
    decisao_original = lote.decisao_parecer

    mock_get_batch.return_value = _DummyTriadeResponse(
        200,
        {
            "batch_id": str(batch_id),
            "status": "completed",
            "metadata": {"edital": "2026", "atualizado": "sim"},
            "documents": [
                {
                    "external_document_id": str(anexo_triade.uuid),
                    "document_id": str(document_id),
                    "status": "completed",
                    "processed_at": "2026-05-31T12:00:00Z",
                    "error": None,
                    "metadata": {"origem": "sync"},
                }
            ],
        },
    )

    response = admin_client_logado.post(
        _changelist_url(),
        data={
            "action": "sincronizar_com_triade",
            "_selected_action": [str(lote.pk)],
        },
    )

    assert response.status_code == 302
    assert mock_get_batch.call_count == 1
    assert mock_get_batch.call_args.args == (str(batch_id),)

    lote.refresh_from_db()
    assert lote.status == "completed"
    assert json.loads(lote.metadata) == {"edital": "2026", "atualizado": "sim"}
    assert lote.ultimo_erro is None
    assert lote.decisao_parecer == decisao_original

    documento_local.refresh_from_db()
    assert documento_local.status == "completed"
    assert documento_local.document_id == document_id
    assert documento_local.processed_at is not None
    assert json.loads(documento_local.metadata) == {"origem": "sync"}


@patch("sme_uniforme_apps.triade.services.TriadeHttpClient.get_batch")
def test_action_sincronizar_ignora_lote_sem_batch_id(
    mock_get_batch, admin_client_logado, settings, proponente_triade
):
    """Lote sem batch_id (TRIADE nunca aceitou) NAO pode ser
    consultado por GET.
    """
    configure_triade_settings(settings)
    lote = TriadeLote.objects.create(
        proponente=proponente_triade,
        external_batch_id="lote-sem-batch",
        source_system="portal_uniforme",
        schema_version="1.0",
        status="payload_ready",
    )

    response = admin_client_logado.post(
        _changelist_url(),
        data={
            "action": "sincronizar_com_triade",
            "_selected_action": [str(lote.pk)],
        },
    )

    assert response.status_code == 302
    assert mock_get_batch.call_count == 0

    lote.refresh_from_db()
    assert lote.status == "payload_ready"


@patch("sme_uniforme_apps.triade.services.TriadeHttpClient.get_batch")
def test_action_sincronizar_registra_erro_em_resposta_nao_sucesso(
    mock_get_batch, admin_client_logado, settings, proponente_triade
):
    """Resposta 5xx ou 404 do TRIADE: registra em ultimo_erro e
    nao altera status do lote.
    """
    configure_triade_settings(settings)
    lote = TriadeLote.objects.create(
        proponente=proponente_triade,
        external_batch_id="proponente-{}".format(proponente_triade.uuid),
        source_system="portal_uniforme",
        schema_version="1.0",
        status="processing",
        batch_id=uuid4(),
    )

    mock_get_batch.return_value = _DummyTriadeResponse(
        503, data=None, text="upstream down"
    )

    response = admin_client_logado.post(
        _changelist_url(),
        data={
            "action": "sincronizar_com_triade",
            "_selected_action": [str(lote.pk)],
        },
    )

    assert response.status_code == 302
    assert mock_get_batch.call_count == 1

    lote.refresh_from_db()
    assert lote.status == "processing"
    assert "503" in lote.ultimo_erro


@patch("sme_uniforme_apps.triade.services.TriadeHttpClient.get_batch")
def test_action_sincronizar_registra_erro_transiente_de_comunicacao(
    mock_get_batch, admin_client_logado, settings, proponente_triade
):
    configure_triade_settings(settings)
    lote = TriadeLote.objects.create(
        proponente=proponente_triade,
        external_batch_id="lote-timeout",
        source_system="portal_uniforme",
        schema_version="1.0",
        status="processing",
        batch_id=uuid4(),
    )

    mock_get_batch.side_effect = TriadeTransientError("timeout upstream")

    response = admin_client_logado.post(
        _changelist_url(),
        data={
            "action": "sincronizar_com_triade",
            "_selected_action": [str(lote.pk)],
        },
    )

    assert response.status_code == 302
    assert mock_get_batch.call_count == 1

    lote.refresh_from_db()
    assert lote.status == "processing"
    assert "timeout upstream" in lote.ultimo_erro


@patch("sme_uniforme_apps.triade.services.TriadeHttpClient.get_batch")
def test_action_sincronizar_processa_lote_misto(
    mock_get_batch, admin_client_logado, settings, proponente_triade
):
    """Mistura: um com batch_id e GET ok, um sem batch_id, um com
    GET retornando 404.
    """
    configure_triade_settings(settings)
    lote_sync = TriadeLote.objects.create(
        proponente=proponente_triade,
        external_batch_id="lote-sync",
        source_system="portal_uniforme",
        schema_version="1.0",
        status="processing",
        batch_id=uuid4(),
    )
    lote_sem_batch = TriadeLote.objects.create(
        proponente=proponente_triade,
        external_batch_id="lote-sem-batch",
        source_system="portal_uniforme",
        schema_version="1.0",
        status="error",
    )
    lote_404 = TriadeLote.objects.create(
        proponente=proponente_triade,
        external_batch_id="lote-404",
        source_system="portal_uniforme",
        schema_version="1.0",
        status="processing",
        batch_id=uuid4(),
    )

    def fake_get_batch(batch_id_str):
        if str(lote_sync.batch_id) == batch_id_str:
            return _DummyTriadeResponse(
                200, {"batch_id": batch_id_str, "status": "completed"}
            )
        return _DummyTriadeResponse(404, data=None, text="not found")

    mock_get_batch.side_effect = fake_get_batch

    response = admin_client_logado.post(
        _changelist_url(),
        data={
            "action": "sincronizar_com_triade",
            "_selected_action": [
                str(lote_sync.pk),
                str(lote_sem_batch.pk),
                str(lote_404.pk),
            ],
        },
    )

    assert response.status_code == 302
    assert mock_get_batch.call_count == 2

    lote_sync.refresh_from_db()
    lote_sem_batch.refresh_from_db()
    lote_404.refresh_from_db()
    assert lote_sync.status == "completed"
    assert lote_sem_batch.status == "error"
    assert "404" in lote_404.ultimo_erro
