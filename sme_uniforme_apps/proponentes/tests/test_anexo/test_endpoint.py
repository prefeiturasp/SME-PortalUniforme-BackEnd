import json

import pytest
from rest_framework import status

from ...models.anexo import Anexo

pytestmark = pytest.mark.django_db


@pytest.fixture
def create(client, payload_anexo):
    return client.post('/anexos/', data=json.dumps(payload_anexo), content_type='application/json')

@pytest.fixture
def delete(client, create):
    result = json.loads(create.content)
    return client.delete('/anexos/{}/'.format(result['uuid']), follow=True)

def test_anexo_api_create_status_code(create):
    response = create
    assert response.status_code == status.HTTP_201_CREATED

def test_anexo_api_create_model_exists(create):
    result = json.loads(create.content)    
    assert Anexo.objects.filter(uuid=result['uuid']).exists()

def test_anexo_api_delete_model(delete):
    assert delete.status_code == status.HTTP_204_NO_CONTENT

def test_anexo_api_create_model_not_exists(client, delete):
    assert not Anexo.objects.exists()


def test_anexo_form_configura_label_e_help_text():
    form = AnexoForm()

    assert form.fields["arquivo"].label == "Documento do proponente"
    assert form.fields["arquivo"].help_text == "Envie apenas arquivos PDF."
    assert form.fields["status"].label == "Status Admin"
    assert form.fields["justificativa"].label == "Justificativa Admin"
    assert form.fields["status"].initial == Anexo.STATUS_PENDENTE
    assert form.fields["tipo_documento"].widget.attrs["style"] == "width: 220px;"
    assert form.fields["justificativa"].widget.attrs["style"] == "width: 340px;"
    assert "status_ia" not in form.fields
    assert "justificativa_ia" not in form.fields


def test_anexo_form_define_title_do_tipo_documento_quando_instancia_tem_valor(
    tipo_documento,
):
    tipo_documento.nome = "Documento muito grande para validar o title do select"
    form = AnexoForm(instance=Anexo(tipo_documento=tipo_documento))

    assert form.fields["tipo_documento"].widget.attrs["title"] == tipo_documento.nome


def test_anexo_create_serializer_configura_label_e_help_text():
    serializer = AnexoCreateSerializer()

    assert serializer.fields["arquivo"].label == "Documento do proponente"
    assert serializer.fields["arquivo"].help_text == "Envie apenas arquivos PDF."


def test_anexo_form_aceita_pdf(tipo_documento):
    form = AnexoForm(
        data={
            "tipo_documento": tipo_documento.id,
            "status": Anexo.STATUS_PENDENTE,
        },
        files={"arquivo": create_uploaded_file("anexo.pdf")},
    )

    assert form.is_valid(), form.errors


@pytest.mark.parametrize("status_admin", [Anexo.STATUS_REPROVADO, Anexo.STATUS_VENCIDO])
def test_anexo_form_copia_justificativa_ia_para_admin(tipo_documento, status_admin):
    anexo = Anexo(
        tipo_documento=tipo_documento,
        status_ia=Anexo.STATUS_REPROVADO,
        justificativa_ia="Documento divergente segundo a IA.",
    )
    form = AnexoForm(
        data={
            "tipo_documento": tipo_documento.id,
            "status": status_admin,
            "justificativa": "",
        },
        files={"arquivo": create_uploaded_file("anexo.pdf")},
        instance=anexo,
    )

    assert form.is_valid(), form.errors
    assert form.cleaned_data["justificativa"] == "Documento divergente segundo a IA."


@pytest.mark.parametrize("file_name", ["anexo.jpg", "anexo.png", "anexo.txt"])
def test_anexo_form_rejeita_arquivo_nao_pdf(tipo_documento, file_name):
    form = AnexoForm(
        data={
            "tipo_documento": tipo_documento.id,
            "status": Anexo.STATUS_PENDENTE,
        },
        files={"arquivo": create_uploaded_file(file_name)},
    )

    assert not form.is_valid()
    assert form.errors["arquivo"] == ["Envie o documento do proponente em PDF."]


@pytest.mark.parametrize(
    "arquivo_invalido", [ARQUIVO_JPG_BASE64, ARQUIVO_PNG_BASE64, ARQUIVO_TXT_BASE64]
)
def test_anexo_api_rejeita_arquivo_nao_pdf(client, payload_anexo, arquivo_invalido):
    payload_anexo["arquivo"] = arquivo_invalido

    response = client.post(
        "/anexos/", data=json.dumps(payload_anexo), content_type="application/json"
    )
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result["arquivo"] == ["Envie o documento do proponente em PDF."]
