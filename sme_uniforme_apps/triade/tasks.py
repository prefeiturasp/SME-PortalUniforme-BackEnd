from celery import shared_task

from .callbacks import TriadeCallbackService
from .exceptions import TriadeTransientError
from .services import TriadeSubmissionService


@shared_task(
    bind=True,
    autoretry_for=(TriadeTransientError,),
    retry_backoff=2,
    retry_kwargs={"max_retries": 6},
)
def orquestrar_envio_lote_triade(
    self,
    proponente_uuid,
    origem_operacional=TriadeSubmissionService.DEFAULT_ORIGEM_OPERACIONAL,
    fluxo=TriadeSubmissionService.DEFAULT_FLUXO,
):
    lote = TriadeSubmissionService().dispatch_proponente_uuid(
        proponente_uuid=proponente_uuid,
        origem_operacional=origem_operacional,
        fluxo=fluxo,
    )
    return {
        "lote_id": lote.id,
        "lote_uuid": str(lote.uuid),
        "external_batch_id": lote.external_batch_id,
        "batch_id": str(lote.batch_id) if lote.batch_id else None,
        "submission_id": str(lote.submission_id) if lote.submission_id else None,
        "status": lote.status,
    }


@shared_task
def processar_callback_triade(callback_id):
    callback = TriadeCallbackService().process_callback(callback_id)
    return {
        "callback_id": callback.id,
        "delivery_id": str(callback.delivery_id),
        "status_processamento": callback.status_processamento,
        "lote_id": callback.lote_id,
    }
