from rest_framework import serializers

from ...models import OfertaDeUniforme
from ....core.models.uniforme import Uniforme


class OfertaDeUniformeSerializer(serializers.ModelSerializer):
    uniforme_categoria = serializers.SerializerMethodField()
    uniforme_quantidade = serializers.SerializerMethodField()
    item = serializers.SlugRelatedField(
        slug_field='nome',
        required=False,
        queryset=Uniforme.objects.all(),
        source='uniforme'
    )

    def get_uniforme_categoria(self, obj):
        return obj.uniforme.categoria

    def get_uniforme_quantidade(self, obj):
        return obj.uniforme.quantidade

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
