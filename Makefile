# assume if python3 exists that python is 2.x
PYTHON := $(shell which python3 || which python)
PIP    := $(shell which pip3 || which pip)

all: tests

install:
	$(PIP) install -q -r requirements.txt

tests: install
	$(PYTHON) -m mypy --ignore-missing-imports slackbuild
	$(PYTHON) -m unittest discover -s tests

deploy: tests
	./deploy.sh
