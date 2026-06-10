import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from ...api.serializers.loja_serializer import (LojaCreateSerializer, LojaSerializer, LojaUpdateFachadaSerializer)

pytestmark = pytest.mark.django_db

PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"


def create_uploaded_file(file_name, content=b"conteudo_teste", content_type=None):
    return SimpleUploadedFile(file_name, content, content_type=content_type)


def create_loja_payload(foto_fachada=None, comprovante_endereco=None):
    payload = {
        "nome_fantasia": "Loja Teste",
        "cep": "27600-000",
        "endereco": "Rua Teste",
        "bairro": "Centro",
        "numero": "123",
        "complemento": "loja 1",
        "telefone": "(11) 4565-9876",
        "numero_iptu": "",
        "foto_fachada": create_uploaded_file("fachada.png", content_type="image/png"),
        "comprovante_endereco": create_uploaded_file(
            "comprovante.pdf",
            content=PDF_BYTES,
            content_type="application/pdf",
        ),
    }

    if foto_fachada is None:
        payload.pop("foto_fachada")
    elif foto_fachada is not False:
        payload["foto_fachada"] = foto_fachada

    if comprovante_endereco is None:
        payload.pop("comprovante_endereco")
    elif comprovante_endereco is not False:
        payload["comprovante_endereco"] = comprovante_endereco

    return payload


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


def test_loja_create_serializer_rejeita_comprovante_endereco_nao_pdf():
    payload_loja = create_loja_payload(
        comprovante_endereco=create_uploaded_file("comprovante.txt")
    )

    serializer = LojaCreateSerializer(data=payload_loja)

    assert not serializer.is_valid()
    assert serializer.errors["comprovante_endereco"] == [
        "Envie o comprovante de endereço do ponto de venda em PDF."
    ]


def test_loja_update_fachada_serializer_configura_label_e_help_text():
    serializer = LojaUpdateFachadaSerializer()

    assert not serializer.fields["foto_fachada"].required
    assert serializer.fields["foto_fachada"].allow_null
    assert serializer.fields["foto_fachada"].label == "Foto da fachada da loja"
    assert (
        serializer.fields["foto_fachada"].help_text
        == "Envie apenas arquivos JPG, JPEG ou PNG."
    )


def test_loja_fachada_update():
    loja_partial_update = LojaUpdateFachadaSerializer(
        data={
            "foto_fachada": create_uploaded_file(
                "fachada.png", content_type="image/png"
            )
        }
    )
    assert loja_partial_update.is_valid()


def test_loja_fachada_update_rejeita_extensao_invalida():
    loja_partial_update = LojaUpdateFachadaSerializer(
        data={"foto_fachada": create_uploaded_file("fachada.txt")}
    )

    assert not loja_partial_update.is_valid()
    assert loja_partial_update.errors["foto_fachada"] == [
        "Envie a foto da fachada em JPG, JPEG ou PNG."
    ]
