import json

import pytest
from rest_framework import status

from ...models.anexo import Anexo

pytestmark = pytest.mark.django_db


@pytest.fixture
def create(client, payload_anexo):
    return client.post('/anexos/', data=json.dumps(payload_anexo), content_type='application/json')

@pytest.fixture
def delete(client, create):
    result = json.loads(create.content)
    return client.delete('/anexos/{}/'.format(result['uuid']), follow=True)

def test_anexo_api_create_status_code(create):
    response = create
    assert response.status_code == status.HTTP_201_CREATED

def test_anexo_api_create_model_exists(create):
    result = json.loads(create.content)    
    assert Anexo.objects.filter(uuid=result['uuid']).exists()

def test_anexo_api_delete_model(delete):
    assert delete.status_code == status.HTTP_204_NO_CONTENT

def test_anexo_api_create_model_not_exists(client, delete):
    assert not Anexo.objects.exists()
