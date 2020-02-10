from django.contrib import admin

from .models import (Uniforme, LimiteCategoria)


@admin.register(Uniforme)
class UniformeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade', 'unidade', 'categoria')
    ordering = ('nome',)
    search_fields = ('nome',)
    list_filter = ('categoria', 'unidade')


@admin.register(LimiteCategoria)
class LimiteCategoriaAdmin(admin.ModelAdmin):
    list_display = ('categoria_uniforme', 'preco_maximo')
    ordering = ('categoria_uniforme',)
    list_filter = ('categoria_uniforme',)
