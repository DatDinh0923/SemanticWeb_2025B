"""Online evidence collection only. A human must review and promote mappings.

Use curl for Windows system TLS support. This script never modifies mappings.
"""
import argparse
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode

from common import ROOT, rows


def fetch(url):
    result = subprocess.run(["curl.exe" if __import__('os').name == 'nt' else 'curl',
                             "--fail", "--silent", "--show-error", "--location",
                             "--retry", "2", "--max-time", "40", url],
                            capture_output=True, check=True)
    return json.loads(result.stdout)


def collect(row):
    qid = row["wikidata_uri"].rsplit("/", 1)[1]
    slug = row["dbpedia_uri"].split("/resource/", 1)[1]
    wd_url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    # Fetch just the identity evidence, not megabytes of unrelated DBpedia facts.
    sparql = f"SELECT ?p ?o WHERE {{ <{row['dbpedia_uri']}> ?p ?o . VALUES ?p {{ <http://www.w3.org/2002/07/owl#sameAs> <http://www.w3.org/2000/01/rdf-schema#label> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> }} }}"
    db_url = "https://dbpedia.org/sparql?" + urlencode({"query": sparql, "format": "application/sparql-results+json"})
    entity = fetch(wd_url)["entities"][qid]
    db = {}
    for binding in fetch(db_url)["results"]["bindings"]:
        value = binding["o"]
        db.setdefault(binding["p"]["value"], []).append({"value": value["value"], "lang": value.get("xml:lang")})
    equivalents = [v["value"] for v in db.get("http://www.w3.org/2002/07/owl#sameAs", [])]
    labels = [v["value"] for v in db.get("http://www.w3.org/2000/01/rdf-schema#label", []) if v.get("lang") == "en"]
    types = [v["value"] for v in db.get("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", []) if v["value"].startswith("http://dbpedia.org/ontology/")]
    evidence = {
        "entity_id": row["entity_id"], "wikidata_uri": row["wikidata_uri"], "dbpedia_uri": row["dbpedia_uri"],
        "checked_on": datetime.now(timezone(timedelta(hours=7))).date().isoformat(),
        "wikidata_source": wd_url, "wikidata_revision": entity["lastrevid"],
        "wikidata_label": entity["labels"]["en"]["value"],
        "wikidata_description": entity["descriptions"]["en"]["value"],
        "wikipedia_title": entity["sitelinks"]["enwiki"]["title"],
        "wikidata_instance_of": [v["mainsnak"].get("datavalue", {}).get("value", {}).get("id") for v in entity["claims"].get("P31", [])],
        "dbpedia_source": db_url, "dbpedia_labels": labels, "dbpedia_types": types,
        "dbpedia_links_to_wikidata": row["wikidata_uri"] in equivalents,
        "wikipedia_title_matches_dbpedia": entity["sitelinks"]["enwiki"]["title"].replace(" ", "_") == slug,
    }
    path = ROOT / "data/links/evidence" / (row["entity_id"] + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="Fetch a single entity ID")
    args = parser.parse_args()
    selected = [r for r in rows(ROOT / "data/links/entity-links.csv") if not args.only or r["entity_id"] == args.only]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for evidence in pool.map(collect, selected):
            print(json.dumps(evidence, ensure_ascii=True), flush=True)


if __name__ == "__main__":
    main()
