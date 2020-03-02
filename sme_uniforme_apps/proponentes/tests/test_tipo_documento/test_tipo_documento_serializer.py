import pytest

from sme_uniforme_apps.proponentes.api.serializers.tipo_documento_serializer import TipoDocumentoSerializer

pytestmark = pytest.mark.django_db


def test_tipo_documento_serializer(tipo_documento):
    tipo_documento_serializer = TipoDocumentoSerializer(tipo_documento)

    assert tipo_documento_serializer.data is not None
    assert tipo_documento_serializer.data['nome']
    assert tipo_documento_serializer.data['obrigatorio']
    assert tipo_documento_serializer.data['id']
