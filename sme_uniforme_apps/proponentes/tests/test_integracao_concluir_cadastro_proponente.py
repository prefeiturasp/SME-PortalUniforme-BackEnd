import pytest
from rest_framework import status

from ..models import Proponente

pytestmark = pytest.mark.django_db


def test_proponente_api_concluir_cadastro(client, proponente):
    assert Proponente.objects.get(uuid=proponente.uuid).status == Proponente.STATUS_EM_PROCESSO
    response = client.patch(f'/proponentes/{proponente.uuid}/concluir-cadastro/', content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert Proponente.objects.get(uuid=proponente.uuid).status == Proponente.STATUS_INSCRITO

