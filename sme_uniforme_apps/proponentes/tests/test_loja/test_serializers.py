import pytest

from ...api.serializers.loja_serializer import (LojaCreateSerializer, LojaSerializer, LojaUpdateFachadaSerializer)

pytestmark = pytest.mark.django_db


def test_loja_serializer(loja_fisica):

    loja_serializer = LojaSerializer(loja_fisica)

    assert loja_serializer.data is not None
    assert loja_serializer.data['uuid']
    assert loja_serializer.data['alterado_em']
    assert loja_serializer.data['criado_em']
    assert loja_serializer.data['id']
    assert loja_serializer.data['cep']
    assert loja_serializer.data['endereco']
    assert loja_serializer.data['bairro']
    assert loja_serializer.data['numero']
    assert loja_serializer.data['complemento']
    assert loja_serializer.data['latitude'] is None
    assert loja_serializer.data['longitude'] is None
    assert loja_serializer.data['numero_iptu'] is not None
    assert loja_serializer.data['telefone']
    assert loja_serializer.data['nome_fantasia']
    assert loja_serializer.data['foto_fachada']


def test_loja_create_serializer_configura_campos_de_upload():
    serializer = LojaCreateSerializer()
    comprovante = serializer.fields["comprovante_endereco"]
    foto_fachada = serializer.fields["foto_fachada"]

    assert not comprovante.required
    assert comprovante.allow_null
    assert comprovante.label == "Comprovante de endereço do ponto de venda"
    assert comprovante.help_text == "Campo opcional. Se enviado, deve estar em PDF."
    assert not foto_fachada.required
    assert foto_fachada.allow_null
    assert foto_fachada.label == "Foto da fachada da loja"
    assert foto_fachada.help_text == "Envie apenas arquivos JPG, JPEG ou PNG."


def test_loja_update_fachada_serializer_configura_label_e_help_text():
    serializer = LojaUpdateFachadaSerializer()

    assert serializer.fields["foto_fachada"].label == "Foto da fachada da loja"
    assert (
        serializer.fields["foto_fachada"].help_text
        == "Envie apenas arquivos JPG, JPEG ou PNG."
    )


def test_loja_fachada_update(payload_update_fachada_loja):
    loja_partial_update = LojaUpdateFachadaSerializer(data=payload_update_fachada_loja)
    assert loja_partial_update.is_valid()


def test_loja_fachada_update_rejeita_extensao_invalida(arquivo_txt_base64):
    loja_partial_update = LojaUpdateFachadaSerializer(
        data={"foto_fachada": arquivo_txt_base64}
    )

    assert not loja_partial_update.is_valid()
    assert loja_partial_update.errors["foto_fachada"] == [
        "Envie a foto da fachada em JPG, JPEG ou PNG."
    ]
