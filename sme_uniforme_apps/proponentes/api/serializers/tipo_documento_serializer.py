from rest_framework import serializers

from ...models import TipoDocumento


class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = ('id', 'nome', 'obrigatorio', 'tem_data_validade', 'obrigatorio_sme')
