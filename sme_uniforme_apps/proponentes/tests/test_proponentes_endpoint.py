import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_url_authorized(authenticated_client):
    response = authenticated_client.get('/proponentes/')
    assert response.status_code == status.HTTP_200_OK


def test_url_lookup(authenticated_client):
    response = authenticated_client.get('/proponentes/lookup/')
    assert response.status_code == status.HTTP_200_OK


def test_url_verifica_cnpj(authenticated_client):
    response = authenticated_client.get('/proponentes/verifica-cnpj/')
    assert response.status_code == status.HTTP_200_OK
