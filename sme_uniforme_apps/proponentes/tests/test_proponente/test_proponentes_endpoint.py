import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_url_authorized(authenticated_client):
    response = authenticated_client.get('/proponentes/')
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_url_verifica_cnpj(authenticated_client):
    response = authenticated_client.get('/proponentes/verifica-cnpj/')
    assert response.status_code == status.HTTP_200_OK


def test_url_concluir_cadastro(authenticated_client, proponente):
    response = authenticated_client.patch(f'/proponentes/{proponente.uuid}/concluir-cadastro/')
    assert response.status_code == status.HTTP_200_OK


def test_url_verifica_email(authenticated_client):
    response = authenticated_client.get('/proponentes/verifica-email/')
    assert response.status_code == status.HTTP_200_OK
