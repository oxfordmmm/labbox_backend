init:
	pip install -e .[dev]
create-env:
	python3 -m venv .env
venv:
	source .env/bin/activate
test:
	pytest src/app