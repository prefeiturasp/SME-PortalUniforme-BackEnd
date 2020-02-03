from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase


class MeioDeRecebimento(ModeloBase):
    nome = models.CharField('Meio de recebimento', unique=True, max_length=100, blank=True, default='')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Meio de recebimento"
        verbose_name_plural = "Meios de recebimento"
