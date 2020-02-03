from smtplib import SMTPServerDisconnected

import environ
from celery import shared_task

from ..core.helpers.enviar_email import enviar_email_html

env = environ.Env()


# https://docs.celeryproject.org/en/latest/userguide/tasks.html
@shared_task(
    autoretry_for=(SMTPServerDisconnected,),
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
)
def enviar_email_confirmacao_cadastro(email, contexto):
    print(f'Confirmação de cadastro (Protocolo:{contexto["protocolo"]}) enviada para {email}.')
    return enviar_email_html(
        'Recebemos o seu cadastro',
        'email_confirmacao_cadastro',
        contexto,
        email
    )
