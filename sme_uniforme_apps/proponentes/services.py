from .models.lista_negra import ListaNegra


def cnpj_esta_bloqueado(cnpj):
    return ListaNegra.cnpj_bloqueado(cnpj)
