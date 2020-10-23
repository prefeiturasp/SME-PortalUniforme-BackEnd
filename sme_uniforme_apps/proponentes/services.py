import logging

import requests
from django.conf import settings

from ..custom_user.models import User
from .models.lista_negra import ListaNegra

LAYERS = 'address'
BUNDARY = 'whosonfirst:locality:101965533'
API_URL = f'{settings.GEOREF_API_URL}/v1/search'

log = logging.getLogger(__name__)


def cnpj_esta_bloqueado(cnpj):
    return ListaNegra.cnpj_bloqueado(cnpj)


def cria_usuario_proponentes_existentes(queryset):
    for proponente in queryset.all():
        if not proponente.usuario:
            novo_usuario = User.objects.create_user(email=proponente.email,
                                                    first_name=proponente.responsavel,
                                                    password="".join([n for n in proponente.cnpj if n.isdigit()])[:5])
            proponente.usuario = novo_usuario
            proponente.save()


def muda_status_de_proponentes(queryset, novo_status):
    for proponente in queryset.all():
        if proponente.status != novo_status:
            proponente.status = novo_status
            proponente.save()
        if novo_status == "CREDENCIADO":
            atualiza_coordenadas_lojas(proponente.lojas)


def envia_email_pendencias(queryset):
    for proponente in queryset.all():
        proponente.comunicar_pendencia()


def atualiza_coordenadas(queryset):
    for proponente in queryset.all():
        atualiza_coordenadas_lojas(proponente.lojas)


def atualiza_coordenadas_lojas(lojas):
    log.info("Atualizando coordendas das lojas físicas")
    for loja in lojas.all():
        params = {
            'text': f'{loja.endereco}, {loja.numero}, {loja.bairro}, {loja.cep}',
            'layers': LAYERS,
            'boundary.gid': BUNDARY}
        try:
            log.info(f"Buscando coordenadas: {params}")
            response = requests.get(API_URL, params=params)
            log.info(f"retorno da api: {response.json()}")
            loja.latitude, loja.longitude = busca_latitude_e_longitude(response.json())
            loja.save()
        except Exception as e:
            log.info(f"Erro ao acessar georef.sme API: {e.__str__()}")


def busca_latitude_e_longitude(payload):
    if not payload['features']:
        raise Exception(f"API não retornou dados válidos: {payload}")

    # A georef.sme API retorna longitude e latitude
    # mas o retorno será latitude e longitude 
    return payload['features'][0]['geometry']['coordinates'][::-1]


def haversine(lat, lon):
    """
    Formula haversine para buscar as lojas ordenando pela distancia.
    Para limitar os resultados a partir de uma distancia, descomentar a linha do where.
    """
    return f"""
        SELECT id
            FROM ( SELECT
                    id,
                    111.045 * DEGREES(ACOS(COS(RADIANS({lat}))
                    * COS(RADIANS(latitude))
                    * COS(RADIANS(longitude) - RADIANS({lon})) + SIN(RADIANS({lat}))
                    * SIN(RADIANS(latitude)))) AS distance_in_km
                 FROM proponentes_loja) as distancias
--             WHERE distancias.distance_in_km <= 10
            """
