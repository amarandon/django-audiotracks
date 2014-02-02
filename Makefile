test: lint
	tox

coverage:
	coverage run --source=audiotracks setup.py test
	coverage report

lint:
	flake8 audiotracks
