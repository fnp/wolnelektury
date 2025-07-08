.PHONY: deploy test shell


UID != id -u
GID != id -g


deploy: src/wolnelektury/localsettings.py
	pip install -r requirements/requirements.txt
	src/manage.py migrate --noinput
	src/manage.py update_counters
	src/manage.py collectstatic --noinput


.ONESHELL:
test:
	rm -r htmlcov &
	docker-compose run --rm dev sh -c '\
		python -Wall -m coverage run --branch --source='.' --data-file ../.coverage ./manage.py test; \
		coverage html --data-file ../.coverage -d htmlcov; \
		coverage report --data-file ../.coverage'
	mv -f src/htmlcov .


shell:
	UID=$(UID) GID=$(GID) docker-compose run --rm dev bash


build:
	UID=$(UID) GID=$(GID) docker-compose build dev --no-cache
