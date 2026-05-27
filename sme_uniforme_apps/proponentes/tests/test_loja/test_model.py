import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from ...admin import LojasInLine, LojaAdmin
from ...models import Loja
from ...models.forms import LojaAdminForm

pytestmark = pytest.mark.django_db


def create_uploaded_file(file_name):
    return SimpleUploadedFile(file_name, b"conteudo_teste")


def create_loja_admin_form(file_name):
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
        files={"foto_fachada": create_uploaded_file(file_name)},
    )


def test_loja(proponente, loja_fisica):
    assert isinstance(loja_fisica, Loja)


def test_admin_loja_esconde_comprovante_endereco():
    assert LojasInLine.form == LojaAdminForm
    assert LojasInLine.exclude == ("comprovante_endereco",)
    assert LojaAdmin.exclude == ("comprovante_endereco",)


def test_loja_admin_form_configura_label_e_help_text():
    form = LojaAdminForm()

    assert form.fields["foto_fachada"].label == "Foto da fachada da loja"
    assert (
        form.fields["foto_fachada"].help_text
        == "Envie apenas arquivos JPG, JPEG ou PNG."
    )


@pytest.mark.parametrize("file_name", ["fachada.png", "fachada.jpg", "fachada.jpeg"])
def test_loja_admin_form_aceita_uploads_de_imagem(file_name):
    form = create_loja_admin_form(file_name)

    assert form.is_valid(), form.errors


@pytest.mark.parametrize("file_name", ["fachada.pdf", "fachada.txt"])
def test_loja_admin_form_rejeita_uploads_invalidos(file_name):
    form = create_loja_admin_form(file_name)

    assert not form.is_valid()
    assert form.errors["foto_fachada"] == [
        "Envie a foto da fachada em JPG, JPEG ou PNG."
    ]


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
