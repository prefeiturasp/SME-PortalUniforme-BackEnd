import logging

from drf_base64.serializers import ModelSerializer
from rest_framework import serializers

from ...models import Anexo, Proponente

log = logging.getLogger(__name__)


class AnexoSerializer(ModelSerializer):
    class Meta:
        model = Anexo
        fields = '__all__'


class AnexoCreateSerializer(serializers.ModelSerializer):
    proponente = serializers.UUIDField()

    def create(self, validated_data):
        log.debug("Criando anexo!")
        proponent_uuid = validated_data.pop('proponente')
        proponente = Proponente.objects.get(uuid=proponent_uuid)
        anexo = Anexo.objects.create(
            proponente=proponente,
            **validated_data)
        log.debug("Anexo uuid: {} criado!".format(anexo.uuid))
        return anexo.as_dict()

    class Meta:
        model = Anexo
        exclude = ('id',)
