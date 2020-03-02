import pytest
from django.core.exceptions import ValidationError

from ...models import Loja

pytestmark = pytest.mark.django_db


def test_loja(proponente, loja_fisica):
    assert isinstance(loja_fisica, Loja)


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
