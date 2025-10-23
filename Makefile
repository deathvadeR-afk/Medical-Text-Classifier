#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = Medical-Text-Classifier
PYTHON_VERSION = 3.10
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python dependencies
.PHONY: requirements
requirements:
	$(PYTHON_INTERPRETER) -m pip install -U pip
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt
	



## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete


## Lint using ruff (use `make format` to do formatting)
.PHONY: lint
lint:
	ruff format --check
	ruff check

## Format source code with ruff
.PHONY: format
format:
	ruff check --fix
	ruff format



## Run tests
.PHONY: test
test:
	python -m pytest tests

## Run simple startup test
.PHONY: test-startup
test-startup:
	python test_startup.py

## Run simple test (alias)
.PHONY: test-simple
test-simple:
	python test_startup.py

## Download Data from storage system
.PHONY: sync_data_down
sync_data_down:
	aws s3 sync s3://storage/data/ \
		data/ 
	

## Upload Data to storage system
.PHONY: sync_data_up
sync_data_up:
	aws s3 sync data/ \
		s3://storage/data 
	



## Set up Python interpreter environment
.PHONY: create_environment
create_environment:
	@bash -c "if [ ! -z `which virtualenvwrapper.sh` ]; then source `which virtualenvwrapper.sh`; mkvirtualenv $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER); else mkvirtualenv.bat $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER); fi"
	@echo ">>> New virtualenv created. Activate with:\nworkon $(PROJECT_NAME)"
	



#################################################################################
# PROJECT RULES                                                                 #
#################################################################################


## Make dataset
.PHONY: data
data: requirements
	$(PYTHON_INTERPRETER) src/dataset.py

#################################################################################
# DOCKER COMMANDS                                                               #
#################################################################################

## Build Docker image
.PHONY: docker-build
docker-build:
	docker build -t medical-text-classifier:latest .

## Run Docker container
.PHONY: docker-run
docker-run:
	docker run -d \
		--name medical-api \
		-p 8000:8000 \
		-e DATABASE_URL=${DATABASE_URL} \
		medical-text-classifier:latest

## Stop Docker container
.PHONY: docker-stop
docker-stop:
	docker stop medical-api || true
	docker rm medical-api || true

## View Docker logs
.PHONY: docker-logs
docker-logs:
	docker logs -f medical-api

## Start services with docker-compose
.PHONY: docker-up
docker-up:
	docker-compose up -d

## Stop services with docker-compose
.PHONY: docker-down
docker-down:
	docker-compose down

## View docker-compose logs
.PHONY: docker-compose-logs
docker-compose-logs:
	docker-compose logs -f

## Build and push Docker image to registry
.PHONY: docker-push
docker-push: docker-build
	docker tag medical-text-classifier:latest ${DOCKER_REGISTRY}/medical-text-classifier:latest
	docker push ${DOCKER_REGISTRY}/medical-text-classifier:latest

#################################################################################
# CI/CD COMMANDS                                                                #
#################################################################################

## Run CI pipeline locally
.PHONY: ci
ci: clean lint test-all

## Run pre-commit checks
.PHONY: pre-commit
pre-commit: format lint test-unit

## Deploy to staging
.PHONY: deploy-staging
deploy-staging:
	@echo "Deploying to staging environment..."
	# Add deployment commands here

## Deploy to production
.PHONY: deploy-production
deploy-production:
	@echo "Deploying to production environment..."
	# Add deployment commands here

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
