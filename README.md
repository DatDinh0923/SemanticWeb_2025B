# Premier League Linked Open Data

This project publishes ten seasons of English Premier League results
(2011/12 to 2020/21) as validated five-star Linked Open Data: an OWL ontology,
RDF with resolvable HTTP URIs, verified links to Wikidata and DBpedia, and a
SPARQL endpoint and terminal for querying it.

## Dataset summary

- 1 competition, 10 seasons, 35 clubs, 3,800 matches
- 52,609 instance-data triples (52,815 with the ontology)
- 46 externally linked entities: the competition, every season, and every club
- 92 `owl:sameAs` links to Wikidata and DBpedia, each backed by saved
  identity evidence
- 16 competency questions with saved SPARQL queries, plus a federated query
  into Wikidata
- Provenance for every match back to its source file and line (PROV-O)
- DCAT, VoID, and PROV-O publication metadata
- A generated static page and Turtle description for every local resource

The source data comes from the public-domain
[football.csv England dataset](https://github.com/footballcsv/england).

## How the project meets the assignment

| Requirement | Where |
| --- | --- |
| 1. Define an ontology | [`ontology/football.ttl`](ontology/football.ttl), explained in [`docs/ontology.md`](docs/ontology.md) |
| 2. Collect relevant data | Ten source CSV files listed in [`config/seasons.csv`](config/seasons.csv); cleaned by [`src/clean_data.py`](src/clean_data.py) |
| 3. Transform into 4★ | [`src/convert_to_rdf.py`](src/convert_to_rdf.py) → [`data/rdf/football-data.ttl`](data/rdf/football-data.ttl); HTTP URIs served by the static site |
| 4. Link to other datasets for 5★ | [`data/links/`](data/links/), method in [`docs/data-and-linking.md`](docs/data-and-linking.md) |
| 5. SPARQL endpoint / terminal | Fuseki via [`docker-compose.yml`](docker-compose.yml); terminal [`src/run_sparql.py`](src/run_sparql.py); [`queries/`](queries/) |

## Pipeline

```text
OpenFootball CSV (10 seasons)
      -> season manifest + club alias table      config/
      -> normalized entity CSV files              data/processed/
      -> RDF/Turtle with HTTP URIs + provenance   data/rdf/football-data.ttl
      -> verified Wikidata and DBpedia links      data/links/
      -> SHACL validation                         shapes/, data/rdf/validation-report.ttl
      -> SPARQL terminal, Fuseki endpoint, static Linked Data site
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
test suite, and builds the publication site in `_site/`. It works offline.

Individual commands:

```bash
python3 src/clean_data.py
python3 src/convert_to_rdf.py
python3 src/validate_rdf.py
python3 src/run_sparql.py --all
python3 -m unittest discover -s src -p 'test_*.py'
```

On Windows without `make`, run the same commands with `python` and
`.semweb\Scripts\python.exe`.

## SPARQL terminal

Run all sixteen saved queries locally:

```bash
python3 src/run_sparql.py --all
```

Run one query:

```bash
python3 src/run_sparql.py queries/14-season-champions.rq
```

Run the federated query, which follows the `owl:sameAs` links into Wikidata
for each club's stadium and founding year (needs internet):

```bash
python3 src/run_sparql.py queries/federated/wikidata-club-facts.rq
```

The terminal loads the ontology together with the data, so ontology-aware
queries give the same answers as the Fuseki endpoint.

## Fuseki endpoint

Start Fuseki and load the generated ontology and data:

```bash
docker compose up -d
python3 src/load_fuseki.py
```

Default local credentials are `admin` / `admin`. Override the password with
the `FUSEKI_ADMIN_PASSWORD` environment variable. Docker binds Fuseki to
`127.0.0.1`, so the development endpoint is not exposed to the local network.

- Web interface: <http://localhost:3030/> (log in as `admin` / `admin`)
- SPARQL endpoint: <http://localhost:3030/football/sparql>
- Graph Store endpoint: <http://localhost:3030/football/data>

The dataset list and admin pages require the login; querying does not. Open
the web interface in a regular browser such as Firefox or Chrome and enter the
credentials when prompted, or open <http://admin:admin@localhost:3030/>.
Embedded browsers, such as the VS Code Simple Browser, do not show the login
prompt, so the dataset list keeps showing "Loading..." there.

If the page never loads at all, run `docker compose logs fuseki`: a stack
trace there usually means `fuseki/server.ttl` is not valid Turtle.

Query the running endpoint from the terminal:

```bash
python3 src/run_sparql.py --all --endpoint
```

All sixteen queries return the same results from Fuseki 5.1 and from the
local rdflib terminal. Stop the server with `docker compose down`.

## Linked Data site

Project resources use HTTP URIs under:

```text
https://datdinh0923.github.io/SemanticWeb_2025B/
```

`src/build_site.py` turns every resource into a page at its own URI, with a
Turtle download (`data.ttl`), embedded JSON-LD, and a list of the resources
that refer to it, so a browser can follow links in both directions. Preview it
locally:

```bash
make site
python3 -m http.server 8000 --directory _site
```

The site is live at <https://datdinh0923.github.io/SemanticWeb_2025B/>. It is
published by `.github/workflows/pages.yml` on every push to `main` or
`dqdat-dev`; see [`docs/publication-checklist.md`](docs/publication-checklist.md).

## Validation and tests

- **Cleaning** checks each season is a complete double round-robin and stops
  on an unknown club name, reporting the file and line.
- **SHACL** (`shapes/football-shapes.ttl`) checks types, cardinalities,
  datatypes, links, metadata, and cross-resource rules: draw typing, winner
  and loser against the score, dates inside the season, one source file per
  season, and no repeated fixture.
- **External links** are published only when verified and backed by passing
  evidence.
- **The test suite** (61 tests) covers each stage. Among other things it
  recomputes every season's full league table directly from the original CSV
  files, checks the champions query against the real champions, rejects
  deliberately broken data and links, and checks that the pipeline reproduces
  the committed files byte for byte.

## Five-star status

| Level | Evidence |
| --- | --- |
| 1 star | CC0 data license; public Turtle download at <https://datdinh0923.github.io/SemanticWeb_2025B/download/football-data.ttl> |
| 2 stars | Structured CSV and RDF data |
| 3 stars | Non-proprietary CSV and Turtle formats |
| 4 stars | HTTP URIs for the dataset, competition, seasons, clubs, matches, and ontology, resolvable through the static site |
| 5 stars | 92 verified `owl:sameAs` links to Wikidata and DBpedia |

## Project structure

```text
config/            season manifest and club alias table
england_csv/       original source data and its license
data/processed/    normalized CSV tables
data/links/        verified external mappings and identity evidence
data/rdf/          generated RDF and SHACL validation report
docs/              competency questions and design documentation
fuseki/            Fuseki server settings for Docker
ontology/          OWL ontology
queries/           saved SPARQL queries; federated/ needs internet
shapes/            SHACL shapes
src/               pipeline, validation, query, endpoint, and site tools
_site/             generated publication site; not committed
```

## Team branches merged into this version

This branch combines the strongest parts of the three team branches:

- **dqdat-dev**: HTTP URI namespace and static Linked Data site, DCAT/VoID/
  PROV metadata, SHACL shapes, Docker Fuseki, CI, and the test approach.
- **phongph5**: the ten-season Premier League scope, season manifest, club
  alias table, per-match source provenance, link evidence files, and
  standings checked against an independent calculation.
- **hung**: the richer OWL axioms (cardinalities, disjointness, `participant`
  property hierarchy, property chain), VoID class partitions, and the
  federated Wikidata query.

hung's branch also covered the lower divisions and the FA Cup. Those are not
included because several phoenix clubs received incorrect identities and
links; see [`docs/data-and-linking.md`](docs/data-and-linking.md) and
[`docs/multi-season-roadmap.md`](docs/multi-season-roadmap.md).

The data license is documented in [`LICENSE-DATA.md`](LICENSE-DATA.md).
