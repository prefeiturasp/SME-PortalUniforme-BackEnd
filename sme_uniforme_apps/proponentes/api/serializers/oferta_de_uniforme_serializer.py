from rest_framework import serializers

from ...models import OfertaDeUniforme
from ....core.models.uniforme import Uniforme


class OfertaDeUniformeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfertaDeUniforme
        fields = '__all__'


class OfertaDeUniformeCreateSerializer(serializers.ModelSerializer):
    uniforme = serializers.SlugRelatedField(
        slug_field='id',
        required=False,
        queryset=Uniforme.objects.all()
    )

    class Meta:
        model = OfertaDeUniforme
        exclude = ('id', 'proponente')
