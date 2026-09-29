import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.forms.models import inlineformset_factory
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone

from ...admin import AnexosInLine, ProponenteAdmin
from ...models import Anexo, Proponente
from ...models.forms import AnexoForm

pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture
def admin_user():
    usuario = User.objects.create_superuser(email="gestor@teste.com", password="123456")
    usuario.first_name = "Gestor"
    usuario.last_name = "Contrato"
    usuario.save()
    return usuario


@pytest.fixture
def admin_client_logado(client, admin_user):
    client.force_login(admin_user)
    return client


def test_tela_admin_do_proponente_exibe_campos_ia_e_admin(admin_client_logado, anexo):
    response = admin_client_logado.get(
        reverse("admin:proponentes_proponente_change", args=[anexo.proponente.pk])
    )

    assert response.status_code == 200
    conteudo = response.content.decode("utf-8")
    assert "Status IA" in conteudo
    assert "Justificativa IA" in conteudo
    assert "Status Admin" in conteudo
    assert "Justificativa Admin" in conteudo
    assert 'name="anexos-0-status"' in conteudo
    assert 'name="anexos-0-status_ia"' not in conteudo
    assert 'name="anexos-0-justificativa_ia"' not in conteudo
    assert "proponentes/js/anexos-inline.js" not in conteudo
    assert "anexo-ia-justificativa" in conteudo
    assert "querySelector" in conteudo


def test_save_formset_do_admin_copia_justificativa_e_registra_auditoria(
    admin_user,
    proponente,
    anexo,
):
    site = AdminSite()
    model_admin = ProponenteAdmin(Proponente, site)
    formset_class = inlineformset_factory(
        Proponente,
        Anexo,
        form=AnexoForm,
        extra=0,
        can_delete=True,
    )
    prefix = formset_class.get_default_prefix()
    anexo.status_ia = Anexo.STATUS_REPROVADO
    anexo.justificativa_ia = "Documento divergente segundo a IA."
    anexo.save(update_fields=["status_ia", "justificativa_ia"])
    data = {
        f"{prefix}-TOTAL_FORMS": "1",
        f"{prefix}-INITIAL_FORMS": "1",
        f"{prefix}-MIN_NUM_FORMS": "0",
        f"{prefix}-MAX_NUM_FORMS": "1000",
        f"{prefix}-0-id": str(anexo.id),
        f"{prefix}-0-proponente": str(proponente.id),
        f"{prefix}-0-tipo_documento": str(anexo.tipo_documento_id),
        f"{prefix}-0-data_validade": "",
        f"{prefix}-0-status": Anexo.STATUS_REPROVADO,
        f"{prefix}-0-justificativa": "",
    }
    formset = formset_class(data=data, instance=proponente, prefix=prefix)

    assert formset.is_valid(), formset.errors

    request = RequestFactory().post("/")
    request.user = admin_user

    model_admin.save_formset(request, None, formset, change=True)

    anexo.refresh_from_db()

    assert anexo.justificativa == "Documento divergente segundo a IA."
    assert anexo.ultima_alteracao_admin_por == admin_user
    assert anexo.ultima_alteracao_admin_em is not None


def test_inline_exibe_informacao_de_auditoria_no_admin(
    admin_client_logado, admin_user, anexo
):
    anexo.ultima_alteracao_admin_por = admin_user
    anexo.ultima_alteracao_admin_em = timezone.now()
    anexo.save(
        update_fields=["ultima_alteracao_admin_por", "ultima_alteracao_admin_em"]
    )

    response = admin_client_logado.get(
        reverse("admin:proponentes_proponente_change", args=[anexo.proponente.pk])
    )

    assert response.status_code == 200
    conteudo = response.content.decode("utf-8")
    assert "anexo-auditoria" in conteudo
    assert "Gestor Contrato" in conteudo
    assert (
        timezone.localtime(anexo.ultima_alteracao_admin_em).strftime("%d/%m/%Y")
        in conteudo
    )


def test_inline_monta_texto_de_auditoria_com_nome_e_data(admin_user, anexo):
    inline = AnexosInLine(Proponente, AdminSite())
    anexo.ultima_alteracao_admin_por = admin_user
    anexo.ultima_alteracao_admin_em = timezone.now()

    texto = inline.ultima_alteracao_admin_info(anexo)

    assert "Gestor Contrato" in texto
    assert (
        timezone.localtime(anexo.ultima_alteracao_admin_em).strftime("%d/%m/%Y")
        in texto
    )


def test_inline_exibe_justificativa_ia_em_bloco_readonly_com_hook_js(anexo):
    inline = AnexosInLine(Proponente, AdminSite())
    anexo.status_ia = Anexo.STATUS_REPROVADO
    anexo.justificativa_ia = "Documento divergente segundo a IA."

    html = inline.justificativa_ia_info(anexo)

    assert "<details" in html
    assert "Documento divergente segundo a IA." in html
    assert "anexo-ia-justificativa" in html
    assert 'data-justificativa-ia="Documento divergente segundo a IA."' in html


def test_inline_remove_prefixo_analise_da_ia_do_data_atributo_para_hook_js(anexo):
    inline = AnexosInLine(Proponente, AdminSite())
    anexo.status_ia = Anexo.STATUS_REPROVADO
    anexo.justificativa_ia = (
        "Análise da IA: Documento divergente segundo a IA."
    )

    html = inline.justificativa_ia_info(anexo)

    assert 'data-justificativa-ia="Documento divergente segundo a IA."' in html
    assert (
        "Análise da IA: Documento divergente segundo a IA." in html
    ), "O texto completo com prefixo deve continuar visível no título e no corpo do details"


def test_inline_remove_prefixo_analise_da_ia_com_espacos_e_caixa_alta(anexo):
    inline = AnexosInLine(Proponente, AdminSite())
    anexo.status_ia = Anexo.STATUS_REPROVADO
    anexo.justificativa_ia = "   ANÁLISE DA IA:  Documento divergente."

    html = inline.justificativa_ia_info(anexo)

    assert 'data-justificativa-ia="Documento divergente."' in html


def test_inline_deixa_justificativa_ia_vazia_quando_nao_ha_texto(anexo):
    inline = AnexosInLine(Proponente, AdminSite())
    anexo.justificativa_ia = ""

    html = inline.justificativa_ia_info(anexo)

    assert "Sem justificativa de IA." not in html
    assert "<details" not in html
    assert 'data-justificativa-ia=""' in html


def test_inline_exibe_status_ia_em_formato_compacto(anexo):
    inline = AnexosInLine(Proponente, AdminSite())
    anexo.status_ia = Anexo.STATUS_REPROVADO

    html = inline.status_ia_info(anexo)

    assert "anexo-status-ia" in html
    assert "Reprovado" in html


def test_inline_exibe_status_ia_desconhecido_sem_choices_fixos(anexo):
    inline = AnexosInLine(Proponente, AdminSite())
    anexo.status_ia = "EM_ANALISE_EXTERNA_MANUAL"

    html = inline.status_ia_info(anexo)

    assert "EM_ANALISE_EXTERNA_MANUAL" in html
    assert "anexo-status-ia-em-analise-externa-manual" in html
