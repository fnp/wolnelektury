FROM python:3.8 AS base

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

RUN     apt-get install -y \
	texlive-extra-utils \
	texlive-lang-greek \
	texlive-lang-other \
	texlive-luatex \
	texlive-fonts-extra \
	texlive-fonts-extra-links \
	fonts-noto-core fonts-noto-extra


# fonts
RUN cp -a /usr/local/lib/python*/site-packages/librarian/fonts /usr/local/share/fonts
RUN fc-cache

WORKDIR /app/src


FROM base AS dev

#RUN pip install --no-cache-dir coverage


FROM base AS prod

RUN pip install --no-cache-dir gunicorn

COPY src /app/src
