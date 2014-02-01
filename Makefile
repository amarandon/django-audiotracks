test: lint
	python testing/runtests.py

coverage:
	coverage run --source=audiotracks testing/runtests.py
	coverage report

lint:
	flake8 audiotracks
