# Data source and external linking

## Source dataset

- Dataset: English Premier League match results, 2011/12 to 2020/21
- Repository: <https://github.com/footballcsv/england>
- Source files: the ten `eng.1.csv` files listed in `config/seasons.csv`
- Original project: <https://github.com/openfootball/england>
- License: CC0 1.0 Universal / public domain dedication
- Records used: 3,800 matches (380 per season) involving 35 clubs

The original CSV files are kept unmodified in `england_csv/`. The cleaner
produces normalized tables with ISO dates, numeric scores, stable identifiers,
explicit competition and season references, and the source file and line of
every match.

## Why ten Premier League seasons

The scope is a deliberate trade-off between size and correctness:

- Each season is checked as a complete double round-robin (380 matches, 20
  clubs, 38 rounds of 10, every home/away fixture exactly once). A missing,
  duplicated, or moved match stops the pipeline.
- 35 clubs is small enough to verify every external identity.
- Lower divisions were tried on another branch and introduced identity
  errors. Phoenix clubs, refounded under a similar name, were merged with the
  original club and linked to the wrong Wikidata item: Halifax Town AFC
  (1998–2002, dissolved 2008) and FC Halifax Town (founded 2008), or Chester
  City (dissolved 2010) and Chester FC (founded 2010). A false `owl:sameAs`
  is worse than a missing one, so those divisions stay out until each such
  club has a reviewed identity.

## Club identity

The sources spell clubs differently across seasons (`Manchester Utd` and
`Manchester United FC`, `Wolves` and `Wolverhampton Wanderers FC`).
`config/team-aliases.csv` maps all 54 source spellings to 35 reviewed IDs:

- The canonical name must slugify to the team ID, so an ID cannot drift away
  from the club it names.
- An unknown spelling stops the cleaner with its file and line number; the
  cleaner never invents a club from a guessed name.

## Link targets

Local resources are linked to two established Linked Open Data datasets:

- Wikidata: `http://www.wikidata.org/entity/...`
- DBpedia: `http://dbpedia.org/resource/...`

`data/links/entity-links.csv` contains 46 linked entities — 1 competition,
10 seasons, and 35 clubs — each with one Wikidata and one DBpedia link,
giving 92 `owl:sameAs` statements. The RDF describes separate VoID linksets
for Wikidata and DBpedia with their link predicate and size.

## Identity evidence

Every mapping has an evidence file in `data/links/evidence/<type>/<id>.json`,
collected by `src/collect_link_evidence.py` from the live Wikidata entity and
the DBpedia SPARQL endpoint. The file records the Wikidata revision, label,
description, `instance of` (P31) classes, English Wikipedia title, DBpedia
labels, types, and `owl:sameAs` links. These checks must all pass:

| Check | Catches |
| --- | --- |
| Wikidata type is an association football club/team, league, or sports season | Disambiguation pages, people, stadiums |
| Wikidata sport (P641) is association football | Other sports with the same name |
| A season is a season *of* the Premier League (P3450 = Q9448) | Same-named seasons of other leagues |
| English Wikipedia title equals the DBpedia resource name | Wikidata and DBpedia pointing at different things |
| DBpedia's own `owl:sameAs` points back to the same Wikidata item | Mismatched pairs |

The checks were needed. Searching Wikidata for "2018–19 Premier League" also
returns the *Premier League of Bosnia and Herzegovina* season, and "2020–21
Premier League" also returns a disambiguation page. Chelsea F.C. is typed as a
*men's association football team* rather than a *club*, so both classes are
accepted for clubs.

All 46 mappings passed on 2026-10-05 and are marked `verified`. The converter
refuses to publish a mapping that is not `verified`, has no verification date,
lacks an evidence file, or whose evidence names other URIs or records a failed
check. The pipeline reads only the saved evidence and works offline.

To re-check the links:

```bash
python3 src/collect_link_evidence.py            # report only
python3 src/collect_link_evidence.py --promote  # mark passing rows verified
```

DBpedia's public endpoint sometimes answers HTTP 503. The collector reports
such rows as errors without changing them; retry them with `--only <ids>`.

## Semantics of `owl:sameAs`

`owl:sameAs` is the strongest link in Linked Data: it states that two URIs
denote the same individual, so a reasoner may copy every statement about one
onto the other. `src/check_reasoning.py` shows this happening: under OWL 2 RL
all 3,800 matches gain a Wikidata URI as home team, the 35 Wikidata club URIs
become `foot:FootballTeam`s, and the 46 Wikidata and DBpedia URIs are inferred
to be the same as each other. Halpin et al. ("When owl:sameAs isn't the
Same", ISWC 2010) showed that much of the Web uses `owl:sameAs` for weaker
relations such as "is closely related to" or "describes the same topic", which
makes such inferences wrong.

The saved evidence shows where our links sit close to that line:

- **Club or team.** `foot:FootballTeam` is "a club whose identity persists
  across seasons", but the matches are played by the men's first team.
  Wikidata types Chelsea F.C. (Q9616) as a *men's association football team*
  while describing it as a *club*, and DBpedia types every club as a
  `dbo:Organisation`.
- **Competition or organisation.** DBpedia types the Premier League as a
  `dbo:Organisation` and `dbo:SoccerLeague`; we model it as a
  `schema:EventSeries` of seasons.
- **Season types.** DBpedia types the 2018–19 Premier League as a
  `dbo:SportsTeamSeason` as well as a `dbo:FootballLeagueSeason`.

None of these makes the merged graph inconsistent, but only because our
ontology says nothing about Wikidata or DBpedia classes. In every case the
URIs refer to the same real-world referent as used in practice (the Wikipedia article and the Wikidata item cover the
club, its first team and its results together). We therefore keep
`owl:sameAs`, which is what the five-star scheme, VoID linksets and Linked
Data browsers expect, and limit the risk with the evidence checks above.

Weaker alternatives were considered:

| Predicate | Meaning | Why not used |
| --- | --- | --- |
| `skos:exactMatch` | Two concepts can be used interchangeably | Defined between `skos:Concept`s; using it on clubs and seasons would type them as concepts |
| `schema:sameAs` | A web page that unambiguously identifies the item | No logical semantics, and its range is a URL of a page rather than an entity |
| `rdfs:seeAlso` | More information is available here | Too weak to carry identity; generic consumers cannot merge data |

If the club/team distinction is needed later, the clean solution is a separate
class for the club organisation linked to its team, with `owl:sameAs` only
between resources of the same kind.

## Candidate discovery

`src/suggest_links.py` queries the Wikidata search API for possible mappings
and writes them, marked `unverified`, to the ignored file
`data/links/wikidata-suggestions.csv`. It refuses to overwrite the verified
mapping. Candidate discovery is not entity resolution: a new candidate becomes
a link only after it is added to `entity-links.csv` and passes the evidence
checks above.

## Publication metadata

The generated graph uses:

- DCAT to describe the downloadable Turtle distribution and landing page
- VoID to describe the URI space, data dump, vocabularies, class partitions,
  entity and triple counts, and linksets
- PROV-O to connect the dataset, every season, and every match to the source
  CSV files and the transformation activity
- Dublin Core Terms for title, creator, publisher, dates, source, and license

The generated static site makes each project URI resolvable to a
human-readable page with a resource-specific Turtle representation and a list
of the resources that refer to it.

## Five-star progression

1. The source is openly licensed under CC0.
2. The data is structured and machine-readable.
3. CSV and Turtle are non-proprietary formats.
4. RDF uses HTTP URIs that resolve to pages describing each resource.
5. Clubs, seasons, and the competition link to Wikidata and DBpedia.
