from .triade_lote import TriadeLote


class TriadeEstatistica(TriadeLote):
    class Meta:
        proxy = True
        verbose_name = "Estatistica TRIADE"
        verbose_name_plural = "Estatisticas TRIADE"
