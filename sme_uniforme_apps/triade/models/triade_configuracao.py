from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase, SingletonModel


class TriadeConfiguracao(SingletonModel, ModeloBase):
    habilitado = models.BooleanField(default=True)
    enviar_apenas_documentos_obrigatorios = models.BooleanField(default=False)

    def __str__(self):
        return "Configuracao TRIADE"

    class Meta:
        verbose_name = "Configuracao TRIADE"
        verbose_name_plural = "Configuracoes TRIADE"
