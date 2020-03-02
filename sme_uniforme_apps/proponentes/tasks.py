import logging

from smtplib import SMTPServerDisconnected

import environ
from celery import shared_task

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
