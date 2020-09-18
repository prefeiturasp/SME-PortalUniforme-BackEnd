import datetime

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django.contrib.auth import get_user_model

from ..serializers.usuario_serializer import UsuarioSerializer

User = get_user_model()


class UsuarioViewset(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UsuarioSerializer
    queryset = User.objects.all()
    lookup_field = 'username'

    @action(detail=False, methods=["GET"], permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UsuarioSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=False, methods=['POST'], url_path='atualizar-senha/(?P<usuario_id>.*)/(?P<token_reset>.*)')  # noqa
    def atualizar_senha(self, request, usuario_id=None, token_reset=None):
        # TODO: melhorar este método
        senha1 = request.data.get('senha1')
        senha2 = request.data.get('senha2')
        if senha1 != senha2:
            return Response({'detail': 'Senhas divergem'}, status.HTTP_400_BAD_REQUEST)
        try:
            usuario = User.objects.get(id=usuario_id)
        except ObjectDoesNotExist:
            return Response({'detail': 'Não existe usuário com este e-mail ou RF'},
                            status=status.HTTP_400_BAD_REQUEST)
        token_generator = PasswordResetTokenGenerator()
        if token_generator.check_token(usuario, token_reset):
            usuario.set_password(senha1)
            usuario.last_login = datetime.datetime.now()
            usuario.save()
            return Response({'sucesso': 'senha atualizada com sucesso'}, status.HTTP_200_OK)
        else:
            return Response({'detail': 'Token inválido'}, status.HTTP_400_BAD_REQUEST)
