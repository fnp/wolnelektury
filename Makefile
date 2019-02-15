.PHONY: deploy test


deploy: src/wolnelektury/localsettings.py
	git submodule update --init
	pip install -r requirements/requirements.txt
	src/manage.py migrate --noinput
	src/manage.py update_counters
	src/manage.py collectstatic --noinput


.ONESHELL:
test:
	cd src
	coverage run --branch --source='.' ./manage.py test; true
	rm -rf ../htmlcov
	coverage html -d ../htmlcov.new
	rm -rf ../htmlcov
	mv ../htmlcov.new ../htmlcov
	coverage report
	rm .coverage
