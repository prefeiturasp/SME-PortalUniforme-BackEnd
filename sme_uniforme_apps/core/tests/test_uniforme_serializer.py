import pytest

from ..api.serializers.uniforme_serializer import UniformeSerializer, UniformeLookUpSerializer

pytestmark = pytest.mark.django_db


def test_uniforme_serializer(uniforme):

    uniforme_serializer = UniformeSerializer(uniforme)

    assert uniforme_serializer.data is not None
    assert uniforme_serializer.data['criado_em']
    assert uniforme_serializer.data['alterado_em']
    assert uniforme_serializer.data['nome']


def test_uniforme_lookup_serializer(uniforme):

    uniforme_serializer = UniformeLookUpSerializer(uniforme)

    assert uniforme_serializer.data is not None
    assert uniforme_serializer.data['nome']

