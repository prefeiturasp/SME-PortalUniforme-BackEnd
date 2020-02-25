from decouple import config

from config import celery_app

from ..core.helpers.enviar_email import enviar_email_html


@celery_app.task()
def enviar_email_info_acesso(email, nome, senha):
    link = 'http://{}/#/login/'.format(config('SERVER_NAME'))
    return enviar_email_html(
        'Suas informações de acesso ao Portal do Uniforme',
        'email_info_acesso',
        {'url': link,
         'nome': nome,
         'login': email,
         'senha': senha
         },
        email
    )
