"""Terminal interface to the ViDBpedia SPARQL endpoint.

    python src/query.py "SELECT ?s WHERE { ?s a vidbo:VietnameseMonarch } LIMIT 5"
    python src/query.py -f queries/cq02_paternal_grandfather.rq
    python src/query.py --list                 # list the competency-question queries
    python src/query.py --cq 2                 # run competency question no. 2
    python src/query.py                        # interactive shell (end a query with ';' on its own line)

Common prefixes (vidbo, vidbr, dbo, dbr, rdf, rdfs, owl, xsd, foaf, dct, skos, geo) are added automatically.
"""
import argparse
import os
import re
import shutil
import sys
import textwrap
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
ENDPOINT = os.environ.get("VIDBPEDIA_ENDPOINT", "http://localhost:3030/vidbpedia/sparql")
PREFIXES = {
    "vidbr": "http://vi.dbpedia.example.org/resource/", "vidbo": "http://vi.dbpedia.example.org/ontology/",
    "dbr": "http://dbpedia.org/resource/", "dbo": "http://dbpedia.org/ontology/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#", "xsd": "http://www.w3.org/2001/XMLSchema#",
    "foaf": "http://xmlns.com/foaf/0.1/", "dct": "http://purl.org/dc/terms/",
    "skos": "http://www.w3.org/2004/02/skos/core#", "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",
    "wd": "http://www.wikidata.org/entity/",
    "graph": "http://vi.dbpedia.example.org/graph/",
}


def with_prefixes(q):
    declared = {m.lower() for m in re.findall(r"PREFIX\s+(\w*):", q, re.I)}
    head = "".join(f"PREFIX {k}: <{v}>\n" for k, v in PREFIXES.items() if k not in declared)
    return head + q


def short(v):
    for k, ns in PREFIXES.items():
        if v.startswith(ns):
            return f"{k}:{v[len(ns):]}"
    return v


def run(q, fmt="table"):
    q = with_prefixes(q)
    is_select = re.search(r"^\s*(SELECT|ASK)\b", re.sub(r"(?m)^\s*(PREFIX|#).*$", "", q).strip(), re.I)
    accept = "application/sparql-results+json" if is_select else "text/turtle"
    r = requests.post(ENDPOINT, data={"query": q}, headers={"Accept": accept}, timeout=300)
    r.encoding = "utf-8"
    if r.status_code != 200:
        print(f"Error {r.status_code}:\n{r.text[:2000]}")
        return
    if not is_select:
        print(r.text)
        return
    j = r.json()
    if "boolean" in j:
        print("ASK ->", j["boolean"])
        return
    cols, rows = j["head"]["vars"], j["results"]["bindings"]
    table = [[short(b[c]["value"]) if c in b else "" for c in cols] for b in rows]
    if fmt == "tsv":
        print("\t".join(cols))
        for row in table:
            print("\t".join(row))
        return
    width = shutil.get_terminal_size((140, 20)).columns
    maxw = max(12, (width - 3 * len(cols)) // max(1, len(cols)))
    widths = [min(maxw, max([len(c) + 1] + [len(r[i]) for r in table])) for i, c in enumerate(cols)]
    line = "+".join("-" * (w + 2) for w in widths)
    print(line)
    print("|".join(f" {('?' + c)[:w]:<{w}} " for c, w in zip(cols, widths)))
    print(line)
    for row in table:
        print("|".join(f" {textwrap.shorten(v, w, placeholder='…') if len(v) > w else v:<{w}} " for v, w in zip(row, widths)))
    print(line)
    print(f"{len(table)} row(s)")


def cq_files():
    return sorted((ROOT / "queries").glob("*.rq"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="?")
    ap.add_argument("-f", "--file")
    ap.add_argument("--cq", type=int, help="run competency question number N")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--tsv", action="store_true")
    a = ap.parse_args()
    fmt = "tsv" if a.tsv else "table"
    if sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    if a.list:
        for i, f in enumerate(cq_files(), 1):
            first = next((l.lstrip("# ").strip() for l in f.read_text(encoding="utf8").splitlines() if l.startswith("#")), "")
            print(f"{i:2d}. {f.name:45s} {first}")
        return
    if a.cq:
        f = cq_files()[a.cq - 1]
        text = f.read_text(encoding="utf8")
        print("\n".join(l for l in text.splitlines() if l.startswith("#")))
        run(text, fmt)
        return
    if a.file:
        run(Path(a.file).read_text(encoding="utf8"), fmt)
        return
    if a.query:
        run(a.query, fmt)
        return
    print(f"ViDBpedia SPARQL shell — endpoint {ENDPOINT}\nEnd a query with ';' on its own line. Ctrl+C to exit.")
    buf = []
    try:
        while True:
            line = input("sparql> " if not buf else "   ...> ")
            if line.strip() == ";":
                if buf:
                    run("\n".join(buf), fmt)
                buf = []
            else:
                buf.append(line)
    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == "__main__":
    main()
