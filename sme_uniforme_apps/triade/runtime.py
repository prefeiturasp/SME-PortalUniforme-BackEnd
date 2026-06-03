from dataclasses import dataclass

from django.conf import settings


@dataclass(frozen=True)
class TriadeRuntimeConfig:
    enabled: bool
    send_only_required_documents: bool


def get_triade_runtime_config():
    enabled = getattr(settings, "TRIADE_ENABLED", False)
    send_only_required_documents = getattr(
        settings, "TRIADE_SEND_ONLY_REQUIRED_DOCUMENTS", False
    )

    from .models import TriadeConfiguracao

    configuracao = TriadeConfiguracao.objects.order_by("pk").first()
    if not configuracao:
        return TriadeRuntimeConfig(
            enabled=enabled,
            send_only_required_documents=send_only_required_documents,
        )

    return TriadeRuntimeConfig(
        enabled=configuracao.habilitado,
        send_only_required_documents=configuracao.enviar_apenas_documentos_obrigatorios,
    )


def is_triade_enabled():
    return get_triade_runtime_config().enabled
