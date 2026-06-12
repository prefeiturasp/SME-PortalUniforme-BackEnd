import logging

from django.core.exceptions import ObjectDoesNotExist
from drf_base64.serializers import ModelSerializer
from rest_framework import serializers

from .tipo_documento_serializer import TipoDocumentoSerializer
from ...models import Anexo, Proponente
from ...upload_validation import PDF_EXTENSIONS, validate_upload_extension

log = logging.getLogger(__name__)


class AnexoSerializer(ModelSerializer):
    tipo_documento = TipoDocumentoSerializer()

    class Meta:
        model = Anexo
        fields = (
            "id",
            "criado_em",
            "alterado_em",
            "uuid",
            "proponente",
            "arquivo",
            "data_validade",
            "status",
            "justificativa",
            "tipo_documento",
        )


class AnexoCreateSerializer(serializers.ModelSerializer):
    proponente = serializers.UUIDField()

    def validate_arquivo(self, value):
        try:
            validate_upload_extension(value, PDF_EXTENSIONS, 'Envie o documento do proponente em PDF.')
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))

        return value

    def create(self, validated_data):
        log.info("Criando anexo!")
        proponent_uuid = validated_data.pop('proponente')
        proponente = Proponente.objects.get(uuid=proponent_uuid)
        try:
            anexo = Anexo.objects.get(
                tipo_documento=validated_data.get('tipo_documento'),
                proponente=proponente
            )
            anexo.arquivo = validated_data.get('arquivo')
            anexo.data_validade = validated_data.get('data_validade')
            anexo.status = Anexo.STATUS_PENDENTE
            anexo.save()
        except ObjectDoesNotExist:
            anexo = Anexo.objects.create(
                proponente=proponente,
                **validated_data)
            log.info("Anexo uuid: {} criado!".format(anexo.uuid))
        return anexo.as_dict()

    class Meta:
        model = Anexo
        exclude = (
            "id",
            "status_ia",
            "justificativa_ia",
            "ultima_alteracao_admin_por",
            "ultima_alteracao_admin_em",
        )
        extra_kwargs = {
            'arquivo': {
                'label': 'Documento do proponente',
                'help_text': 'Envie apenas arquivos PDF.',
            }
        }
