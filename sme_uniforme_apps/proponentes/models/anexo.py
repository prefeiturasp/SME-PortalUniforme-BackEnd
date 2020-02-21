from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase
from .proponente import Proponente
from .tipo_documento import TipoDocumento


class Anexo(ModeloBase):
    historico = AuditlogHistoryField()

    proponente = models.ForeignKey(Proponente, on_delete=models.CASCADE, blank=True, null=True, related_name='anexos')

    arquivo = models.FileField()

    tipo_documento = models.ForeignKey(
        TipoDocumento,
        on_delete=models.PROTECT,
        blank=True, null=True,
        related_name='anexos'
    )

    def as_dict(self):
        return {
            "proponente": self.proponente.uuid,
            "arquivo": self.arquivo,
            "tipo_documento": self.tipo_documento,
            "uuid": self.uuid
        }

    class Meta:
        verbose_name = "Anexo"
        verbose_name_plural = "Anexos"


auditlog.register(Anexo)
