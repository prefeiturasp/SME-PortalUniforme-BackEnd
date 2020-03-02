import pytest
from rest_framework import status

from sme_uniforme_apps.proponentes.models import Anexo, Proponente

pytestmark = pytest.mark.django_db


def test_proponente_api_concluir_cadastro(client, proponente):
    assert Proponente.objects.get(uuid=proponente.uuid).status == Proponente.STATUS_EM_PROCESSO
    response = client.patch(f'/proponentes/{proponente.uuid}/concluir-cadastro/', content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert Proponente.objects.get(uuid=proponente.uuid).status == Proponente.STATUS_INSCRITO

def test_proponente_api_concluir_cadastro_sem_documentos_obrigatorios(client, proponente, tipo_documento):
    assert Proponente.objects.get(uuid=proponente.uuid).status == Proponente.STATUS_EM_PROCESSO
    response = client.patch(f'/proponentes/{proponente.uuid}/concluir-cadastro/', content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == "Documento obrigatório ainda precisa ser enviado!"
