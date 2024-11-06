FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN set -ex \
    && addgroup --system --gid 1010 app-users \
    && adduser --system --uid 1010 --gid 1010 --no-create-home user \
    && apt-get update \
    && apt-get upgrade -y \
    && pip install -r requirements.txt \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY app.py .

COPY utils .

USER user

EXPOSE 8501

FROM python:3.10-slim

ENV PYTHONBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .

RUN set -ex \
    && addgroup --system --gid 1010 app-users \
    && adduser --system --uid 1010 --gid 1010 --no-create-home user \
    && apt-get update \
    && apt-get upgrade -y \
    && pip install -r requirements.txt \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY app.py .
COPY ./utils ./utils

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py"]
