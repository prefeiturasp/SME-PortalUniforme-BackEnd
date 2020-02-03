import pytest

from ..api.serializers.proponente_serializer import ProponenteSerializer, ProponenteLookUpSerializer

pytestmark = pytest.mark.django_db


def test_proponente_serializer(proponente):

    proponente_serializer = ProponenteSerializer(proponente)

    assert proponente_serializer.data is not None
    assert proponente_serializer.data['cnpj']
    assert proponente_serializer.data['razao_social']
    assert proponente_serializer.data['alterado_em']
    assert proponente_serializer.data['uuid']
    assert proponente_serializer.data['responsavel']
    assert proponente_serializer.data['end_logradouro']
    assert proponente_serializer.data['end_cidade']
    assert proponente_serializer.data['end_uf']
    assert proponente_serializer.data['end_cep']
    assert proponente_serializer.data['telefone']
    assert proponente_serializer.data['email']
    assert proponente_serializer.data['criado_em']
    assert proponente_serializer.data['id']
    assert proponente_serializer.data['ofertas_de_uniformes'] is not None
    assert proponente_serializer.data['lojas'] is not None
    assert proponente_serializer.data['arquivos_anexos'] is not None


def test_proponente_lookup_serializer(proponente):

    proponente_serializer = ProponenteLookUpSerializer(proponente)

    assert proponente_serializer.data is not None
    assert proponente_serializer.data['razao_social']
    assert proponente_serializer.data['uuid']

