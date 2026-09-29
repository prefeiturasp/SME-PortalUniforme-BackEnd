import environ

from rest_framework import serializers
from ...models import Loja
from ...upload_validation import (
    IMAGE_EXTENSIONS,
    PDF_EXTENSIONS,
    validate_upload_extension,
)

env = environ.Env()
SERVER_NAME = f'{env("SERVER_NAME")}'

class LojaSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    comprovante_endereco = serializers.SerializerMethodField('get_comprovante_endereco')

    def get_comprovante_endereco(self, obj):
        if bool(obj.comprovante_endereco):
            return '%s%s' % (SERVER_NAME, obj.comprovante_endereco.url)
        else:
            return None

    def get_email(self, obj):
        return obj.proponente.email

    class Meta:
        model = Loja
        fields = '__all__'


class LojaCreateSerializer(serializers.ModelSerializer):

    def validate_foto_fachada(self, value):
        if not value:
            return value

        try:
            validate_upload_extension(value, IMAGE_EXTENSIONS, 'Envie a foto da fachada em JPG, JPEG ou PNG.')
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))

        return value

    def validate_comprovante_endereco(self, value):
        if not value:
            return value

        try:
            validate_upload_extension(
                value,
                PDF_EXTENSIONS,
                'Envie o comprovante de endereço do ponto de venda em PDF.',
            )
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))

        return value

    class Meta:
        model = Loja
        exclude = ('id', 'proponente')
        extra_kwargs = {
            'comprovante_endereco': {
                'label': 'Comprovante de endereço do ponto de venda',
                'help_text': 'Campo opcional. Se enviado, deve estar em PDF.',
                'required': False,
                'allow_null': True,
            },
            'foto_fachada': {
                'label': 'Foto da fachada da loja',
                'help_text': 'Envie apenas arquivos JPG, JPEG ou PNG.',
                'required': False,
                'allow_null': True,
            },
        }


class LojaUpdateFachadaSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)
    nome_fantasia = serializers.CharField(read_only=True)

    def validate_foto_fachada(self, value):
        if not value:
            return value

        try:
            validate_upload_extension(value, IMAGE_EXTENSIONS, 'Envie a foto da fachada em JPG, JPEG ou PNG.')
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))

        return value

    class Meta:
        model = Loja
        fields = ('uuid', 'nome_fantasia', 'foto_fachada',)
        extra_kwargs = {
            'foto_fachada': {
                'label': 'Foto da fachada da loja',
                'help_text': 'Envie apenas arquivos JPG, JPEG ou PNG.',
            }
        }
