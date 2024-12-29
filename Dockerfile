#Usar a imagem base do Python
FROM python:3.12

# Instalar dependências de sistema necessárias
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

# Instalar o Poetry
RUN pip install poetry

#Copiar os arquivos pyproject.toml e poetry.lock da raiz do projeto para o contêiner
COPY pyproject.toml ./
COPY poetry.lock ./

# Instalar as dependências sem o pacote raiz
RUN poetry install --no-root --without dev

# Copiar o restante do código do projeto para o contêiner
COPY . ./

# Expor a porta que o Django vai usar
EXPOSE 8000

# Comando para rodar o Django
CMD ["gunicorn", "--bind", ":8000", "--workers", "1", "--reload", "mysite.wsgi"]