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
