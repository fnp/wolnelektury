FROM python:3.8 AS base

ARG UID=1000
ARG GID=1000

RUN     apt-get update && apt-get install -y \
	git \
	calibre \
	texlive-xetex texlive-lang-polish \
	libespeak-dev

COPY requirements/requirements.txt requirements.txt

# numpy -> aeneas
RUN pip install numpy
RUN pip install aeneas

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir \
    psycopg2-binary \
    django-debug-toolbar==3.2.2 \
    python-bidi

RUN addgroup --gid $GID app
RUN adduser --gid $GID --home /app --uid $UID app

RUN     apt-get install -y \
	texlive-extra-utils \
	texlive-lang-greek \
	texlive-lang-other \
	texlive-luatex \
	texlive-fonts-extra \
	texlive-fonts-extra-links \
	fonts-noto-core fonts-noto-extra


USER app

# fonts
RUN cp -a /usr/local/lib/python*/site-packages/librarian/fonts /app/.fonts
RUN fc-cache

WORKDIR /app/src


FROM base AS dev

RUN pip install --no-cache-dir coverage
USER app


FROM base AS prod

RUN pip install --no-cache-dir gunicorn

USER app
COPY src /app/src
