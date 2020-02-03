import pytest

from model_bakery import baker


@pytest.fixture
def uniforme():
    return baker.make('Uniforme', nome='Calça')


@pytest.fixture
def meio_de_recebimento():
    return baker.make('MeioDeRecebimento', nome='Visa')
