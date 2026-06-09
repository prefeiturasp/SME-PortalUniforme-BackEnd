import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from sme_uniforme_apps.proponentes.models import Proponente


@pytest.fixture
def proponente_triade():
    return baker.make(
        "Proponente",
        cnpj="00.529.476/0001-14",
        razao_social="Empresa Teste LTDA",
        end_logradouro="Rua Teste, 123",
        end_cidade="Sao Paulo",
        end_uf="SP",
        end_cep="01001-000",
        telefone="(11) 3333-4444",
        email="triade-builder@teste.com",
        responsavel="Maria Responsavel",
        status=Proponente.STATUS_INSCRITO,
    )


@pytest.fixture
def tipo_documento_triade():
    return baker.make(
        "TipoDocumento",
        identificador="cartao_cnpj",
        nome="Cartao CNPJ",
        obrigatorio=True,
        visivel=True,
    )


@pytest.fixture
def arquivo_pdf():
    return SimpleUploadedFile(
        "cartao_cnpj.pdf",
        b"%PDF-1.4 conteudo de teste",
        content_type="application/pdf",
    )


@pytest.fixture
def loja_primeira(proponente_triade):
    return baker.make(
        "Loja",
        proponente=proponente_triade,
        nome_fantasia="Loja Centro",
        cep="01001-000",
        endereco="Praca da Se",
        bairro="Centro",
        numero="100",
        telefone="(11) 3333-4444",
        site="https://primeira-loja.exemplo.com",
    )


@pytest.fixture
def loja_segunda(proponente_triade):
    return baker.make(
        "Loja",
        proponente=proponente_triade,
        nome_fantasia="Loja Bairro",
        cep="02002-000",
        endereco="Rua Dois",
        bairro="Bairro",
        numero="200",
        telefone="(11) 4444-5555",
    )


@pytest.fixture
def anexo_triade(proponente_triade, tipo_documento_triade, arquivo_pdf):
    return baker.make(
        "Anexo",
        proponente=proponente_triade,
        tipo_documento=tipo_documento_triade,
        arquivo=arquivo_pdf,
    )
