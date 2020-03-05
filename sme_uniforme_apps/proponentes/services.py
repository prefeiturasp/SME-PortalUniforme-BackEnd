import logging
import requests

from .models.lista_negra import ListaNegra
from ..custom_user.models import User


LAYERS = 'address'
BUNDARY = 'whosonfirst:locality:101965533'
API_URL = 'https://georef.sme.prefeitura.sp.gov.br/v1/search'

log = logging.getLogger(__name__)


def cnpj_esta_bloqueado(cnpj):
    return ListaNegra.cnpj_bloqueado(cnpj)


def cria_usuario_novo_proponente(proponente):
    User.cria_usuario(email=proponente.email, nome=proponente.responsavel, senha=proponente.protocolo)


def muda_status_de_proponentes(queryset, novo_status):
     for proponente in queryset.all():
            if proponente.status != novo_status:
                proponente.status = novo_status
                proponente.save()
            if novo_status == "APROVADO":
                atualiza_coordenadas_lojas(proponente.lojas)


def atualiza_coordenadas_lojas(lojas):
    log.info("Atualizando coordendas das lojas físicas")
    for loja in lojas.all():
        params = {
            'text': f'{loja.endereco}, {loja.numero}, {loja.bairro}', 
            'layers': LAYERS, 
            'boundary.gid': BUNDARY}
        try:
            log.info(f"Buscando coordenadas: {params}")
            response = requests.get(API_URL, params=params)
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

