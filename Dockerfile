FROM python:3.9-trixie AS base

ARG UID=1000
ARG GID=1000

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

FROM base AS dev

#RUN pip install --no-cache-dir coverage


FROM base AS prod

RUN pip install --no-cache-dir gunicorn

COPY src /app/src
