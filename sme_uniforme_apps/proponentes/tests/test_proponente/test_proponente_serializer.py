import pytest
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from sme_uniforme_apps.core.models import Uniforme

from sme_uniforme_apps.proponentes.api.serializers.proponente_serializer import (
    ProponenteCreateSerializer,
    ProponenteLookUpSerializer,
    ProponenteSerializer,
)

pytestmark = pytest.mark.django_db


def test_proponente_serializer(proponente):

    proponente_serializer = ProponenteSerializer(proponente)

    assert proponente_serializer.data is not None
    assert proponente_serializer.data['cnpj']
    assert proponente_serializer.data['razao_social']
    assert proponente_serializer.data['alterado_em']
    assert proponente_serializer.data['uuid']
    assert proponente_serializer.data['responsavel']
    assert proponente_serializer.data['end_logradouro']
    assert proponente_serializer.data['end_cidade']
    assert proponente_serializer.data['end_uf']
    assert proponente_serializer.data['end_cep']
    assert proponente_serializer.data['telefone']
    assert proponente_serializer.data['email']
    assert proponente_serializer.data['criado_em']
    assert proponente_serializer.data['id']
    assert proponente_serializer.data['ofertas_de_uniformes'] is not None
    assert proponente_serializer.data['lojas'] is not None
    assert proponente_serializer.data['arquivos_anexos'] is not None


def test_proponente_lookup_serializer(proponente):

    proponente_serializer = ProponenteLookUpSerializer(proponente)

    assert proponente_serializer.data is not None
    assert proponente_serializer.data['razao_social']
    assert proponente_serializer.data['uuid']


def test_proponente_create_serializer_cria_loja_com_comprovante_endereco(
    payload_proponente_sem_anexos,
    settings,
    tmp_path,
):
    settings.MEDIA_ROOT = str(tmp_path)
    baker.make(
        "LimiteCategoria",
        categoria_uniforme=Uniforme.CATEGORIA_KIT_VERAO,
        preco_maximo=999,
    )
    baker.make(
        "LimiteCategoria",
        categoria_uniforme=Uniforme.CATEGORIA_KIT_INVERNO,
        preco_maximo=999,
    )
    payload_proponente_sem_anexos["lojas"][0]["foto_fachada"] = SimpleUploadedFile(
        "fachada.png",
        b"conteudo_teste",
        content_type="image/png",
    )
    payload_proponente_sem_anexos["lojas"][0]["comprovante_endereco"] = (
        SimpleUploadedFile(
            "comprovante.pdf",
            b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
            content_type="application/pdf",
        )
    )

    serializer = ProponenteCreateSerializer(data=payload_proponente_sem_anexos)

    assert serializer.is_valid(), serializer.errors

    proponente = serializer.save()
    loja = proponente.lojas.get(nome_fantasia="Loja A")
    proponente_serializer = ProponenteSerializer(proponente)
    comprovante_url = next(
        loja_payload["comprovante_endereco"]
        for loja_payload in proponente_serializer.data["lojas"]
        if loja_payload["nome_fantasia"] == "Loja A"
    )

    assert loja.comprovante_endereco
    assert Path(loja.comprovante_endereco.path).exists()
    assert comprovante_url
    assert comprovante_url.endswith(".pdf")

    loja.comprovante_endereco.delete(save=False)
