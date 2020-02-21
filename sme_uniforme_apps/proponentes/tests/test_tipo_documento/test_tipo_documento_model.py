import pytest
from django.contrib import admin

from sme_uniforme_apps.proponentes.admin import TipoDocumentoAdmin
from sme_uniforme_apps.proponentes.models import TipoDocumento

pytestmark = pytest.mark.django_db


def test_instancia(tipo_documento):
    assert isinstance(tipo_documento, TipoDocumento)
    assert tipo_documento.nome
    assert tipo_documento.obrigatorio


def test_srt_model(tipo_documento):
    assert tipo_documento.__str__() == 'Certidão Negativa (obrigatório)'


def test_meta_modelo(tipo_documento):
    assert tipo_documento._meta.verbose_name == 'Tipo de documento'
    assert tipo_documento._meta.verbose_name_plural == 'Tipos de documentos'


def test_admin():
    model_admin = TipoDocumentoAdmin(TipoDocumento, admin.site)
    # pylint: disable=W0212
    assert admin.site._registry[TipoDocumento]
    assert model_admin.list_display == ('nome', 'obrigatorio')
    assert model_admin.ordering == ('nome',)
    assert model_admin.search_fields == ('nome',)
