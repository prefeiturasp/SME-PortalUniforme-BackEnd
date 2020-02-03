from django.db import models

from .validators import cnpj_validation

from sme_uniforme_apps.core.models_abstracts import ModeloBase


class ListaNegra(ModeloBase):

    cnpj = models.CharField(
        "CNPJ", max_length=20, validators=[cnpj_validation], blank=True, null=True, default="", unique=True
    )
    razao_social = models.CharField("Razão Social", max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.cnpj} - {self.razao_social}"

    @classmethod
    def cnpj_bloqueado(cls, cnpj):
        return cls.objects.filter(cnpj=cnpj).exists()

    class Meta:
        verbose_name = "CNPJ bloqueado"
        verbose_name_plural = "CNPJ's bloqueados"
