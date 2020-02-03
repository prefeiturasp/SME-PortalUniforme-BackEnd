import pytest

from django.contrib import admin
from model_bakery import baker

from ..admin import MeioDeRecebimentoAdmin
from ..models import MeioDeRecebimento

pytestmark = pytest.mark.django_db


@pytest.fixture
def meio_de_recebimento():
    return baker.make(
        'MeioDeRecebimento',
        nome='teste',
    )


def test_instance_model(meio_de_recebimento):
    assert isinstance(meio_de_recebimento, MeioDeRecebimento)
    assert meio_de_recebimento.nome
    assert meio_de_recebimento.criado_em
    assert meio_de_recebimento.alterado_em
    assert meio_de_recebimento.uuid
    assert meio_de_recebimento.id


def test_srt_model(meio_de_recebimento):
    assert meio_de_recebimento.__str__() == 'teste'


def test_meta_modelo(meio_de_recebimento):
    assert meio_de_recebimento._meta.verbose_name == 'Meio de recebimento'
    assert meio_de_recebimento._meta.verbose_name_plural == 'Meios de recebimento'


def test_admin():
    model_admin = MeioDeRecebimentoAdmin(MeioDeRecebimento, admin.site)
    # pylint: disable=W0212
    assert admin.site._registry[MeioDeRecebimento]
    assert model_admin.list_display == ('nome',)
    assert model_admin.ordering == ('nome',)
    assert model_admin.search_fields == ('nome',)
