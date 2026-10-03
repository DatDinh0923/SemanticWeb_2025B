"""One offline command: normalize, convert, validate, then acceptance tests."""
import subprocess
import sys

from clean_data import clean_all
from common import ROOT
from convert_to_rdf import convert
from validate_rdf import main as validate


def main():
    matches, teams = clean_all()
    print(f"Cleaned {matches} matches / {teams} clubs / 10 seasons", flush=True)
    convert()
    validate()
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "src", "-p", "test_*.py", "-v"], cwd=ROOT, check=True)
    print("Pipeline complete. All ten SPARQL questions and CSV reference checks passed.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"Pipeline failed: {exc}") from exc
