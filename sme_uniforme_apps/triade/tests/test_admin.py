import hashlib
import hmac
import json
from uuid import uuid4

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from model_bakery import baker

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
    assert "Decisao do lote" in conteudo
    assert "Status do documento" in conteudo
    assert "triade-card--status" in conteudo
    assert "triade-card--decision" in conteudo
    assert "Visao geral" in conteudo
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
