import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ..api.viewsets.limites_categorias_viewset import LimitesCategoriasViewSet

pytestmark = pytest.mark.django_db


def test_limites_categorias_view_set(limite_categoria, fake_user):
    request = APIRequestFactory().get("")
    limite_categoria_detalhe = LimitesCategoriasViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = limite_categoria_detalhe(request, id=limite_categoria.id)

    assert response.status_code == status.HTTP_200_OK
