import pytest

from sme_uniforme_apps.core.api.serializers.limite_categoria_serializer import LimiteCategoriaSerializer

pytestmark = pytest.mark.django_db


def test_limite_categoria_serializer(limite_categoria):
    limite_categoria_serializer = LimiteCategoriaSerializer(limite_categoria)

    assert limite_categoria_serializer.data is not None
    assert limite_categoria_serializer.data['categoria_uniforme']
    assert limite_categoria_serializer.data['preco_maximo']
