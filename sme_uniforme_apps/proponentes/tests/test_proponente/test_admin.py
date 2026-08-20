from datetime import datetime
from uuid import uuid4

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from sme_uniforme_apps.triade.models import TriadeLote
from sme_uniforme_apps.triade.statuses import TRIADE_LOTE_STATUS_LABELS

from ...admin import ProponenteAdmin
from ...models import Proponente

pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        email="gestor-triade@teste.com", password="123456"
    )


@pytest.fixture
def admin_client_logado(client, admin_user):
    client.force_login(admin_user)
    return client


@pytest.fixture
def model_admin():
    return ProponenteAdmin(Proponente, AdminSite())


def _cria_lote(proponente, status, criado_em):
    lote = TriadeLote.objects.create(
        proponente=proponente,
        external_batch_id="lote-{}".format(uuid4()),
        status=status,
    )
    TriadeLote.objects.filter(pk=lote.pk).update(criado_em=criado_em)
    return lote


def test_validacao_triade_exibe_label_do_status(proponente, model_admin):
    _cria_lote(
        proponente,
        status="processing",
        criado_em=timezone.make_aware(datetime(2026, 6, 1)),
    )

    valor = model_admin.validacao_triade(proponente)

    assert valor == TRIADE_LOTE_STATUS_LABELS["processing"]
    assert valor != "processing"


def test_validacao_triade_usa_lote_mais_recente_por_criado_em(proponente, model_admin):
    _cria_lote(
        proponente,
        status="completed",
        criado_em=timezone.make_aware(datetime(2026, 1, 1)),
    )
    _cria_lote(
        proponente,
        status="processing",
        criado_em=timezone.make_aware(datetime(2026, 6, 1)),
    )

    assert model_admin.validacao_triade(proponente) == "Em processamento"


def test_validacao_triade_sem_lote_exibe_placeholder(proponente, model_admin):
    assert model_admin.validacao_triade(proponente) == "-"


def test_validacao_triade_normaliza_status_antes_de_rotular(proponente, model_admin):
    _cria_lote(
        proponente,
        status="  PROCESSING  ",
        criado_em=timezone.make_aware(datetime(2026, 6, 1)),
    )

    assert model_admin.validacao_triade(proponente) == "Em processamento"


def test_validacao_triade_fica_imediatamente_apos_protocolo_no_list_display(model_admin):
    posicao_protocolo = model_admin.list_display.index("protocolo")

    assert model_admin.list_display[posicao_protocolo + 1] == "validacao_triade"


def test_get_queryset_prefetch_lotes_sem_n_plus_1(admin_user, model_admin):
    proponentes_criados = [
        baker.make(
            "Proponente",
            cnpj="00.529.476/0001-{:02d}".format(i),
            email="prefetch-{}@teste.com".format(i),
            razao_social="Teste",
            end_cep="99999-000",
            telefone="(99) 99999-9999",
            responsavel="Fulano",
        )
        for i in range(1, 4)
    ]

    proponente_1 = proponentes_criados[0]
    proponente_2 = proponentes_criados[1]
    proponente_3 = proponentes_criados[2]

    lote_antigo = _cria_lote(
        proponente_1,
        status="completed",
        criado_em=timezone.make_aware(datetime(2026, 1, 1)),
    )
    lote_recente = _cria_lote(
        proponente_1,
        status="processing",
        criado_em=timezone.make_aware(datetime(2026, 6, 1)),
    )
    _cria_lote(
        proponente_2,
        status="error",
        criado_em=timezone.make_aware(datetime(2026, 6, 1)),
    )

    request = RequestFactory().get("/")
    request.user = admin_user
    queryset = model_admin.get_queryset(request)

    with CaptureQueriesContext(connection) as ctx:
        proponentes = list(queryset)

    assert len(ctx.captured_queries) == 2

    proponente_1_carregado = next(p for p in proponentes if p.pk == proponente_1.pk)

    assert proponente_1_carregado.triade_lotes.all()[0] == lote_recente
    assert [lote.id for lote in proponente_1_carregado.triade_lotes.all()] == [
        lote_recente.id,
        lote_antigo.id,
    ]

    with CaptureQueriesContext(connection) as ctx:
        valores = {
            p.pk: model_admin.validacao_triade(p) for p in proponentes
        }

    assert len(ctx.captured_queries) == 0
    assert valores == {
        proponente_1.pk: "Em processamento",
        proponente_2.pk: "Erro",
        proponente_3.pk: "-",
    }


def test_changelist_exibe_coluna_validacao_triade(admin_client_logado, proponente):
    _cria_lote(
        proponente,
        status="processing",
        criado_em=timezone.make_aware(datetime(2026, 6, 1)),
    )

    response = admin_client_logado.get(
        reverse("admin:proponentes_proponente_changelist")
    )

    assert response.status_code == 200
    conteudo = response.content.decode("utf-8")
    assert "Validação TRIADE" in conteudo
    assert "Em processamento" in conteudo