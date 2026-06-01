import json

import pytest
from rest_framework import status

from ...models.loja import Loja

pytestmark = pytest.mark.django_db


ARQUIVO_PNG_BASE64 = "data:image/png;base64,iVBORw0KGgo="
ARQUIVO_JPG_BASE64 = "data:image/jpg;base64,/9j/4AAQSkZJRgABAQ=="
ARQUIVO_JPEG_BASE64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ=="
ARQUIVO_PDF_BASE64 = "data:application/pdf;base64,JVBERi0xLjQKJUVPRgo="
ARQUIVO_TXT_BASE64 = "data:text/plain;base64,Q09OVEVVRE8gVEVTVEU="


@pytest.mark.parametrize(
    "foto_fachada", [ARQUIVO_PNG_BASE64, ARQUIVO_JPG_BASE64, ARQUIVO_JPEG_BASE64]
)
def test_update_loja_fachada(client, loja_fisica, foto_fachada):
    foto_fachada_antes = Loja.objects.get(uuid=str(loja_fisica.uuid)).foto_fachada
    response = client.patch("/lojas/{}/".format(loja_fisica.uuid), data=json.dumps({"foto_fachada": foto_fachada}), content_type="application/json")
    assert Loja.objects.exists()
    assert response.status_code == status.HTTP_200_OK
    assert (Loja.objects.get(uuid=str(loja_fisica.uuid)).foto_fachada != foto_fachada_antes)


@pytest.mark.parametrize("foto_fachada", [ARQUIVO_PDF_BASE64, ARQUIVO_TXT_BASE64])
def test_update_loja_fachada_rejeita_extensao_invalida(
    client, loja_fisica, foto_fachada
):
    response = client.patch(
        "/lojas/{}/".format(loja_fisica.uuid),
        data=json.dumps({"foto_fachada": foto_fachada}),
        content_type="application/json",
    )
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result["foto_fachada"] == ["Envie a foto da fachada em JPG, JPEG ou PNG."]
