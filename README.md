# Premier League Linked Open Data

This project converts the 2018/19 English Premier League teams and match
results into validated Linked Open Data. It is five-star-ready locally and
becomes published five-star open data when the generated GitHub Pages site is
publicly reachable.

## Dataset summary

- 1 competition
- 1 season
- 20 teams
- 380 matches
- 4,626 instance-data triples
- 22 externally linked entities
- 44 `owl:sameAs` links to Wikidata and DBpedia
- 12 competency questions and saved SPARQL queries
- DCAT, VoID, and PROV-O publication metadata
- A generated static page and Turtle description for every local RDF resource
- Explicit league tier, draw, winner, and loser semantics validated with SHACL

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

This cleans the source data, generates RDF, validates it with SHACL, runs the
test suite, and builds the publication site in `_site/`.

Individual commands:

```bash
python3 src/clean_data.py
python3 src/convert_to_rdf.py
python3 src/validate_rdf.py
python3 src/run_sparql.py --all
```

Optional Wikidata candidate discovery is separate from the verified mapping:

```bash
make suggest-links
```

This networked command writes `data/links/wikidata-suggestions.csv` with every
candidate marked `unverified`. It refuses to overwrite
`data/links/entity-links.csv`; identity must be checked manually before a URI
is copied into the verified mapping.

The generated graph is written to `data/rdf/football-data.ttl`. The SHACL
report is written to `data/rdf/validation-report.ttl`.

## SPARQL terminal

Run all twelve saved queries:

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
the `FUSEKI_ADMIN_PASSWORD` environment variable. Docker binds Fuseki to
`127.0.0.1`, so the development endpoint is not exposed to the local network.

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
_site/                 generated publication site; not committed
```

## Repository and URI namespace

The source-code repository is:

```text
https://github.com/DatDinh0923/SemanticWeb_2025B
```

Project resources use:

```text
https://datdinh0923.github.io/SemanticWeb_2025B/
```

The repository URL and RDF namespace are intentionally different. GitHub Pages
serves the RDF namespace after publication.

## Static Linked Data site

Build and preview the Pages artifact locally:

```bash
make site
python3 -m http.server 8000 --directory _site
```

Open <http://localhost:8000/>. The generated site contains:

- A dataset landing page and RDF download
- Human-readable pages for all teams, matches, seasons, and ontology terms
- Resource-specific Turtle downloads
- The ontology, SHACL shapes, normalized CSV files, and external-link mapping

When the repository is ready for publication, select **GitHub Actions** under
GitHub **Settings -> Pages** and merge to `main`. The Pages workflow validates
and rebuilds the project before deployment. See
[`docs/publication-checklist.md`](docs/publication-checklist.md).

## Five-star status

| Level | Evidence |
| --- | --- |
| 1 star | CC0 data license and public download after Pages deployment |
| 2 stars | Structured CSV and RDF data |
| 3 stars | Non-proprietary CSV and Turtle formats |
| 4 stars | Stable HTTP URIs for the dataset, teams, matches, season, and ontology |
| 5 stars | 44 verified `owl:sameAs` links to Wikidata and DBpedia |

The data license is documented in [`LICENSE-DATA.md`](LICENSE-DATA.md).
The controlled expansion plan is documented in
[`docs/multi-season-roadmap.md`](docs/multi-season-roadmap.md).
