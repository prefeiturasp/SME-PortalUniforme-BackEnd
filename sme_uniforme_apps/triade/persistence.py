from django.utils import timezone


def _normalize_update_fields(update_fields):
    fields = list(update_fields or ())
    fields.append("alterado_em")
    return tuple(dict.fromkeys(fields))


def save_with_alterado_em(instance, update_fields):
    instance.alterado_em = timezone.now()
    instance.save(update_fields=_normalize_update_fields(update_fields))


def queryset_update_with_alterado_em(queryset, **kwargs):
    kwargs["alterado_em"] = timezone.now()
    return queryset.update(**kwargs)
