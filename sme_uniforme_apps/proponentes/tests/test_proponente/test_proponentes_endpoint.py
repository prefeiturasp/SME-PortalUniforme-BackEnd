import json
from pathlib import Path
from unittest.mock import patch

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


ARQUIVO_JPG_BASE64 = "data:image/jpg;base64,/9j/4AAQSkZJRgABAQ=="

MISSING = object()


def create_payload_atualiza_lojas(
    uniforme_nome, comprovante_endereco=MISSING, loja_id=None
):
    loja = {
        "nome_fantasia": "Loja Atualizada",
        "cep": "27600-000",
        "endereco": "Rua Atualizada",
        "bairro": "Centro",
        "numero": "10",
        "complemento": "",
        "telefone": "(11) 4565-9876",
        "numero_iptu": "",
    }
    if loja_id:
        loja["id"] = loja_id
    if comprovante_endereco is not MISSING:
        loja["comprovante_endereco"] = comprovante_endereco

    return {
        "lojas": [loja],
        "ofertas_de_uniformes": [
            {
                "nome": uniforme_nome,
                "valor": "10.00",
            }
        ],
    }


def test_url_authorized(authenticated_client):
    response = authenticated_client.get('/proponentes/')
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_url_verifica_cnpj(authenticated_client):
    response = authenticated_client.get('/proponentes/verifica-cnpj/')
    assert response.status_code == status.HTTP_200_OK


def test_url_concluir_cadastro(authenticated_client, proponente):
    response = authenticated_client.patch(f'/proponentes/{proponente.uuid}/concluir-cadastro/')
    assert response.status_code == status.HTTP_200_OK


def test_url_verifica_email(authenticated_client):
    response = authenticated_client.get('/proponentes/verifica-email/')
    assert response.status_code == status.HTTP_200_OK


@patch(
    "sme_uniforme_apps.proponentes.api.viewsets.proponentes_viewset.atualiza_coordenadas_lojas"
)
def test_url_atualiza_lojas_sem_comprovante_endereco(
    mock_atualiza_coordenadas_lojas, client, proponente, uniforme_calca
):
    payload = create_payload_atualiza_lojas(uniforme_calca.nome)

    response = client.patch(
        f"/proponentes/{proponente.uuid}/atualiza-lojas/",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert proponente.lojas.count() == 1
    assert not proponente.lojas.first().comprovante_endereco
    mock_atualiza_coordenadas_lojas.assert_called_once()


@patch(
    "sme_uniforme_apps.proponentes.api.viewsets.proponentes_viewset.atualiza_coordenadas_lojas"
)
def test_url_atualiza_lojas_adiciona_comprovante_endereco_pdf(
    mock_atualiza_coordenadas_lojas,
    client,
    proponente,
    uniforme_calca,
    arquivo_anexo_base64,
    settings,
    tmp_path,
):
    settings.MEDIA_ROOT = str(tmp_path)
    payload = create_payload_atualiza_lojas(
        uniforme_calca.nome,
        comprovante_endereco=arquivo_anexo_base64,
    )

    response = client.patch(
        f"/proponentes/{proponente.uuid}/atualiza-lojas/",
        data=json.dumps(payload),
        content_type="application/json",
    )
    result = json.loads(response.content)
    proponente.refresh_from_db()
    loja_fisica = proponente.lojas.first()

    assert response.status_code == status.HTTP_200_OK
    assert loja_fisica.comprovante_endereco
    assert Path(loja_fisica.comprovante_endereco.path).exists()
    assert result["lojas"][0]["comprovante_endereco"].endswith(".pdf")
    mock_atualiza_coordenadas_lojas.assert_called_once()

    loja_fisica.comprovante_endereco.delete(save=False)


@patch(
    "sme_uniforme_apps.proponentes.api.viewsets.proponentes_viewset.atualiza_coordenadas_lojas"
)
def test_url_atualiza_lojas_com_comprovante_endereco_pdf(
    mock_atualiza_coordenadas_lojas,
    client,
    proponente,
    loja_fisica,
    uniforme_calca,
    arquivo_anexo_base64,
    settings,
    tmp_path,
):
    settings.MEDIA_ROOT = str(tmp_path)
    payload = create_payload_atualiza_lojas(
        uniforme_calca.nome,
        comprovante_endereco=arquivo_anexo_base64,
        loja_id=loja_fisica.id,
    )

    response = client.patch(
        f"/proponentes/{proponente.uuid}/atualiza-lojas/",
        data=json.dumps(payload),
        content_type="application/json",
    )
    result = json.loads(response.content)

    loja_fisica.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert loja_fisica.comprovante_endereco
    assert Path(loja_fisica.comprovante_endereco.path).exists()
    assert result["lojas"][0]["comprovante_endereco"].endswith(".pdf")
    mock_atualiza_coordenadas_lojas.assert_called_once()

    loja_fisica.comprovante_endereco.delete(save=False)


@patch(
    "sme_uniforme_apps.proponentes.api.viewsets.proponentes_viewset.atualiza_coordenadas_lojas"
)
def test_url_atualiza_lojas_remove_comprovante_endereco(
    mock_atualiza_coordenadas_lojas,
    client,
    proponente,
    loja_fisica,
    uniforme_calca,
    arquivo_anexo_base64,
    settings,
    tmp_path,
):
    settings.MEDIA_ROOT = str(tmp_path)
    # Primeiro adiciona comprovante
    payload_adiciona = create_payload_atualiza_lojas(
        uniforme_calca.nome,
        comprovante_endereco=arquivo_anexo_base64,
        loja_id=loja_fisica.id,
    )
    client.patch(
        f"/proponentes/{proponente.uuid}/atualiza-lojas/",
        data=json.dumps(payload_adiciona),
        content_type="application/json",
    )
    loja_fisica.refresh_from_db()
    assert loja_fisica.comprovante_endereco

    # Agora remove comprovante enviando None
    payload_remove = create_payload_atualiza_lojas(
        uniforme_calca.nome,
        comprovante_endereco=None,
        loja_id=loja_fisica.id,
    )
    response = client.patch(
        f"/proponentes/{proponente.uuid}/atualiza-lojas/",
        data=json.dumps(payload_remove),
        content_type="application/json",
    )
    result = json.loads(response.content)
    loja_fisica.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert not loja_fisica.comprovante_endereco
    assert result["lojas"][0]["comprovante_endereco"] is None
    mock_atualiza_coordenadas_lojas.assert_called()


@patch(
    "sme_uniforme_apps.proponentes.api.viewsets.proponentes_viewset.atualiza_coordenadas_lojas"
)
@pytest.mark.parametrize(
    "comprovante_endereco",
    [ARQUIVO_JPG_BASE64, "data:text/plain;base64,Q09OVEVVRE8gVEVTVEU="],
)
def test_url_atualiza_lojas_rejeita_comprovante_endereco_nao_pdf(
    mock_atualiza_coordenadas_lojas,
    client,
    proponente,
    loja_fisica,
    uniforme_calca,
    comprovante_endereco,
):
    payload = create_payload_atualiza_lojas(
        uniforme_calca.nome,
        comprovante_endereco=comprovante_endereco,
        loja_id=loja_fisica.id,
    )

    response = client.patch(
        f"/proponentes/{proponente.uuid}/atualiza-lojas/",
        data=json.dumps(payload),
        content_type="application/json",
    )
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == ["Envie o comprovante de endereço do ponto de venda em PDF."]
    mock_atualiza_coordenadas_lojas.assert_not_called()
