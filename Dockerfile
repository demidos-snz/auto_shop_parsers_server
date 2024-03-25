ARG BASE_IMAGE=python:3.10-slim-bullseye
FROM ${BASE_IMAGE}

ENV PYTHONWARNINGS=ignore \
    USER_APP=bot \
    APP_DIR=/app

WORKDIR $APP_DIR
RUN useradd -ms /bin/bash $USER_APP

RUN apt-get update && apt-get upgrade -y

# 2024-3-25
# Chromium 120.0.6099.224 built on Debian 11.8, running on Debian 11.9
# ChromeDriver 120.0.6099.224 (3587067cafd6f5b1e567380acb485d96e623ef39-refs/branch-heads/6099@{#1761})
RUN apt-get install chromium -y
RUN apt-get install chromium-driver -y

COPY ./ ./

RUN pip install -r requirements.txt

RUN chown -R ${USER_APP}. ${APP_DIR}
RUN su ${USER_APP}
