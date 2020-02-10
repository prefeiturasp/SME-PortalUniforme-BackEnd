from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase
from .proponente import Proponente
from ...core.models.uniforme import Uniforme


# from auditlog.models import AuditlogHistoryField
# from auditlog.registry import auditlog


class OfertaDeUniforme(ModeloBase):
    # historico = AuditlogHistoryField()

    proponente = models.ForeignKey(Proponente, on_delete=models.CASCADE, related_name='ofertas_de_uniformes',
                                   blank=True, null=True)
    uniforme = models.ForeignKey(Uniforme, on_delete=models.PROTECT, related_name='proponentes')
    preco = models.DecimalField('Preço', max_digits=9, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.uniforme.nome} - {self.preco} - {self.proponente.razao_social if self.proponente else ''}"

    class Meta:
        verbose_name = "oferta de uniforme"
        verbose_name_plural = "ofertas de uniforme"
        unique_together = ['proponente', 'uniforme']

# TODO Corrigir erro que da ao excluir um proponente quando o log da oferta de uniforme está ativo
# auditlog.register(OfertaDeUniforme)
