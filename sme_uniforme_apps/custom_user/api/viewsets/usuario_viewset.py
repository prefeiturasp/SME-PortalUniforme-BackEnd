from rest_framework import viewsets
from django.contrib.auth import get_user_model

from ..serializers.usuario_serializer import UsuarioSerializer

User = get_user_model()


class UsuarioViewset(viewsets.ModelViewSet):
    serializer_class = UsuarioSerializer
    queryset = User.objects.all()
    lookup_field = 'uuid'
