import os

PDF_EXTENSIONS = ("pdf",)
IMAGE_EXTENSIONS = ("jpg", "jpeg", "png")


def get_upload_extension(value):
    if not value:
        return ""

    if hasattr(value, "name"):
        return _extension_from_name(value.name)

    if isinstance(value, str):
        if ";base64," in value:
            header = value.split(";base64,", 1)[0]
            return header.split("/")[-1].lower()

        return _extension_from_name(value)

    return ""


def validate_upload_extension(value, allowed_extensions, error_message):
    extension = get_upload_extension(value)

    if extension not in allowed_extensions:
        raise ValueError(error_message)

    return extension


def _extension_from_name(file_name):
    _, extension = os.path.splitext(file_name or "")
    return extension.lower().lstrip(".")
