# SPARQL queries

The sixteen saved queries correspond to the competency questions in
`docs/competency-questions.md`. Queries about one season or club name it in a
`VALUES` line or in the triple patterns; edit that IRI to ask about another.

Run one query locally:

```bash
python3 src/run_sparql.py queries/14-season-champions.rq
```

Run all queries locally, or against a running Fuseki endpoint:

```bash
python3 src/run_sparql.py --all
python3 src/run_sparql.py --all --endpoint
```

The same query files can be pasted into the Fuseki web interface or submitted
to `http://localhost:3030/football/sparql`. All sixteen were checked to return
the same results from rdflib and from Fuseki 5.1.

## Federated queries

`federated/wikidata-club-facts.rq` follows the `owl:sameAs` links into
Wikidata to fetch each club's home venue and founding year. It needs internet
access and runs from the terminal:

```bash
python3 src/run_sparql.py queries/federated/wikidata-club-facts.rq
```

Fuseki cannot run it: the Wikidata Query Service rejects the default Java
user agent that Jena sends (HTTP 403). The federated query is kept out of the
offline test suite for the same reason.
