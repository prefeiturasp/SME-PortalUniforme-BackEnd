from django.db.models.expressions import RawSQL
from django.template.loader import render_to_string
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from sme_uniforme_apps.utils.html_to_pdf_response import html_to_pdf_response
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
        queryset = Loja.objects.filter(
            proponente__status=Proponente.STATUS_CREDENCIADO).exclude(
            latitude__isnull=True).exclude(
            longitude__isnull=True)
        latitude = self.request.query_params.get('latitude', None)
        longitude = self.request.query_params.get('longitude', None)
        if latitude and longitude:
            lat = float(latitude)
            lon = float(longitude)
            queryset = queryset.filter(id__in=RawSQL(haversine(lat, lon), params=''))
            # queryset = queryset.raw(haversine(lat, lon))

            for loja in queryset:
                loja.distancia = loja.get_distancia(lat, lon)
        else:
            for loja in queryset:
                loja.distancia = 0
        return queryset

    @action(detail=False, url_path='pdf-lojas-credenciadas', methods=['get'])
    def pdf_lojas_credenciadas(self, request):
        html_string = render_to_string(
            'lojas_credenciadas.html',
            {'lojas': self.get_queryset()}
        )
        return html_to_pdf_response(html_string, f'lojas_credenciadas.pdf')