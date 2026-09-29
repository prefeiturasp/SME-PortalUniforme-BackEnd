from django.core import validators
from django.core.exceptions import ValidationError

from ..cnpj import CNPJ_VALIDATION_MESSAGE, validate_cnpj

phone_validation = validators.RegexValidator(
    regex=r"^\(\d{2}\) [\d\-]{9,10}$",
    message="Digite o telefone no formato (XX) 12345-6789. Entre 8 ou 9 digitos",
)


cep_validation = validators.RegexValidator(
    regex=r"^\d{5}-\d{3}$", message="Digite o CEP no formato XXXXX-XXX. Com 8 digitos"
)


cpf_validation = validators.RegexValidator(
    regex=r"^\d{3}\.\d{3}\.\d{3}\-\d{2}$",
    message="Digite o CPF ou CNPJ no formato XX.XXX.XXX/XXXX-XX ou XXX.XXX.XXX-XX.",
)


def cpf_cnpj_validation(value):
    if not value:
        return

    try:
        cpf_validation(value)
        return
    except ValidationError:
        pass

    try:
        cnpj_validation(value)
    except ValidationError:
        raise ValidationError(
            "Digite o CPF ou CNPJ no formato XX.XXX.XXX/XXXX-XX ou XXX.XXX.XXX-XX."
        )


def cnpj_validation(value):
    if not value:
        return

    if not validate_cnpj(value):
        raise ValidationError(CNPJ_VALIDATION_MESSAGE)
