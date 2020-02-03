import pytest

from ..models import ListaNegra


pytestmark = pytest.mark.django_db


def test_instance(proponente, lista_negra):
    assert isinstance(lista_negra, ListaNegra)
    assert lista_negra.cnpj
    assert lista_negra.razao_social


def test_cnpj_bloqueado_resultado_positivo(lista_negra):
    assert ListaNegra.cnpj_bloqueado(lista_negra.cnpj)


def test_cnpj_bloqueado_resultado_negativo(lista_negra):
    cnpj_nao_bloqueado = '73.110.385/0001-13'
    assert not ListaNegra.cnpj_bloqueado(cnpj_nao_bloqueado)

