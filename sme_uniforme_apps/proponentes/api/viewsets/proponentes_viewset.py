from django_filters import rest_framework as filters

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter


from ..serializers.proponente_serializer import ProponenteSerializer, ProponenteCreateSerializer, \
    ProponenteLookUpSerializer
from ...models import Proponente, ListaNegra


class ProponentesViewSet(viewsets.ModelViewSet):

    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = Proponente.objects.all()
    serializer_class = ProponenteSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('end_uf', )
    ordering_fields = ('razao_social',)
    search_fields = ('uuid', 'cnpj')

    def get_queryset(self):
        return self.queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProponenteSerializer
        elif self.action == 'list':
            return ProponenteSerializer
        else:
            return ProponenteCreateSerializer

    @action(detail=False)
    def lookup(self, _):
        return Response(ProponenteLookUpSerializer(self.queryset.order_by('razao_social'), many=True).data)

    @action(detail=False, url_path='verifica-cnpj')
    def verifica_cnpj(self, request):
        cnpj = request.query_params.get('cnpj')
        if cnpj:
            result = {
                        'result': 'OK',
                        'cnpj_valido': 'Sim' if Proponente.cnpj_valido(cnpj) else 'Não',
                        'cnpj_cadastrado': 'Sim' if Proponente.cnpj_ja_cadastrado(cnpj) else 'Não',
                        'cnpj_bloqueado': 'Sim' if ListaNegra.cnpj_bloqueado(cnpj) else 'Não'

                     }
        else:
            result = {
                        'result': 'Erro',
                        'mensagem': 'Informe o cnpj na url. Ex: /proponentes/?cnpj=53.894.798/0001-29'
                     }

        return Response(result)
