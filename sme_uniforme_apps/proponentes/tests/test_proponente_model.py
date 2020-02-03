import pytest

from django.contrib import admin

from ..admin import ProponenteAdmin
from ..models import Proponente

pytestmark = pytest.mark.django_db


def test_instance_model(proponente):
    model = proponente
    assert isinstance(model, Proponente)
    assert model.cnpj
    assert model.razao_social
    assert model.end_logradouro
    assert model.end_cidade
    assert model.end_uf
    assert model.end_cep
    assert model.telefone
    assert model.email
    assert model.responsavel
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.status


def test_srt_model(proponente):
    assert proponente.__str__() == 'Fulano - teste@teste.com - (99) 99999-9999'


def test_meta_modelo(proponente):
    assert proponente._meta.verbose_name == 'Proponente'
    assert proponente._meta.verbose_name_plural == 'Proponentes'


def test_admin():
    model_admin = ProponenteAdmin(Proponente, admin.site)
    # pylint: disable=W0212
    assert admin.site._registry[Proponente]
    assert model_admin.list_display == (
        'protocolo', 'cnpj', 'razao_social', 'responsavel', 'telefone', 'email', 'ultima_alteracao', 'status')
    assert model_admin.ordering == ('-alterado_em',)
    assert model_admin.search_fields == ('uuid', 'cnpj', 'razao_social', 'responsavel')


def test_protocolo(proponente):
    protocolo = proponente.uuid.urn[9:17].upper()
    assert proponente.protocolo == protocolo


def test_cnpj_ja_cadastrado_resultado_positivo(proponente):
    assert Proponente.cnpj_ja_cadastrado(proponente.cnpj)


def test_cnpj_ja_cadastrado_resultado_negativo(proponente):
    cnpj_nao_cadastrado = '73.110.385/0001-13'
    assert not Proponente.cnpj_ja_cadastrado(cnpj_nao_cadastrado)


def test_cnpj_valido_resultado_positivo():
    cnpj_valido = '73.110.385/0001-13'
    assert Proponente.cnpj_valido(cnpj_valido)


def test_cnpj_valido_resultado_negativo():
    cnpj_invalido = '73.110.385/0001-00'
    assert not Proponente.cnpj_valido(cnpj_invalido)


def test_proponente_status_default_inscrito(proponente):
    assert proponente.status == Proponente.STATUS_INSCRITO
