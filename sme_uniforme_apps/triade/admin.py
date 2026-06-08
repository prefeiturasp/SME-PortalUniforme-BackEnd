import json

from django.contrib import admin
from django.template.response import TemplateResponse
from django.utils.dateparse import parse_date
from django.utils.html import format_html

from .models import (
    TriadeCallback,
    TriadeConfiguracao,
    TriadeDocumento,
    TriadeEstatistica,
    TriadeLote,
)
from .statuses import (
    TRIADE_CALLBACK_PROCESSING_LABELS,
    TRIADE_CALLBACK_PROCESSING_STATUSES,
    TRIADE_DECISAO_LABELS,
    TRIADE_DECISOES,
    TRIADE_DOCUMENTO_STATUS_LABELS,
    TRIADE_DOCUMENTO_STATUSES,
    TRIADE_LOTE_STATUS_LABELS,
    TRIADE_LOTE_STATUSES,
    merge_known_and_observed_values,
    normalize_decisao,
    normalize_status,
)


class TriadeReadOnlyAdmin(admin.ModelAdmin):

    readonly_fields = ()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        model_fields = [field.name for field in self.model._meta.fields]
        extra_fields = [
            field for field in self.readonly_fields if field not in model_fields
        ]
        return model_fields + extra_fields

    def render_large_text(self, value, rows=18):
        if not value:
            return "-"

        rendered_value = value
        try:
            rendered_value = json.dumps(
                json.loads(value), ensure_ascii=False, indent=2, sort_keys=True
            )
        except (TypeError, ValueError):
            pass

        return format_html(
            '<textarea readonly rows="{}" style="width:100%;font-family:monospace;white-space:pre;">{}</textarea>',
            rows,
            rendered_value,
        )

    def has_change_permission(self, request, obj=None):
        return obj is None or super(TriadeReadOnlyAdmin, self).has_change_permission(
            request, obj
        )


@admin.register(TriadeLote)
class TriadeLoteAdmin(TriadeReadOnlyAdmin):
    readonly_fields = ("payload_envio_formatado",)
    list_display = (
        "external_batch_id",
        "proponente",
        "status",
        "batch_id",
        "submission_id",
        "criado_em",
        "alterado_em",
    )
    list_filter = ("status", "source_system", "schema_version")
    list_select_related = ("proponente",)
    ordering = ("-criado_em",)
    search_fields = (
        "external_batch_id",
        "=batch_id",
        "=submission_id",
        "proponente__cnpj",
        "proponente__razao_social",
    )

    def get_fields(self, request, obj=None):
        fields = [field.name for field in self.model._meta.fields]
        return [
            "payload_envio_formatado" if field == "payload_envio" else field
            for field in fields
        ]

    def payload_envio_formatado(self, obj):
        return self.render_large_text(obj.payload_envio)

    payload_envio_formatado.short_description = "Payload envio"


@admin.register(TriadeDocumento)
class TriadeDocumentoAdmin(TriadeReadOnlyAdmin):
    list_display = (
        "external_document_id",
        "lote",
        "anexo",
        "status",
        "decisao",
        "document_id",
        "criado_em",
    )
    list_filter = ("status", "decisao")
    list_select_related = ("lote", "anexo")
    ordering = ("-criado_em",)
    search_fields = (
        "external_document_id",
        "=document_id",
        "external_document_type",
        "document_type",
        "title",
        "=anexo__uuid",
    )


@admin.register(TriadeCallback)
class TriadeCallbackAdmin(TriadeReadOnlyAdmin):
    readonly_fields = ("payload_bruto_formatado",)
    list_display = (
        "delivery_id",
        "lote",
        "status_processamento",
        "external_batch_id",
        "batch_id",
        "criado_em",
        "processado_em",
    )
    list_filter = ("status_processamento",)
    list_select_related = ("lote",)
    ordering = ("-criado_em",)
    search_fields = (
        "=delivery_id",
        "external_batch_id",
        "=batch_id",
        "=submission_id",
        "payload_hash",
    )

    def get_fields(self, request, obj=None):
        fields = [field.name for field in self.model._meta.fields]
        return [
            "payload_bruto_formatado" if field == "payload_bruto" else field
            for field in fields
        ]

    def payload_bruto_formatado(self, obj):
        return self.render_large_text(obj.payload_bruto)

    payload_bruto_formatado.short_description = "Payload bruto"


@admin.register(TriadeConfiguracao)
class TriadeConfiguracaoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "habilitado",
        "enviar_apenas_documentos_obrigatorios",
        "alterado_em",
    )
    readonly_fields = ("criado_em", "alterado_em", "uuid")
    fields = (
        "habilitado",
        "enviar_apenas_documentos_obrigatorios",
        "uuid",
        "criado_em",
        "alterado_em",
    )

    def has_add_permission(self, request):
        return not TriadeConfiguracao.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TriadeEstatistica)
class TriadeEstatisticaAdmin(admin.ModelAdmin):
    change_list_template = "admin/triade/triadeestatistica/change_list.html"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        filtros = self._build_filters(request)
        lotes = self._filter_lotes(filtros)
        callbacks = self._filter_callbacks(lotes, filtros)
        documentos = self._filter_documentos(lotes, filtros)
        catalog = self._build_catalog()
        metrics = self._build_metrics(lotes, callbacks, documentos, catalog)

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Estatisticas TRIADE",
            "filters": filtros,
            "catalog": catalog,
            "metrics": metrics,
            "status_lote_options": catalog["lotes"]["status"],
            "decisao_lote_options": catalog["lotes"]["decisoes"],
            "status_callback_options": catalog["callbacks"]["status"],
            "status_documento_options": catalog["documentos"]["status"],
            "decisao_documento_options": catalog["documentos"]["decisoes"],
            "lotes_cards": self._build_lotes_cards(metrics["lotes"]),
            "callbacks_cards": self._build_callbacks_cards(metrics["callbacks"]),
            "documentos_cards": self._build_documentos_cards(metrics["documentos"]),
            "lotes_por_status": self._rows_from_counts(
                catalog["lotes"]["status"], metrics["lotes"]["status"]
            ),
            "lotes_por_decisao": self._rows_from_counts(
                catalog["lotes"]["decisoes"], metrics["lotes"]["decisoes"]
            ),
            "callbacks_por_status": self._rows_from_counts(
                catalog["callbacks"]["status"], metrics["callbacks"]["status"]
            ),
            "documentos_por_status": self._rows_from_counts(
                catalog["documentos"]["status"], metrics["documentos"]["status"]
            ),
            "documentos_por_decisao": self._rows_from_counts(
                catalog["documentos"]["decisoes"], metrics["documentos"]["decisoes"]
            ),
            "recent_lotes": lotes.select_related("proponente")
            .distinct()
            .order_by("-criado_em")[:10],
        }

        if extra_context:
            context.update(extra_context)

        return TemplateResponse(request, self.change_list_template, context)

    def _build_filters(self, request):
        return {
            "data_inicial": request.GET.get("data_inicial", ""),
            "data_final": request.GET.get("data_final", ""),
            "status_lote": request.GET.get("status_lote", ""),
            "decisao_lote": request.GET.get("decisao_lote", ""),
            "status_callback": request.GET.get("status_callback", ""),
            "status_documento": request.GET.get("status_documento", ""),
            "decisao_documento": request.GET.get("decisao_documento", ""),
        }

    def _filter_lotes(self, filtros):
        queryset = TriadeLote.objects.all()

        data_inicial = parse_date(filtros["data_inicial"])
        if data_inicial:
            queryset = queryset.filter(criado_em__date__gte=data_inicial)

        data_final = parse_date(filtros["data_final"])
        if data_final:
            queryset = queryset.filter(criado_em__date__lte=data_final)

        if filtros["status_lote"]:
            queryset = queryset.filter(status__iexact=filtros["status_lote"])

        if filtros["decisao_lote"]:
            queryset = queryset.filter(decisao_parecer__iexact=filtros["decisao_lote"])

        if filtros["status_callback"]:
            queryset = queryset.filter(
                callbacks__status_processamento__iexact=filtros["status_callback"]
            )

        if filtros["status_documento"]:
            queryset = queryset.filter(
                documentos__status__iexact=filtros["status_documento"]
            )

        if filtros["decisao_documento"]:
            queryset = queryset.filter(
                documentos__decisao__iexact=filtros["decisao_documento"]
            )

        return queryset.distinct()

    def _filter_callbacks(self, lotes, filtros):
        queryset = TriadeCallback.objects.filter(lote__in=lotes)
        if filtros["status_callback"]:
            queryset = queryset.filter(
                status_processamento__iexact=filtros["status_callback"]
            )
        return queryset.distinct()

    def _filter_documentos(self, lotes, filtros):
        queryset = TriadeDocumento.objects.filter(lote__in=lotes)
        if filtros["status_documento"]:
            queryset = queryset.filter(status__iexact=filtros["status_documento"])
        if filtros["decisao_documento"]:
            queryset = queryset.filter(decisao__iexact=filtros["decisao_documento"])
        return queryset.distinct()

    def _build_metrics(self, lotes, callbacks, documentos, catalog):
        lote_status_counts = self._count_values(
            lotes,
            "status",
            [item["value"] for item in catalog["lotes"]["status"]],
        )
        lote_decisao_counts = self._count_values(
            lotes,
            "decisao_parecer",
            [item["value"] for item in catalog["lotes"]["decisoes"]],
        )
        callback_status_counts = self._count_values(
            callbacks,
            "status_processamento",
            [item["value"] for item in catalog["callbacks"]["status"]],
        )
        documento_status_counts = self._count_values(
            documentos,
            "status",
            [item["value"] for item in catalog["documentos"]["status"]],
        )
        documento_decisao_counts = self._count_values(
            documentos,
            "decisao",
            [item["value"] for item in catalog["documentos"]["decisoes"]],
        )

        return {
            "lotes": {
                "total": lotes.count(),
                "sem_callback": lotes.filter(callback_recebido_em__isnull=True).count(),
                "status": lote_status_counts,
                "decisoes": lote_decisao_counts,
            },
            "callbacks": {
                "total": callbacks.count(),
                "status": callback_status_counts,
            },
            "documentos": {
                "total": documentos.count(),
                "status": documento_status_counts,
                "decisoes": documento_decisao_counts,
            },
        }

    def _build_catalog(self):
        return {
            "lotes": {
                "status": self._build_catalog_items(
                    self._option_values(
                        TriadeLote,
                        "status",
                        normalize_status,
                        TRIADE_LOTE_STATUSES,
                    ),
                    TRIADE_LOTE_STATUS_LABELS,
                ),
                "decisoes": self._build_catalog_items(
                    self._option_values(
                        TriadeLote,
                        "decisao_parecer",
                        normalize_decisao,
                        TRIADE_DECISOES,
                    ),
                    TRIADE_DECISAO_LABELS,
                ),
            },
            "callbacks": {
                "status": self._build_catalog_items(
                    self._option_values(
                        TriadeCallback,
                        "status_processamento",
                        normalize_status,
                        TRIADE_CALLBACK_PROCESSING_STATUSES,
                    ),
                    TRIADE_CALLBACK_PROCESSING_LABELS,
                ),
            },
            "documentos": {
                "status": self._build_catalog_items(
                    self._option_values(
                        TriadeDocumento,
                        "status",
                        normalize_status,
                        TRIADE_DOCUMENTO_STATUSES,
                    ),
                    TRIADE_DOCUMENTO_STATUS_LABELS,
                ),
                "decisoes": self._build_catalog_items(
                    self._option_values(
                        TriadeDocumento,
                        "decisao",
                        normalize_decisao,
                        TRIADE_DECISOES,
                    ),
                    TRIADE_DECISAO_LABELS,
                ),
            },
        }

    def _option_values(self, model, field_name, normalizer, known_values):
        observed_values = model.objects.exclude(
            **{"{}__isnull".format(field_name): True}
        )
        observed_values = observed_values.exclude(**{field_name: ""}).values_list(
            field_name, flat=True
        )
        return merge_known_and_observed_values(
            known_values, observed_values, normalizer
        )

    def _build_catalog_items(self, values, labels):
        items = []
        for value in values:
            label = labels.get(value, value)
            items.append(
                {
                    "value": value,
                    "label": label,
                    "display": (
                        "{} ({})".format(label, value) if label != value else value
                    ),
                }
            )
        return items

    def _count_values(self, queryset, field_name, values):
        counts = {}
        for value in values:
            counts[value] = queryset.filter(
                **{"{}__iexact".format(field_name): value}
            ).count()
        return counts

    def _rows_from_counts(self, catalog_items, counts):
        return [
            {
                "value": item["value"],
                "label": item["label"],
                "display": item["display"],
                "total": counts.get(item["value"], 0),
            }
            for item in catalog_items
        ]

    def _build_lotes_cards(self, metrics):
        return [
            {
                "label": "Total de lotes",
                "value": metrics["total"],
                "kind": "neutral",
                "kind_label": "Visao geral",
            },
            {
                "label": "Lotes sem callback",
                "value": metrics["sem_callback"],
                "kind": "neutral",
                "kind_label": "Visao geral",
            },
            {
                "label": "Lotes em processamento",
                "value": metrics["status"].get("processing", 0),
                "kind": "status",
                "kind_label": "Status",
            },
            {
                "label": "Lotes aguardando revisao",
                "value": metrics["status"].get("pending_review", 0),
                "kind": "status",
                "kind_label": "Status",
            },
            {
                "label": "Lotes concluidos",
                "value": metrics["status"].get("completed", 0),
                "kind": "status",
                "kind_label": "Status",
            },
            {
                "label": "Lotes com erro",
                "value": metrics["status"].get("error", 0),
                "kind": "status",
                "kind_label": "Status",
            },
            {
                "label": "Lotes aprovados",
                "value": metrics["decisoes"].get("APROVADO", 0),
                "kind": "decision",
                "kind_label": "Decisao",
            },
            {
                "label": "Lotes reprovados",
                "value": metrics["decisoes"].get("REPROVADO", 0),
                "kind": "decision",
                "kind_label": "Decisao",
            },
            {
                "label": "Lotes com pendencia",
                "value": metrics["decisoes"].get("PENDENCIA", 0),
                "kind": "decision",
                "kind_label": "Decisao",
            },
        ]

    def _build_callbacks_cards(self, metrics):
        return [
            {
                "label": "Total de callbacks",
                "value": metrics["total"],
                "kind": "neutral",
                "kind_label": "Visao geral",
            },
            {
                "label": "Callbacks recebidos",
                "value": metrics["status"].get("recebido", 0),
                "kind": "status",
                "kind_label": "Status",
            },
            {
                "label": "Callbacks enfileirados",
                "value": metrics["status"].get("enfileirado", 0),
                "kind": "status",
                "kind_label": "Status",
            },
            {
                "label": "Callbacks processando",
                "value": metrics["status"].get("processando", 0),
                "kind": "status",
                "kind_label": "Status",
            },
            {
                "label": "Callbacks processados",
                "value": metrics["status"].get("processado", 0),
                "kind": "status",
                "kind_label": "Status",
            },
            {
                "label": "Callbacks duplicados",
                "value": metrics["status"].get("duplicado", 0),
                "kind": "status",
                "kind_label": "Status",
            },
            {
                "label": "Callbacks com erro",
                "value": metrics["status"].get("erro", 0),
                "kind": "status",
                "kind_label": "Status",
            },
        ]

    def _build_documentos_cards(self, metrics):
        return [
            {
                "label": "Total de documentos",
                "value": metrics["total"],
                "kind": "neutral",
                "kind_label": "Visao geral",
            },
            {
                "label": "Documentos em processamento",
                "value": metrics["status"].get("processing", 0),
                "kind": "status",
                "kind_label": "Status",
            },
            {
                "label": "Documentos aguardando revisao",
                "value": metrics["status"].get("pending_review", 0),
                "kind": "status",
                "kind_label": "Status",
            },
            {
                "label": "Documentos concluidos",
                "value": metrics["status"].get("completed", 0),
                "kind": "status",
                "kind_label": "Status",
            },
            {
                "label": "Documentos com erro",
                "value": metrics["status"].get("error", 0),
                "kind": "status",
                "kind_label": "Status",
            },
            {
                "label": "Documentos aprovados",
                "value": metrics["decisoes"].get("APROVADO", 0),
                "kind": "decision",
                "kind_label": "Decisao",
            },
            {
                "label": "Documentos reprovados",
                "value": metrics["decisoes"].get("REPROVADO", 0),
                "kind": "decision",
                "kind_label": "Decisao",
            },
            {
                "label": "Documentos em pendencia",
                "value": metrics["decisoes"].get("PENDENCIA", 0),
                "kind": "decision",
                "kind_label": "Decisao",
            },
        ]
