PYTHON ?= .semweb/bin/python
PIP ?= .semweb/bin/pip

.PHONY: setup clean-data rdf validate queries test pipeline endpoint-up endpoint-load endpoint-down

setup:
	$(PIP) install -r requirements.txt

clean-data:
	$(PYTHON) src/clean_data.py

rdf:
	$(PYTHON) src/convert_to_rdf.py

validate:
	$(PYTHON) src/validate_rdf.py

queries:
	$(PYTHON) src/run_sparql.py --all

test:
	$(PYTHON) -B -m unittest discover -s src -p 'test_*.py' -v

pipeline: clean-data rdf validate test

endpoint-up:
	docker compose up -d

endpoint-load:
	$(PYTHON) src/load_fuseki.py

endpoint-down:
	docker compose down
