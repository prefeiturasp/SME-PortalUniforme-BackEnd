from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from .validators import phone_validation, cep_validation
from sme_uniforme_apps.core.models_abstracts import ModeloBase

from .proponente import Proponente


class Loja(ModeloBase):
    historico = AuditlogHistoryField()

    proponente = models.ForeignKey(Proponente, on_delete=models.CASCADE, blank=True, null=True, related_name='lojas')

    cep = models.CharField("CEP", max_length=20, validators=[cep_validation])
    endereco = models.CharField("Logradouro", max_length=255)
    bairro = models.CharField("Bairro", max_length=255)
    numero = models.CharField("Numero", max_length=255, blank=True, default="")
    complemento = models.CharField("Complemento", max_length=255, null=True, blank=True)

    latitude = models.CharField("Latitude", max_length=255, blank=True, default="")
    longitude = models.CharField("longitude", max_length=255, blank=True, default="")

    numero_iptu = models.CharField("Numero IPTU", max_length=20, blank=True, default="")

    telefone = models.CharField(
        "Telefone", max_length=20, validators=[phone_validation], blank=True, null=True, default=""
    )

    def __str__(self):
        return f"{self.proponente.razao_social if self.proponente else ''} - {self.endereco}"

    class Meta:
        verbose_name = "Loja física"
        verbose_name_plural = "Lojas físicas"


auditlog.register(Loja)
