from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ...api.serializers.anexo_serializer import AnexoSerializer
from ...api.serializers.loja_serializer import LojaSerializer, LojaCreateSerializer
from ...api.serializers.oferta_de_uniforme_serializer import (OfertaDeUniformeSerializer,
                                                              OfertaDeUniformeCreateSerializer)
from ...models import Proponente, Anexo, TipoDocumento


class ProponenteSerializer(serializers.ModelSerializer):
    ofertas_de_uniformes = OfertaDeUniformeSerializer(many=True)
    lojas = LojaSerializer(many=True)
    arquivos_anexos = serializers.ListField(
        child=AnexoSerializer()
    )

    class Meta:
        model = Proponente
        fields = '__all__'


class ProponenteCreateSerializer(serializers.ModelSerializer):
    arquivos_anexos = serializers.ListField(
        child=AnexoSerializer()
    )
    ofertas_de_uniformes = OfertaDeUniformeCreateSerializer(many=True)
    lojas = LojaCreateSerializer(many=True)

    @staticmethod
    def falta_documento_obrigatorio(arquivos_anexos):
        tipos_documentos_obrigatorios = TipoDocumento.tipos_obrigatorios()
        for anexo in arquivos_anexos:
            tipos_documentos_obrigatorios.discard(anexo.get("tipo_documento").id)

        if tipos_documentos_obrigatorios:
            return TipoDocumento.objects.get(id=next(iter(tipos_documentos_obrigatorios)))
        else:
            return None

    def create(self, validated_data):

        arquivos_anexos = validated_data.pop('arquivos_anexos', [])
        ofertas_de_uniformes = validated_data.pop('ofertas_de_uniformes')
        lojas = validated_data.pop('lojas')

        proponente = Proponente.objects.create(**validated_data)

        ofertas_lista = []
        for oferta in ofertas_de_uniformes:
            oferta_object = OfertaDeUniformeCreateSerializer().create(oferta)
            ofertas_lista.append(oferta_object)
        proponente.ofertas_de_uniformes.set(ofertas_lista)

        lojas_lista = []
        for loja in lojas:
            loja_object = LojaCreateSerializer().create(loja)
            lojas_lista.append(loja_object)
        proponente.lojas.set(lojas_lista)

        documento_faltante = self.falta_documento_obrigatorio(arquivos_anexos)
        if documento_faltante:
            raise ValidationError(f'Não foi enviado o documento {documento_faltante}.')

        tamanho_total_dos_arquivos = 0
        for anexo in arquivos_anexos:
            file_size = anexo.get('arquivo').size
            tamanho_total_dos_arquivos += file_size
            if tamanho_total_dos_arquivos > 10485760:
                raise ValidationError("O tamanho total máximo dos arquivos é 10MB")

            Anexo.objects.create(
                proponente=proponente,
                arquivo=anexo.get("arquivo"),
                tipo_documento=anexo.get("tipo_documento")
            )

        return proponente

    class Meta:
        model = Proponente
        exclude = ('id',)


class ProponenteLookUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = Proponente
        fields = ('uuid', 'razao_social')
