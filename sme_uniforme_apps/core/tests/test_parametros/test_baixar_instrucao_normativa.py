import pytest
from rest_framework.test import APIClient

from ...models import Parametros

pytestmark = pytest.mark.django_db


def test_download_instrucao_normativa(arquivo):
    p = Parametros.objects.create(instrucao_normativa=arquivo)

    client = APIClient()
    response = client.get('/instrucao-normativa', follow=True)
    assert response.status_code == 200
    assert '/django_media' in response.data
    assert Parametros.objects.first()
