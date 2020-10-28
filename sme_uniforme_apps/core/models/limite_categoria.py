import logging

from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase

from .uniforme import Uniforme

log = logging.getLogger(__name__)


class LimiteCategoria(ModeloBase):
    categoria_uniforme = models.CharField(
        max_length=20,
        choices=Uniforme.CATEGORIA_CHOICES,
        default=Uniforme.CATEGORIA_KIT_VERAO,
        unique=True,
    )
    preco_maximo = models.DecimalField('Preço máximo', max_digits=9, decimal_places=2, default=0.00)
    obrigatorio = models.BooleanField('Categoria obrigatoria?', default=True)

    def __str__(self):
        return f'{Uniforme.CATEGORIA_NOMES[self.categoria_uniforme]} Preço Máximo: R$ {self.preco_maximo:.2f}'

    @classmethod
    def limites_por_categoria_as_dict(cls):
        result = {}
        for categoria in cls.objects.filter(obrigatorio=True):
            result[categoria.categoria_uniforme] = categoria.preco_maximo
        log.info(f"Limites por categoria: {result}")
        return result

    class Meta:
        verbose_name = "Limite e obrigatoriedade da categoria"
        verbose_name_plural = "Limites e obrigatoriedades de categorias"
