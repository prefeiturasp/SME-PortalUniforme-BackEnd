import pytest
from rest_framework.test import APIClient

from ...models import Parametros


pytestmark = pytest.mark.django_db


def test_download_edital(arquivo):
    p = Parametros.objects.create(edital=arquivo)

    client = APIClient()
    response = client.get('/edital', follow=True)
    print(response.content)
    assert response.status_code == 200
    assert b'CONTEUDO TESTE TESTE TESTE' == response.content
    assert Parametros.objects.first()