"""Step 3c - Data-quality validation with SHACL (closed-world constraints).

Validates the extracted + inferred data against ontology/shapes.ttl and writes
data/rdf/shacl_report.json (number of violations per shape / message, with examples).

Usage:  python src/validate.py
"""
import json
import time
from collections import Counter, defaultdict
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import RDF

ROOT = Path(__file__).resolve().parent.parent
RDF_DIR = ROOT / "data" / "rdf"
SH = Namespace("http://www.w3.org/ns/shacl#")
# only the predicates the shapes look at (keeps pyshacl fast on a 1M+ triple dataset)
V = "http://vi.dbpedia.example.org/ontology/"
NEEDED = {V + p for p in ("birthDate", "deathDate", "birthYear", "deathYear", "hasFather", "hasMother", "ageAtDeath",
                          "startYear", "endYear", "adminCode", "population", "area", "adminLevel", "commander")}
NEEDED |= {"http://www.w3.org/2000/01/rdf-schema#label", "http://www.w3.org/2003/01/geo/wgs84_pos#lat",
           "http://www.w3.org/2003/01/geo/wgs84_pos#long", str(RDF.type)}


def main():
    t0 = time.time()
    data = Graph()
    for n in ("labels", "labels_referenced", "instance_types", "mappingbased_literals", "mappingbased_objects", "tenures",
              "geo_coordinates", "inferred"):
        f = RDF_DIR / f"{n}.ttl"
        if not f.exists():
            continue
        g = Graph().parse(f)
        for t in g:
            if str(t[1]) in NEEDED:
                data.add(t)
    print(f"{len(data):,} triples to validate ({time.time() - t0:.0f}s)")
    shapes = Graph().parse(ROOT / "ontology" / "shapes.ttl")
    conforms, report, _ = validate(data, shacl_graph=shapes, inference="none", allow_warnings=True)
    by = Counter()
    examples = defaultdict(list)
    for r in report.subjects(RDF.type, SH.ValidationResult):
        comp = str(report.value(r, SH.sourceConstraintComponent)).rsplit("#", 1)[-1]
        path = str(report.value(r, SH.resultPath)).rsplit("/", 1)[-1].rsplit("#", 1)[-1]
        msg = str(report.value(r, SH.resultMessage) or "")
        key = f"{path} / {comp}"
        by[key] += 1
        if len(examples[key]) < 5:
            examples[key].append({"focus": str(report.value(r, SH.focusNode)),
                                  "value": str(report.value(r, SH.value)), "message": msg[:200]})
    out = {"conforms": conforms, "violations": sum(by.values()), "by_constraint": dict(by.most_common()),
           "examples": examples, "seconds": round(time.time() - t0)}
    (RDF_DIR / "shacl_report.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf8")
    print(f"conforms={conforms}  violations={out['violations']:,}  ({out['seconds']}s)")
    for k, v in by.most_common(15):
        print(f"   {v:>6,}  {k}")


if __name__ == "__main__":
    main()
