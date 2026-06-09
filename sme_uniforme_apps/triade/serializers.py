from rest_framework import serializers


class TriadeCallbackDocumentoSchemaSerializer(serializers.Serializer):
    external_document_id = serializers.CharField()
    document_id = serializers.UUIDField(required=False, allow_null=True)
    decisao = serializers.CharField(required=False, allow_blank=True)
    justificativa = serializers.CharField(required=False, allow_blank=True)
    external_document_type = serializers.CharField(required=False, allow_blank=True)
    document_type = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    processed_at = serializers.DateTimeField(required=False)
    error = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    metadata = serializers.DictField(required=False)


class TriadeCallbackPayloadSchemaSerializer(serializers.Serializer):
    external_reference_id = serializers.CharField(required=False, allow_blank=True)
    external_batch_id = serializers.CharField(required=False, allow_blank=True)
    submission_id = serializers.UUIDField(required=False, allow_null=True)
    batch_id = serializers.UUIDField(required=False, allow_null=True)
    analysis_desk_id = serializers.CharField(required=False, allow_blank=True)
    source_system = serializers.CharField(required=False, allow_blank=True)
    schema_version = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.DictField(required=False)
    decisao_parecer = serializers.CharField(required=False, allow_blank=True)
    parecer_texto = serializers.CharField(required=False, allow_blank=True)
    confirmado_em = serializers.DateTimeField(required=False)
    confirmado_por = serializers.CharField(required=False, allow_blank=True)
    documents = TriadeCallbackDocumentoSchemaSerializer(many=True, required=False)
