from django.db import models

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

from .validators import phone_validation, cep_validation
from sme_uniforme_apps.core.models_abstracts import ModeloBase

from .proponente import Proponente

import geopy.distance

class Loja(ModeloBase):
    historico = AuditlogHistoryField()

    proponente = models.ForeignKey(Proponente, on_delete=models.CASCADE, blank=True, null=True, related_name='lojas')

    nome_fantasia = models.CharField(max_length=100, blank=True, default="")
    cep = models.CharField("CEP", max_length=20, validators=[cep_validation])
    endereco = models.CharField("Logradouro", max_length=255)
    bairro = models.CharField("Bairro", max_length=255)
    numero = models.CharField("Numero", max_length=255, blank=True, default="")
    complemento = models.CharField("Complemento", max_length=255, null=True, blank=True)

    comprovante_endereco = models.FileField("Comprovante de Endereço", blank=True, null=True, max_length=255)

    latitude = models.FloatField("Latitude", blank=True, null=True)
    longitude = models.FloatField("longitude", blank=True, null=True)

    numero_iptu = models.CharField("Numero IPTU", max_length=20, blank=True, default="")

    telefone = models.CharField(
        "Telefone", max_length=20, validators=[phone_validation], blank=True, null=True, default=""
    )

    foto_fachada = models.FileField('Foto da fachada da loja', blank=True, null=True)

    site = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome_fantasia}"

    def get_distancia(self, lat, lon):
        origem = (lat, lon)
        destino = (self.latitude, self.longitude)
        return geopy.distance.distance(origem, destino).km

    class Meta:
        verbose_name = "Loja física"
        verbose_name_plural = "Lojas físicas"
        ordering = ('id', )


auditlog.register(Loja)
