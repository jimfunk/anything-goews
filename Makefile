SHELL := /bin/bash

PYTHON = python3

VIRTUALENV_DIR = venv
VIRTUALENV = $(VIRTUALENV_DIR)/.stamp
SANIC = $(VIRTUALENV_DIR)/bin/sanic

NPM = npm

FRONTEND_DIR = frontend
FRONTEND_ENV_DIR = $(FRONTEND_DIR)/node_modules
FRONTEND_ENV = $(FRONTEND_ENV_DIR)/.stamp
FRONTEND_DIST = $(FRONTEND_DIR)/dist/index.html
FRONTEND_SOURCES = \
	$(FRONTEND_DIR)/index.html \
	$(FRONTEND_DIR)/svelte.config.js \
	$(FRONTEND_DIR)/vite.config.js \
	$(FRONTEND_DIR)/package.json \
	$(shell find $(FRONTEND_DIR)/src -type f 2>/dev/null)

all: server
.PHONY: all

#
# Virtualenv
#
$(VIRTUALENV): requirements.txt
	$(PYTHON) -m venv $(VIRTUALENV_DIR)
	$(VIRTUALENV_DIR)/bin/pip install -r requirements.txt
	touch $(VIRTUALENV)

virtualenv: $(VIRTUALENV)
.PHONY: virtualenv

#
# Frontend
#
$(FRONTEND_ENV): $(FRONTEND_DIR)/package.json
	cd $(FRONTEND_DIR); $(NPM) install
	touch $(FRONTEND_ENV)

$(FRONTEND_DIST): $(FRONTEND_ENV) $(FRONTEND_SOURCES)
	cd $(FRONTEND_DIR); $(NPM) run build

frontend: $(FRONTEND_DIST)
.PHONY: frontend

#
# Server
#
server: virtualenv frontend
.PHONY: server

serve: virtualenv frontend
	$(SANIC) server.server &
	cd $(FRONTEND_DIR); npm run dev
.PHONY: serve

#
# Tests
#
PYTEST = $(VIRTUALENV_DIR)/bin/pytest

test: virtualenv
	$(PYTEST) tests/ -v
.PHONY: test

#
# Cleanup
#
clean:
	rm -rf $(FRONTEND_DIR)/dist
	rm -rf $(FRONTEND_ENV)
	rm -rf $(VIRTUALENV) $(VIRTUALENV_DIR)/lib $(VIRTUALENV_DIR)/bin $(VIRTUALENV_DIR)/include
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete

.PHONY: clean
