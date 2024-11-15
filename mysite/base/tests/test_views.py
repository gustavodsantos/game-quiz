import pytest
from django.urls import reverse

from mysite.base.models import Aluno


@pytest.mark.django_db
def test_home_post_new_user(client):
    url = reverse('base:home')
    data = {'email': 'novo@teste.com', 'nome': 'Novo Usuário'}

    response = client.post(url, data)

    aluno = Aluno.objects.filter(email='novo@teste.com').first()
    assert aluno is not None
    assert response.status_code == 302
    assert response.url == '/perguntas/1'


@pytest.mark.django_db
def test_home_post_existing_user(client):
    aluno = Aluno.objects.create(email='existente@teste.com', nome='Usuário Existente')
    url = reverse('base:home')
    data = {'email': aluno.email}

    response = client.post(url, data)

    assert response.status_code == 302
    assert response.url == '/perguntas/1'
    assert client.session['aluno_id'] == aluno.id
