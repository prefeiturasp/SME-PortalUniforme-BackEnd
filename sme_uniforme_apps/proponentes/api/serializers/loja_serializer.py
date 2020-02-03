from rest_framework import serializers

from ...models import Loja


class LojaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loja
        fields = '__all__'


class LojaCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loja
        exclude = ('id', 'proponente')
