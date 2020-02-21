from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny

from ..serializers.tipo_documento_serializer import TipoDocumentoSerializer
from ...models import TipoDocumento


class TiposDocumentoViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'id'
    queryset = TipoDocumento.objects.filter(visivel=True).all()
    serializer_class = TipoDocumentoSerializer
    permission_classes = [AllowAny]
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    ordering_fields = ('nome',)
    search_fields = ('uuid', 'id', 'nome')
    filter_fields = ('obrigatorio',)

    def get_queryset(self):
        return self.queryset

    def get_serializer_class(self):
        return TipoDocumentoSerializer
