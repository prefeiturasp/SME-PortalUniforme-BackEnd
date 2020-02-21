import pytest
from unittest.mock import patch
from model_bakery import baker

from ...models.proponente import Proponente

pytestmark = pytest.mark.django_db


@patch('sme_uniforme_apps.proponentes.models.proponente.Proponente.comunicar_pre_cadastro')
def test_comunica_pre_cadastro(mock_comunicar_pre_cadastro):
    baker.make('Proponente')
    assert mock_comunicar_pre_cadastro.called


@patch('sme_uniforme_apps.proponentes.models.proponente.Proponente.comunicar_cadastro')
def test_comunica_cadastro(mock_comunicar_cadastro):
    proponente = baker.make('Proponente')
    Proponente.concluir_cadastro(proponente.uuid)
    assert mock_comunicar_cadastro.called

