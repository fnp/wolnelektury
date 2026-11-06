.PHONY: deploy test up down build shell logs restart


UID := $(shell id -u)
GID := $(shell id -g)


deploy: src/wolnelektury/localsettings.py
	pip install -r requirements/requirements.txt
	src/manage.py migrate --noinput
	src/manage.py update_counters
	src/manage.py collectstatic --noinput


TEST_COMPOSE := docker compose -f docker-compose.test.yml

test:
	mkdir -p htmlcov
	UID=$(UID) GID=$(GID) $(TEST_COMPOSE) run --rm --build test sh -c '\
	  python -Wall -m coverage run --branch --source=. ./manage.py test $(ARGS); s=$$?; \
	  coverage report --skip-covered; coverage html -d /app/htmlcov; exit $$s'; \
	status=$$?; $(TEST_COMPOSE) down; exit $$status


up:
	UID=$(UID) GID=$(GID) docker compose up --build -d

down:
	docker compose down

build:
	UID=$(UID) GID=$(GID) docker compose build

shell:
	UID=$(UID) GID=$(GID) docker compose exec web bash

logs:
	docker compose logs -f

restart:
	docker compose restart
