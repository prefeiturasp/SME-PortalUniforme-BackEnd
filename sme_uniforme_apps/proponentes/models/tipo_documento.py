from django.core.validators import RegexValidator
from django.db import models

from sme_uniforme_apps.core.models_abstracts import ModeloBase


class TipoDocumento(ModeloBase):
    identificador = models.CharField(
        "Identificador",
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        help_text="Use apenas letras, números, hífen e underscore.",
        validators=[
            RegexValidator(
                regex=r"^[0-9A-Za-z_-]+$",
                message="Use apenas letras, números, hífen e underscore.",
            )
        ],
    )
    nome = models.TextField('Tipo de documento', unique=True)
    obrigatorio = models.BooleanField(default=True)
    visivel = models.BooleanField(default=True)
    tem_data_validade = models.BooleanField(default=False)
    obrigatorio_sme = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.nome} {"(obrigatório)" if self.obrigatorio else ""}'

    @classmethod
    def tipos_obrigatorios(cls):
        return set(cls.objects.filter(obrigatorio=True).values_list('id', flat=True))

    class Meta:
        verbose_name = "Tipo de documento"
        verbose_name_plural = "Tipos de documentos"
