import pytest

from django.contrib import admin
from model_bakery import baker

from ..admin import UniformeAdmin
from ..models import Uniforme

pytestmark = pytest.mark.django_db


@pytest.fixture
def uniforme():
    return baker.make(
        'Uniforme',
        nome='teste',
    )


def test_instance_model(uniforme):
    model = uniforme
    assert isinstance(model, Uniforme)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(uniforme):
    assert uniforme.__str__() == 'teste'


def test_meta_modelo(uniforme):
    assert uniforme._meta.verbose_name == 'Peça de Uniforme'
    assert uniforme._meta.verbose_name_plural == 'Peças de Uniforme'


def test_admin():
    model_admin = UniformeAdmin(Uniforme, admin.site)
    # pylint: disable=W0212
    assert admin.site._registry[Uniforme]
    assert model_admin.list_display == ('nome',)
    assert model_admin.ordering == ('nome',)
    assert model_admin.search_fields == ('nome',)
