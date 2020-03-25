from rest_framework import serializers

from ...models import Loja


class LojaSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    def get_email(self, obj):
        return obj.proponente.email

    class Meta:
        model = Loja
        fields = '__all__'


class LojaCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loja
        exclude = ('id', 'proponente')


class LojaUpdateFachadaSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)
    nome_fantasia = serializers.CharField(read_only=True)

    class Meta:
        model = Loja
        fields = ('uuid', 'nome_fantasia', 'foto_fachada',)
