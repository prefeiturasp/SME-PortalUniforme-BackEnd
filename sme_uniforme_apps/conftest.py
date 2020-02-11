import pytest
from model_bakery import baker

from .core.models import Uniforme


@pytest.fixture
def fake_user(client, django_user_model):
    password = 'teste'
    email = 'fake@user.com'
    user = django_user_model.objects.create_user(email=email, password=password, validado=True, )
    client.login(email=email, password=password)
    return user


@pytest.fixture
def authenticated_client(client, django_user_model):
    email = 'teste@teste.com'
    password = '@987654321'
    u = django_user_model.objects.create_user(email=email, password=password)
    u.validado = True
    u.save()
    client.login(email=email, password=password)
    return client


@pytest.fixture
def uniforme_calca():
    return baker.make(
        'Uniforme',
        nome='Calça',
        categoria=Uniforme.CATEGORIA_MALHARIA,
        unidade=Uniforme.UNIDADE_UNIDADE,
        quantidade=1
    )


@pytest.fixture
def uniforme_camisa():
    return baker.make(
        'Uniforme',
        nome='Camisa',
        categoria=Uniforme.CATEGORIA_MALHARIA,
        unidade=Uniforme.UNIDADE_UNIDADE,
        quantidade=1
    )


@pytest.fixture
def uniforme_meias():
    return baker.make(
        'Uniforme',
        nome='Meias',
        categoria=Uniforme.CATEGORIA_MALHARIA,
        unidade=Uniforme.UNIDADE_PAR,
        quantidade=5
    )


@pytest.fixture
def uniforme_tenis():
    return baker.make(
        'Uniforme',
        nome='Tenis',
        categoria=Uniforme.CATEGORIA_CALCADO,
        unidade=Uniforme.UNIDADE_PAR,
        quantidade=1
    )
