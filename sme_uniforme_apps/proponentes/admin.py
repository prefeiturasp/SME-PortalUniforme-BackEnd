from django.contrib import admin

from .models import (Proponente, OfertaDeUniforme, Loja, Anexo, ListaNegra)

from .services import cnpj_esta_bloqueado


class UniformesFornecidosInLine(admin.TabularInline):
    model = OfertaDeUniforme
    extra = 1  # Quantidade de linhas que serão exibidas.


class LojasInLine(admin.StackedInline):
    model = Loja
    extra = 1  # Quantidade de linhas que serão exibidas.


class AnexosInLine(admin.TabularInline):
    model = Anexo
    extra = 1  # Quantidade de linhas que serão exibidas.


@admin.register(Proponente)
class ProponenteAdmin(admin.ModelAdmin):
    def verifica_bloqueio_cnpj(self, request, queryset):
        for proponente in queryset.all():
            bloqueado = cnpj_esta_bloqueado(proponente.cnpj)
            if (bloqueado and proponente.status == Proponente.STATUS_INSCRITO) or (
                    not bloqueado and proponente.status == Proponente.STATUS_BLOQUEADO):
                proponente.save()

        self.message_user(request, "Bloqueios verificados.")

    def ultima_alteracao(self, obj):
        return obj.alterado_em.strftime("%d/%m/%Y %H:%M:%S")

    ultima_alteracao.admin_order_field = 'alterado_em'
    ultima_alteracao.short_description = 'Última alteração'

    verifica_bloqueio_cnpj.short_description = 'Verifica bloqueio de CNPJs'

    actions = ['verifica_bloqueio_cnpj']
    list_display = ('protocolo', 'cnpj', 'razao_social', 'responsavel', 'telefone', 'email', 'ultima_alteracao',
                    'status')
    ordering = ('-alterado_em',)
    search_fields = ('uuid', 'cnpj', 'razao_social', 'responsavel')
    list_filter = ('status',)
    inlines = [UniformesFornecidosInLine, LojasInLine, AnexosInLine]


@admin.register(OfertaDeUniforme)
class OfertaDeUniformeAdmin(admin.ModelAdmin):
    @staticmethod
    def protocolo(oferta):
        return oferta.proponente.protocolo

    list_display = ('protocolo', 'proponente', 'uniforme', 'preco')
    ordering = ('proponente',)
    search_fields = ('proponente__uuid', 'uniforme__nome',)
    list_filter = ('uniforme',)


@admin.register(ListaNegra)
class ListaNegraAdmin(admin.ModelAdmin):
    list_display = ('cnpj', 'razao_social')
    ordering = ('razao_social',)
    search_fields = ('cnpj', 'razao_social')
