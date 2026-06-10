import json

import pytest
from model_bakery import baker
from rest_framework import status

from sme_uniforme_apps.core.models import Uniforme
from sme_uniforme_apps.proponentes.models import Proponente

pytestmark = pytest.mark.django_db


def configure_limites_permissivos():
    baker.make(
        "LimiteCategoria",
        categoria_uniforme=Uniforme.CATEGORIA_KIT_VERAO,
        preco_maximo=999,
    )
    baker.make(
        "LimiteCategoria",
        categoria_uniforme=Uniforme.CATEGORIA_KIT_INVERNO,
        preco_maximo=999,
    )


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
    configure_limites_permissivos()
    payload_proponente["ofertas_de_uniformes"] = payload_ofertas_de_uniformes_faltando_a_camisa
    response = client.post('/proponentes/', data=json.dumps(payload_proponente), content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result[0] == 'Não foram fornecidos todos os itens da categoria Kit Verão. ' \
                        'Não é permitido o fornecimento parcial de uma categoria.'


def test_proponente_api_create_sem_anexos(client, payload_proponente_sem_anexos):
    configure_limites_permissivos()
    response = client.post('/proponentes/', data=json.dumps(payload_proponente_sem_anexos),
                           content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)
    assert Proponente.objects.filter(uuid=result["uuid"]).exists()


def test_proponente_api_create_com_cnpj_alfanumerico(
    client,
    payload_proponente_sem_anexos,
):
    configure_limites_permissivos()
    payload_proponente_sem_anexos["cnpj"] = "AB.12C.3D4/0001-39"

    response = client.post(
        "/proponentes/",
        data=json.dumps(payload_proponente_sem_anexos),
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)
    assert Proponente.objects.filter(uuid=result["uuid"]).exists()


def test_proponente_api_create_rejeita_cnpj_alfanumerico_duplicado_com_formato_diferente(
    client,
    payload_proponente_sem_anexos,
):
    configure_limites_permissivos()
    Proponente.objects.create(
        cnpj="AB.12C.3D4/0001-39",
        razao_social="Empresa Existente",
        end_logradouro="Rua Teste",
        end_cidade="São Paulo",
        end_uf="SP",
        end_cep="99999-000",
        telefone="(11) 99999-9999",
        email="existente@teste.com",
        responsavel="Responsavel Existente",
    )
    payload_proponente_sem_anexos["cnpj"] = "ab12c3d4000139"

    response = client.post(
        "/proponentes/",
        data=json.dumps(payload_proponente_sem_anexos),
        content_type="application/json",
    )
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result["cnpj"] == ["Já existe um proponente com este CNPJ."]
