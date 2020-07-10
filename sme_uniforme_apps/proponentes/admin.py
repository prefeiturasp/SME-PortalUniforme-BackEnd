from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (Proponente, OfertaDeUniforme, Loja, Anexo, ListaNegra, TipoDocumento)
from .services import cnpj_esta_bloqueado, muda_status_de_proponentes, atualiza_coordenadas


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

    verifica_bloqueio_cnpj.short_description = 'Verifica bloqueio de CNPJs'

    def muda_status_para_inscrito(self, request, queryset):
        muda_status_de_proponentes(queryset, Proponente.STATUS_INSCRITO)
        self.message_user(request, f'Status alterados para {Proponente.STATUS_NOMES[Proponente.STATUS_INSCRITO]}.')

    muda_status_para_inscrito.short_description = f'Status ==> {Proponente.STATUS_NOMES[Proponente.STATUS_INSCRITO]}.'

    def muda_status_para_em_processo(self, request, queryset):
        muda_status_de_proponentes(queryset, Proponente.STATUS_EM_PROCESSO)
        self.message_user(request, f'Status alterados para {Proponente.STATUS_NOMES[Proponente.STATUS_EM_PROCESSO]}.')

    muda_status_para_em_processo.short_description = \
        f'Status ==> {Proponente.STATUS_NOMES[Proponente.STATUS_EM_PROCESSO]}.'

    def muda_status_para_aprovado(self, request, queryset):
        muda_status_de_proponentes(queryset, Proponente.STATUS_APROVADO)
        self.message_user(request, f'Status alterados para {Proponente.STATUS_NOMES[Proponente.STATUS_APROVADO]}.')

    muda_status_para_aprovado.short_description = f'Status ==> {Proponente.STATUS_NOMES[Proponente.STATUS_APROVADO]}.'

    def muda_status_para_reprovado(self, request, queryset):
        muda_status_de_proponentes(queryset, Proponente.STATUS_REPROVADO)
        self.message_user(request, f'Status alterados para {Proponente.STATUS_NOMES[Proponente.STATUS_REPROVADO]}.')

    muda_status_para_reprovado.short_description = f'Status ==> {Proponente.STATUS_NOMES[Proponente.STATUS_REPROVADO]}.'
    
    def muda_status_para_pendente(self, request, queryset):
        muda_status_de_proponentes(queryset, Proponente.STATUS_PENDENTE)
        self.message_user(request, f'Status alterados para {Proponente.STATUS_NOMES[Proponente.STATUS_PENDENTE]}.')

    muda_status_para_pendente.short_description = f'Status ==> {Proponente.STATUS_NOMES[Proponente.STATUS_PENDENTE]}.'

    def muda_status_para_em_analise(self, request, queryset):
        muda_status_de_proponentes(queryset, Proponente.STATUS_EM_ANALISE)
        self.message_user(request, f'Status alterados para {Proponente.STATUS_NOMES[Proponente.STATUS_EM_ANALISE]}.')

    muda_status_para_em_analise.short_description = f'Status ==> {Proponente.STATUS_NOMES[Proponente.STATUS_EM_ANALISE]}.'

    def muda_status_para_credenciado(self, request, queryset):
        muda_status_de_proponentes(queryset, Proponente.STATUS_CREDENCIADO)
        self.message_user(request, f'Status alterados para {Proponente.STATUS_NOMES[Proponente.STATUS_CREDENCIADO]}.')

    muda_status_para_credenciado.short_description = f'Status ==> {Proponente.STATUS_NOMES[Proponente.STATUS_CREDENCIADO]}.'

    def atualiza_coordenadas_action(self, request, queryset):
        atualiza_coordenadas(queryset)
        self.message_user(request, f'Coordenadas das lojas físicas para proponentes CREDENCIADOS foram atualizados.')

    atualiza_coordenadas_action.short_description = f'Atualiza coordenadas.'


    def ultima_alteracao(self, obj):
        return obj.alterado_em.strftime("%d/%m/%Y %H:%M:%S")

    ultima_alteracao.admin_order_field = 'alterado_em'
    ultima_alteracao.short_description = 'Última alteração'

    actions = [
        'verifica_bloqueio_cnpj',
        'muda_status_para_aprovado',
        'muda_status_para_reprovado',
        'muda_status_para_pendente',
        'muda_status_para_em_analise',
        'muda_status_para_inscrito', 
        'muda_status_para_em_processo',
        'muda_status_para_credenciado',
        'atualiza_coordenadas_action']
    list_display = ('protocolo', 'cnpj', 'razao_social', 'responsavel', 'telefone', 'email', 'ultima_alteracao',
                    'status')
    ordering = ('-alterado_em',)
    search_fields = ('uuid', 'cnpj', 'razao_social', 'responsavel')
    list_filter = ('status',)
    inlines = [UniformesFornecidosInLine, LojasInLine, AnexosInLine]
    readonly_fields = ('uuid', 'id', 'cnpj', 'razao_social')


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


@admin.register(Loja)
class LojaAdmin(admin.ModelAdmin):
    @staticmethod
    def protocolo(loja):
        return loja.proponente.protocolo

    @staticmethod
    @mark_safe
    def fachada(loja):
        foto = loja.foto_fachada
        return f'<img src="{foto.url}" width="64px"/>' if foto else ""

    fachada.allow_tags = True

    list_display = ('protocolo', 'nome_fantasia', 'fachada', 'cep', 'endereco', 'numero', 'complemento', 'bairro')
    ordering = ('nome_fantasia',)
    search_fields = ('proponente__uuid', 'nome_fantasia',)
    list_filter = ('bairro',)


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    def inverte_visivel(self, request, queryset):
        for tipo_documento in queryset.all():
            tipo_documento.visivel = not tipo_documento.visivel
            tipo_documento.save()

        self.message_user(request, "Parâmetro 'visível' atualizado.")

    inverte_visivel.short_description = "Inverter o parâmetro 'visível' "

    def inverte_obrigatorio(self, request, queryset):
        for tipo_documento in queryset.all():
            tipo_documento.obrigatorio = not tipo_documento.obrigatorio
            tipo_documento.save()

        self.message_user(request, "Parâmetro 'obrigatório' atualizado.")

    inverte_obrigatorio.short_description = "Inverter o parâmetro 'obrigatório' "

    list_display = ('nome', 'obrigatorio', 'visivel')
    ordering = ('nome',)
    search_fields = ('nome',)
    list_filter = ('obrigatorio', 'visivel')
    actions = ['inverte_visivel', 'inverte_obrigatorio']
