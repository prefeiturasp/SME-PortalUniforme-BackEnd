import pytest
from django.contrib import admin

from ..admin import LimiteCategoriaAdmin
from ..models import LimiteCategoria

pytestmark = pytest.mark.django_db


def test_instance_model(limite_categoria):
    assert isinstance(limite_categoria, LimiteCategoria)
    assert limite_categoria.categoria_uniforme
    assert limite_categoria.preco_maximo
    assert limite_categoria.criado_em
    assert limite_categoria.alterado_em
    assert limite_categoria.uuid
    assert limite_categoria.id


def test_srt_model(limite_categoria):
    assert limite_categoria.__str__() == 'Calçados Preço Máximo: R$ 100.50'


def test_meta_modelo(limite_categoria):
    assert limite_categoria._meta.verbose_name == "Limite da categoria"
    assert limite_categoria._meta.verbose_name_plural == "Limites de categorias"


def test_admin():
    model_admin = LimiteCategoriaAdmin(LimiteCategoria, admin.site)
    # pylint: disable=W0212
    assert admin.site._registry[LimiteCategoria]
    assert model_admin.list_display == ('categoria_uniforme', 'preco_maximo')
    assert model_admin.ordering == ('categoria_uniforme',)
    assert model_admin.list_filter == ('categoria_uniforme',)
