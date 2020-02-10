import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ..api.viewsets.tipos_documento_viewset import TiposDocumentoViewSet

pytestmark = pytest.mark.django_db


def test_tipos_documento_view_set(tipo_documento, fake_user):
    request = APIRequestFactory().get("")
    tipo_documento_detalhe = TiposDocumentoViewSet.as_view({'get': 'retrieve'})
    force_authenticate(request, user=fake_user)
    response = tipo_documento_detalhe(request, id=tipo_documento.id)

    assert response.status_code == status.HTTP_200_OK
