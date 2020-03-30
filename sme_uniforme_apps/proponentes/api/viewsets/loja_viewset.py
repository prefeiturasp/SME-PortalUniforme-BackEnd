from django.db.models.expressions import RawSQL
from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from ..serializers.loja_serializer import LojaUpdateFachadaSerializer
from ..serializers.proponente_serializer import LojaCredenciadaSerializer
from ...models.loja import Loja
from ...models.proponente import Proponente
from ...services import haversine


class LojaUpdateFachadaViewSet(mixins.UpdateModelMixin, GenericViewSet):
    lookup_field = "uuid"
    queryset = Loja.objects.all()
    serializer_class = LojaUpdateFachadaSerializer
    permission_classes = [AllowAny]


class LojaViewSet(mixins.ListModelMixin, GenericViewSet):
    lookup_field = "uuid"
    queryset = Loja.objects.all()
    serializer_class = LojaCredenciadaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Loja.objects.filter(proponente__status=Proponente.STATUS_CREDENCIADO)
        latitude = self.request.query_params.get('latitude', None)
        longitude = self.request.query_params.get('longitude', None)
        if latitude and longitude:
            lat = float(latitude)
            lon = float(longitude)
            queryset = queryset.filter(id__in=RawSQL(haversine(lat, lon), params=''))
            # queryset = queryset.raw(haversine(lat, lon))

            for loja in queryset:
                loja.distancia = loja.get_distancia(lat, lon)

            return queryset
