# Publication checklist

The repository can be developed privately. It becomes public Linked Open Data
only after the generated site and RDF downloads are reachable without login.

## Before publication

- Run `make pipeline` and confirm all tests and SHACL validation pass.
- Preview `_site/` locally with `python3 -m http.server 8000 --directory _site`.
- Check the root page, ontology page, one season, one team, one match, and all
  downloads.
- Merge the reviewed development branch into `main`.
- Keep the dataset license and source attribution in the release.

## GitHub configuration

1. The repository is public (done on 2026-10-05).
2. Open **Settings -> Pages** and set **Source** to **GitHub Actions**. Until
   this is done the Pages API reports `has_pages: false` and every project URI
   returns 404.
3. Push or merge to `main`; `.github/workflows/pages.yml` builds and deploys
   the validated site. The workflow can also be started by hand from the
   **Actions** tab (`workflow_dispatch`).
4. Wait for the Pages workflow to finish successfully.

## Public verification

Verify that these return HTTP 200 without signing into GitHub:

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

- **1 star:** achieved publicly when the CC0 dataset is available online.
- **2 stars:** structured CSV and RDF data are supplied.
- **3 stars:** CSV and Turtle are open, non-proprietary formats.
- **4 stars:** the RDF identifies entities with project HTTP URIs.
- **5 stars:** those entities link to Wikidata and DBpedia with `owl:sameAs`.

Until the site is public, the repository is technically five-star-ready but is
not yet published five-star open data.
