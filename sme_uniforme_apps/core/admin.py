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

admin.site.register(Parametros)
