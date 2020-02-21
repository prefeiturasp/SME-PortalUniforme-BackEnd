import json

import pytest
from rest_framework import status

from ...models.loja import Loja

pytestmark = pytest.mark.django_db


def test_update_loja_fachada(client, payload_update_fachada_loja, loja_fisica):
    response = client.patch("/lojas/{}/".format(loja_fisica.uuid)) 
    result = json.loads(response.content)
    assert Loja.objects.exists()
    assert response.status_code == status.HTTP_200_OK
    assert Loja.objetcs.get(uuid=loja_fisica.uuid).foto_fachada == payload_update_fachada_loja.foto_fachada
