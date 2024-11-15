# game-quiz

Projeto "game-quiz" é um jogo de perguntas e respostas, com ranking de pontuação

## Pastas do projeto

Na pasta raiz se encontram:

1. A pasta docker. Nela se encontram os arquivos de conteinerização usando docker.

2. A pasta config. Nela se encontra um arquivo de configuração para o projeto.

3. Nessa pasta se encontram os arquivos do projeto Django.

Será usado o Poetry como gestor de pacotes.

Por isso, para instalar o projeto com as dependência de desenvolvimento rode:

```bash
poetry install --with dev
```

Para rodar seu servidor Django ative o ambiente virtual:

```bash
poetry shell
```

Então rode

```bash
python manage.py runserver
```

## Padrão de código

Esse projeto usa o Ruff como linter, e o Taskipy como executor de tarefas:

para verificar seu código em busca de problemas de estilo e possíveis erros:
```bash
task lint
```

para formatar automaticamente seu código de acordo com as regras do Ruff:
```bash
task format
```

para executar seus testes:
```bash
task test
```

## Configurações de instância

Para ler configurações de instância esse projeto usa a lib [python decouple](https://pypi.org/project/python-decouple/).
Ela é importada no arquivo settings.py


