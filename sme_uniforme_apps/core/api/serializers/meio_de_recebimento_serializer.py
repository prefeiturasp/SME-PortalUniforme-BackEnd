from rest_framework import serializers

from ...models import MeioDeRecebimento


class MeioDeRecebimentoSerializer(serializers.ModelSerializer):

    class Meta:
        model = MeioDeRecebimento
        fields = '__all__'


class MeioDeRecebimentoLookUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = MeioDeRecebimento
        fields = ('id', 'nome')
