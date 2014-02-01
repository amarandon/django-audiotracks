test:
	python testing/runtests.py

coverage:
	coverage run --source=audiotracks testing/runtests.py
	coverage report
