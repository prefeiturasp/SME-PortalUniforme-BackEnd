import pytest

from model_bakery import baker


@pytest.fixture
def uniforme():
    return baker.make('Uniforme', nome='Calça')

