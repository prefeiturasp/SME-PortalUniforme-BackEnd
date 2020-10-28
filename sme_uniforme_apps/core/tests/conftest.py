import pytest

from django.core.files.uploadedfile import SimpleUploadedFile

from model_bakery import baker

from ..models import Uniforme


@pytest.fixture
def uniforme():
    return baker.make('Uniforme', nome='Calça')


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(f'documento_teste.pdf', bytes(f'CONTEUDO TESTE TESTE TESTE', encoding="utf-8"))


@pytest.fixture
def parametros(arquivo):
    return baker.make(
        'Parametros',
        edital=arquivo,
        instrucao_normativa=arquivo
    )


@pytest.fixture
def limite_categoria():
    return baker.make('LimiteCategoria', categoria_uniforme=Uniforme.CATEGORIA_KIT_INVERNO, preco_maximo=100.50)


@pytest.fixture
def limite_categoria_verao():
    return baker.make('LimiteCategoria', categoria_uniforme=Uniforme.CATEGORIA_KIT_VERAO, preco_maximo=50.00)

