import pytest

pytestmark = pytest.mark.django_db


def test_docs_exibem_endpoint_do_callback_triade(client):
    response = client.get("/docs/")

    assert response.status_code == 200
    conteudo = response.content.decode("utf-8")
    assert "triade" in conteudo
    assert "callback" in conteudo
    assert "X-TRIADE-Signature" in conteudo
