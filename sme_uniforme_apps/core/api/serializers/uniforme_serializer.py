from rest_framework import serializers

from ...models import Uniforme


class UniformeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Uniforme
        fields = '__all__'


class UniformeLookUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = Uniforme
        fields = ('id', 'nome')
