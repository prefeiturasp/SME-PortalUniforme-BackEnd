import pytest

from ..api.serializers.meio_de_recebimento_serializer import MeioDeRecebimentoSerializer, MeioDeRecebimentoLookUpSerializer

pytestmark = pytest.mark.django_db


def test_meio_de_recebimento_serializer(meio_de_recebimento):

    meio_de_recebimento_serializer = MeioDeRecebimentoSerializer(meio_de_recebimento)

    assert meio_de_recebimento_serializer.data is not None
    assert meio_de_recebimento_serializer.data['criado_em']
    assert meio_de_recebimento_serializer.data['alterado_em']
    assert meio_de_recebimento_serializer.data['id']
    assert meio_de_recebimento_serializer.data['uuid']
    assert meio_de_recebimento_serializer.data['nome']


def test_meio_de_recebimento_lookup_serializer(meio_de_recebimento):

    meio_de_recebimento_serializer = MeioDeRecebimentoLookUpSerializer(meio_de_recebimento)

    assert meio_de_recebimento_serializer.data is not None
    assert meio_de_recebimento_serializer.data['id']
    assert meio_de_recebimento_serializer.data['nome']

