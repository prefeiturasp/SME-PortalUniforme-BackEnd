from mypy_django_plugin.transformers import querysets
from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
import math

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
        latitude = self.request.query_params.get('latitude', None)
        longitude = self.request.query_params.get('longitude', None)
        if latitude and longitude:
            latitude = float(latitude)
            longitude = float(longitude)
            print('lat = {} | lon = {}.'.format(repr(latitude), repr(longitude)))
            # return queryset.raw(f'SELECT *, (111.045 * acos(cos(radians(latitude)) * cos(radians(lat)) * cos(radians(longitude) - radians(lng)) + sin(radians(latitude)) * sin(radians(lat)))) AS distance FROM public.proponentes_loja HAVING distance <= 5')
            # return queryset.raw(f'SELECT *, (6371 * DEGREES(acos(cos(radians({lat}))'
            #              f'* cos(radians(CAST(latitude AS DECIMAL)))'
            #              f'* cos(radians(CAST(longitude AS DECIMAL)) - radians({lon}))'
            #              f'+ sin(radians({lat}))'
            #              f'* sin(radians(CAST(latitude AS DECIMAL))))) as distance FROM public.proponentes.loja HAVING distance <= 1')

            # Haversine formula = https://en.wikipedia.org/wiki/Haversine_formula
            R = 111.045  # earth radius
            bearing = 1.57  # 90 degrees bearing converted to radians.
            distance = 10  # distance in km

            lat1 = math.radians(latitude)  # lat in radians
            long1 = math.radians(longitude)  # long in radians

            lat2 = math.asin(math.sin(lat1) * math.cos(distance / R) +
                             math.cos(lat1) * math.sin(distance / R) * math.cos(bearing))

            long2 = long1 + math.atan2(math.sin(bearing) * math.sin(distance / R) * math.cos(lat1),
                                       math.cos(distance / R) - math.sin(lat1) * math.sin(lat2))

            lat2 = math.degrees(lat2)
            long2 = math.degrees(long2)

            queryset = queryset.filter(latitude__lte=str(lat2))\
                .filter(longitude__lte=str(long2))
            print(queryset)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return LojaLookUpSerializer
        else:
            return LojaSerializer
