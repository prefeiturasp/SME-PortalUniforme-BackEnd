import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_url_authorized(authenticated_client):
    response = authenticated_client.get('/meios-de-recebimento/')
    assert response.status_code == status.HTTP_200_OK


def test_url_lookup(authenticated_client):
    response = authenticated_client.get('/meios-de-recebimento/lookup/')
    assert response.status_code == status.HTTP_200_OK
