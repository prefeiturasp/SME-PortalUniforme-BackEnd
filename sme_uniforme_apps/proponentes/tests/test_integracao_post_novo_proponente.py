import json

import pytest
from rest_framework import status

from ..models import Proponente

pytestmark = pytest.mark.django_db


def test_proponente_api_create(client, payload_proponente):
    response = client.post('/proponentes/', data=json.dumps(payload_proponente), content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert Proponente.objects.filter(uuid=result["uuid"]).exists()

    # Verifica se a gravação dos anexos foi feita registrando os tipos de documento
    novo_proponente = Proponente.objects.get(uuid=result["uuid"])
    for anexo in novo_proponente.anexos.all():
        assert anexo.tipo_documento is not None


def test_proponente_api_create_valida_tipo_documento_obrigatorio(
        client, payload_proponente,
        payload_arquivos_anexos_faltando_documentos_obrigatorios):
    payload_proponente["arquivos_anexos"] = payload_arquivos_anexos_faltando_documentos_obrigatorios
    response = client.post('/proponentes/', data=json.dumps(payload_proponente), content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result[0] == 'Não foi enviado o documento Certidão Negativa (obrigatório).'


def test_proponente_api_create_valida_limite_categoria(
        client, payload_proponente,
        payload_ofertas_de_uniformes_acima_limite,
        uniforme_camisa, uniforme_calca, uniforme_tenis, uniforme_meias,
        limite_categoria_calcado, limite_categoria_malharia):
    payload_proponente["ofertas_de_uniformes"] = payload_ofertas_de_uniformes_acima_limite
    response = client.post('/proponentes/', data=json.dumps(payload_proponente), content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result[0] == 'Valor total da categoria Peças Têxteis está acima do limite de R$ 50.00.'
