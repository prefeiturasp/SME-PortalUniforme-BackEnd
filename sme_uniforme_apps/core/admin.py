from django.contrib import admin

from .models import (Uniforme, )


@admin.register(Uniforme)
class UniformeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade', 'unidade', 'categoria')
    ordering = ('nome',)
    search_fields = ('nome',)
    list_filter = ('categoria', 'unidade')
