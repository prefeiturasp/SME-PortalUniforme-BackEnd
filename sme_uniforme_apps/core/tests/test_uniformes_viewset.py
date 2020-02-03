import pytest

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ..api.viewsets.uniformes_viewset import UniformesViewSet
from ..models.uniforme import Uniforme

pytestmark = pytest.mark.django_db


def test_uniformes_view_set(uniforme, fake_user):
    request = APIRequestFactory().get("")
    uniforme_detalhe = UniformesViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = uniforme_detalhe(request, id=uniforme.id)

    assert response.status_code == status.HTTP_200_OK
