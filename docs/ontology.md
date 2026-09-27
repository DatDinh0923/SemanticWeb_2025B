# Ontology overview

The ontology models the smallest useful Premier League domain supported by the
selected source data.

```mermaid
classDiagram
    Competition "1" <-- "1" Season : partOfCompetition
    Competition "1" <-- "380" FootballMatch : partOfCompetition
    Season "1" <-- "380" FootballMatch : playedInSeason
    FootballTeam "1" <-- "many" FootballMatch : homeTeam
    FootballTeam "1" <-- "many" FootballMatch : awayTeam

    class FootballMatch {
        date matchDate
        positiveInteger roundNumber
        nonNegativeInteger homeGoals
        nonNegativeInteger awayGoals
    }

    class FootballTeam {
        langString name
        IRI sameAs
    }

    class Season {
        langString name
        date startDate
        date endDate
    }

    class Competition {
        langString name
        langString spatialCoverage
    }
```

## Vocabulary reuse

- Schema.org supplies `SportsEvent`, `SportsTeam`, `Event`, `name`,
  `startDate`, `endDate`, `homeTeam`, and `awayTeam` semantics.
- Dublin Core supplies dataset metadata and `isPartOf` semantics.
- OWL supplies ontology declarations, functional properties, and `sameAs`.
- XSD supplies date and numeric datatypes.

Project-specific properties are used only for football facts that do not have
a sufficiently precise reused property, such as full-time home and away goals.
