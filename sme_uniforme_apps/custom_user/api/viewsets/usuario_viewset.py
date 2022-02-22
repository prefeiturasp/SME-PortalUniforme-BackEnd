import datetime
import logging
import environ

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django.contrib.auth import get_user_model
from sme_uniforme_apps.proponentes.models import Proponente
from sme_uniforme_apps.proponentes.tasks import enviar_email_recuperar_senha
from sme_uniforme_apps.utils.ofuscar_email import ofuscar_email

from ..serializers.usuario_serializer import UsuarioSerializer

log = logging.getLogger(__name__)
User = get_user_model()


class UsuarioViewset(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UsuarioSerializer
    queryset = User.objects.all()

    @action(detail=False, methods=["GET"], permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UsuarioSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=False, methods=['POST'], permission_classes=(AllowAny,), url_path='atualizar-senha/(?P<usuario_id>.*)/(?P<token_reset>.*)')  # noqa
    def atualizar_senha(self, request, usuario_id=None, token_reset=None):
        senha1 = request.data.get('senha1')
        senha2 = request.data.get('senha2')
        if senha1 != senha2:
            return Response({'detail': 'Senhas divergem'}, status.HTTP_400_BAD_REQUEST)
        try:
            usuario = User.objects.get(id=usuario_id)
        except ObjectDoesNotExist:
            return Response({'detail': 'Não existe usuário com este e-mail'},
                            status=status.HTTP_400_BAD_REQUEST)
        token_generator = PasswordResetTokenGenerator()
        if token_generator.check_token(usuario, token_reset):
            usuario.set_password(senha1)
            usuario.last_login = datetime.datetime.now()
            usuario.save()
            return Response({'sucesso': 'senha atualizada com sucesso'}, status.HTTP_200_OK)
        else:
            return Response({'detail': 'Token inválido'}, status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'], url_path='atualizar-senha-logado',
            permission_classes=(IsAuthenticated,))  # noqa
    def atualizar_senha_logado(self, request, pk=None):
        try:
            usuario = Proponente.objects.get(uuid=pk).usuario
            assert usuario.check_password(request.data.get('senha_atual')) is True, 'Senha atual divergente'
            senha1 = request.data.get('senha1')
            senha2 = request.data.get('senha2')
            assert senha1 == senha2, 'Senha e confirmar senha divergem'
            usuario.set_password(senha1)
            usuario.save()
            return Response({'detail': 'Senha atualizada com sucesso'}, status=status.HTTP_200_OK)
        except AssertionError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=(AllowAny,), url_path='recuperar-senha/(?P<email>.*)')
    def recuperar_senha(self, request, email=None):
        try:
            usuario = User.objects.get(email=email)
        except ObjectDoesNotExist:
            return Response({'detail': 'Não existe usuário com este e-mail'},
                            status=status.HTTP_400_BAD_REQUEST)
        log.info(f'Enviando recuperação de senha enviada para {usuario.email}.')
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(usuario)
        env = environ.Env()
        url = f'{env("SERVER_NAME")}/recuperar-senha?id={str(usuario.id)}&confirmationKey={token}'
        enviar_email_recuperar_senha.delay(
            usuario.email,
            {
                'url': url
            }
        )
        return Response({'email': f'{ofuscar_email(usuario.email)}'},
                        status=status.HTTP_200_OK)
