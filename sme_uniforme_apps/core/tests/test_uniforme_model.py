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
    assert model.categoria
    assert model.unidade
    assert model.quantidade


def test_srt_model(uniforme):
    assert uniforme.__str__() == 'teste (1 unidade)'


def test_meta_modelo(uniforme):
    assert uniforme._meta.verbose_name == 'Peça de Uniforme'
    assert uniforme._meta.verbose_name_plural == 'Peças de Uniforme'


def test_admin():
    model_admin = UniformeAdmin(Uniforme, admin.site)
    # pylint: disable=W0212
    assert admin.site._registry[Uniforme]
    assert model_admin.list_display == ('nome', 'quantidade', 'unidade', 'categoria')
    assert model_admin.ordering == ('nome',)
    assert model_admin.search_fields == ('nome',)
    assert model_admin.list_filter == ('categoria', 'unidade')


def test_metodo_qtd_itens_por_categoria_as_dict(uniforme_camisa, uniforme_meias, uniforme_tenis):
    qtd_itens_por_categoria = Uniforme.qtd_itens_por_categoria_as_dict()
    esperado = {
        Uniforme.CATEGORIA_MALHARIA: 2,
        Uniforme.CATEGORIA_CALCADO: 1,
    }
    assert qtd_itens_por_categoria == esperado


def test_metodo_qtd_itens_por_categoria_as_dict_quando_nao_ha_itens():
    qtd_itens_por_categoria = Uniforme.qtd_itens_por_categoria_as_dict()
    esperado = {
        Uniforme.CATEGORIA_MALHARIA: 0,
        Uniforme.CATEGORIA_CALCADO: 0,
    }
    assert qtd_itens_por_categoria == esperado


def test_metodo_categorias_to_json(uniforme_meias, uniforme_tenis):
    esperado = [
        {
            'id': Uniforme.CATEGORIA_MALHARIA,
            'nome': Uniforme.CATEGORIA_NOMES[Uniforme.CATEGORIA_MALHARIA],
            'uniformes': [{'descricao': 'Meias (5 pares)',
                           'id': uniforme_meias.id,
                           'nome': 'Meias',
                           'quantidade': 5,
                           'unidade': 'PAR'}]
        },
        {
            'id': Uniforme.CATEGORIA_CALCADO,
            'nome': Uniforme.CATEGORIA_NOMES[Uniforme.CATEGORIA_CALCADO],
            'uniformes': [{'descricao': 'Tenis (1 par)',
                           'id': uniforme_tenis.id,
                           'nome': 'Tenis',
                           'quantidade': 1,
                           'unidade': 'PAR'}]
        }
    ]
    resultado = Uniforme.categorias_to_json()
    assert esperado == resultado
