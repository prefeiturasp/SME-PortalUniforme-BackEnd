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
        latitude = self.request.query_params.get('latitude', None)
        longitude = self.request.query_params.get('longitude', None)
        if latitude and longitude:
            lat = float(latitude)
            lon = float(longitude)
            query = f"""SELECT *
            FROM ( SELECT *,
                        111.045 * DEGREES(ACOS(COS(RADIANS({lat}))
                                                   * COS(RADIANS(latitude)) * COS(RADIANS(longitude) - RADIANS({lon}))
                                                   + SIN(RADIANS({lat})) * SIN(RADIANS(latitude)))) AS distance_in_km
                 FROM proponentes_loja loja
                 INNER JOIN proponentes_proponente proponente on loja.proponente_id = proponente.id
                 WHERE proponente.status = 'CREDENCIADO'
                 ORDER BY distance_in_km) as distancias
            """

            return queryset.raw(query)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return LojaLookUpSerializer
        else:
            return LojaSerializer
