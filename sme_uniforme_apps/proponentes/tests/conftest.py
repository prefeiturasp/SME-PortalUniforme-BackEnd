import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from ...core.models import Uniforme
from ..models.proponente import Proponente


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
def arquivo():
    return SimpleUploadedFile(f'anexo_teste.txt', bytes(f'CONTEUDO TESTE TESTE TESTE', encoding="utf-8"))


@pytest.fixture
def loja_fisica(proponente, arquivo):
    return baker.make(
        'Loja',
        proponente=proponente,
        nome_fantasia='Loja Teste',
        cep='27600-000',
        endereco='Rua Teste',
        bairro='Centro',
        numero='123',
        complemento='loja 1',
        telefone='(11) 4565-9876',
        foto_fachada=arquivo,
    )

@pytest.fixture
def payload_update_fachada_loja(arquivo_anexo_base64):
    return {
        "foto_fachada": arquivo_anexo_base64,
    }


@pytest.fixture
def anexo(proponente, arquivo, tipo_documento):
    return baker.make(
        'Anexo',
        arquivo=arquivo,
        proponente=proponente,
        tipo_documento=tipo_documento
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
        status=Proponente.STATUS_INSCRITO
    )


@pytest.fixture
def tipo_documento():
    return baker.make(
        'TipoDocumento',
        nome='Certidão Negativa',
        obrigatorio=True,
        visivel=True
    )


@pytest.fixture
def tipo_documento_nao_obrigatorio():
    return baker.make(
        'TipoDocumento',
        nome='Carta de Recomendação',
        obrigatorio=False,
    )


@pytest.fixture
def arquivo_anexo_base64():
    return "data:text/plain/txt;base64,RW5kZXJl528gSVB2NDoJMTAuNDkuMjMuOTANClNlcnZpZG9yZXMgRE5TIElQdjQ6CTEwLjQ5LjE2LjQwCjEwLjQ5LjE2LjQzDQpTdWZpeG8gRE5TIFByaW3hcmlvOgllZHVjYWNhby5pbnRyYW5ldA0KRmFicmljYW50ZToJSW50ZWwNCkRlc2NyaefjbzoJSW50ZWwoUikgRXRoZXJuZXQgQ29ubmVjdGlvbiBJMjE4LUxNDQpWZXJz428gZG8gZHJpdmVyOgkxMi4xMy4xNy40DQpFbmRlcmXnbyBm7XNpY28gKE1BQyk6CTc0LUU2LUUyLUQwLUVDLTNF"

@pytest.fixture
def payload_anexo(arquivo_anexo_base64, tipo_documento, proponente):
    return {
        "arquivo": arquivo_anexo_base64,
        "proponente": str(proponente.uuid),
        "tipo_documento": tipo_documento.id
    }

@pytest.fixture
def payload_arquivos_anexos_faltando_documentos_obrigatorios(tipo_documento_nao_obrigatorio, arquivo_anexo_base64):
    return [
        {
            "arquivo": arquivo_anexo_base64,
            "tipo_documento": tipo_documento_nao_obrigatorio.id
        }
    ]


@pytest.fixture
def payload_arquivos_anexos_nao_faltando_documentos_obrigatorios(tipo_documento, tipo_documento_nao_obrigatorio,
                                                                 arquivo_anexo_base64):
    return [
        {
            "arquivo": arquivo_anexo_base64,
            "tipo_documento": tipo_documento.id
        },
        {
            "arquivo": arquivo_anexo_base64,
            "tipo_documento": tipo_documento_nao_obrigatorio.id
        }
    ]


@pytest.fixture
def payload_ofertas_de_uniformes(uniforme_camisa, uniforme_calca, uniforme_tenis, uniforme_meias):
    return [
        {
            "preco": "10.00",
            "uniforme": uniforme_calca.id,
        },
        {
            "preco": "20.00",
            "uniforme": uniforme_camisa.id
        },
        {
            "preco": "30.00",
            "uniforme": uniforme_meias.id
        },
        {
            "preco": "40.00",
            "uniforme": uniforme_tenis.id
        }
    ]


@pytest.fixture
def payload_ofertas_de_uniformes_acima_limite(uniforme_camisa, uniforme_calca, uniforme_tenis, uniforme_meias):
    return [
        {
            "preco": "10.00",
            "uniforme": uniforme_calca.id,
        },
        {
            "preco": "80.00",
            "uniforme": uniforme_camisa.id
        },
        {
            "preco": "30.00",
            "uniforme": uniforme_meias.id
        },
        {
            "preco": "40.00",
            "uniforme": uniforme_tenis.id
        }
    ]


@pytest.fixture
def payload_ofertas_de_uniformes_faltando_a_camisa(uniforme_calca, uniforme_tenis, uniforme_meias):
    return [
        {
            "preco": "10.00",
            "uniforme": uniforme_calca.id,
        },
        {
            "preco": "30.00",
            "uniforme": uniforme_meias.id
        },
        {
            "preco": "40.00",
            "uniforme": uniforme_tenis.id
        }
    ]


@pytest.fixture
def payload_lojas(arquivo_anexo_base64):
    return [
        {
            "nome_fantasia": "Loja A",
            "cep": "27600-000",
            "endereco": "Rua ABC",
            "bairro": "São João",
            "numero": "565",
            "complemento": "Teste",
            "latitude": 0,
            "longitude": 0,
            "numero_iptu": "",
            "telefone": "(55) 4344-8765",
            "foto_fachada": arquivo_anexo_base64
        },
        {
            "nome_fantasia": "Loja B",
            "cep": "04120-021",
            "endereco": "Rua Teste",
            "bairro": "Centro",
            "numero": "133",
            "complemento": 0,
            "longitude": 0,
            "numero_iptu": "",
            "telefone": "(24) 9988-29105",
            "foto_fachada": arquivo_anexo_base64
        }
    ]


@pytest.fixture
def payload_lojas_sem_fotos_fachada():
    return [
        {
            "nome_fantasia": "Loja A",
            "cep": "27600-000",
            "endereco": "Rua ABC",
            "bairro": "São João",
            "numero": "565",
            "complemento": "Teste",
            "latitude": 0,
            "longitude": 0,
            "numero_iptu": "",
            "telefone": "(55) 4344-8765",
        },
        {
            "nome_fantasia": "Loja B",
            "cep": "04120-021",
            "endereco": "Rua Teste",
            "bairro": "Centro",
            "numero": "133",
            "complemento": "apt 102",
            "latitude": 0,
            "longitude": 0,
            "numero_iptu": "",
            "telefone": "(24) 9988-29105",
        }
    ]


@pytest.fixture
def payload_proponente(payload_ofertas_de_uniformes, payload_lojas,
                       payload_arquivos_anexos_nao_faltando_documentos_obrigatorios,
                       tipo_documento):
    return {
        "ofertas_de_uniformes": payload_ofertas_de_uniformes,
        "lojas": payload_lojas,
        "arquivos_anexos": payload_arquivos_anexos_nao_faltando_documentos_obrigatorios,
        "cnpj": "27.561.647/0001-49",
        "razao_social": "Postman 3 SA",
        "end_logradouro": "Rua XPTO, 23 fundos",
        "end_cidade": "São Paulo",
        "end_uf": "SP",
        "end_cep": "12600-000",
        "telefone": "(11) 99777-5105",
        "email": "postman3@teste.com",
        "responsavel": "Ana Postman da Silva"
    }


@pytest.fixture
def payload_proponente_sem_anexos(payload_ofertas_de_uniformes, payload_lojas_sem_fotos_fachada, tipo_documento):
    return {
        "ofertas_de_uniformes": payload_ofertas_de_uniformes,
        "lojas": payload_lojas_sem_fotos_fachada,
        "cnpj": "27.561.647/0001-49",
        "razao_social": "Postman 3 SA",
        "end_logradouro": "Rua XPTO, 23 fundos",
        "end_cidade": "São Paulo",
        "end_uf": "SP",
        "end_cep": "12600-000",
        "telefone": "(11) 99777-5105",
        "email": "postman3@teste.com",
        "responsavel": "Ana Postman da Silva"
    }


@pytest.fixture
def limite_categoria_malharia():
    return baker.make('LimiteCategoria', categoria_uniforme=Uniforme.CATEGORIA_KIT_VERAO, preco_maximo=100)


@pytest.fixture
def limite_categoria_calcados():
    return baker.make('LimiteCategoria', categoria_uniforme=Uniforme.CATEGORIA_KIT_INVERNO, preco_maximo=50)


@pytest.fixture
def limite_categoria_calcado():
    return baker.make('LimiteCategoria', categoria_uniforme=Uniforme.CATEGORIA_KIT_INVERNO, preco_maximo=100.50)


@pytest.fixture
def limite_categoria_malharia():
    return baker.make('LimiteCategoria', categoria_uniforme=Uniforme.CATEGORIA_KIT_VERAO, preco_maximo=50.00)
