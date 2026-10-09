# Multi-season roadmap

The dataset now covers ten complete Premier League seasons (2011/12 to
2020/21). This page records what the expansion established and the gates for
growing further.

## Done

- `config/seasons.csv` is a checked manifest: each row names a source file,
  season ID, label, and expected match and team counts.
- `config/team-aliases.csv` gives every club one persistent, reviewed ID; all
  54 source spellings map to 35 clubs.
- The cleaner checks each season as a complete double round-robin and keeps
  the source file and line of every match.
- All 46 external identities (1 competition, 10 seasons, 35 clubs) have saved
  evidence and pass the identity checks in `docs/data-and-linking.md`.
- Cross-season competency questions (head-to-head, season statistics,
  champions, club participation) have regression tests. The standings for
  every season are compared with an independent calculation from the original
  CSV files.
- SHACL validation, deterministic RDF output, and the static site cover the
  combined dataset.

## Adding another Premier League season

1. Add the season's `eng.1.csv` to the manifest with its expected counts.
2. Run `python3 src/clean_data.py`. Add any unknown club spelling it reports
   to the alias table, reusing the existing ID when it is the same club.
3. Add the season (and any new club) to `data/links/entity-links.csv` as a
   `candidate`, then run `python3 src/collect_link_evidence.py --promote`.
4. Run `make pipeline` and update the expected counts in the tests.

Seasons before 2011/12 use the same format. 1992/93 to 1994/95 had 22 clubs
and 462 matches, which the manifest's expected counts already allow.

## Lower divisions and cups

Adding the Football League and National League needs extra identity rules
first. Several clubs were dissolved and refounded under a similar name
(phoenix clubs), such as Halifax Town AFC and FC Halifax Town, or Chester City
and Chester FC. Each must keep its own ID and Wikidata link, so the alias
table needs a validity period for such names before those divisions are
imported.

Cup files should be imported only after their rounds map to explicit `stage`
values and replays and walkovers have a documented policy. The ontology
already defines `Cup` and `stage` for this.

## Acceptance gates

An added season is ready only when all source rows are accounted for, entity
IDs are collision-free, every linked entity passes the evidence checks, saved
queries have regression expectations, SHACL passes, and two pipeline runs
produce byte-identical tracked artifacts.
