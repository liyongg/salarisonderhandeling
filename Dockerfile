FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.7.12 /uv /uvx /bin/

ENV PYTHONBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN set -ex \
    && addgroup --system --gid 1010 app-users \
    && adduser --system --uid 1010 --gid 1010 --no-create-home user \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY app.py .
COPY ./utils ./utils

ENV PATH="/app/.venv/bin:$PATH"

RUN uv sync --locked

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py"]
