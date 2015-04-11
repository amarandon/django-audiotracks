test: lint
	tox

coverage:
	coverage run --source=audiotracks setup.py test
	coverage report -m

lint:
	flake8 audiotracks
