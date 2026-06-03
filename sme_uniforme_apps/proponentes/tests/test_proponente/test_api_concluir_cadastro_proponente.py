import pytest
from rest_framework import status
from unittest.mock import patch

from sme_uniforme_apps.proponentes.models import Anexo, Proponente
from sme_uniforme_apps.triade.models import TriadeConfiguracao

pytestmark = pytest.mark.django_db


def test_proponente_api_concluir_cadastro(client, proponente):
    assert Proponente.objects.get(uuid=proponente.uuid).status == Proponente.STATUS_EM_PROCESSO
    response = client.patch(f'/proponentes/{proponente.uuid}/concluir-cadastro/', content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert Proponente.objects.get(uuid=proponente.uuid).status == Proponente.STATUS_INSCRITO

@patch("sme_uniforme_apps.triade.tasks.orquestrar_envio_lote_triade.delay")
def test_proponente_api_concluir_cadastro_enfileira_task_triade(
    mock_delay, client, proponente, settings
):
    settings.TRIADE_ENABLED = True

    response = client.patch(
        f"/proponentes/{proponente.uuid}/concluir-cadastro/",
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    mock_delay.assert_called_once_with(str(proponente.uuid))


@patch("sme_uniforme_apps.triade.tasks.orquestrar_envio_lote_triade.delay")
def test_proponente_api_concluir_cadastro_configuracao_do_banco_pode_habilitar_triade(
    mock_delay, client, proponente, settings
):
    settings.TRIADE_ENABLED = False
    TriadeConfiguracao.objects.create(habilitado=True)

    response = client.patch(
        f"/proponentes/{proponente.uuid}/concluir-cadastro/",
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    mock_delay.assert_called_once_with(str(proponente.uuid))


@patch("sme_uniforme_apps.triade.tasks.orquestrar_envio_lote_triade.delay")
def test_proponente_api_concluir_cadastro_configuracao_do_banco_pode_desabilitar_triade(
    mock_delay, client, proponente, settings
):
    settings.TRIADE_ENABLED = True
    TriadeConfiguracao.objects.create(habilitado=False)

    response = client.patch(
        f"/proponentes/{proponente.uuid}/concluir-cadastro/",
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    mock_delay.assert_not_called()


@patch(
    "sme_uniforme_apps.triade.tasks.orquestrar_envio_lote_triade.delay",
    side_effect=RuntimeError("fila indisponivel"),
)
def test_proponente_api_concluir_cadastro_nao_falha_quando_enfileiramento_triade_quebra(
    mock_delay, client, proponente, settings
):
    settings.TRIADE_ENABLED = True

    response = client.patch(
        f"/proponentes/{proponente.uuid}/concluir-cadastro/",
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        Proponente.objects.get(uuid=proponente.uuid).status
        == Proponente.STATUS_INSCRITO
    )
    mock_delay.assert_called_once_with(str(proponente.uuid))


def test_proponente_api_concluir_cadastro_sem_documentos_obrigatorios(
    client, proponente, tipo_documento
):
    assert (
        Proponente.objects.get(uuid=proponente.uuid).status
        == Proponente.STATUS_EM_PROCESSO
    )
    response = client.patch(f'/proponentes/{proponente.uuid}/concluir-cadastro/', content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == "Documento obrigatório ainda precisa ser enviado!"
