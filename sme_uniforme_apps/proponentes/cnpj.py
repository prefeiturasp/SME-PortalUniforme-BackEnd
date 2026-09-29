import re

CNPJ_VALIDATION_MESSAGE = "Digite CNPJ válido no formato XX.XXX.XXX/XXXX-XX, com letras e números quando aplicável."
CNPJ_LENGTH = 14
CNPJ_BODY_LENGTH = 12
CNPJ_FORMATTED_RE = re.compile(
    r"^[A-Z0-9]{2}\.[A-Z0-9]{3}\.[A-Z0-9]{3}/[A-Z0-9]{4}-\d{2}$"
)
CNPJ_COMPACT_RE = re.compile(r"^[A-Z0-9]{12}\d{2}$")
CNPJ_FIRST_DV_WEIGHTS = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
CNPJ_SECOND_DV_WEIGHTS = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)


def sanitize_cnpj(value):
    return str(value or "").strip().upper()


def compact_cnpj(value):
    return "".join(char for char in sanitize_cnpj(value) if char.isalnum())


def format_cnpj(value):
    compact = compact_cnpj(value)
    if not CNPJ_COMPACT_RE.fullmatch(compact):
        return sanitize_cnpj(value)

    return "{}.{}.{}/{}-{}".format(
        compact[:2],
        compact[2:5],
        compact[5:8],
        compact[8:12],
        compact[12:],
    )


def first_access_password(value):
    compact = compact_cnpj(value)
    if not compact:
        return ""
    return compact[:5]


def validate_cnpj(value):
    compact = compact_cnpj(value)
    if not CNPJ_COMPACT_RE.fullmatch(compact):
        return False

    if compact.isdigit() and len(set(compact)) == 1:
        return False

    expected_dvs = _calculate_dvs(compact[:CNPJ_BODY_LENGTH])
    return compact[-2:] == expected_dvs


def _calculate_dvs(body):
    first_digit = _calculate_dv(body, CNPJ_FIRST_DV_WEIGHTS)
    second_digit = _calculate_dv(body + first_digit, CNPJ_SECOND_DV_WEIGHTS)
    return first_digit + second_digit


def _calculate_dv(base, weights):
    total = sum(_character_value(char) * weight for char, weight in zip(base, weights))
    remainder = total % 11
    return "0" if remainder < 2 else str(11 - remainder)


def _character_value(char):
    return ord(char) - 48
