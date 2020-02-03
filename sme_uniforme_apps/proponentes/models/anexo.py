from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from sme_uniforme_apps.core.models_abstracts import ModeloBase

from .proponente import Proponente


class Anexo(ModeloBase):
    historico = AuditlogHistoryField()

    proponente = models.ForeignKey(Proponente, on_delete=models.CASCADE, blank=True, null=True, related_name='anexos')

    arquivo = models.FileField()

    # def __str__(self):
    #     return f"{self.proponente.razao_social} - {self.endereco}"

    class Meta:
        verbose_name = "Anexo"
        verbose_name_plural = "Anexos"


auditlog.register(Anexo)
