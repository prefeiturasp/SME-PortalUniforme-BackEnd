import pytest

from django.core.files.uploadedfile import SimpleUploadedFile

from model_bakery import baker


@pytest.fixture
def uniforme():
    return baker.make('Uniforme', nome='Calça')


@pytest.fixture
def meio_de_recebimento():
    return baker.make('MeioDeRecebimento', nome='Visa')


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(f'documento_teste.pdf', bytes(f'CONTEUDO TESTE TESTE TESTE', encoding="utf-8"))


@pytest.fixture
def parametros(arquivo):
    return baker.make(
        'Parametros',
        edital=arquivo
    )