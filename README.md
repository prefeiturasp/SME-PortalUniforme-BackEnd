# SME-PortalUniforme-BackEnd
========

Portal do programa de captação de fornecedores de uniforme escolar da Secretaria de Educação da cidade de São Paulo.

License: MIT

Versão: 1.1.0


## Release Notes

### 1.1.0 - 10/03/2020 - Sprint 3
* Status "Em processo" passa para "Pré-cadastro"
* São criados os status "em análise", "pendente", "reprovado", "aprovado" e "credenciado"

### 1.0.0 - 02/03/2020 - Sprint 2
* Reformulação do processo de inscrição de fornecedores. Cadastro dividido em duas fases: Pré-cadastro e Cadastro


### 0.1.0 - 31/01/2020 - Sprint 1
* Portal do programa 
* Inscrição de proponentes a fornecedor de uniformes


### Para desenvolver

1.  Clone o repositório.
2.  Crie um Virtualenv com Python 3.6
3.  Ative o Virtualenv.
4.  Instale as dependências.
5.  Configure a instância com o .env
6.  Execute os testes.
7.  Faça um Pull Request com o seu desenvolvimento

```console
git clone https://github.com/prefeiturasp/SME-PortalUniforme-BackEnd.git back
cd back
python -m venv .venv
source .venv/bin/activate
pip install -r requirements\local.txt
cp env_sample .env
pytest
```

### Tema do Admin
Para instalar o tema do Admin

```console
python manage.py loaddata admin_interface_theme_uswds.json
```

### Filas Celery
**Subir o Celery Worker**
```console
celery  -A config worker --loglevel=info
```

**Subir o Celery Beat**
```console
celery  -A config beat --loglevel=info
```

**Monitorar os processos no celery**
```console
flower -A config --port=5555
```

**Limpar os processos no celery**
```console
celery  -A config purge
```
