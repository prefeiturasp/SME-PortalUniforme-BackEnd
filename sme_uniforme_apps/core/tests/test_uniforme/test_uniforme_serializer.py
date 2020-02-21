import pytest

from sme_uniforme_apps.core.api.serializers.uniforme_serializer import UniformeSerializer, UniformeLookUpSerializer

pytestmark = pytest.mark.django_db


def test_uniforme_serializer(uniforme):

    uniforme_serializer = UniformeSerializer(uniforme)

    assert uniforme_serializer.data is not None
    assert uniforme_serializer.data['quantidade']
    assert uniforme_serializer.data['unidade']
    assert uniforme_serializer.data['nome']
    assert uniforme_serializer.data['categoria']


def test_uniforme_lookup_serializer(uniforme):

    uniforme_serializer = UniformeLookUpSerializer(uniforme)

    assert uniforme_serializer.data is not None
    assert uniforme_serializer.data['nome']

