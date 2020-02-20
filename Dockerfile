#FROM python:3.6-jessie
FROM python:3.6-alpine3.8
ENV PYTHONUNBUFFERED 1
ADD . /code
WORKDIR /code

RUN apk update && apk add postgresql-dev tzdata && \
  cp /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime && \
  apk add --no-cache \
  --virtual=.build-dependencies \
  gcc \
  g++ \
  musl-dev \
  git \
  python3-dev \
  jpeg-dev \
  # Pillow
  zlib-dev \
  freetype-dev \
  lcms2-dev \
  openjpeg-dev \
  tiff-dev \
  tk-dev \
  tcl-dev \
  harfbuzz-dev \
  fribidi-dev && \
  python -m pip --no-cache install -U pip && \
  #    python -m pip --no-cache install Cython && \
  #    python -m pip --no-cache install numpy && \
  python -m pip --no-cache install -r requirements/production.txt && \
  apk del --purge .build-dependencies

CMD gunicorn config.wsgi:application --bind=0.0.0.0:8001 -w 8 && \
  celery -A config worker --loglevel=info --concurrency=3 -n worker1@%h

EXPOSE 8001
