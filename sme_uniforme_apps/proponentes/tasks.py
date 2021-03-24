import datetime
import logging

from smtplib import SMTPServerDisconnected

import environ
from celery import shared_task
from celery.schedules import crontab
from celery.task import periodic_task
from django.db.models import Q

from config import celery_app
from ..core.helpers.enviar_email import enviar_email_html

env = environ.Env()

log = logging.getLogger(__name__)


# https://docs.celeryproject.org/en/latest/userguide/tasks.html
@shared_task(
    autoretry_for=(SMTPServerDisconnected,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def enviar_email_confirmacao_cadastro(email, contexto):
    return enviar_email_html(
        'Obrigado pelo envio do seu cadastro',
        'email_confirmacao_cadastro',
        contexto,
        email
    )


@shared_task(
    autoretry_for=(SMTPServerDisconnected,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def enviar_email_confirmacao_pre_cadastro(email, contexto):
    log.info(f'Confirmação de pré-cadastro (Protocolo:{contexto["protocolo"]}) enviada para {email}.')
    return enviar_email_html(
        'Pré-cadastro realizado. Finalize seu cadastro!',
        'email_confirmacao_pre_cadastro',
        contexto,
        email
    )


@shared_task(
    autoretry_for=(SMTPServerDisconnected,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def enviar_email_recuperar_senha(email, contexto):
    log.info(f'Recuperar senha enviada para {email}.')
    return enviar_email_html(
        'Recupere sua senha',
        'email_recuperar_senha',
        contexto,
        email
    )


@shared_task(
    autoretry_for=(SMTPServerDisconnected,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def enviar_email_pendencia(email):
    return enviar_email_html(
        'Cadastro Portal do Uniforme Escolar',
        'email_pendencias_proponente',
        None,
        email
    )

  
@periodic_task(run_every=crontab(hour=17, minute=0))
def alterar_status_documentos_vencidos():
    from ..proponentes.models import Anexo
    anexos = Anexo.objects.filter(data_validade__lt=datetime.date.today()).filter(~Q(status=Anexo.STATUS_VENCIDO))
    anexos.update(status=Anexo.STATUS_VENCIDO, justificativa="Documento vencido")


@celery_app.task(soft_time_limit=1000, time_limit=1200)
def enviar_email_documentos_proximos_vencimento():
    from ..proponentes.models import Proponente
    from ..core.models import Parametros

    daqui_a_5_dias = datetime.date.today() + datetime.timedelta(days=5)
    proponentes_anexos_obrigatorios_sme = Proponente.objects.filter(
        anexos__data_validade=daqui_a_5_dias, anexos__tipo_documento__obrigatorio_sme=True).filter(
        status__in=[Proponente.STATUS_EM_ANALISE, Proponente.STATUS_CREDENCIADO, Proponente.STATUS_APROVADO]
    ).distinct()

    proponentes_anexos = Proponente.objects.filter(
        anexos__data_validade=daqui_a_5_dias, anexos__tipo_documento__obrigatorio_sme=False).filter(
        status__in=[Proponente.STATUS_EM_ANALISE, Proponente.STATUS_CREDENCIADO, Proponente.STATUS_APROVADO]
    ).distinct()

    log.info("Proponentes com anexos próximos do fim da validade: %s", proponentes_anexos.count())

    for proponente in proponentes_anexos.all():
        enviar_email_html(
            'Documento(s) próximo(s) do vencimento',
            'email_documentos_proximos_vencimento',
            None,
            proponente.email
        )

    log.info("Proponentes com anexos obrigatórios sme próximos do fim da validade: %s",
             proponentes_anexos_obrigatorios_sme.count())
    email_sme = Parametros.objects.first().email_sme if Parametros.objects.first() else ''
    for proponente in proponentes_anexos_obrigatorios_sme.all():
        enviar_email_html(
            f'[Uniformes] Documento(s) próximo(s) do vencimento para o protocolo {proponente.protocolo}',
            'email_documentos_proximos_vencimento_nucleo',
            {"proponente": f'{proponente.razao_social} - {proponente.cnpj}'},
            email_sme
        )
