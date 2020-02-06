from django.contrib import admin

from .models import MeioDeRecebimento, Parametros, Uniforme


@admin.register(Uniforme)
class UniformeAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    ordering = ('nome',)
    search_fields = ('nome',)


@admin.register(MeioDeRecebimento)
class MeioDeRecebimentoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    ordering = ('nome',)
    search_fields = ('nome',)


@admin.register(Parametros)
class ParametrosAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        return not Parametros.objects.exists()

    list_display = ('uuid', 'edital', 'criado_em')
    readyonly_field = ('criado_em',)
    fields = ('edital', )
