from django.contrib import admin

from .models import (Uniforme, )


@admin.register(Uniforme)
class UniformeAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    ordering = ('nome',)
    search_fields = ('nome',)
