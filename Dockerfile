# Base system and requirements.

FROM python:3.9-trixie AS base

ARG UID=8100
ARG GID=8100

RUN     apt-get update && apt-get install -y \
	git \
	calibre \
	texlive-xetex texlive-lang-polish \
	texlive-extra-utils \
	texlive-lang-greek \
	texlive-lang-other \
	texlive-luatex \
	texlive-fonts-extra \
	texlive-fonts-extra-links \
	fonts-noto-core fonts-noto-extra


COPY requirements/requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir \
    psycopg2-binary \
    django-debug-toolbar==3.2.2

RUN addgroup --gid $GID app && \
    adduser --gid $GID --home /app --uid $UID app


# fonts
RUN cp -a /usr/local/lib/python*/site-packages/librarian/fonts /usr/share/fonts
RUN fc-cache

USER app

WORKDIR /app/src

RUN mkdir /app/.ipython



# dev
# Assumes code will be mounted.

FROM base AS dev

#RUN pip install --no-cache-dir coverage


# prod-base
# Installs code and production requirements.

FROM base AS prod-base

USER root

RUN pip install --no-cache-dir gunicorn

USER app

COPY src /app/src


# static-builder
# Static files are collected here. Statics are then copied into an Nginx image,
# and staticfiles.json manifest file is copied back into production image.

FROM prod-base AS static-builder

RUN python manage.py collectstatic --noinput


# nginx
# Contains static files and nginx config.

FROM nginx:alpine AS nginx

ARG UID=8100
ARG GID=8100

# COPY nginx.conf conf.d/...

RUN addgroup -g $GID app && addgroup nginx app
COPY --from=static-builder /app/var/static /app/var/static




# Postgres with Polish hunspell dictionary withoud diacritics
# to allow full text search without diacritics.

# --- Stage 1: prepare dictionary files ---
FROM python:3.13-slim-trixie AS polish-dict

RUN apt-get update \
 && apt-get install -y --no-install-recommends hunspell-pl \
 && rm -rf /var/lib/apt/lists/*

COPY scripts/fold_hunspell.py /usr/local/bin/fold_hunspell.py

RUN set -eu; \
    mkdir /out; cd /tmp; \
    enc="$(sed -n 's/^SET[[:space:]]*//p' /usr/share/hunspell/pl_PL.aff | tr -d '\r')"; \
    iconv -f "${enc:-UTF-8}" -t UTF-8 /usr/share/hunspell/pl_PL.dic > pl.dict; \
    iconv -f "${enc:-UTF-8}" -t UTF-8 /usr/share/hunspell/pl_PL.aff > pl.affix; \
    python3 /usr/local/bin/fold_hunspell.py pl.dict pl.affix \
        /out/polish.dict /out/polish.affix; \
    dpkg-query -W -f='hunspell-pl ${Version}\n' hunspell-pl > /out/polish.version

# --- Stage 2: actual Postgres image with the dictionary ---
FROM postgres:18 AS postgres

COPY --from=polish-dict /out/ /tmp/polish-dict/
RUN mv /tmp/polish-dict/* "/usr/share/postgresql/$PG_MAJOR/tsearch_data/" \
 && rmdir /tmp/polish-dict

COPY scripts/postgres-polish.sql /docker-entrypoint-initdb.d/10-postgres-polish.sql



# prod
# That's the production image with staticfiles.json manifest file added.

FROM prod-base AS prod

COPY --from=static-builder /app/var/static/staticfiles.json /app/var/static/staticfiles.json
