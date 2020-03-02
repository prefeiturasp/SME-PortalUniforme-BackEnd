import json

import pytest
from rest_framework import status

from ...models.loja import Loja

pytestmark = pytest.mark.django_db


def test_update_loja_fachada(client, payload_update_fachada_loja, loja_fisica):
    foto_fachada_antes = Loja.objects.get(uuid=str(loja_fisica.uuid)).foto_fachada
    response = client.patch("/lojas/{}/".format(loja_fisica.uuid), data=json.dumps(payload_update_fachada_loja), content_type='application/json') 
    result = json.loads(response.content)
    assert Loja.objects.exists()
    assert response.status_code == status.HTTP_200_OK
    assert Loja.objects.get(uuid=str(loja_fisica.uuid)).foto_fachada != foto_fachada_antes
