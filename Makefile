SHELL := /bin/bash
MIN_PYTHON_VERSION = 3.11.0
INSTALLED_PYTHON := $(shell python -V | grep -Po '(?<=Python)(.+)')
MIN_VERSION_MET := $(shell if awk "BEGIN {exit !($(INSTALLED_PYTHON) >= $(MIN_PYTHON_VERSION))}"; then echo true; else echo false; fi)
LOCAL_PYTHON_PATH = .Python/bin/python$(shell echo $(MIN_PYTHON_VERSION)|grep  -Po '[0-9]{1,2}.[0-9]{1,2}')
MINIMUM_COVERAGE = 80
WD = $(shell pwd)

define venv_run
	source .venv/bin/activate && $1
endef

all: init standards test

create-environment:
ifeq ($(MIN_VERSION_MET), true)
	python -m venv .venv
else
ifeq (,$(wildcard $(LOCAL_PYTHON_PATH)))
	mkdir -p .Python
	wget https://www.python.org/ftp/python/$(MIN_PYTHON_VERSION)/Python-$(MIN_PYTHON_VERSION).tgz -O Python-$(MIN_PYTHON_VERSION).tgz
	tar -xvzf Python-$(MIN_PYTHON_VERSION).tgz
	cd Python-$(MIN_PYTHON_VERSION) && ./configure --prefix $(WD)/.Python && make && make install
	rm Python-$(MIN_PYTHON_VERSION).tgz
	rm -R Python-$(MIN_PYTHON_VERSION)
endif
	$(LOCAL_PYTHON_PATH) -m venv .venv
endif

install-dev:
	$(call venv_run, pip install --upgrade pip)
	$(call venv_run, pip install .[dev])
	$(call venv_run, pip install -e .)
install:
	$(call venv_run, pip install --upgrade pip)
	$(call venv_run, pip install .)

dev-init: create-environment install-dev
init: create-environment install

# testing / standards
pytest:
	$(call venv_run, pytest -v)
safety:
	$(call venv_run, safety check)
bandit:
	$(call venv_run, bandit -r src/)
flake:
	$(call venv_run, flake8 src/)
coverage:
	$(call venv_run, coverage run --omit .venv -m pytest && coverage report -m --fail-under=$(MINIMUM_COVERAGE))
autopep8:
	$(call venv_run, autopep8  --in-place --recursive src/*)
pkg_size:
	test/package_size.sh
test: pytest coverage pkg_size
standards: autopep8 bandit flake safety

clean:
	find -name *egg-info -exec rm -R {} \;
	rm -R build .pytest_cache

build: init standards test install