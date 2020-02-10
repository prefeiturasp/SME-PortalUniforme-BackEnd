import pytest
from model_bakery import baker

from ..models import Uniforme


@pytest.fixture
def uniforme():
    return baker.make('Uniforme', nome='Calça')


@pytest.fixture
def limite_categoria():
    return baker.make('LimiteCategoria', categoria_uniforme=Uniforme.CATEGORIA_CALCADO, preco_maximo=100.50)


@pytest.fixture
def limite_categoria_malharia():
    return baker.make('LimiteCategoria', categoria_uniforme=Uniforme.CATEGORIA_MALHARIA, preco_maximo=50.00)
