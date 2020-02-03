import pytest

from ..api.serializers.anexo_serializer import AnexoSerializer

pytestmark = pytest.mark.django_db


def test_anexo_serializer(anexo):

    anexo_serializer = AnexoSerializer(anexo)

    assert anexo_serializer.data is not None
    assert anexo_serializer.data['uuid']
    assert anexo_serializer.data['alterado_em']
    assert anexo_serializer.data['criado_em']
    assert anexo_serializer.data['id']
    assert anexo_serializer.data['arquivo']

