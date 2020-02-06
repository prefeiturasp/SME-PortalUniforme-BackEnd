from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase
from .uniforme import Uniforme


class LimiteCategoria(ModeloBase):
    categoria_uniforme = models.CharField(
        max_length=10,
        choices=Uniforme.CATEGORIA_CHOICES,
        default=Uniforme.CATEGORIA_MALHARIA,
        unique=True,
    )
    preco_maximo = models.DecimalField('Preço máximo', max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{Uniforme.CATEGORIA_NOMES[self.categoria_uniforme]} Preço Máximo: R$ {self.preco_maximo:.2f}'

    class Meta:
        verbose_name = "Limite da categoria"
        verbose_name_plural = "Limites de categorias"
