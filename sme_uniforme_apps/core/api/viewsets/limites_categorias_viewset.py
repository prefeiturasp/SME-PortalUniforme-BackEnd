from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from ..serializers.limite_categoria_serializer import LimiteCategoriaSerializer
from ...models import LimiteCategoria


class LimitesCategoriasViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'id'
    queryset = LimiteCategoria.objects.all()
    serializer_class = LimiteCategoriaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return self.queryset

    def get_serializer_class(self):
        return LimiteCategoriaSerializer
