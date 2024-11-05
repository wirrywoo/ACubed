.PHONY: start
#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BUCKET = [OPTIONAL] your-bucket-for-syncing-data (do not include 's3://')
PROFILE = default
PROJECT_NAME = ACubed
PYTHON_INTERPRETER = python3
API_BASE_PATH = api
UI_BASE_PATH = ui

ifeq (,$(shell which conda))
HAS_CONDA=False
else
HAS_CONDA=True
endif

#################################################################################
# COMMANDS                                                                      #
#################################################################################

# ## Initialize acubed api and ui. Run `make start source=api` to initialize api only.
# start:
# 	@if [ "$(source)" = "api" ]; then pipenv run fastapi run $(API_BASE_PATH)/server.py; else pipenv run $(UI_BASE_PATH)/start.sh; fi

## Standardize all line endings in codebase 
resolve_line_endings:
	find . -type f -exec dos2unix {} \;

## Refresh MongoDB database with new data from FFR's API
refresh_database: 
	pipenv run $(PYTHON_INTERPRETER) -m scripts.refresh_database

## Run Jupyter session
notebook:
	pipenv run $(PYTHON_INTERPRETER) -m ipykernel install --user --name=acubed
	pipenv run jupyter notebook

## Removes acubed environment and factory reset workspace
uninstall:
	pipenv --rm
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name '*.egg-info' -exec rm -r {} +
	find . -type d -name '*.mypy_cache' -exec rm -r {} +
	find . -type f -name "*.lock" -delete

## Check lint using pylint
lint:
	pipenv run pylint acubed scripts


## Check types using mypy
types:
	pipenv run mypy acubed scripts --config-file .config/mypy.ini

# ## Install local dependencies
# install_dependencies:
# 	brew install python@3.10

## Set up acubed environment
install:
	PIPENV_VENV_IN_PROJECT=1 pipenv install -d

test_environment:
	pipenv run $(PYTHON_INTERPRETER) test_environment.py

# start_api:
# 	pipenv run fastapi run $(API_BASE_PATH)/server.py

# start_app:
# 	pipenv run $(UI_BASE_PATH)/start.sh
	
#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=30 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
