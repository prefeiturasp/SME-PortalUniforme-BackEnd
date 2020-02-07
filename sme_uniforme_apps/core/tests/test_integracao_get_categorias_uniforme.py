import json

import pytest
from rest_framework import status

from ..models import Uniforme

pytestmark = pytest.mark.django_db


def test_uniformes_api_get_categorias(client, uniforme_meias, uniforme_tenis):
    response = client.get('/uniformes/categorias/', content_type='application/json')
    result = json.loads(response.content)

    esperado = [
        {
            'id': Uniforme.CATEGORIA_MALHARIA,
            'nome': Uniforme.CATEGORIA_NOMES[Uniforme.CATEGORIA_MALHARIA]
        },
        {
            'id': Uniforme.CATEGORIA_CALCADO,
            'nome': Uniforme.CATEGORIA_NOMES[Uniforme.CATEGORIA_CALCADO]
        }
    ]
    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
