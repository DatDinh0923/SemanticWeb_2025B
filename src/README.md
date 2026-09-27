# Project scripts

The scripts implement the complete data pipeline:

| Script | Purpose |
| --- | --- |
| `clean_data.py` | Normalize the source match CSV into entity tables. |
| `convert_to_rdf.py` | Convert the tables and external links to RDF/Turtle. |
| `validate_rdf.py` | Validate the generated graph against SHACL shapes. |
| `run_sparql.py` | Run saved SPARQL queries as a local terminal. |
| `load_fuseki.py` | Load the ontology and data into the Fuseki endpoint. |

Run it from the project root:

```bash
python3 src/clean_data.py
```

The default input is:

```text
england_csv/2010s/2018-19/eng.1.csv
```

The cleaning command creates:

```text
data/processed/competitions.csv
data/processed/seasons.csv
data/processed/teams.csv
data/processed/matches.csv
```

The output separates each ontology entity into its own table. Matches refer to
teams, seasons, and competitions through stable IDs rather than display names.

Generate and validate the RDF:

```bash
python3 src/convert_to_rdf.py
python3 src/validate_rdf.py
```

Run the saved SPARQL queries locally:

```bash
python3 src/run_sparql.py --all
```

Run the tests with:

```bash
python3 -m unittest discover -s src -p 'test_*.py'
```

Use `python3 src/clean_data.py --help` to select another input, season, or
output directory. The default validation expects a complete Premier League
season with 380 matches and 20 teams.
