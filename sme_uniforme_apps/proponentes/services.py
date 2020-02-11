from .models.lista_negra import ListaNegra
from ..custom_user.models import User


def cnpj_esta_bloqueado(cnpj):
    return ListaNegra.cnpj_bloqueado(cnpj)


def cria_usuario_novo_proponente(proponente):
    User.cria_usuario(email=proponente.email, nome=proponente.responsavel, senha=proponente.protocolo)
