#!/usr/bin/env python3
"""Replace Fuseki's default graph with the generated football dataset."""

from __future__ import annotations

import argparse
import base64
import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = PROJECT_ROOT / "data/rdf/football-data.ttl"
DEFAULT_ONTOLOGY = PROJECT_ROOT / "ontology/football.ttl"


def authorization_header(username: str, password: str) -> str:
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def wait_for_fuseki(base_url: str, timeout: int) -> None:
    deadline = time.monotonic() + timeout
    ping_url = f"{base_url.rstrip('/')}/$/ping"
    while time.monotonic() < deadline:
        try:
            with urlopen(ping_url, timeout=2) as response:
                if response.status == 200:
                    return
        except (HTTPError, URLError, TimeoutError):
            time.sleep(1)
    raise RuntimeError(f"Fuseki did not become ready within {timeout} seconds")


def send_graph(
    base_url: str,
    dataset: str,
    graph_path: Path,
    username: str,
    password: str,
    method: str,
) -> None:
    endpoint = f"{base_url.rstrip('/')}/{dataset}/data?default"
    request = Request(
        endpoint,
        data=graph_path.read_bytes(),
        method=method,
        headers={
            "Authorization": authorization_header(username, password),
            "Content-Type": "text/turtle; charset=utf-8",
        },
    )
    with urlopen(request, timeout=30) as response:
        if response.status not in {200, 201, 204}:
            raise RuntimeError(f"Unexpected Fuseki upload status: {response.status}")


def remote_triple_count(base_url: str, dataset: str) -> int:
    query = "SELECT (COUNT(*) AS ?count) WHERE { ?s ?p ?o }"
    endpoint = f"{base_url.rstrip('/')}/{dataset}/query?{urlencode({'query': query})}"
    request = Request(endpoint, headers={"Accept": "application/sparql-results+json"})
    with urlopen(request, timeout=15) as response:
        result = json.load(response)
    return int(result["results"]["bindings"][0]["count"]["value"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Load generated RDF into Fuseki.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--ontology", type=Path, default=DEFAULT_ONTOLOGY)
    parser.add_argument("--base-url", default="http://localhost:3030")
    parser.add_argument("--dataset", default="football")
    parser.add_argument("--username", default="admin")
    parser.add_argument(
        "--password",
        default=os.environ.get("FUSEKI_ADMIN_PASSWORD", "admin"),
    )
    parser.add_argument("--wait-seconds", type=int, default=30)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        wait_for_fuseki(args.base_url, args.wait_seconds)
        send_graph(
            args.base_url,
            args.dataset,
            args.data,
            args.username,
            args.password,
            "PUT",
        )
        send_graph(
            args.base_url,
            args.dataset,
            args.ontology,
            args.username,
            args.password,
            "POST",
        )
        count = remote_triple_count(args.base_url, args.dataset)
    except (OSError, HTTPError, URLError, RuntimeError, KeyError, ValueError) as exc:
        raise SystemExit(f"Fuseki load failed: {exc}") from exc

    print(f"Loaded {count} triples into dataset '{args.dataset}'.")
    print(f"SPARQL endpoint: {args.base_url.rstrip('/')}/{args.dataset}/sparql")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
