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
	cd src
	python -Wall -m coverage run --branch --source='.' ./manage.py test; true
	coverage html -d ../htmlcov.new
	rm -rf ../htmlcov
	mv ../htmlcov.new ../htmlcov
	coverage report
	rm .coverage


shell:
	UID=$(UID) GID=$(GID) docker compose run --rm dev bash


build:
	docker compose build dev
