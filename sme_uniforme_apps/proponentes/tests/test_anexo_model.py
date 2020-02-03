import pytest

from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import Anexo


pytestmark = pytest.mark.django_db


def test_loja(anexo):
    assert isinstance(anexo, Anexo)



