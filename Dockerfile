FROM python:3.9-slim-buster

WORKDIR /src
COPY poetry.lock pyproject.toml /src/

RUN pip install poetry==1.1.11
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction

COPY . /src/
