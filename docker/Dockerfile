# syntax=docker/dockerfile:1
# syntax directive is used to enable Docker BuildKit

ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim AS base

ARG PROJECT_DIR="/src"
ARG APP_USER="app"
ARG APP_GROUP="app"
ARG NEW_UID
ARG NEW_GID

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_CACHE_DIR=/tmp/poetry-cache \
    POETRY_VIRTUALENVS_CREATE=false

# Create a non-privileged user that the app will run under.
RUN groupadd --system ${APP_GROUP} --gid=${NEW_GID} && \
    adduser \
        --disabled-password \
        --gecos "" \
        --uid ${NEW_UID} \
        --gid ${NEW_GID} \
        ${APP_USER}

RUN apt update && \
    apt install -y \
        git \
        gnupg2 \
        make \
        postgresql-client-15 \
        postgresql-client-common

RUN pip3 install --upgrade pip && \
    pip3 install poetry --no-cache-dir

WORKDIR ${PROJECT_DIR}

FROM base AS builder

COPY ./pyproject.toml ./poetry.lock ./

RUN --mount=type=cache,target=${POETRY_CACHE_DIR} poetry install --no-root --no-interaction

FROM base AS final

COPY --from=builder /usr/local /usr/local
RUN chown -R ${APP_USER}:${APP_GROUP} /usr/local/lib/python3.11
ADD . /src

COPY ./docker/init-standalone.sh /usr/local/bin
COPY ./docker/init.sh /usr/local/bin

ARG standalone=false

RUN if [ "$standalone" = "true" ] ; then \
    ln -sf /usr/local/bin/init-standalone.sh /docker-entrypoint.sh; \
  else \
    ln -sf /usr/local/bin/init.sh /docker-entrypoint.sh ; \
  fi

USER ${APP_USER}

EXPOSE 8503:8503
WORKDIR ${PROJECT_DIR}

ENV PYTHONPATH=${PROJECT_DIR}

CMD ["/docker-entrypoint.sh", "metadata_db"]
