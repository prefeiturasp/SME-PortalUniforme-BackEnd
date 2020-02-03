from drf_base64.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ...models import Anexo


class AnexoSerializer(ModelSerializer):
    class Meta:
        model = Anexo
        fields = '__all__'


class AnexoCreateSerializer(serializers.ModelSerializer):

    def validate_anexo(self, anexo):
        file_size = anexo.size

        if file_size > 10485760:
            raise ValidationError("O tamanho máximo de um arquivo é 10MB")
        else:
            return anexo

    class Meta:
        model = Anexo
        exclude = ('id', 'proponente')
