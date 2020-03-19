from mypy_django_plugin.transformers import querysets
from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from ..serializers.loja_serializer import LojaUpdateFachadaSerializer, LojaSerializer, LojaLookUpSerializer
from ...models.loja import Loja
from ...models.proponente import Proponente


class LojaUpdateFachadaViewSet(mixins.UpdateModelMixin, GenericViewSet):
    lookup_field = "uuid"
    queryset = Loja.objects.all()
    serializer_class = LojaUpdateFachadaSerializer
    permission_classes = [AllowAny]


class LojaViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    lookup_field = "uuid"
    queryset = Loja.objects.all()
    serializer_class = LojaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Loja.objects.filter(proponente__status=Proponente.STATUS_CREDENCIADO)
        # vestuario = self.request.query_params.get('vestuario', None)
        # calcado = self.request.query_params.get('calcado', None)
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return LojaLookUpSerializer
        else:
            return LojaSerializer
