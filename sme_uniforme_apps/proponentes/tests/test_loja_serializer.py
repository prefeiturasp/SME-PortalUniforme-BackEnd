import pytest

from ..api.serializers.loja_serializer import LojaSerializer

pytestmark = pytest.mark.django_db


def test_loja_serializer(loja_fisica):

    loja_serializer = LojaSerializer(loja_fisica)

    assert loja_serializer.data is not None
    assert loja_serializer.data['uuid']
    assert loja_serializer.data['alterado_em']
    assert loja_serializer.data['criado_em']
    assert loja_serializer.data['id']
    assert loja_serializer.data['cep']
    assert loja_serializer.data['endereco']
    assert loja_serializer.data['bairro']
    assert loja_serializer.data['numero']
    assert loja_serializer.data['complemento']
    assert loja_serializer.data['latitude'] is not None
    assert loja_serializer.data['longitude'] is not None
    assert loja_serializer.data['numero_iptu'] is not None
    assert loja_serializer.data['telefone']
