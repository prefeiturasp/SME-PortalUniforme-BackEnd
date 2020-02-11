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
        edital=arquivo
    )

def limite_categoria():
    return baker.make('LimiteCategoria', categoria_uniforme=Uniforme.CATEGORIA_CALCADO, preco_maximo=100.50)


@pytest.fixture
def limite_categoria_malharia():
    return baker.make('LimiteCategoria', categoria_uniforme=Uniforme.CATEGORIA_MALHARIA, preco_maximo=50.00)

