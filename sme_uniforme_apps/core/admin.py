from django.contrib import admin

from .models import LimiteCategoria, Parametros, Uniforme


@admin.register(Uniforme)
class UniformeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade', 'unidade', 'categoria')
    ordering = ('nome',)
    search_fields = ('nome',)
    list_filter = ('categoria', 'unidade')


@admin.register(Parametros)
class ParametrosAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        return not Parametros.objects.exists()

    list_display = ('id', 'edital', 'instrucao_normativa', 'alterado_em')
    readyonly_field = ('alterado_em',)
    fields = ('edital', 'instrucao_normativa')


@admin.register(LimiteCategoria)
class LimiteCategoriaAdmin(admin.ModelAdmin):
    list_display = ('categoria_uniforme', 'preco_maximo')
    ordering = ('categoria_uniforme',)
    list_filter = ('categoria_uniforme',)

