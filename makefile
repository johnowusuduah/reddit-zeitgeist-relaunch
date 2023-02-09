install:
	pip install -r requirements.txt

run:
	export FLASK_APP=app.py
	export FLASK_ENV=development
	flask run

test:
	python -m unittest discover

clean:
	rm -rf __pycache__/
	rm -f *.pyc
	rm -f *.log
	rm -f .coverage
	rm -rf htmlcov/