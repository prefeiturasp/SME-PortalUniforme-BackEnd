import json

import pytest
from rest_framework import status

from sme_uniforme_apps.proponentes.models import Proponente

pytestmark = pytest.mark.django_db


def test_proponente_api_create_valida_limite_categoria(
        client, payload_proponente,
        payload_ofertas_de_uniformes_acima_limite,
        uniforme_camisa, uniforme_calca, uniforme_tenis, uniforme_meias,
        limite_categoria_calcado, limite_categoria_malharia):
    payload_proponente["ofertas_de_uniformes"] = payload_ofertas_de_uniformes_acima_limite
    response = client.post('/proponentes/', data=json.dumps(payload_proponente), content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result[0] == 'Valor total da categoria Kit Verão está acima do limite de R$ 50.00.'


def test_proponente_api_create_valida_fornecimento_total_categoria(
        client, payload_proponente,
        payload_ofertas_de_uniformes_faltando_a_camisa,
        uniforme_camisa, uniforme_calca, uniforme_tenis, uniforme_meias):
    payload_proponente["ofertas_de_uniformes"] = payload_ofertas_de_uniformes_faltando_a_camisa
    response = client.post('/proponentes/', data=json.dumps(payload_proponente), content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result[0] == 'Não foram fornecidos todos os itens da categoria Kit Verão. ' \
                        'Não é permitido o fornecimento parcial de uma categoria.'


def test_proponente_api_create_sem_anexos(client, payload_proponente_sem_anexos):
    response = client.post('/proponentes/', data=json.dumps(payload_proponente_sem_anexos),
                           content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)
    assert Proponente.objects.filter(uuid=result["uuid"]).exists()
