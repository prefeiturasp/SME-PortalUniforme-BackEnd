import pytest
import json
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_proponente_api_valida_cnpj_ja_cadastrado(client, proponente):
    response = client.get(f'/proponentes/verifica-cnpj/?cnpj={proponente.cnpj}', content_type='application/json')
    result = json.loads(response.content)
    print('Result', result)

    assert response.status_code == status.HTTP_200_OK
    assert result == {
                'result': 'OK',
                'cnpj_valido': 'Sim',
                'cnpj_cadastrado': 'Sim',
                'cnpj_bloqueado': 'Não'
            }


def test_proponente_api_valida_cnpj_nao_cadastrado(client, proponente):
    response = client.get('/proponentes/verifica-cnpj/?cnpj=91.359.880/0001-42', content_type='application/json')
    result = json.loads(response.content)
    print('Result', result)

    assert response.status_code == status.HTTP_200_OK
    assert result == {
                'result': 'OK',
                'cnpj_valido': 'Sim',
                'cnpj_cadastrado': 'Não',
                'cnpj_bloqueado': 'Não'
            }


def test_proponente_api_valida_cnpj_invalido(client, proponente):
    response = client.get('/proponentes/verifica-cnpj/?cnpj=99.999.999/9001-99', content_type='application/json')
    result = json.loads(response.content)
    print('Result', result)

    assert response.status_code == status.HTTP_200_OK
    assert result == {
                'result': 'OK',
                'cnpj_valido': 'Não',
                'cnpj_cadastrado': 'Não',
                'cnpj_bloqueado': 'Não'
            }


def test_proponente_api_valida_cnpj_erro(client, proponente):
    response = client.get('/proponentes/verifica-cnpj/', content_type='application/json')
    result = json.loads(response.content)
    print('Result', result)

    assert response.status_code == status.HTTP_200_OK
    assert result == {
                'result': 'Erro',
                'mensagem': 'Informe o cnpj na url. Ex: /proponentes/verifica-cnpj/?cnpj=53.894.798/0001-29'
            }


def test_proponente_api_valida_cnpj_bloqueado(client, cnpj_bloqueado, lista_negra):
    response = client.get(f'/proponentes/verifica-cnpj/?cnpj={cnpj_bloqueado}', content_type='application/json')
    result = json.loads(response.content)
    print('Result', result)

    assert response.status_code == status.HTTP_200_OK
    assert result == {
                'result': 'OK',
                'cnpj_valido': 'Sim',
                'cnpj_cadastrado': 'Não',
                'cnpj_bloqueado': 'Sim'
            }
