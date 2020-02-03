from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from ..serializers.meio_de_recebimento_serializer import MeioDeRecebimentoSerializer, MeioDeRecebimentoLookUpSerializer
from ...models import MeioDeRecebimento


class MeiosDeRecebimentoViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'id'
    queryset = MeioDeRecebimento.objects.all()
    serializer_class = MeioDeRecebimentoSerializer
    permission_classes = [AllowAny]
    filter_backends = (SearchFilter, OrderingFilter)
    ordering_fields = ('nome',)
    search_fields = ('uuid', 'id', 'nome')

    def get_queryset(self):
        return self.queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MeioDeRecebimentoSerializer
        elif self.action == 'list':
            return MeioDeRecebimentoLookUpSerializer
        else:
            return MeioDeRecebimentoSerializer

    @action(detail=False)
    def lookup(self, _):
        return Response(MeioDeRecebimentoLookUpSerializer(self.queryset.order_by('nome'), many=True).data)
