import environ

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from brazilnum.cnpj import validate_cnpj
from django.core import validators
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from sme_uniforme_apps.core.models_abstracts import ModeloBase
from .validators import phone_validation, cep_validation, cnpj_validation
from ..services import cnpj_esta_bloqueado
from ..tasks import enviar_email_confirmacao_cadastro, enviar_email_confirmacao_pre_cadastro


class Proponente(ModeloBase):
    historico = AuditlogHistoryField()

    UF_CHOICES = (
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MG', 'Minas Gerais'),
        ('MS', 'Mato Grosso do Sul'),
        ('MT', 'Mato Grosso'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('PR', 'Paraná'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('RS', 'Rio Grande do Sul'),
        ('SC', 'Santa Catarina'),
        ('SE', 'Sergipe'),
        ('SP', 'São Paulo'),
        ('TO', 'Tocantins'),
    )

    # Status Choice
    STATUS_INSCRITO = 'INSCRITO'
    STATUS_BLOQUEADO = 'BLOQUEADO'
    STATUS_EM_PROCESSO = 'EM_PROCESSO'

    STATUS_NOMES = {
        STATUS_INSCRITO: 'Inscrito',
        STATUS_BLOQUEADO: 'Bloqueado',
        STATUS_EM_PROCESSO: 'Em processo'
    }

    STATUS_CHOICES = (
        (STATUS_INSCRITO, STATUS_NOMES[STATUS_INSCRITO]),
        (STATUS_BLOQUEADO, STATUS_NOMES[STATUS_BLOQUEADO]),
        (STATUS_EM_PROCESSO, STATUS_NOMES[STATUS_EM_PROCESSO]),
    )

    cnpj = models.CharField(
        "CNPJ", max_length=20, validators=[cnpj_validation], blank=True, null=True, default="", unique=True
    )
    razao_social = models.CharField("Razão Social", max_length=255, blank=True, null=True)

    end_logradouro = models.CharField(
        'endereço',
        max_length=100,
        blank=True
    )

    end_cidade = models.CharField(
        'cidade',
        max_length=80,
        blank=True
    )

    end_uf = models.CharField(
        'estado',
        max_length=2,
        blank=True,
        choices=UF_CHOICES,
        default='SP'
    )

    end_cep = models.CharField(
        'cep',
        max_length=10,
        blank=True,
        default='',
        validators=[cep_validation]
    )

    telefone = models.CharField(
        "Telefone", max_length=20, validators=[phone_validation], blank=True, null=True, default=""
    )

    email = models.CharField(
        "E-mail", max_length=255, validators=[validators.EmailValidator()], blank=True, null=True, default="",
        unique=True
    )

    responsavel = models.CharField("Responsável", max_length=255, blank=True, null=True)

    status = models.CharField(
        'status',
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_EM_PROCESSO
    )

    def __str__(self):
        return f"{self.responsavel} - {self.email} - {self.telefone}"

    def comunicar_pre_cadastro(self):
        if self.email:
            env = environ.Env()
            url = f'https://{env("SERVER_NAME")}/cadastro?uuid={self.uuid}'
            enviar_email_confirmacao_pre_cadastro.delay(self.email,
                                                        {'protocolo': self.protocolo, 'url_cadastro': url})

    def comunicar_cadastro(self):
        if self.email:
            enviar_email_confirmacao_cadastro.delay(self.email, {'protocolo': self.protocolo})

    @property
    def protocolo(self):
        return f'{self.uuid.urn[9:17].upper()}'

    @property
    def arquivos_anexos(self):
        return self.anexos.all()

    @classmethod
    def cnpj_ja_cadastrado(cls, cnpj):
        return cls.objects.filter(cnpj=cnpj).exists()

    @staticmethod
    def cnpj_valido(cnpj):
        return validate_cnpj(cnpj)

    @classmethod
    def bloqueia_por_cnpj(cls, cnpj):
        Proponente.objects.filter(cnpj=cnpj).update(status=Proponente.STATUS_BLOQUEADO)

    @classmethod
    def desbloqueia_por_cnpj(cls, cnpj):
        Proponente.objects.filter(cnpj=cnpj).update(status=Proponente.STATUS_INSCRITO)

    @classmethod
    def concluir_cadastro(cls, uuid):
        proponente = Proponente.objects.get(uuid=uuid)
        proponente.status = Proponente.STATUS_INSCRITO
        proponente.save()
        proponente.comunicar_cadastro()

    class Meta:
        verbose_name = "Proponente"
        verbose_name_plural = "Proponentes"


@receiver(post_save, sender=Proponente)
def proponente_post_save(instance, created, **kwargs):
    if created and instance:
        instance.comunicar_pre_cadastro()


@receiver(pre_save, sender=Proponente)
def proponente_pre_save(instance, **kwargs):
    if instance.status == Proponente.STATUS_INSCRITO and instance.cnpj and cnpj_esta_bloqueado(instance.cnpj):
        instance.status = Proponente.STATUS_BLOQUEADO

    elif instance.status == Proponente.STATUS_BLOQUEADO and instance.cnpj and not cnpj_esta_bloqueado(instance.cnpj):
        instance.status = Proponente.STATUS_INSCRITO


auditlog.register(Proponente)
