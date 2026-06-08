TRIADE_LOTE_STATUSES = (
    "payload_ready",
    "received",
    "processing",
    "pending_review",
    "completed",
    "error",
)

TRIADE_DOCUMENTO_STATUSES = (
    "received",
    "processing",
    "pending_review",
    "completed",
    "error",
)

TRIADE_DECISOES = (
    "APROVADO",
    "REPROVADO",
    "PENDENCIA",
)

TRIADE_CALLBACK_PROCESSING_STATUSES = (
    "recebido",
    "enfileirado",
    "processando",
    "processado",
    "duplicado",
    "erro",
)

TRIADE_LOTE_STATUS_LABELS = {
    "payload_ready": "Payload pronto",
    "received": "Recebido",
    "processing": "Em processamento",
    "pending_review": "Aguardando revisão",
    "completed": "Concluído",
    "error": "Erro",
}

TRIADE_DOCUMENTO_STATUS_LABELS = {
    "received": "Recebido",
    "processing": "Em processamento",
    "pending_review": "Aguardando revisão",
    "completed": "Concluído",
    "error": "Erro",
}

TRIADE_DECISAO_LABELS = {
    "APROVADO": "Aprovado",
    "REPROVADO": "Reprovado",
    "PENDENCIA": "Pendência",
}

TRIADE_CALLBACK_PROCESSING_LABELS = {
    "recebido": "Recebido",
    "enfileirado": "Enfileirado",
    "processando": "Processando",
    "processado": "Processado",
    "duplicado": "Duplicado",
    "erro": "Erro",
}


def normalize_status(value):
    if value is None:
        return None

    normalized = str(value).strip().lower()
    return normalized or None


def normalize_decisao(value):
    if value is None:
        return None

    normalized = str(value).strip().upper()
    return normalized or None


def merge_known_and_observed_values(known_values, observed_values, normalizer):
    merged = []
    seen = set()

    for value in list(known_values) + list(observed_values):
        normalized = normalizer(value)
        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        merged.append(normalized)

    return merged
