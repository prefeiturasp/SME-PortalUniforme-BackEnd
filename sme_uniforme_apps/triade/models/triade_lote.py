from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase
from sme_uniforme_apps.proponentes.models import Proponente


class TriadeLote(ModeloBase):
    proponente = models.ForeignKey(
        Proponente,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="triade_lotes",
    )
    external_batch_id = models.CharField(max_length=128, unique=True, db_index=True)
    batch_id = models.UUIDField(blank=True, null=True, unique=True)
    submission_id = models.UUIDField(blank=True, null=True, unique=True)
    analysis_desk_id = models.CharField(max_length=255, blank=True, null=True)
    source_system = models.CharField(max_length=100, blank=True, null=True)
    schema_version = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=30, blank=True, null=True)
    decisao_parecer = models.CharField(max_length=20, blank=True, null=True)
    parecer_texto = models.TextField(blank=True, null=True)
    confirmado_em = models.DateTimeField(blank=True, null=True)
    confirmado_por = models.CharField(max_length=255, blank=True, null=True)
    payload_envio = models.TextField(blank=True, null=True)
    metadata = models.TextField(blank=True, null=True)
    resposta_criacao = models.TextField(blank=True, null=True)
    status_http_criacao = models.PositiveSmallIntegerField(blank=True, null=True)
    resposta_inicio = models.TextField(blank=True, null=True)
    status_http_inicio = models.PositiveSmallIntegerField(blank=True, null=True)
    ultimo_erro = models.TextField(blank=True, null=True)
    enviado_em = models.DateTimeField(blank=True, null=True)
    iniciado_em = models.DateTimeField(blank=True, null=True)
    callback_recebido_em = models.DateTimeField(blank=True, null=True)
    concluido_em = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.external_batch_id

    class Meta:
        verbose_name = "Lote TRIADE"
        verbose_name_plural = "Lotes TRIADE"
        ordering = ("-criado_em",)
