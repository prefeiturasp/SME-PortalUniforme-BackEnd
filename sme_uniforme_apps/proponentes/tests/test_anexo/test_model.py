import pytest

from ...models import Anexo

pytestmark = pytest.mark.django_db


def test_instancia(anexo):
    assert isinstance(anexo, Anexo)
    assert anexo.proponente
    assert anexo.arquivo
    assert anexo.tipo_documento
