#!/usr/bin/env python3
"""Collect identity evidence for every external link in the mapping file.

For each local entity, the script records the Wikidata revision, type claims
and English Wikipedia title, plus DBpedia's own owl:sameAs links. It then runs
identity checks that a same-name club, a disambiguation page, or another
country's "Premier League" season would fail.

Collection needs network access and is not part of the offline pipeline. The
conversion only reads the saved evidence. A row moves from ``candidate`` to
``verified`` only with ``--promote`` and only if every check passes; a reviewer
should still read the evidence summary before committing the result.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LINKS = PROJECT_ROOT / "data/links/entity-links.csv"
USER_AGENT = (
    "SemanticWeb_2025B-link-evidence/1.0 "
    "(https://github.com/DatDinh0923/SemanticWeb_2025B)"
)

ASSOCIATION_FOOTBALL = "Q2736"
PREMIER_LEAGUE = "Q9448"
# Wikidata classes that identify the right kind of thing for each entity type.
EXPECTED_INSTANCE_OF = {
    "team": {
        "Q476028",  # association football club
        "Q15944511",  # association football team
        "Q103229495",  # men's association football team (e.g. Chelsea F.C.)
    },
    "competition": {"Q15991303"},  # association football league
    "season": {"Q27020041"},  # sports season
}
SAME_AS = "http://www.w3.org/2002/07/owl#sameAs"
RDFS_LABEL = "http://www.w3.org/2000/01/rdf-schema#label"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"


def fetch_json(url: str, accept: str = "application/json", attempts: int = 5) -> dict:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(request, timeout=40) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError):
            if attempt == attempts:
                raise
            # Public endpoints rate-limit bursts; back off before retrying.
            time.sleep(3 * attempt)
    raise RuntimeError("unreachable")


def claim_ids(entity: dict, property_id: str) -> list[str]:
    values = []
    for claim in entity.get("claims", {}).get(property_id, []):
        value = claim["mainsnak"].get("datavalue", {}).get("value", {})
        if isinstance(value, dict) and "id" in value:
            values.append(value["id"])
    return values


def collect(row: dict[str, str]) -> dict:
    entity_type = row["entity_type"]
    qid = row["wikidata_uri"].rsplit("/", 1)[1]
    dbpedia_uri = row["dbpedia_uri"]
    dbpedia_slug = unquote(dbpedia_uri.split("/resource/", 1)[1])

    wikidata_url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    entity = fetch_json(wikidata_url)["entities"][qid]

    sparql = (
        f"SELECT ?p ?o WHERE {{ <{dbpedia_uri}> ?p ?o . "
        f"VALUES ?p {{ <{SAME_AS}> <{RDFS_LABEL}> <{RDF_TYPE}> }} }}"
    )
    dbpedia_url = "https://dbpedia.org/sparql?" + urlencode(
        {"query": sparql, "format": "application/sparql-results+json"}
    )
    bindings = fetch_json(dbpedia_url, "application/sparql-results+json")["results"][
        "bindings"
    ]
    dbpedia_same_as = sorted(
        {b["o"]["value"] for b in bindings if b["p"]["value"] == SAME_AS}
    )
    dbpedia_labels = sorted(
        {
            b["o"]["value"]
            for b in bindings
            if b["p"]["value"] == RDFS_LABEL and b["o"].get("xml:lang") == "en"
        }
    )
    dbpedia_types = sorted(
        {
            b["o"]["value"]
            for b in bindings
            if b["p"]["value"] == RDF_TYPE
            and b["o"]["value"].startswith("http://dbpedia.org/ontology/")
        }
    )

    instance_of = claim_ids(entity, "P31")
    wikipedia_title = entity.get("sitelinks", {}).get("enwiki", {}).get("title", "")
    checks = {
        "wikidata_type_matches": bool(EXPECTED_INSTANCE_OF[entity_type] & set(instance_of)),
        "wikidata_sport_is_association_football": (
            ASSOCIATION_FOOTBALL in claim_ids(entity, "P641")
        ),
        "wikipedia_title_matches_dbpedia": (
            wikipedia_title.replace(" ", "_") == dbpedia_slug
        ),
        "dbpedia_links_to_wikidata": row["wikidata_uri"] in dbpedia_same_as,
    }
    if entity_type == "season":
        checks["wikidata_season_of_premier_league"] = PREMIER_LEAGUE in claim_ids(
            entity, "P3450"
        )

    return {
        "entity_type": entity_type,
        "entity_id": row["entity_id"],
        "wikidata_uri": row["wikidata_uri"],
        "dbpedia_uri": dbpedia_uri,
        "checked_on": datetime.now(timezone(timedelta(hours=7))).date().isoformat(),
        "wikidata_source": wikidata_url,
        "wikidata_revision": entity["lastrevid"],
        "wikidata_label": entity.get("labels", {}).get("en", {}).get("value", ""),
        "wikidata_description": (
            entity.get("descriptions", {}).get("en", {}).get("value", "")
        ),
        "wikidata_instance_of": instance_of,
        "wikipedia_title": wikipedia_title,
        "dbpedia_source": dbpedia_url,
        "dbpedia_labels": dbpedia_labels,
        "dbpedia_types": dbpedia_types,
        "checks": checks,
        "passed": all(checks.values()),
    }


def read_links(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        return list(reader.fieldnames or []), [dict(row) for row in reader]


def write_links(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--links", type=Path, default=DEFAULT_LINKS)
    parser.add_argument("--only", nargs="+", help="Collect evidence for these entity IDs only.")
    parser.add_argument(
        "--promote",
        action="store_true",
        help="Mark rows whose checks all pass as verified.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    fieldnames, rows = read_links(args.links)
    selected = [row for row in rows if not args.only or row["entity_id"] in args.only]
    if not selected:
        raise SystemExit(f"No mapping rows selected from {args.links}")

    failures: list[str] = []
    errors: list[str] = []
    for row in selected:
        try:
            evidence = collect(row)
        except (HTTPError, URLError, TimeoutError, KeyError, ValueError) as exc:
            # A network error says nothing about identity: keep the row as it is.
            errors.append(row["entity_id"])
            print(f"{row['entity_type']:<11} {row['entity_id']:<28} ERROR {exc}")
            continue
        finally:
            # DBpedia's public endpoint answers 503 to bursts of requests.
            time.sleep(1)

        evidence_path = PROJECT_ROOT / row["evidence"]
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        failed = [name for name, ok in evidence["checks"].items() if not ok]
        status = "PASS" if evidence["passed"] else "FAIL " + ", ".join(failed)
        print(
            f"{row['entity_type']:<11} {row['entity_id']:<28} "
            f"{evidence['wikidata_label']!r:<40} {status}"
        )
        if evidence["passed"]:
            if args.promote:
                row["status"] = "verified"
                row["verified_on"] = evidence["checked_on"]
        else:
            failures.append(row["entity_id"])
            row["status"] = "candidate"
            row["verified_on"] = ""

    if args.promote:
        write_links(args.links, fieldnames, rows)
    passed = len(selected) - len(failures) - len(errors)
    print(f"{passed} passed, {len(failures)} failed, {len(errors)} errors.")
    if errors:
        print("Retry the errors with: --only " + " ".join(errors))
    return 1 if failures or errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
