import pytest
from rest_framework.test import APIClient

from ...models import Parametros

pytestmark = pytest.mark.django_db


def test_download_edital(arquivo):
    p = Parametros.objects.create(edital=arquivo)

    client = APIClient()
    response = client.get('/edital', follow=True)
    assert response.status_code == 200
    assert '/django_media' in response.data
    assert Parametros.objects.first()
