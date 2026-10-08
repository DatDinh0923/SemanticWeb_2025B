# Competency Questions

Competency questions describe what the football knowledge graph must be able
to answer. They keep the ontology and RDF conversion focused on the available
data: ten complete English Premier League seasons, 2011/12 to 2020/21.

The questions are split into **domain questions**, which a football analyst
would ask, and **technical checks**, which test the linking, the metadata and
the ontology rather than football knowledge. The CQ numbers are kept so they
match the query file names. The "Ontology terms" column lists the terms each
query actually uses (`foot:` unless prefixed; `schema:name` and `rdfs:label`
are omitted).

## Domain questions: one season

Each of these names one season (2018/19 by default) in the query; changing
that IRI asks the same question about any other season.

| ID | Question | Query | Ontology terms |
| --- | --- | --- | --- |
| CQ1 | Which teams played in a given season? | `01-list-teams.rq` | `FootballTeam`, `homeTeam`, `awayTeam`, `playedInSeason` |
| CQ2 | Which matches did a team play in a season, and was it home or away? | `02-team-matches.rq` | `homeTeam`, `awayTeam`, `homeGoals`, `awayGoals`, `matchDate`, `playedInSeason` |
| CQ4 | Which matches in a season ended in a draw? | `04-drawn-matches.rq` | `Draw`, `homeTeam`, `awayTeam`, `homeGoals`, `matchDate`, `playedInSeason` |
| CQ5 | How many goals did each team score at home in a season? | `05-home-goals-by-team.rq` | `FootballMatch`, `homeTeam`, `homeGoals`, `playedInSeason` |
| CQ6 | How many matches were played in each round of a season? | `06-matches-per-round.rq` | `FootballMatch`, `roundNumber`, `playedInSeason` |
| CQ11 | What is the final league table of a season, using three points for a win? | `11-season-standings.rq` | `homeTeam`, `awayTeam`, `homeGoals`, `awayGoals`, `playedInSeason` |

## Domain questions: across seasons

| ID | Question | Query | Ontology terms |
| --- | --- | --- | --- |
| CQ3 | Which match or matches had the most goals across all seasons? | `03-highest-scoring-matches.rq` | `FootballMatch`, `homeGoals`, `awayGoals`, `matchDate`, `playedInSeason` |
| CQ7 | Which matches were played within a given date range? | `07-january-2019-matches.rq` | `FootballMatch`, `matchDate` |
| CQ12 | What are the head-to-head results between two clubs across all seasons? | `12-head-to-head.rq` | `homeTeam`, `awayTeam`, `homeGoals`, `awayGoals`, `winner`, `matchDate`, `playedInSeason`, `seasonLabel` |
| CQ13 | How do goals per match and home advantage change from season to season? | `13-season-statistics.rq` | `FootballMatch`, `homeGoals`, `awayGoals`, `playedInSeason`, `seasonLabel` |
| CQ14 | Which club won each season, computed only from match results? | `14-season-champions.rq` | `homeTeam`, `awayTeam`, `homeGoals`, `awayGoals`, `playedInSeason`, `seasonLabel` |
| CQ15 | In how many seasons did each club play, and when? | `15-team-participation.rq` | `homeTeam`, `playedInSeason`, `seasonLabel` |
| CQ17 | What stadium and founding year does Wikidata record for each club? | `federated/wikidata-club-facts.rq` | `homeTeam`, `playedInSeason`, `owl:sameAs`; Wikidata `P115`, `P571` via `SERVICE` |

## Technical checks

| ID | Question | Query | Ontology terms |
| --- | --- | --- | --- |
| CQ8 | Which season and competition does each match belong to? | `08-match-season-competition.rq` | `FootballMatch`, `playedInSeason`, `partOfCompetition` |
| CQ9 | What are the start and end dates of each season? | `09-season-dates.rq` | `Season`, `seasonLabel`, `schema:startDate`, `schema:endDate` |
| CQ10 | Which local resources link to Wikidata or DBpedia, and to what? | `10-external-links.rq` | `Competition`, `Season`, `FootballTeam`, `owl:sameAs` |
| CQ16 | How does the data look through the ontology's schema.org view? | `16-ontology-reasoning.rq` | `participant`, `schema:SportsEvent`, `schema:SportsTeam`, `schema:EventSeries`, `schema:competitor`, `rdfs:subClassOf`, `rdfs:subPropertyOf` |

## Term coverage

16 of the 22 `foot:` terms are used by at least one query. The six that are
not are deliberate: `League` and `tier` type the competition but no question
filters on them; `loser` mirrors `winner`; `sourceLine` is provenance; `Cup`
and `stage` are extension points with no instances in the league-only data.

## Scope notes

- CQ1–CQ9 and CQ11–CQ15 are answered from facts generated from the source
  CSV files. `Draw`, `winner`, and `loser` are derived from the two scores and
  checked against them by SHACL; aggregates such as standings, champions, and
  season statistics are always calculated in SPARQL, never stored.
- The champions query (CQ14) and the standings query (CQ11) are checked in the
  test suite against the real champions and against tables computed directly
  from the original CSV files for all ten seasons.
- CQ10 and CQ17 depend on the external-linking stage. CQ17 reads live data
  from Wikidata and needs internet access.
- CQ16 does not use a reasoner: `rdfs:subClassOf*` and `rdfs:subPropertyOf*`
  property paths emulate subclass and sub-property entailment at query time,
  so it needs the ontology loaded with the data. `src/check_reasoning.py`
  computes the same counts with an OWL 2 RL reasoner and checks that they
  agree (see [ontology.md](ontology.md#reasoning-check)).
- Players, managers, stadiums, transfers, lower divisions, and cup
  competitions are outside the dataset because the selected source files do
  not describe them reliably. Stadiums are reachable through CQ17 instead.

## Acceptance criteria

The ontology and generated dataset are sufficient when a SPARQL query can be
written for every question above without relying on undocumented fields or
parsing values from labels.
