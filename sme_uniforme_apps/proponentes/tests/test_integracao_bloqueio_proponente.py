import pytest

from model_bakery import baker

from ..models import Proponente, ListaNegra


pytestmark = pytest.mark.django_db


def test_nao_bloqueia_ao_cadastrar_proponente_com_cnpj_bloqueado(lista_negra, cnpj_bloqueado):
    # Ao criar um proponente cujo CNPJ está na lista negra o status deve ficar como EM_PROCESSO e não como BLOQUEADO
    novo_proponente = baker.make(
        'Proponente',
        cnpj=cnpj_bloqueado,
        razao_social='Teste Bloqueado',
        end_logradouro='Rua Bloqueio, 123 apt. 101 Centro',
        end_cidade='São Paulo',
        end_uf='SP',
        end_cep='99999-000',
        telefone='(99) 99999-8888',
        email='bloqueado@teste.com',
        responsavel='José Bloqueio da Silva',
    )

    assert novo_proponente.status == Proponente.STATUS_EM_PROCESSO


def test_bloqueia_ao_concluir_cadastro_de_proponente_com_cnpj_bloqueado(lista_negra, cnpj_bloqueado):
    # Ao concluir o cadastro de um proponente cujo CNPJ esteja na lista negra o seu status deve ficar como BLOQUEADO
    novo_proponente = baker.make(
        'Proponente',
        cnpj=cnpj_bloqueado,
        razao_social='Teste Bloqueado',
        end_logradouro='Rua Bloqueio, 123 apt. 101 Centro',
        end_cidade='São Paulo',
        end_uf='SP',
        end_cep='99999-000',
        telefone='(99) 99999-8888',
        email='bloqueado@teste.com',
        responsavel='José Bloqueio da Silva',
    )

    assert novo_proponente.status == Proponente.STATUS_EM_PROCESSO

    novo_proponente.status = Proponente.STATUS_INSCRITO
    novo_proponente.save()

    proponente = Proponente.objects.get(id=novo_proponente.id)
    assert proponente.status == Proponente.STATUS_BLOQUEADO


def test_desbloqueia_ao_atualizar_proponente_sem_cnpj_bloqueado(proponente_bloqueado, cnpj_bloqueado):
    assert proponente_bloqueado.status == Proponente.STATUS_BLOQUEADO
    ListaNegra.objects.get(cnpj=cnpj_bloqueado).delete()
    proponente_bloqueado.save()
    proponente = Proponente.objects.get(id=proponente_bloqueado.id)
    assert proponente.status == Proponente.STATUS_INSCRITO


