import pytest
import json
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_proponente_api_valida_email_ja_cadastrado(client, proponente):
    response = client.get(f'/proponentes/verifica-email/?email={proponente.email}', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {
                'result': 'OK',
                'email_valido': 'Sim',
                'email_cadastrado': 'Sim'
            }


def test_proponente_api_valida_email_nao_cadastrado(client, proponente):
    response = client.get('/proponentes/verifica-email/?email=esse@nao.tem', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {
                'result': 'OK',
                'email_valido': 'Sim',
                'email_cadastrado': 'Não'
            }


def test_proponente_api_valida_email_invalido(client, proponente):
    response = client.get('/proponentes/verifica-email/?email=assimnaopode', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {
                'result': 'OK',
                'email_valido': 'Não',
                'email_cadastrado': 'Não'
            }


def test_proponente_api_valida_email_erro(client, proponente):
    response = client.get('/proponentes/verifica-email/', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {
                'result': 'Erro',
                'mensagem': 'Informe o email na url. Ex: /proponentes/verifica-email/?email=teste@teste.com'
            }



