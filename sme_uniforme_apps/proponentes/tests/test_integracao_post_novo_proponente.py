import json

import pytest
from rest_framework import status

from ..models import Proponente

pytestmark = pytest.mark.django_db


@pytest.fixture
def arquivo_anexo_base64():
    return "data:text/plain/txt;base64,RW5kZXJl528gSVB2NDoJMTAuNDkuMjMuOTANClNlcnZpZG9yZXMgRE5TIElQdjQ6CTEwLjQ5LjE2LjQwCjEwLjQ5LjE2LjQzDQpTdWZpeG8gRE5TIFByaW3hcmlvOgllZHVjYWNhby5pbnRyYW5ldA0KRmFicmljYW50ZToJSW50ZWwNCkRlc2NyaefjbzoJSW50ZWwoUikgRXRoZXJuZXQgQ29ubmVjdGlvbiBJMjE4LUxNDQpWZXJz428gZG8gZHJpdmVyOgkxMi4xMy4xNy40DQpFbmRlcmXnbyBm7XNpY28gKE1BQyk6CTc0LUU2LUUyLUQwLUVDLTNF"


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
def payload_ofertas_de_uniformes(uniforme_camisa, uniforme_calca):
    return [
        {
            "preco": "100.00",
            "uniforme": uniforme_calca.id
        },
        {
            "preco": "200.00",
            "uniforme": uniforme_camisa.id
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
            "latitude": "",
            "longitude": "",
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
            "complemento": "apt 102",
            "latitude": "",
            "longitude": "",
            "numero_iptu": "",
            "telefone": "(24) 9988-29105",
            "foto_fachada": arquivo_anexo_base64
        }
    ]


@pytest.fixture
def payload(payload_ofertas_de_uniformes, payload_lojas, payload_arquivos_anexos_nao_faltando_documentos_obrigatorios,
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


def test_proponente_api_create(client, payload):
    response = client.post('/proponentes/', data=json.dumps(payload), content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert Proponente.objects.filter(uuid=result["uuid"]).exists()

    # Verifica se a gravação dos anexos foi feita registrando os tipos de documento
    novo_proponente = Proponente.objects.get(uuid=result["uuid"])
    for anexo in novo_proponente.anexos.all():
        assert anexo.tipo_documento is not None


def test_proponente_api_create_valida_tipo_documento_obrigatorio(
        client, payload,
        payload_arquivos_anexos_faltando_documentos_obrigatorios):
    payload["arquivos_anexos"] = payload_arquivos_anexos_faltando_documentos_obrigatorios
    response = client.post('/proponentes/', data=json.dumps(payload), content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result[0] == 'Não foi enviado o documento Certidão Negativa (obrigatório).'
