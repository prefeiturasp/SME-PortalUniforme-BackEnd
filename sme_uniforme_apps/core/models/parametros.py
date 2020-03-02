from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase, SingletonModel


class Parametros(SingletonModel, ModeloBase):
    edital = models.FileField(blank=True, null=True)
    instrucao_normativa = models.FileField('Instrução Normativa', blank=True, null=True)

    def __str__(self):
        return self.edital.name

    class Meta:
        verbose_name = "Parâmetro"
        verbose_name_plural = "Parâmetros"
