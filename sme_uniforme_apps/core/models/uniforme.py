from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase


class Uniforme(ModeloBase):
    nome = models.CharField('Peça de uniforme', unique=True, max_length=100, blank=True, default='')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Peça de Uniforme"
        verbose_name_plural = "Peças de Uniforme"
