# Multi-season roadmap

The published dataset intentionally remains the complete 2018/19 Premier
League season. Expanding record count is not worth introducing incomplete
results, unstable identities, or unverified links. The existing pipeline is a
tested baseline for a controlled later expansion.

## Supported foundation

- Season and competition IDs already appear explicitly in every normalized
  match row.
- A competition is classified as a `League` and carries its national `tier`.
- The ontology defines future-ready `Cup` and `stage` terms without claiming
  that cup data exists in the current graph.
- Draw, winner, and loser facts are derived from scores rather than copied from
  inconsistent text labels.
- Static resource pages, SHACL validation, and query regression tests are
  generated from the resulting graph.

## Expansion sequence

1. Add one complete league season at a time and verify its expected match and
   team counts before combining graphs.
2. Replace the single-season command defaults with a checked manifest that
   records source file, competition, tier, season, and expected counts.
3. Give each club identity a persistent reviewed ID. Do not remove annotations
   such as founding year or phoenix-club status when two clubs share a name.
4. Extend external mappings only after manual identity checks; never treat a
   search result as an automatic `owl:sameAs` assertion.
5. Add season-specific query fixtures and cross-season competency questions,
   then run SHACL and deterministic-build checks over the combined dataset.
6. Import cup files only after their rounds can be mapped to explicit `stage`
   values and incomplete or replay records have a documented policy.

## Acceptance gates

An added season is ready only when all source rows are accounted for, entity
IDs are collision-free, every linked entity is manually verified, saved query
results have regression expectations, SHACL passes, and two pipeline runs
produce byte-identical tracked artifacts.
