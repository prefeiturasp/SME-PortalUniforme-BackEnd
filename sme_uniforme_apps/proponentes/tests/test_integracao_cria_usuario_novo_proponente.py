import json

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

pytestmark = pytest.mark.django_db

User = get_user_model()


# def test_proponente_api_create(client, payload_proponente):
#     response = client.post('/proponentes/', data=json.dumps(payload_proponente), content_type='application/json')
#
#     assert response.status_code == status.HTTP_201_CREATED
#     assert User.objects.get(email=payload_proponente['email'])
