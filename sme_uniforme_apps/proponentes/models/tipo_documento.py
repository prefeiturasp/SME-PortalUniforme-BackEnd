from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase


class TipoDocumento(ModeloBase):
    nome = models.CharField('Tipo de documento', unique=True, max_length=100)
    obrigatorio = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.nome} {"(obrigatório)" if self.obrigatorio else ""}'

    class Meta:
        verbose_name = "Tipo de documento"
        verbose_name_plural = "Tipos de documentos"
