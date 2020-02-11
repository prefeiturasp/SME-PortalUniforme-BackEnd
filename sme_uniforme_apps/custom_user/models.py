from django.db import models
from django_use_email_as_username.models import BaseUser, BaseUserManager


class User(BaseUser):
    objects = BaseUserManager()
    validado = models.BooleanField('Validado', default=False,
                                   help_text="Identificar se o cadastro de usuário já foi validado")

    @classmethod
    def cria_usuario(cls, email, nome, senha):
        novo_usuario = cls.objects.create(email=email, first_name=nome, )
        novo_usuario.set_password(senha)
        novo_usuario.save()

        # TODO Reativar envio de e-mail de acesso quando estiver concluida a funcionanlidade de login do proponente
        # enviar_email_info_acesso.delay(email=email, nome=nome, senha=senha)
