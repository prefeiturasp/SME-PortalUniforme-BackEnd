import logging

from django.http import Http404
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ...models import Parametros

log = logging.getLogger(__name__)


class InstrucaoNormativaViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def get_object(self):
        """Busca o objeto do modelo Parametros

        Raises:
            Http404: Quando objeto não encontrado

        Returns:
            Parametros (Parametros): Instância do objeto parâmetros.
        """
        try:
            return Parametros.objects.first()
        except Parametros.DoesNotExist:
            raise Http404

    def list(self, request, *args, **kwargs):
        """Busca o arquivo do edital e suas informações

        Raises:
            Http404: Quando arquivo não encontrado

        Returns:
            edital_url (str): url do edital.
        """
        parametros = self.get_object()
        instrucao_normativa_url = parametros.instrucao_normativa.url
        log.info(f"Url da instrução normativa: {instrucao_normativa_url}")
        return Response(instrucao_normativa_url)
