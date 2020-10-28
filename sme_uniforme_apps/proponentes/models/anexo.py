from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase
from .proponente import Proponente
from .tipo_documento import TipoDocumento


class Anexo(ModeloBase):
    # Status Choice
    STATUS_APROVADO = 'APROVADO'
    STATUS_REPROVADO = 'REPROVADO'
    STATUS_PENDENTE = 'PENDENTE'
    STATUS_VENCIDO = 'VENCIDO'

    STATUS_NOMES = {
        STATUS_APROVADO: 'Aprovado',
        STATUS_REPROVADO: 'Reprovado',
        STATUS_PENDENTE: 'Pendente',
        STATUS_VENCIDO: 'Vencido'
    }

    STATUS_CHOICES = (
        (STATUS_APROVADO, STATUS_NOMES[STATUS_APROVADO]),
        (STATUS_REPROVADO, STATUS_NOMES[STATUS_REPROVADO]),
        (STATUS_PENDENTE, STATUS_NOMES[STATUS_PENDENTE]),
        (STATUS_VENCIDO, STATUS_NOMES[STATUS_VENCIDO]),
    )

    historico = AuditlogHistoryField()

    proponente = models.ForeignKey(Proponente, on_delete=models.CASCADE, blank=True, null=True, related_name='anexos')

    arquivo = models.FileField()

    data_validade = models.DateField(null=True, blank=True)

    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_PENDENTE
    )

    justificativa = models.TextField('Justificativa', blank=True, null=True)

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
            "data_validade": self.data_validade,
            "uuid": self.uuid
        }

    class Meta:
        verbose_name = "Anexo"
        verbose_name_plural = "Anexos"


auditlog.register(Anexo)
