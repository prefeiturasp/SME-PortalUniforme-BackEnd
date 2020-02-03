import pytest

from django.core.files.uploadedfile import SimpleUploadedFile

from model_bakery import baker


@pytest.fixture
def proponente():
    return baker.make(
        'Proponente',
        cnpj='00.529.476/0001-14',
        razao_social='Teste',
        end_logradouro='Rua Teste, 123 apt. 101 Centro',
        end_cidade='São Paulo',
        end_uf='SP',
        end_cep='99999-000',
        telefone='(99) 99999-9999',
        email='teste@teste.com',
        responsavel='Fulano',
    )


@pytest.fixture
def cnpj_bloqueado():
    return '00.529.476/0001-14'


@pytest.fixture
def uniforme_calca():
    return baker.make('Uniforme', nome='Calça')


@pytest.fixture
def uniforme_camisa():
    return baker.make('Uniforme', nome='Camisa')


@pytest.fixture
def loja_fisica(proponente):
    return baker.make(
        'Loja',
        proponente=proponente,
        cep='27600-000',
        endereco='Rua Teste',
        bairro='Centro',
        numero='123',
        complemento='loja 1',
        telefone='(11) 4565-9876'

    )


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(f'anexo_teste.txt', bytes(f'CONTEUDO TESTE TESTE TESTE', encoding="utf-8"))


@pytest.fixture
def anexo(proponente, arquivo):
    return baker.make(
        'Anexo',
        arquivo=arquivo
    )


@pytest.fixture
def oferta_de_uniforme(proponente, uniforme_calca):
    return baker.make(
            'OfertaDeUniforme',
            proponente=proponente,
            uniforme=uniforme_calca,
            preco=100.35
        )


@pytest.fixture
def lista_negra(cnpj_bloqueado):
    return baker.make(
        'ListaNegra',
        cnpj=cnpj_bloqueado,
        razao_social='Teste Bloqueado',
    )


@pytest.fixture
def proponente_bloqueado(cnpj_bloqueado, lista_negra):
    return baker.make(
        'Proponente',
        cnpj=cnpj_bloqueado,
        razao_social='Teste Bloqueado',
        end_logradouro='Rua Bloqueio, 123 apt. 101 Centro',
        end_cidade='São Paulo',
        end_uf='SP',
        end_cep='99999-000',
        telefone='(99) 99999-8888',
        email='bloqueado@teste.com',
        responsavel='José Bloqueio da Silva',
    )