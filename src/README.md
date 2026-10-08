# Project scripts

The scripts implement the complete data pipeline:

| Script | Purpose |
| --- | --- |
| `clean_data.py` | Normalize the seasons in `config/seasons.csv` into entity tables. |
| `convert_to_rdf.py` | Convert the tables and verified external links to RDF/Turtle. |
| `validate_rdf.py` | Validate the generated graph against SHACL shapes. |
| `check_reasoning.py` | Compare query counts without and with OWL 2 RL reasoning; check that the axioms catch deliberate errors. |
| `run_sparql.py` | SPARQL terminal: run saved queries locally or against an endpoint. |
| `load_fuseki.py` | Load the ontology and data into the Fuseki endpoint. |
| `build_site.py` | Generate dereferenceable resource pages and public downloads. |
| `suggest_links.py` | Find unverified Wikidata candidates without changing verified links. |
| `collect_link_evidence.py` | Record and check identity evidence for every external link. |

Run them from the project root.

## Cleaning

```bash
python3 src/clean_data.py
```

The cleaner reads two reviewed configuration files:

- `config/seasons.csv` lists each source file with its season ID, label, and
  expected match and team counts.
- `config/team-aliases.csv` maps every club spelling found in the sources
  (`Manchester Utd`, `Wolves`, ...) to one persistent team ID and name.

Each season must be a complete double round-robin: the expected number of
matches and teams, every home/away fixture exactly once, and every round with
the same number of matches. An unknown club spelling stops the run with its
file and line number instead of creating a new club from a guessed name.

The command writes `data/processed/{competitions,seasons,teams,matches}.csv`.
Every match keeps the source file and line it came from.

## RDF, validation, and site

```bash
python3 src/convert_to_rdf.py
python3 src/validate_rdf.py
python3 src/check_reasoning.py
python3 src/build_site.py
```

## SPARQL terminal

```bash
python3 src/run_sparql.py --all                                  # local rdflib
python3 src/run_sparql.py queries/14-season-champions.rq
python3 src/run_sparql.py --all --endpoint                        # running Fuseki
python3 src/run_sparql.py queries/federated/wikidata-club-facts.rq  # needs internet
```

The local terminal loads the ontology together with the data, as the Fuseki
loader does, so ontology-aware queries such as `16-ontology-reasoning.rq`
return the same results in both.

## External links

```bash
python3 src/suggest_links.py                    # candidates only
python3 src/collect_link_evidence.py            # check every mapping
python3 src/collect_link_evidence.py --only arsenal chelsea
python3 src/collect_link_evidence.py --promote  # mark passing rows verified
```

These commands need the network and are excluded from `make pipeline`. See
`docs/data-and-linking.md` for the identity checks.

## Tests

```bash
python3 -m unittest discover -s src -p 'test_*.py'
```
