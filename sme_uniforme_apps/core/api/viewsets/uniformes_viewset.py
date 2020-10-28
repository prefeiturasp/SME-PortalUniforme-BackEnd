from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ...models import Uniforme
from ..serializers.uniforme_serializer import (UniformeLookUpSerializer,
                                               UniformeSerializer)


class UniformesViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'id'
    queryset = Uniforme.objects.all()
    serializer_class = UniformeSerializer
    permission_classes = [AllowAny]
    filter_backends = (SearchFilter, OrderingFilter)
    ordering_fields = ('nome',)
    search_fields = ('uuid', 'id', 'nome')

    def get_queryset(self):
        return self.queryset

    def get_serializer_class(self):
        return UniformeSerializer

    @action(detail=False)
    def lookup(self, _):
        return Response(UniformeLookUpSerializer(self.queryset.order_by('nome'), many=True).data)

    @action(detail=False)
    def categorias(self, _):
        return Response(Uniforme.categorias_to_json())

    @action(detail=False, url_path='lookup-categorias')
    def lookup_categorias(self, _):
        return Response(Uniforme.categorias_lookup_to_json())
