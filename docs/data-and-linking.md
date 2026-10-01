# Data source and external linking

## Source dataset

- Dataset: English Premier League 2018/19 match results
- Repository: <https://github.com/footballcsv/england>
- Source file: `2010s/2018-19/eng.1.csv`
- Original project: <https://github.com/openfootball/england>
- License: CC0 1.0 Universal / public domain dedication
- Records used: 380 matches involving 20 teams

The original CSV is retained without modification. `src/clean_data.py`
produces normalized tables with ISO dates, numeric scores, stable identifiers,
and explicit competition and season references.

## Link targets

The local resources are linked to two established Linked Open Data datasets:

- Wikidata: `http://www.wikidata.org/entity/...`
- DBpedia: `http://dbpedia.org/resource/...`

The mapping file contains 22 linked local entities:

- 20 football teams
- 1 competition
- 1 season

Each entity has one Wikidata link and one DBpedia link, resulting in 44
`owl:sameAs` statements.

The RDF also describes separate VoID linksets for Wikidata and DBpedia. Each
linkset records its target dataset, link predicate, and number of links.

## Matching method

Links were created with exact English-label matching and manually checked
against entity descriptions on 2026-09-27. Manual description checks were
important because names such as "Everton F.C.", "Crystal Palace F.C.", and
"Manchester City F.C." have multiple Wikidata candidates.

`owl:sameAs` is used only when the external resource represents the same club,
competition, or season. The mappings and verification method are recorded in
`data/links/entity-links.csv`.

The conversion rejects missing mappings, duplicate external targets, malformed
Wikidata identifiers, and non-DBpedia resource URIs.

## Publication metadata

The generated graph uses:

- DCAT to describe the downloadable Turtle distribution and landing page
- VoID to describe the URI space, data dump, entity count, and linksets
- PROV-O to connect the generated dataset to the source CSV and transformation
- Dublin Core Terms for title, creator, publisher, dates, source, and license

The generated static site makes each project URI resolvable to a human-readable
page with a resource-specific Turtle representation when GitHub Pages is
enabled.

## Five-star progression

1. The source is openly licensed under CC0.
2. The data is structured and machine-readable.
3. CSV and Turtle are non-proprietary formats.
4. RDF uses HTTP URIs for resources and vocabulary terms.
5. Local resources link to Wikidata and DBpedia.
