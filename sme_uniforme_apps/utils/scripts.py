from sme_uniforme_apps.proponentes.models.proponente import Proponente
from sme_uniforme_apps.core.models.uniforme import Uniforme


def reseta_status_e_ofertas_dos_proponentes():
    """
    Exclui todos os itens de ofertas de todos os proponentes;
    Aplica o status inscritos para os proponentes;
    """

    print('### >>> Limpa as ofertas de uniforme')
    limpa_ofertas_de_uniforme()
    print('### >>> Seta os proponentes com status de inscrito')
    set_status_inscrito()


def limpa_ofertas_de_uniforme():
    proponentes = Proponente.objects.all()
    for p in proponentes:
        p.ofertas_de_uniformes.all().delete()


def set_status_inscrito():
    proponentes = Proponente.objects.exclude(status=Proponente.STATUS_INSCRITO)
    proponentes.update(status=Proponente.STATUS_INSCRITO)


def migra_uniformes_para_categoria_padrao():
    uniformes = Uniforme.objects.all()
    print('### >>> Migra itens de unidforme para categoria padrão')
    uniformes.update(categoria=Uniforme.CATEGORIA_KIT_UNIFORME)