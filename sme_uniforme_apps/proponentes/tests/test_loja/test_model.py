import pytest
from pathlib import Path

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory

from ...admin import LojasInLine, LojaAdmin
from ...models import Loja, Proponente
from ...models.forms import LojaAdminForm

pytestmark = pytest.mark.django_db

User = get_user_model()
MISSING = object()


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        email="gestor-loja@teste.com", password="123456"
    )


PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"


def create_uploaded_file(file_name, content=b"conteudo_teste", content_type=None):
    return SimpleUploadedFile(file_name, content, content_type=content_type)


def create_pdf_uploaded_file(file_name="comprovante.pdf"):
    return create_uploaded_file(file_name, PDF_BYTES, "application/pdf")


def create_image_uploaded_file(file_name="fachada.png"):
    return create_uploaded_file(file_name, content_type="image/png")


def create_loja_admin_form(foto_fachada=MISSING, comprovante_endereco=MISSING):
    files = {}

    if foto_fachada is MISSING:
        foto_fachada = create_image_uploaded_file()
    if comprovante_endereco is MISSING:
        comprovante_endereco = create_pdf_uploaded_file()

    if foto_fachada is not None:
        files["foto_fachada"] = foto_fachada
    if comprovante_endereco is not None:
        files["comprovante_endereco"] = comprovante_endereco

    return LojaAdminForm(
        data={
            "nome_fantasia": "Loja Teste",
            "cep": "27600-000",
            "endereco": "Rua Teste",
            "bairro": "Centro",
            "numero": "123",
            "complemento": "loja 1",
            "telefone": "(11) 4565-9876",
            "numero_iptu": "",
            "site": "",
        },
        files=files,
    )


def test_loja(proponente, loja_fisica):
    assert isinstance(loja_fisica, Loja)


def test_admin_loja_exibe_comprovante_endereco(proponente, admin_user):
    request = RequestFactory().get("/")
    request.user = admin_user
    loja_admin = LojaAdmin(Loja, AdminSite())
    inline = LojasInLine(Proponente, AdminSite())

    assert LojasInLine.form == LojaAdminForm
    assert "comprovante_endereco" in loja_admin.get_form(request).base_fields
    assert (
        "comprovante_endereco"
        in inline.get_formset(request, proponente).form.base_fields
    )


def test_admin_loja_protocolo_nao_quebra_sem_proponente():
    loja_admin = LojaAdmin(Loja, AdminSite())
    loja = Loja(
        nome_fantasia="Loja Sem Proponente",
        cep="01001-000",
        endereco="Rua Teste",
        bairro="Centro",
        numero="100",
    )

    assert loja_admin.protocolo(loja) == "-"


def test_loja_admin_form_configura_label_e_help_text():
    form = LojaAdminForm()

    assert not form.fields["comprovante_endereco"].required
    assert (
        form.fields["comprovante_endereco"].label
        == "Comprovante de endereço do ponto de venda"
    )
    assert (
        form.fields["comprovante_endereco"].help_text
        == "Campo opcional. Se enviado, deve estar em PDF."
    )
    assert not form.fields["foto_fachada"].required
    assert form.fields["foto_fachada"].label == "Foto da fachada da loja"
    assert (
        form.fields["foto_fachada"].help_text
        == "Envie apenas arquivos JPG, JPEG ou PNG."
    )


@pytest.mark.parametrize("file_name", ["fachada.png", "fachada.jpg", "fachada.jpeg"])
def test_loja_admin_form_aceita_uploads_de_imagem(file_name):
    form = create_loja_admin_form(foto_fachada=create_uploaded_file(file_name))

    assert form.is_valid(), form.errors


@pytest.mark.parametrize("file_name", ["fachada.pdf", "fachada.txt"])
def test_loja_admin_form_rejeita_uploads_invalidos(file_name):
    form = create_loja_admin_form(foto_fachada=create_uploaded_file(file_name))

    assert not form.is_valid()
    assert form.errors["foto_fachada"] == [
        "Envie a foto da fachada em JPG, JPEG ou PNG."
    ]


def test_loja_admin_form_aceita_comprovante_endereco_pdf():
    form = create_loja_admin_form(
        comprovante_endereco=create_pdf_uploaded_file(),
    )

    assert form.is_valid(), form.errors


@pytest.mark.parametrize("file_name", ["comprovante.jpg", "comprovante.txt"])
def test_loja_admin_form_rejeita_comprovante_endereco_invalido(file_name):
    form = create_loja_admin_form(
        comprovante_endereco=create_uploaded_file(file_name),
    )

    assert not form.is_valid()
    assert form.errors["comprovante_endereco"] == [
        "Envie o comprovante de endereço do ponto de venda em PDF."
    ]


def test_loja_persiste_comprovante_endereco_no_disco(settings, tmp_path, proponente):
    settings.MEDIA_ROOT = str(tmp_path)
    loja = Loja.objects.create(
        proponente=proponente,
        nome_fantasia="Loja Teste",
        cep="27600-000",
        endereco="Rua Teste",
        bairro="Centro",
        numero="123",
        complemento="loja 1",
        telefone="(11) 4565-9876",
        comprovante_endereco=create_pdf_uploaded_file(),
    )

    assert loja.comprovante_endereco
    assert loja.comprovante_endereco.name.endswith(".pdf")
    assert Path(loja.comprovante_endereco.path).exists()

    loja.comprovante_endereco.delete(save=False)


def test_validacao_telefone_fora_formato(proponente):
    loja_com_tel_fora_do_formato = Loja(
        proponente=proponente,
        cep='27600-000',
        endereco='Rua Teste',
        bairro='Centro',
        numero='123',
        complemento='loja 1',
        telefone='1145659876'
    )

    with pytest.raises(ValidationError):
        loja_com_tel_fora_do_formato.full_clean()


def test_validacao_telefone_formato_fixo(proponente):
    loja_com_tel_fora_do_formato = Loja(
        proponente=proponente,
        cep='27600-000',
        endereco='Rua Teste',
        bairro='Centro',
        numero='123',
        complemento='loja 1',
        telefone='(24) 2452-2568'
    )
    loja_com_tel_fora_do_formato.save()

    loja_com_tel_fora_do_formato.full_clean()

    assert Loja.objects.all().exists()


def test_validacao_telefone_formato_celular(proponente):
    loja_com_tel_fora_do_formato = Loja(
        proponente=proponente,
        cep='27600-000',
        endereco='Rua Teste',
        bairro='Centro',
        numero='123',
        complemento='loja 1',
        telefone='(24) 9988-29105'
    )
    loja_com_tel_fora_do_formato.save()

    loja_com_tel_fora_do_formato.full_clean()

    assert Loja.objects.all().exists()
