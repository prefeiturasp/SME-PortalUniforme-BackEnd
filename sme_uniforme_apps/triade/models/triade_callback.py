from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase

from .triade_lote import TriadeLote


class TriadeCallback(ModeloBase):
    lote = models.ForeignKey(
        TriadeLote,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="callbacks",
    )
    delivery_id = models.UUIDField(unique=True, db_index=True)
    external_batch_id = models.CharField(
        max_length=128, blank=True, null=True, db_index=True
    )
    batch_id = models.UUIDField(blank=True, null=True, db_index=True)
    submission_id = models.UUIDField(blank=True, null=True, db_index=True)
    assinatura_recebida = models.CharField(max_length=255, blank=True, null=True)
    payload_bruto = models.TextField(blank=True, null=True)
    payload_hash = models.CharField(max_length=64, db_index=True)
    status_processamento = models.CharField(max_length=30, default="recebido")
    erro = models.TextField(blank=True, null=True)
    processado_em = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.delivery_id)

    class Meta:
        verbose_name = "Callback TRIADE"
        verbose_name_plural = "Callbacks TRIADE"
        ordering = ("-criado_em",)
