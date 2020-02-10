from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..serializers.uniforme_serializer import UniformeSerializer, UniformeLookUpSerializer
from ...models import Uniforme


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
