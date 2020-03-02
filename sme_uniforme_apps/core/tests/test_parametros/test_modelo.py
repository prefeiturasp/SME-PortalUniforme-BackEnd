import pytest

from ...models import Parametros

pytestmark = pytest.mark.django_db


def test_parametros_model(parametros):
    assert isinstance(parametros, Parametros)
    assert parametros.edital
    assert parametros.instrucao_normativa

