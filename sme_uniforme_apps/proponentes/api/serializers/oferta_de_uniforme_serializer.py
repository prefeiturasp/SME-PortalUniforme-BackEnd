from rest_framework import serializers

from ...models import OfertaDeUniforme
from ....core.models.uniforme import Uniforme


class OfertaDeUniformeSerializer(serializers.ModelSerializer):
    uniforme_categoria = serializers.SerializerMethodField()
    uniforme_quantidade = serializers.SerializerMethodField()
    nome = serializers.SerializerMethodField()

    def get_uniforme_categoria(self, obj):
        return obj.uniforme.categoria

    def get_uniforme_quantidade(self, obj):
        return obj.uniforme.quantidade

    def get_nome(self, obj):
        return obj.uniforme.nome

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


class OfertaDeUniformeLookupSerializer(serializers.ModelSerializer):
    uniforme_categoria = serializers.SerializerMethodField()
    uniforme_categoria_display = serializers.SerializerMethodField()
    item = serializers.SlugRelatedField(
        slug_field='nome',
        required=False,
        queryset=Uniforme.objects.all(),
        source='uniforme'
    )

    def get_uniforme_categoria(self, obj):
        return obj.uniforme.categoria

    def get_uniforme_categoria_display(self, obj):
        return obj.uniforme.get_categoria_display()

    class Meta:
        model = OfertaDeUniforme
        fields = ('uniforme_categoria_display', 'uniforme_categoria', 'item', 'preco')
