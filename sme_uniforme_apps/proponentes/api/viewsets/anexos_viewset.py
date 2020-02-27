from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from ...models import Anexo
from ..serializers.anexo_serializer import (AnexoCreateSerializer,
                                            AnexoSerializer)


class AnexosViewset(mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = Anexo.objects.all()
    serializer_class = AnexoSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return AnexoCreateSerializer
        return AnexoSerializer
