# Publication checklist

The dataset is published as Linked Open Data at
<https://datdinh0923.github.io/SemanticWeb_2025B/>. This checklist records how
it was published and how to check a new release.

## Before publication

- Run `make pipeline` and confirm all tests and SHACL validation pass.
- Preview `_site/` locally with `python3 -m http.server 8000 --directory _site`.
- Check the root page, ontology page, one season, one team, one match, and all
  downloads.
- Merge the reviewed development branch into `main`.
- Keep the dataset license and source attribution in the release.

## GitHub configuration

1. The repository is public (done on 2026-10-05).
2. **Settings -> Pages -> Source** is set to **GitHub Actions** (done on
   2026-10-05).
3. **Settings -> Environments -> github-pages** allows deployment from both
   `main` and `dqdat-dev` (done on 2026-10-05).
4. A push to `main` or `dqdat-dev` runs `.github/workflows/pages.yml`, which
   runs the full pipeline and deploys the validated site. The workflow can
   also be started by hand from the **Actions** tab (`workflow_dispatch`).
5. Wait for the Pages workflow to finish successfully.

## Public verification

These URLs returned HTTP 200 without signing in on 2026-10-05, and the
published Turtle matched the local build byte for byte. Re-check them after
each release:

```text
https://datdinh0923.github.io/SemanticWeb_2025B/
https://datdinh0923.github.io/SemanticWeb_2025B/download/football-data.ttl
https://datdinh0923.github.io/SemanticWeb_2025B/ontology/
https://datdinh0923.github.io/SemanticWeb_2025B/resource/team/arsenal/
https://datdinh0923.github.io/SemanticWeb_2025B/resource/season/premier-league-2018-19/
```

The URI without a final slash may redirect to the generated resource page.
Each resource page also provides a resource-specific Turtle file named
`data.ttl`.

## Star status

- **1 star:** the CC0 dataset is available online.
- **2 stars:** structured CSV and RDF data are supplied.
- **3 stars:** CSV and Turtle are open, non-proprietary formats.
- **4 stars:** the RDF identifies entities with project HTTP URIs.
- **5 stars:** those entities link to Wikidata and DBpedia with `owl:sameAs`.

All five levels are met by the published site since 2026-10-05.
