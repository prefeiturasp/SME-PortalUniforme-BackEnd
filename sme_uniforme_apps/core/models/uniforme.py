import logging

from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase

log = logging.getLogger(__name__)


class Uniforme(ModeloBase):
    # Categoria Choice
    CATEGORIA_MALHARIA = 'MALHARIA'
    CATEGORIA_CALCADO = 'CALCADO'
    CATEGORIA_KIT_VERAO = 'KIT_VERAO'
    CATEGORIA_KIT_INVERNO = 'KIT_INVERNO'

    CATEGORIA_NOMES = {
        CATEGORIA_MALHARIA: 'Vestuário',
        CATEGORIA_CALCADO: 'Calçados',
        CATEGORIA_KIT_VERAO: 'Kit Verão',
        CATEGORIA_KIT_INVERNO: 'Kit Inverno',
    }

    CATEGORIA_CHOICES = (
        (CATEGORIA_MALHARIA, CATEGORIA_NOMES[CATEGORIA_MALHARIA]),
        (CATEGORIA_CALCADO, CATEGORIA_NOMES[CATEGORIA_CALCADO]),
        (CATEGORIA_KIT_VERAO, CATEGORIA_NOMES[CATEGORIA_KIT_VERAO]),
        (CATEGORIA_KIT_INVERNO, CATEGORIA_NOMES[CATEGORIA_KIT_INVERNO]),
    )

    # Unidade Choice
    UNIDADE_UNIDADE = 'UNIDADE'
    UNIDADE_PAR = 'PAR'

    UNIDADE_NOMES = {
        UNIDADE_UNIDADE: 'Unidade(s)',
        UNIDADE_PAR: 'Par(es)',
    }

    UNIDADE_CHOICES = (
        (UNIDADE_UNIDADE, UNIDADE_NOMES[UNIDADE_UNIDADE]),
        (UNIDADE_PAR, UNIDADE_NOMES[UNIDADE_PAR]),
    )

    nome = models.CharField('Peça de uniforme', unique=True, max_length=100, blank=True, default='')

    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        default=CATEGORIA_KIT_VERAO
    )

    unidade = models.CharField(
        max_length=10,
        choices=UNIDADE_CHOICES,
        default=UNIDADE_UNIDADE
    )

    quantidade = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        if self.unidade == self.UNIDADE_PAR:
            unidades = 'par' if self.quantidade == 1 else 'pares'
        else:
            unidades = 'unidade' if self.quantidade == 1 else 'unidades'

        return f'{self.nome} ({self.quantidade} {unidades})'

    @classmethod
    def qtd_itens_por_categoria_as_dict(cls):
        # Inicializa totais por categoria
        qtd_itens_por_categoria = {categoria: 0 for categoria in cls.CATEGORIA_NOMES.keys()}

        # Conta a quantidade de itens de uniforme por categoria
        for uniforme in cls.objects.all():
            qtd_itens_por_categoria[uniforme.categoria] += 1

        log.info(f"Quantidade de itens por categoria: {qtd_itens_por_categoria}")
        return qtd_itens_por_categoria

    @classmethod
    def categorias_to_json(cls):
        result = []
        for categoria in cls.CATEGORIA_CHOICES:
            uniformes = []
            for uniforme in cls.objects.filter(categoria=categoria[0]):
                uniformes.append(
                    {
                        "id": uniforme.id,
                        "nome": uniforme.nome,
                        "unidade": uniforme.unidade,
                        "quantidade": uniforme.quantidade,
                        "descricao": uniforme.__str__()
                    }
                )
            choice = {
                'id': categoria[0],
                'nome': categoria[1],
                'uniformes': uniformes
            }
            result.append(choice)
        return result

    class Meta:
        verbose_name = "Peça de Uniforme"
        verbose_name_plural = "Peças de Uniforme"
