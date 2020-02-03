import pytest

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ..api.viewsets.proponentes_viewset import ProponentesViewSet
from ..models.proponente import Proponente

pytestmark = pytest.mark.django_db


def test_proponentes_view_set(proponente, fake_user):
    request = APIRequestFactory().get("")
    proponente_detalhe = ProponentesViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = proponente_detalhe(request, uuid=proponente.uuid)

    assert response.status_code == status.HTTP_200_OK
