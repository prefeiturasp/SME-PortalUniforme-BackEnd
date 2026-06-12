from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase
from sme_uniforme_apps.proponentes.models import Anexo

from .triade_lote import TriadeLote


class TriadeDocumento(ModeloBase):
    lote = models.ForeignKey(
        TriadeLote, on_delete=models.CASCADE, related_name="documentos"
    )
    anexo = models.ForeignKey(
        Anexo,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="triade_documentos",
    )
    external_document_id = models.CharField(max_length=255, db_index=True)
    document_id = models.UUIDField(blank=True, null=True, unique=True)
    external_document_type = models.CharField(max_length=255, blank=True, null=True)
    document_type = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=30, blank=True, null=True)
    decisao = models.CharField(max_length=20, blank=True, null=True)
    justificativa = models.TextField(blank=True, null=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    error = models.TextField(blank=True, null=True)
    metadata = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.external_document_id

    class Meta:
        verbose_name = "Documento TRIADE"
        verbose_name_plural = "Documentos TRIADE"
        ordering = ("-criado_em",)
        unique_together = (("lote", "external_document_id"),)
