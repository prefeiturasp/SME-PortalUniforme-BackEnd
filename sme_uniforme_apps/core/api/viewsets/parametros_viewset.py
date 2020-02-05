import os
from django.conf import settings
from django.http import HttpResponse, Http404

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from ...models import Parametros
from ...services import busca_edital


class ParametrosViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def get_object(self):
        try:
            return Parametros.objects.first()
        except Parametros.DoesNotExist:
            raise Http404

    def list(self, request, *args, **kwargs):
        parametros = self.get_object()

        try:
            edital = busca_edital(parametros.edital.name)
            response = HttpResponse(content=edital['content'], content_type=edital['content_type'])
            response['Content-Disposition'] = edital['Content-Disposition']
        except FileNotFoundError:
            raise Http404

        return response

