from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase


class Uniforme(ModeloBase):
    # Categoria Choice
    CATEGORIA_MALHARIA = 'MALHARIA'
    CATEGORIA_CALCADO = 'CALCADO'

    CATEGORIA_NOMES = {
        CATEGORIA_MALHARIA: 'Peças Têxteis',
        CATEGORIA_CALCADO: 'Calçados',
    }

    CATEGORIA_CHOICES = (
        (CATEGORIA_MALHARIA, CATEGORIA_NOMES[CATEGORIA_MALHARIA]),
        (CATEGORIA_CALCADO, CATEGORIA_NOMES[CATEGORIA_CALCADO]),
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
        max_length=10,
        choices=CATEGORIA_CHOICES,
        default=CATEGORIA_MALHARIA
    )

    unidade = models.CharField(
        max_length=10,
        choices=UNIDADE_CHOICES,
        default=UNIDADE_UNIDADE
    )

    quantidade = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f'{self.nome} ({self.quantidade} {self.UNIDADE_NOMES[self.unidade]})'

    class Meta:
        verbose_name = "Peça de Uniforme"
        verbose_name_plural = "Peças de Uniforme"
