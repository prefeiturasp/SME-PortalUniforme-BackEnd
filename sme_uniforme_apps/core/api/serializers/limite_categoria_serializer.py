from rest_framework import serializers

from ...models import LimiteCategoria


class LimiteCategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LimiteCategoria
        fields = ('categoria_uniforme', 'preco_maximo')
