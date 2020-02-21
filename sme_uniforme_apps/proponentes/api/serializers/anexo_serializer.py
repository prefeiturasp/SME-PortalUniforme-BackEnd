from drf_base64.serializers import ModelSerializer
from rest_framework import serializers

from ...models import Anexo, Proponente


class AnexoSerializer(ModelSerializer):
    class Meta:
        model = Anexo
        fields = '__all__'


class AnexoCreateSerializer(serializers.ModelSerializer):
    proponente = serializers.UUIDField()

    def create(self, validated_data):
        proponent_uuid = validated_data.pop('proponente')
        proponente = Proponente.objects.get(uuid=proponent_uuid)
        anexo = Anexo.objects.create(
            proponente=proponente,
            **validated_data)
        return anexo.as_dict()

    class Meta:
        model = Anexo
        exclude = ('id',)
