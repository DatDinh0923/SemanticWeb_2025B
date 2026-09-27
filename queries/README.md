# SPARQL queries

The ten saved queries correspond to the competency questions in
`docs/competency-questions.md`.

Run one query locally:

```bash
python3 src/run_sparql.py queries/03-highest-scoring-matches.rq
```

Run all queries:

```bash
python3 src/run_sparql.py --all
```

The same query files can be pasted into the Fuseki web interface or submitted
to `http://localhost:3030/football/sparql`.
