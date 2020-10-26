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
    daqui_a_5_dias = datetime.date.today() + datetime.timedelta(days=5)
    proponentes = Proponente.objects.filter(anexos__data_validade=daqui_a_5_dias)
    for proponente in proponentes.all():
        enviar_email_html(
            'Documento(s) próximo(s) do vencimento',
            'email_documentos_proximos_vencimento',
            None,
            proponente.email
        )
