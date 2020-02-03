import pytest

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ..api.viewsets.meios_de_recebimento_viewset import MeiosDeRecebimentoViewSet

pytestmark = pytest.mark.django_db


def test_meios_de_recebimento_view_set(meio_de_recebimento, fake_user):
    request = APIRequestFactory().get("")
    meios_de_recebimento_detalhe = MeiosDeRecebimentoViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = meios_de_recebimento_detalhe(request, id=meio_de_recebimento.id)

    assert response.status_code == status.HTTP_200_OK
