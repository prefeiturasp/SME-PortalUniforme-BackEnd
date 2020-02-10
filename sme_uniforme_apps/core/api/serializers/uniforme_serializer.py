from rest_framework import serializers

from ...models import Uniforme


class UniformeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Uniforme
        fields = ('id', 'nome', 'categoria', 'unidade', 'quantidade')


class UniformeLookUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = Uniforme
        fields = ('id', 'nome')
