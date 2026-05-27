from django import forms

from sme_uniforme_apps.proponentes.models import Anexo, Loja, TipoDocumento
from sme_uniforme_apps.proponentes.upload_validation import (
    IMAGE_EXTENSIONS,
    PDF_EXTENSIONS,
    validate_upload_extension,
)


class AnexoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AnexoForm, self).__init__(*args, **kwargs)

        self.fields["tipo_documento"].required = True
        self.fields["arquivo"].label = "Documento do proponente"
        self.fields["arquivo"].help_text = "Envie apenas arquivos PDF."

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
        fields = '__all__'


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
