from django_use_email_as_username.models import BaseUser, BaseUserManager
from django.db import models


class User(BaseUser):
    objects = BaseUserManager()
    validado = models.BooleanField('Validado', default=False,
                                   help_text="Identificar se o cadastro de usuário já foi validado")
