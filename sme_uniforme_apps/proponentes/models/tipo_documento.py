from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase


class TipoDocumento(ModeloBase):
    nome = models.TextField('Tipo de documento', unique=True, max_length=600)
    obrigatorio = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.nome} {"(obrigatório)" if self.obrigatorio else ""}'

    @classmethod
    def tipos_obrigatorios(cls):
        return set(cls.objects.filter(obrigatorio=True).values_list('id', flat=True))

    class Meta:
        verbose_name = "Tipo de documento"
        verbose_name_plural = "Tipos de documentos"
