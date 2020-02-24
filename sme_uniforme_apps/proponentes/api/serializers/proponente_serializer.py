import logging

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ....core.models import LimiteCategoria, Uniforme
from ...api.serializers.anexo_serializer import AnexoSerializer
from ...api.serializers.loja_serializer import (LojaCreateSerializer,
                                                LojaSerializer)
from ...api.serializers.oferta_de_uniforme_serializer import (
    OfertaDeUniformeCreateSerializer, OfertaDeUniformeSerializer)
from ...models import Proponente

log = logging.getLogger(__name__)


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

    ofertas_de_uniformes = OfertaDeUniformeCreateSerializer(many=True)
    lojas = LojaCreateSerializer(many=True)

    @staticmethod
    def categoria_acima_limite(ofertas_de_uniformes):
        limites_por_categoria = LimiteCategoria.limites_por_categoria_as_dict()

        if not limites_por_categoria:
            return None

        # Inicializa totais por categoria
        total_por_categoria = {categoria: 0 for categoria in limites_por_categoria.keys()}

        # Sumariza ofertas por categoria
        for oferta in ofertas_de_uniformes:
            total_por_categoria[oferta['uniforme'].categoria] += (oferta['preco'] * oferta['uniforme'].quantidade)

        # Encontra e retorna a primeira categoria que ficou acima do limite ou None se nenhuma ficou acima
        categoria_acima_do_limite = None
        for categoria in total_por_categoria.keys():
            if total_por_categoria[categoria] > limites_por_categoria[categoria]:
                categoria_acima_do_limite = {'categoria': categoria, 'limite': limites_por_categoria[categoria]}
                break

        return categoria_acima_do_limite

    @staticmethod
    def categoria_faltando_itens(ofertas_de_uniformes):
        qtd_itens_por_categoria = Uniforme.qtd_itens_por_categoria_as_dict()

        categorias_fornecidas = set()

        for oferta in ofertas_de_uniformes:
            categorias_fornecidas.add(oferta['uniforme'].categoria)
            qtd_itens_por_categoria[oferta['uniforme'].categoria] -= 1

        categoria_faltando_itens = None
        for categoria, quantidade in qtd_itens_por_categoria.items():
            # Não é obrigatorio fornecer todas as categorias, mas todos os itens das categorias fornecidas
            if quantidade > 0 and categoria in categorias_fornecidas:
                categoria_faltando_itens = categoria
                break
        return categoria_faltando_itens

    def create(self, validated_data):
        ofertas_de_uniformes = validated_data.pop('ofertas_de_uniformes')
        lojas = validated_data.pop('lojas')

        if not ofertas_de_uniformes:
            msgError = "Pelo menos um oferta deve ser enviada!"
            log.debug(msgError)
            raise ValidationError(msgError)

        if not lojas:
            msgError = "Pelo menos uma loja precisa ser enviada!"
            log.debug(msgError)
            raise ValidationError(msgError)

        categoria_acima_limite = self.categoria_acima_limite(ofertas_de_uniformes)
        log.debug("Categoria acima do limite: {}".format(categoria_acima_limite))
        if categoria_acima_limite:
            log.debug("Categoria acima do limite!")
            raise ValidationError(
                f'Valor total da categoria {Uniforme.CATEGORIA_NOMES[categoria_acima_limite["categoria"]]} '
                f'está acima do limite de R$ {categoria_acima_limite["limite"]:.2f}.')

        categoria_faltando_itens = self.categoria_faltando_itens(ofertas_de_uniformes)
        log.debug("Categoria faltando itens: {}".format(categoria_acima_limite))
        if categoria_faltando_itens:
            log.debug("Categoria com itens faltando!")
            raise ValidationError(
                f'Não foram fornecidos todos os itens da categoria {Uniforme.CATEGORIA_NOMES[categoria_faltando_itens]}'
                f'. Não é permitido o fornecimento parcial de uma categoria.')

        proponente = Proponente.objects.create(**validated_data)
        log.debug("Criando proponente com uuid: {}".format(proponente.uuid))

        ofertas_lista = []
        for oferta in ofertas_de_uniformes:
            oferta_object = OfertaDeUniformeCreateSerializer().create(oferta)
            ofertas_lista.append(oferta_object)
        proponente.ofertas_de_uniformes.set(ofertas_lista)
        log.debug("Proponente {}, Ofertas de uniformes: {}".format(proponente.uuid, ofertas_lista))

        lojas_lista = []
        for loja in lojas:
            loja_object = LojaCreateSerializer().create(loja)
            lojas_lista.append(loja_object)
        proponente.lojas.set(lojas_lista)
        log.debug("Proponente {}, lojas: {}".format(proponente.uuid, ofertas_lista))
        log.debug("Criação de proponente finalizada!")

        return proponente

    class Meta:
        model = Proponente
        exclude = ('id',)


class ProponenteLookUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proponente
        fields = ('uuid', 'razao_social')
