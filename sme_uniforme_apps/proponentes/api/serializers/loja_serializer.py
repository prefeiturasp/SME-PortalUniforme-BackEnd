import environ

from rest_framework import serializers
from config.settings.base import MEDIA_URL
from ...models import Loja


env = environ.Env()
SERVER_NAME = f'{env("SERVER_NAME")}'

class LojaSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    comprovante_endereco = serializers.SerializerMethodField('get_comprovante_endereco')

    def get_comprovante_endereco(self, obj):
        return '%s%s' % (SERVER_NAME, obj.comprovante_endereco.url)

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
