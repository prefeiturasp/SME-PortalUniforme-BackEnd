import pytest


@pytest.fixture
def fake_user(client, django_user_model):
    password = 'teste'
    email = 'teste@teste.com'
    user = django_user_model.objects.create_user(email=email, password=password, validado=True,)
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
