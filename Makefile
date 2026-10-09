PYTHON ?= .semweb/bin/python
PIP ?= .semweb/bin/pip

.PHONY: setup clean-data rdf validate reasoning numbers queries queries-endpoint federated test site pipeline suggest-links link-evidence endpoint-up endpoint-load endpoint-down

setup:
	$(PIP) install -r requirements.txt

clean-data:
	$(PYTHON) src/clean_data.py

rdf:
	$(PYTHON) src/convert_to_rdf.py

validate:
	$(PYTHON) src/validate_rdf.py

reasoning:
	$(PYTHON) src/check_reasoning.py

numbers:
	$(PYTHON) src/report_numbers.py --reasoning

queries:
	$(PYTHON) src/run_sparql.py --all

queries-endpoint:
	$(PYTHON) src/run_sparql.py --all --endpoint

federated:
	$(PYTHON) src/run_sparql.py queries/federated/wikidata-club-facts.rq

test:
	$(PYTHON) -B -m unittest discover -s src -p 'test_*.py' -v

site:
	$(PYTHON) src/build_site.py

pipeline: clean-data rdf validate reasoning test site

suggest-links:
	$(PYTHON) src/suggest_links.py

link-evidence:
	$(PYTHON) src/collect_link_evidence.py

endpoint-up:
	docker compose up -d

endpoint-load:
	$(PYTHON) src/load_fuseki.py

endpoint-down:
	docker compose down
