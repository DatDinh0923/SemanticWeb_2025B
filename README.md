# Premier League Linked Open Data

This project publishes the 2018/19 English Premier League teams and match
results as validated, five-star Linked Open Data.

## Dataset summary

- 1 competition
- 1 season
- 20 teams
- 380 matches
- 3,901 instance-data triples
- 22 externally linked entities
- 44 `owl:sameAs` links to Wikidata and DBpedia
- 10 competency questions and saved SPARQL queries

The source data comes from the public-domain
[football.csv England dataset](https://github.com/footballcsv/england).

## Pipeline

```text
OpenFootball CSV
      -> normalized entity CSV files
      -> RDF/Turtle with HTTP URIs
      -> Wikidata and DBpedia links
      -> SHACL validation
      -> local SPARQL terminal or Fuseki endpoint
```

## Setup

```bash
python3 -m venv .semweb
source .semweb/bin/activate
pip install -r requirements.txt
```

Run the complete local pipeline:

```bash
make pipeline
```

Individual commands:

```bash
python3 src/clean_data.py
python3 src/convert_to_rdf.py
python3 src/validate_rdf.py
python3 src/run_sparql.py --all
```

The generated graph is written to `data/rdf/football-data.ttl`. The SHACL
report is written to `data/rdf/validation-report.ttl`.

## SPARQL terminal

Run all ten saved queries:

```bash
python3 src/run_sparql.py --all
```

Run one query:

```bash
python3 src/run_sparql.py queries/03-highest-scoring-matches.rq
```

## Fuseki endpoint

Start Fuseki and load the generated ontology and data:

```bash
docker compose up -d
python3 src/load_fuseki.py
```

Default local credentials are `admin` / `admin`. Override the password with
the `FUSEKI_ADMIN_PASSWORD` environment variable for a shared deployment.

- Web interface: <http://localhost:3030/>
- SPARQL endpoint: <http://localhost:3030/football/sparql>
- Graph Store endpoint: <http://localhost:3030/football/data>

Stop the local server with:

```bash
docker compose down
```

## Project structure

```text
data/processed/       normalized CSV tables
data/links/           verified external entity mappings
data/rdf/             generated RDF and validation report
docs/                 competency questions and design documentation
ontology/             OWL ontology
queries/              saved SPARQL queries
shapes/               SHACL validation shapes
src/                  pipeline, validation, query, and endpoint tools
```

## URI namespace

Project resources use:

```text
https://datdinh0923.github.io/SemanticWeb_2025B/
```

Enable GitHub Pages for this repository before the final presentation so the
HTTP namespace can resolve to project documentation.
