import pytest
from django.contrib import admin

from sme_uniforme_apps.proponentes.admin import TipoDocumentoAdmin
from sme_uniforme_apps.proponentes.models import TipoDocumento
from sme_uniforme_apps.proponentes.models.forms import TipoDocumentoAdminForm

pytestmark = pytest.mark.django_db


def test_instancia(tipo_documento):
    assert isinstance(tipo_documento, TipoDocumento)
    assert tipo_documento.identificador
    assert tipo_documento.nome
    assert tipo_documento.obrigatorio
    assert tipo_documento.visivel


def test_srt_model(tipo_documento):
    assert tipo_documento.__str__() == 'Certidão Negativa (obrigatório)'


def test_meta_modelo(tipo_documento):
    assert tipo_documento._meta.verbose_name == 'Tipo de documento'
    assert tipo_documento._meta.verbose_name_plural == 'Tipos de documentos'


def test_admin():
    model_admin = TipoDocumentoAdmin(TipoDocumento, admin.site)
    # pylint: disable=W0212
    assert admin.site._registry[TipoDocumento]
    assert model_admin.list_display == ('identificador', 'nome', 'obrigatorio', 'visivel', 'tem_data_validade', 'obrigatorio_sme')
    assert model_admin.ordering == ('nome',)
    assert model_admin.search_fields == ('identificador', 'nome')


def test_admin_form_exige_identificador_para_novo_tipo_documento():
    form = TipoDocumentoAdminForm(
        data={
            "nome": "Documento novo",
            "obrigatorio": True,
            "visivel": True,
            "tem_data_validade": False,
            "obrigatorio_sme": False,
        }
    )

    assert not form.is_valid()
    assert form.errors["identificador"] == ["Informe o identificador alfanumérico."]


def test_admin_form_rejeita_edicao_legada_sem_identificador(tipo_documento):
    tipo_documento.identificador = None
    tipo_documento.save(update_fields=["identificador"])

    form = TipoDocumentoAdminForm(
        instance=tipo_documento,
        data={
            "identificador": "",
            "nome": tipo_documento.nome,
            "obrigatorio": tipo_documento.obrigatorio,
            "visivel": tipo_documento.visivel,
            "tem_data_validade": tipo_documento.tem_data_validade,
            "obrigatorio_sme": tipo_documento.obrigatorio_sme,
        },
    )

    assert not form.is_valid()
    assert form.errors["identificador"] == ["Informe o identificador alfanumérico."]


def test_admin_form_rejeita_edicao_de_tipo_parametrizado_sem_identificador(
    tipo_documento,
):
    form = TipoDocumentoAdminForm(
        instance=tipo_documento,
        data={
            "identificador": "",
            "nome": tipo_documento.nome,
            "obrigatorio": tipo_documento.obrigatorio,
            "visivel": tipo_documento.visivel,
            "tem_data_validade": tipo_documento.tem_data_validade,
            "obrigatorio_sme": tipo_documento.obrigatorio_sme,
        },
    )

    assert not form.is_valid()
    assert form.errors["identificador"] == ["Informe o identificador alfanumérico."]


def test_admin_form_rejeita_identificador_duplicado(tipo_documento):
    form = TipoDocumentoAdminForm(
        data={
            "identificador": tipo_documento.identificador,
            "nome": "Outro documento",
            "obrigatorio": True,
            "visivel": True,
            "tem_data_validade": False,
            "obrigatorio_sme": False,
        }
    )

    assert not form.is_valid()
    assert form.errors["identificador"] == [
        "Já existe um tipo de documento com este identificador."
    ]


def test_admin_form_rejeita_edicao_para_identificador_duplicado_de_outro_tipo(
    tipo_documento, tipo_documento_nao_obrigatorio
):
    form = TipoDocumentoAdminForm(
        instance=tipo_documento_nao_obrigatorio,
        data={
            "identificador": tipo_documento.identificador,
            "nome": tipo_documento_nao_obrigatorio.nome,
            "obrigatorio": tipo_documento_nao_obrigatorio.obrigatorio,
            "visivel": tipo_documento_nao_obrigatorio.visivel,
            "tem_data_validade": tipo_documento_nao_obrigatorio.tem_data_validade,
            "obrigatorio_sme": tipo_documento_nao_obrigatorio.obrigatorio_sme,
        },
    )

    assert not form.is_valid()
    assert form.errors["identificador"] == [
        "Já existe um tipo de documento com este identificador."
    ]
