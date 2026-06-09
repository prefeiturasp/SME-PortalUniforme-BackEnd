import logging

import coreapi
import coreschema
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema

from .callbacks import TriadeCallbackService
from .exceptions import (
    TriadeConfigError,
    TriadePermanentError,
    TriadeRequestError,
    TriadeSignatureError,
)
from .persistence import queryset_update_with_alterado_em, save_with_alterado_em
from .serializers import TriadeCallbackPayloadSchemaSerializer

log = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class TriadeCallbackWebhookView(GenericAPIView):
    """Recebe o callback assinado do TRIADE, registra a entrega e enfileira o processamento em background."""

    http_method_names = ["post"]
    authentication_classes = ()
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser,)
    serializer_class = TriadeCallbackPayloadSchemaSerializer
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(
                name="X-TRIADE-Signature",
                required=True,
                location="header",
                schema=coreschema.String(
                    description="Assinatura HMAC do callback no formato sha256=<hex>."
                ),
            ),
            coreapi.Field(
                name="X-TRIADE-Delivery",
                required=True,
                location="header",
                schema=coreschema.String(
                    description="UUID unico da entrega para deduplicacao."
                ),
            ),
        ]
    )

    def post(self, request, *args, **kwargs):
        service = None
        http_request = request._request
        try:
            service = TriadeCallbackService()
            callback, created = service.register_callback(
                raw_body=http_request.body,
                signature_header=http_request.META.get("HTTP_X_TRIADE_SIGNATURE"),
                delivery_header=http_request.META.get("HTTP_X_TRIADE_DELIVERY"),
            )
        except TriadeSignatureError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)
        except TriadeRequestError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except TriadeConfigError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except TriadePermanentError as exc:
            return Response({"detail": str(exc)}, status=422)

        if not created and callback.status_processamento in (
            service.STATUS_ENFILEIRADO,
            service.STATUS_PROCESSANDO,
            service.STATUS_PROCESSADO,
            service.STATUS_DUPLICADO,
        ):
            return Response({"status": "duplicate"}, status=status.HTTP_200_OK)

        callback.status_processamento = service.STATUS_ENFILEIRADO
        callback.erro = None
        save_with_alterado_em(callback, ("status_processamento", "erro"))

        def enqueue_callback_processing():
            try:
                from .tasks import processar_callback_triade

                processar_callback_triade.delay(callback.id)
            except Exception:
                log.exception(
                    "Falha ao enfileirar processamento do callback TRIADE %s.",
                    callback.delivery_id,
                )
                queryset_update_with_alterado_em(
                    type(callback).objects.filter(pk=callback.pk),
                    status_processamento=service.STATUS_ERRO,
                    erro="Falha ao enfileirar processamento do callback TRIADE.",
                )

        transaction.on_commit(enqueue_callback_processing)
        return Response({"status": "accepted"}, status=status.HTTP_202_ACCEPTED)
