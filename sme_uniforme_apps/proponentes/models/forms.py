from django import forms

from sme_uniforme_apps.proponentes.models import Anexo


class AnexoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AnexoForm, self).__init__(*args, **kwargs)

        self.fields["tipo_documento"].required = True
        self.fields["arquivo"].label = "Documento do proponente"
        self.fields["arquivo"].help_text = "Envie apenas arquivos PDF."
        self.fields["tipo_documento"].widget.attrs["style"] = "width: 220px;"
        self.fields["tipo_documento"].widget.attrs[
            "onchange"
        ] = "this.title=this.options[this.selectedIndex] ? this.options[this.selectedIndex].text : '';"
        if self.instance and self.instance.tipo_documento_id:
            self.fields["tipo_documento"].widget.attrs[
                "title"
            ] = self.instance.tipo_documento.nome
        self.fields["status"].label = "Status Admin"
        self.fields["justificativa"].label = "Justificativa Admin"
        self.fields["status"].initial = self.instance.status or Anexo.STATUS_PENDENTE
        self.fields["status"].widget.attrs["style"] = "width: 140px;"
        self.fields["status"].widget.attrs["onchange"] = (
            "var inline=this.closest('.dynamic-anexos');"
            "var justificativa=inline&&inline.querySelector('textarea[id$=\"-justificativa\"]');"
            "var justificativaIA=inline&&inline.querySelector('.anexo-ia-justificativa');"
            "if((this.value==='REPROVADO'||this.value==='VENCIDO')&&justificativa&&!justificativa.value.trim()&&justificativaIA){"
            "justificativa.value=(justificativaIA.getAttribute('data-justificativa-ia')||'').trim();"
            "}"
        )
        self.fields["justificativa"].widget.attrs["rows"] = 3
        self.fields["justificativa"].widget.attrs["style"] = "width: 340px;"

    def clean(self):
        cleaned_data = super().clean()

        self.instance.status = cleaned_data.get("status")
        self.instance.justificativa = cleaned_data.get("justificativa")
        self.instance.copiar_justificativa_ia_para_admin()
        cleaned_data["justificativa"] = self.instance.justificativa

        return cleaned_data

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get("arquivo")

        if not arquivo or "arquivo" not in self.changed_data:
            return arquivo

        try:
            validate_upload_extension(
                arquivo,
                PDF_EXTENSIONS,
                "Envie o documento do proponente em PDF.",
            )
        except ValueError as exc:
            raise forms.ValidationError(str(exc))

        return arquivo

    class Meta:
        model = Anexo
        exclude = (
            "status_ia",
            "justificativa_ia",
            "ultima_alteracao_admin_por",
            "ultima_alteracao_admin_em",
        )


class LojaAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(LojaAdminForm, self).__init__(*args, **kwargs)

        self.fields["foto_fachada"].label = "Foto da fachada da loja"
        self.fields["foto_fachada"].help_text = (
            "Envie apenas arquivos JPG, JPEG ou PNG."
        )

    def clean_foto_fachada(self):
        foto_fachada = self.cleaned_data.get("foto_fachada")

        if not foto_fachada or "foto_fachada" not in self.changed_data:
            return foto_fachada

        try:
            validate_upload_extension(
                foto_fachada,
                IMAGE_EXTENSIONS,
                "Envie a foto da fachada em JPG, JPEG ou PNG.",
            )
        except ValueError as exc:
            raise forms.ValidationError(str(exc))

        return foto_fachada

    class Meta:
        model = Loja
        fields = "__all__"


class TipoDocumentoAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TipoDocumentoAdminForm, self).__init__(*args, **kwargs)

        self.fields["identificador"].required = True
        self.fields["identificador"].error_messages[
            "required"
        ] = "Informe o identificador alfanumérico."

    def clean_identificador(self):
        identificador = (self.cleaned_data.get("identificador") or "").strip() or None

        if not identificador:
            raise forms.ValidationError("Informe o identificador alfanumérico.")

        if (
            identificador
            and TipoDocumento.objects.exclude(pk=self.instance.pk)
            .filter(identificador=identificador)
            .exists()
        ):
            raise forms.ValidationError(
                "Já existe um tipo de documento com este identificador."
            )

        return identificador

    class Meta:
        model = TipoDocumento
        fields = "__all__"
