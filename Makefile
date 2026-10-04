PYTHON ?= .semweb/bin/python
PIP ?= .semweb/bin/pip

.PHONY: setup clean-data rdf validate queries queries-endpoint federated test site pipeline suggest-links link-evidence endpoint-up endpoint-load endpoint-down

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

queries-endpoint:
	$(PYTHON) src/run_sparql.py --all --endpoint

federated:
	$(PYTHON) src/run_sparql.py queries/federated/wikidata-club-facts.rq

test:
	$(PYTHON) -B -m unittest discover -s src -p 'test_*.py' -v

site:
	$(PYTHON) src/build_site.py

pipeline: clean-data rdf validate test site

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
