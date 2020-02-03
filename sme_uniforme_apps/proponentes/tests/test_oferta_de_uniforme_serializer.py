import pytest

from ..api.serializers.oferta_de_uniforme_serializer import OfertaDeUniformeSerializer

pytestmark = pytest.mark.django_db


def test_oferta_de_uniforme_serializer(oferta_de_uniforme):

    oferta_de_uniforme_serializer = OfertaDeUniformeSerializer(oferta_de_uniforme)

    assert oferta_de_uniforme_serializer.data is not None
    assert oferta_de_uniforme_serializer.data['proponente']
    assert oferta_de_uniforme_serializer.data['uniforme']
    assert oferta_de_uniforme_serializer.data['preco']
    assert oferta_de_uniforme_serializer.data['uuid']
    assert oferta_de_uniforme_serializer.data['alterado_em']
    assert oferta_de_uniforme_serializer.data['criado_em']
    assert oferta_de_uniforme_serializer.data['id']
