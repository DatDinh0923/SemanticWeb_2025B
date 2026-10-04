# Competency Questions

Competency questions describe what the football knowledge graph must be able
to answer. They keep the ontology and RDF conversion focused on the available
data: ten complete English Premier League seasons, 2011/12 to 2020/21.

## Single-season questions

Each of these names one season (2018/19 by default) in the query; changing
that IRI asks the same question about any other season.

| ID | Question | Query | Required terms or data |
| --- | --- | --- | --- |
| CQ1 | Which teams played in a given season? | `01-list-teams.rq` | `FootballTeam`, `homeTeam`, `awayTeam`, `playedInSeason` |
| CQ2 | Which matches did a team play in a season, and was it home or away? | `02-team-matches.rq` | `homeTeam`, `awayTeam`, `matchDate` |
| CQ4 | Which matches in a season ended in a draw? | `04-drawn-matches.rq` | `Draw` |
| CQ5 | How many goals did each team score at home in a season? | `05-home-goals-by-team.rq` | `homeTeam`, `homeGoals` |
| CQ6 | How many matches were played in each round of a season? | `06-matches-per-round.rq` | `roundNumber` |
| CQ11 | What is the final league table of a season, using three points for a win? | `11-season-standings.rq` | `homeGoals`, `awayGoals`, `homeTeam`, `awayTeam` |

## Cross-season questions

| ID | Question | Query | Required terms or data |
| --- | --- | --- | --- |
| CQ3 | Which match or matches had the most goals across all seasons? | `03-highest-scoring-matches.rq` | `homeGoals`, `awayGoals` |
| CQ7 | Which matches were played within a given date range? | `07-january-2019-matches.rq` | `matchDate` |
| CQ8 | Which season and competition does each match belong to? | `08-match-season-competition.rq` | `playedInSeason`, `partOfCompetition` |
| CQ9 | What are the start and end dates of each season? | `09-season-dates.rq` | `Season`, `seasonLabel`, `schema:startDate`, `schema:endDate` |
| CQ12 | What are the head-to-head results between two clubs across all seasons? | `12-head-to-head.rq` | `winner`, `homeTeam`, `awayTeam`, `seasonLabel` |
| CQ13 | How do goals per match and home advantage change from season to season? | `13-season-statistics.rq` | `homeGoals`, `awayGoals`, `playedInSeason` |
| CQ14 | Which club won each season, computed only from match results? | `14-season-champions.rq` | `homeGoals`, `awayGoals`, `playedInSeason` |
| CQ15 | In how many seasons did each club play, and when? | `15-team-participation.rq` | `homeTeam`, `playedInSeason`, `seasonLabel` |

## Linked-data and ontology questions

| ID | Question | Query | Required terms or data |
| --- | --- | --- | --- |
| CQ10 | Which local resources link to Wikidata or DBpedia, and to what? | `10-external-links.rq` | `owl:sameAs` |
| CQ16 | How does the data look through the ontology's schema.org view? | `16-ontology-reasoning.rq` | `rdfs:subClassOf`, `rdfs:subPropertyOf`, `participant` |
| CQ17 | What stadium and founding year does Wikidata record for each club? | `federated/wikidata-club-facts.rq` | `owl:sameAs`, SPARQL 1.1 `SERVICE` |

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
- CQ16 needs the ontology loaded with the data. It shows that every match and
  season is a `schema:SportsEvent` and that `homeTeam`, `awayTeam`, `winner`,
  and `loser` all specialize `foot:participant` and `schema:competitor`.
- Players, managers, stadiums, transfers, lower divisions, and cup
  competitions are outside the dataset because the selected source files do
  not describe them reliably. Stadiums are reachable through CQ17 instead.

## Acceptance criteria

The ontology and generated dataset are sufficient when a SPARQL query can be
written for every question above without relying on undocumented fields or
parsing values from labels.
