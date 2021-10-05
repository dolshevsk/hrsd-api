# pull python image
FROM python:3.9-slim-buster

# set env variables to ease logging and stop creating .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set workdir inside container and copy poetry files
WORKDIR /src
COPY poetry.lock pyproject.toml /src/

# install dependencies
RUN pip install poetry==1.1.11
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction

# copy entire codebase
COPY . /src/
