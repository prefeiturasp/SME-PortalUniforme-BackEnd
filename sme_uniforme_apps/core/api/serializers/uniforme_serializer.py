from rest_framework import serializers

from ...models import Uniforme


class UniformeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Uniforme
        fields = ('id', 'nome', 'categoria', 'unidade', 'quantidade')


class UniformeLookUpSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField('get_nome')

    def get_nome(self, obj):
        return obj.__str__()

    class Meta:
        model = Uniforme
        fields = ('id', 'nome', 'categoria')
