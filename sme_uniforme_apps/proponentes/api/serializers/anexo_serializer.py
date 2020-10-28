import logging

from django.core.exceptions import ObjectDoesNotExist
from drf_base64.serializers import ModelSerializer
from rest_framework import serializers

from .tipo_documento_serializer import TipoDocumentoSerializer
from ...models import Anexo, Proponente

log = logging.getLogger(__name__)


class AnexoSerializer(ModelSerializer):
    tipo_documento = TipoDocumentoSerializer()

    class Meta:
        model = Anexo
        fields = '__all__'


class AnexoCreateSerializer(serializers.ModelSerializer):
    proponente = serializers.UUIDField()

    def create(self, validated_data):
        log.info("Criando anexo!")
        proponent_uuid = validated_data.pop('proponente')
        proponente = Proponente.objects.get(uuid=proponent_uuid)
        try:
            anexo = Anexo.objects.get(
                tipo_documento=validated_data.get('tipo_documento'),
                proponente=proponente
            )
            anexo.arquivo = validated_data.get('arquivo')
            anexo.data_validade = validated_data.get('data_validade')
            anexo.status = Anexo.STATUS_PENDENTE
            anexo.save()
        except ObjectDoesNotExist:
            anexo = Anexo.objects.create(
                proponente=proponente,
                **validated_data)
            log.info("Anexo uuid: {} criado!".format(anexo.uuid))
        return anexo.as_dict()

    class Meta:
        model = Anexo
        exclude = ('id',)
