import pytest

from django.contrib import admin
from model_bakery import baker

from ..models import OfertaDeUniforme
from ..admin import OfertaDeUniformeAdmin


pytestmark = pytest.mark.django_db


def test_oferta_uniforme(oferta_de_uniforme, proponente, uniforme_calca):
    oferta = oferta_de_uniforme

    assert isinstance(oferta, OfertaDeUniforme)
    assert oferta.proponente == proponente
    assert oferta.uniforme == uniforme_calca
    assert oferta.preco == 100.35


def test_admin():
    model_admin = OfertaDeUniformeAdmin(OfertaDeUniforme, admin.site)
    # pylint: disable=W0212
    assert admin.site._registry[OfertaDeUniforme]
    assert model_admin.list_display == ('protocolo', 'proponente',  'uniforme', 'preco')
    assert model_admin.ordering == ('proponente',)
    assert model_admin.search_fields == ('proponente__uuid', 'uniforme__nome',)
    assert model_admin.list_filter == ('uniforme', )


