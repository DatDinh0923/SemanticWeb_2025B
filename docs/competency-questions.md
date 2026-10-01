# Competency Questions

Competency questions describe what the football knowledge graph must be able
to answer. They keep the ontology and RDF conversion focused on the available
Premier League 2018/19 data.

## Core questions

| ID | Question | Required terms or data |
| --- | --- | --- |
| CQ1 | Which teams participated in the 2018/19 Premier League season? | `FootballTeam`, `homeTeam`, `awayTeam`, `playedInSeason` |
| CQ2 | Which matches did a given team play, and was it the home or away team? | `FootballMatch`, `homeTeam`, `awayTeam`, `matchDate` |
| CQ3 | Which match or matches had the highest total number of goals? | `homeGoals`, `awayGoals` |
| CQ4 | Which matches ended in a draw? | `homeGoals`, `awayGoals` |
| CQ5 | How many goals did each team score at home? | `homeTeam`, `homeGoals` |
| CQ6 | How many matches were played in each round? | `roundNumber` |
| CQ7 | Which matches were played within a given date range? | `matchDate` |
| CQ8 | Which season and competition does each match belong to? | `playedInSeason`, `partOfCompetition` |
| CQ9 | What are the start and end dates of the 2018/19 season? | `Season`, `schema:startDate`, `schema:endDate` |
| CQ10 | Which teams have links to Wikidata or DBpedia resources? | `FootballTeam`, `owl:sameAs` |

## Scope notes

- CQ1-CQ9 can be answered from the four cleaned CSV tables.
- CQ10 becomes answerable after the external-linking stage adds `owl:sameAs`
  statements for team resources.
- Players, managers, stadiums, cities, transfers, and live scores are outside
  the first version of the knowledge graph because the selected source file
  does not contain those facts.
- Derived results such as draws and total goals are calculated in SPARQL. They
  are not stored as duplicate facts in the RDF dataset.

## Acceptance criteria

The ontology and generated dataset are sufficient when a SPARQL query can be
written for every question above without relying on undocumented fields or
parsing values from labels.
