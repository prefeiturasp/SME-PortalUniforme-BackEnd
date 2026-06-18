import base64
import uuid

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from sme_uniforme_apps.triade.builders import (
    TriadePayloadBuilder,
    TriadePayloadBuilderError,
)

pytestmark = pytest.mark.django_db


def test_build_payload_monta_payload_com_primeira_loja_e_documento(
    proponente_triade, loja_primeira, loja_segunda, anexo_triade
):
    builder = TriadePayloadBuilder(
        source_system="portal_uniforme", schema_version="1.0"
    )

    payload = builder.build(proponente_triade, external_batch_id="PROTOCOLO-TRIADE-001")

    assert payload["source_system"] == "portal_uniforme"
    assert payload["schema_version"] == "1.0"
    assert payload["external_batch_id"] == "PROTOCOLO-TRIADE-001"
    assert payload["applicant"]["document_number"] == "AB12C3D4000139"
    assert payload["applicant"]["name"] == "Empresa Teste LTDA"
    assert payload["applicant"]["fields"]["nome_fantasia"] == "Loja Centro"
    assert payload["applicant"]["fields"]["bairro"] == "Centro"
    assert payload["applicant"]["fields"]["numero"] == "100"
    assert payload["applicant"]["fields"]["telefone_responsavel"] == "(11) 3333-4444"
    assert payload["applicant"]["fields"]["ponto-venda"] == [
        {
            "nome-loja": "Loja Centro",
            "endereco": "Praca da Se",
            "numero": "100",
            "cep": "01001-000",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "uf": "SP",
            "telefone": "(11) 3333-4444",
            "site": "https://primeira-loja.exemplo.com",
        },
        {
            "nome-loja": "Loja Bairro",
            "endereco": "Rua Dois",
            "numero": "200",
            "cep": "02002-000",
            "bairro": "Bairro",
            "cidade": "São Paulo",
            "uf": "SP",
            "telefone": "(11) 4444-5555",
        },
    ]

    document = payload["documents"][0]
    assert document["external_document_id"] == str(anexo_triade.uuid)
    assert document["document_type"] == "cartao_cnpj"
    assert document["title"].startswith("cartao_cnpj")
    assert document["title"].endswith(".pdf")
    assert "/" not in document["title"]
    assert document["content"]["type"] == "base64"
    assert document["content"]["mime_type"] == "application/pdf"
    assert document["content"]["data"] == base64.b64encode(
        b"%PDF-1.4 conteudo de teste"
    ).decode("ascii")
    assert document["metadata"]["anexo_uuid"] == str(anexo_triade.uuid)
    assert document["metadata"]["proponente_uuid"] == str(proponente_triade.uuid)
    assert document["metadata"]["tipo_documento_identificador"] == "cartao_cnpj"
    assert payload["metadata"]["proponente_uuid"] == str(proponente_triade.uuid)
    assert payload["metadata"]["protocolo"] == proponente_triade.protocolo
    assert payload["metadata"]["status_atual_proponente"] == proponente_triade.status
    assert payload["metadata"]["origem_operacional"] == "concluir-cadastro"
    assert payload["metadata"]["fluxo"] == "mvp_conclusao_cadastro"


def test_build_payload_monta_documentos_de_loja_com_foto_fachada_e_comprovante(
    proponente_triade, loja_primeira, loja_segunda, anexo_triade
):
    builder = TriadePayloadBuilder(
        source_system="portal_uniforme", schema_version="1.0"
    )

    payload = builder.build(proponente_triade, external_batch_id="PROTOCOLO-TRIADE-LOJAS")

    documentos_loja = [
        documento for documento in payload["documents"]
        if documento["document_type"] in ("foto-fachada", "comprovante-endereco")
    ]
    identificadores = [documento["document_type"] for documento in documentos_loja]
    assert identificadores == [
        "foto-fachada",
        "comprovante-endereco",
        "foto-fachada",
        "comprovante-endereco",
    ]

    for documento in documentos_loja:
        assert documento["title"]
        assert documento["content"]["type"] == "base64"
        assert documento["content"]["data"]
        assert documento["metadata"]["loja_uuid"]
        assert documento["metadata"]["proponente_uuid"] == str(proponente_triade.uuid)
        assert documento["metadata"]["tipo_documento_identificador"] == documento["document_type"]

    foto_fachada_centro = documentos_loja[0]
    assert foto_fachada_centro["content"]["mime_type"] == "image/jpeg"
    assert foto_fachada_centro["external_document_id"] == str(
        uuid.uuid5(uuid.UUID(str(loja_primeira.uuid)), "foto_fachada")
    )

    comprovante_centro = documentos_loja[1]
    assert comprovante_centro["content"]["mime_type"] == "application/pdf"
    assert comprovante_centro["external_document_id"] == str(
        uuid.uuid5(uuid.UUID(str(loja_primeira.uuid)), "comprovante_endereco")
    )


def test_build_payload_diferencia_lojas_via_external_document_id_e_metadata(
    proponente_triade, loja_primeira, anexo_triade
):
    loja_mesmo_nome = baker.make(
        "Loja",
        proponente=proponente_triade,
        nome_fantasia=loja_primeira.nome_fantasia,
        cep="02002-000",
        endereco="Rua Outra",
        bairro="Outro Bairro",
        numero="999",
        telefone="(11) 9999-9999",
        foto_fachada=SimpleUploadedFile(
            "fachada2.jpg",
            b"\xff\xd8\xff\xe0outra fachada",
            content_type="image/jpeg",
        ),
        comprovante_endereco=SimpleUploadedFile(
            "comprovante2.pdf",
            b"%PDF-1.4 outro comprovante",
            content_type="application/pdf",
        ),
    )

    builder = TriadePayloadBuilder(
        source_system="portal_uniforme", schema_version="1.0"
    )
    payload = builder.build(proponente_triade, external_batch_id="PROTOCOLO-TRIADE-DUP")

    documentos_loja = [
        documento for documento in payload["documents"]
        if documento["document_type"] in ("foto-fachada", "comprovante-endereco")
    ]
    identificadores = [documento["external_document_id"] for documento in documentos_loja]

    assert len(identificadores) == len(set(identificadores))

    foto_fachada_primeira = next(
        doc for doc in documentos_loja
        if doc["document_type"] == "foto-fachada"
        and doc["metadata"]["loja_id"] == loja_primeira.id
    )
    foto_fachada_mesmo_nome = next(
        doc for doc in documentos_loja
        if doc["document_type"] == "foto-fachada"
        and doc["metadata"]["loja_id"] == loja_mesmo_nome.id
    )
    assert foto_fachada_primeira["document_type"] == foto_fachada_mesmo_nome["document_type"]
    assert foto_fachada_primeira["external_document_id"] != foto_fachada_mesmo_nome["external_document_id"]
    assert foto_fachada_primeira["metadata"]["loja_uuid"] != foto_fachada_mesmo_nome["metadata"]["loja_uuid"]


def test_build_payload_falha_sem_loja(proponente_triade, anexo_triade):
    builder = TriadePayloadBuilder(
        source_system="portal_uniforme", schema_version="1.0"
    )

    with pytest.raises(TriadePayloadBuilderError, match="ao menos uma loja cadastrada"):
        builder.build(proponente_triade, external_batch_id="PROTOCOLO-TRIADE-002")


def test_build_payload_falha_sem_identificador_do_tipo_documento(
    proponente_triade, loja_primeira, arquivo_pdf
):
    tipo_documento_sem_identificador = baker.make(
        "TipoDocumento",
        identificador=None,
        nome="Documento Sem Alias",
        obrigatorio=True,
        visivel=True,
    )
    baker.make(
        "Anexo",
        proponente=proponente_triade,
        tipo_documento=tipo_documento_sem_identificador,
        arquivo=arquivo_pdf,
    )
    builder = TriadePayloadBuilder(
        source_system="portal_uniforme", schema_version="1.0"
    )

    with pytest.raises(
        TriadePayloadBuilderError, match="TipoDocumento.identificador preenchido"
    ):
        builder.build(proponente_triade, external_batch_id="PROTOCOLO-TRIADE-003")
