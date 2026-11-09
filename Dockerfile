# Wolne Lektury images.
#
# Stages marked with ##### are build targets:
#   deps      dev image (docker-compose.yml, code mounted)
#   test      docker-compose.test.yml
#   prod      production app image (default, last stage)
#   nginx     production nginx with static files
#   postgres  Postgres with Polish dictionary
# Stages marked with ===== are intermediate.


# Global build arguments. Stages using UID/GID must redeclare them
# (bare `ARG UID`) to bring them into scope; the defaults are set here.

ARG PYTHON_IMAGE=python:3.10-trixie
ARG UID=8100
ARG GID=8100


##########
#  deps  #############################################################
#
#  Base system and requirements.
#  Used directly as the dev image, with code mounted.
#
FROM ${PYTHON_IMAGE} AS deps

ARG UID
ARG GID

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

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install \
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


#=======#
#  app  #=============================================================
#
#  Code and production requirements. Not production yet: needs
#  staticfiles.json manifest from static-builder.
#
FROM deps AS app

USER root

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install gunicorn

USER app

COPY src /app/src


#==================#
#  static-builder  #==================================================
#
#  Static files are collected here. Statics are then copied into
#  the nginx image, and staticfiles.json manifest is copied back
#  into the test and prod images.
#
FROM app AS static-builder

RUN python manage.py collectstatic --noinput


###########
#  nginx  ############################################################
#
#  Static files for production nginx. Config is mounted.
#
FROM nginx:alpine AS nginx

ARG UID
ARG GID

# COPY nginx.conf conf.d/...

RUN addgroup -g $GID app && addgroup nginx app
COPY --from=static-builder /app/var/static /app/var/static


#===============#
#  polish-dict  #=====================================================
#
#  Polish hunspell dictionary without diacritics, to allow
#  full text search without diacritics.
#
FROM ${PYTHON_IMAGE} AS polish-dict

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


##############
#  postgres  #########################################################
#
#  Postgres with the dictionary from polish-dict.
#
FROM postgres:18 AS postgres

COPY --from=polish-dict /out/ /tmp/polish-dict/
RUN mv /tmp/polish-dict/* "/usr/share/postgresql/$PG_MAJOR/tsearch_data/" \
 && rmdir /tmp/polish-dict

COPY scripts/postgres-polish.sql /docker-entrypoint-initdb.d/10-postgres-polish.sql


##########
#  test  #############################################################
#
#  Production image plus test requirements. Defined before `prod`,
#  so that `prod` stays the default (last) stage.
#
FROM app AS test

USER root
COPY requirements/requirements-test.txt /tmp/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /tmp/requirements-test.txt
USER app
RUN mkdir -p /app/var/counters
COPY --from=static-builder /app/var/static/staticfiles.json /app/var/static/staticfiles.json
CMD ["./manage.py", "test"]


##########
#  prod  #############################################################
#
#  Production image: app + staticfiles.json manifest.
#
FROM app AS prod

COPY --from=static-builder /app/var/static/staticfiles.json /app/var/static/staticfiles.json
