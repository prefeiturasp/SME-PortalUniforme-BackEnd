from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase, SingletonModel
from django.core import validators


class Parametros(SingletonModel, ModeloBase):
    edital = models.FileField(blank=True, null=True)
    instrucao_normativa = models.FileField('Instrução Normativa', blank=True, null=True)
    email_sme = models.CharField(
        "E-mail núcleo.", max_length=255, validators=[validators.EmailValidator()], default="", unique=True
    )

    def __str__(self):
        return self.edital.name

    class Meta:
        verbose_name = "Parâmetro"
        verbose_name_plural = "Parâmetros"
