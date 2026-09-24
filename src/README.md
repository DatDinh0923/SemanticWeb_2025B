# Data cleaner

`clean_data.py` converts the OpenFootball Premier League CSV into normalized
entity tables that can be mapped directly to RDF resources.

Run it from the project root:

```bash
python3 src/clean_data.py
```

The default input is:

```text
england_csv/2010s/2018-19/eng.1.csv
```

The command creates:

```text
data/processed/competitions.csv
data/processed/seasons.csv
data/processed/teams.csv
data/processed/matches.csv
```

The output separates each ontology entity into its own table. Matches refer to
teams, seasons, and competitions through stable IDs rather than display names.

Run the tests with:

```bash
python3 -m unittest discover -s src -p 'test_*.py'
```

Use `python3 src/clean_data.py --help` to select another input, season, or
output directory. The default validation expects a complete Premier League
season with 380 matches and 20 teams.
