"""Collect the numbers used by the slides and the paper into presentation/facts.json."""
import json
from collections import Counter
from pathlib import Path

from rdflib import Graph
from rdflib.namespace import RDF

ROOT = Path(__file__).resolve().parent.parent
V = "http://vi.dbpedia.example.org/ontology/"
TRANSITIVE = {"hasAncestor", "hasDescendant", "locatedIn", "contains", "partOfConflict", "hasSubConflict",
              "intellectualLineage"}
CHAINS = {"hasGrandparent", "hasGrandchild", "hasPaternalGrandfather", "uncleOrAunt", "bornWithin", "diedWithin",
          "participatedIn", "tookPlaceWithin", "servedUnder", "servedBy", "memberOfDynasty", "ruledAsMemberOf",
          "dynastyMember"}
RULES = {"sibling", "ageAtDeath", "durationYears", "populationDensity", "reignedDuringConflict"}


def main():
    g = Graph().parse(ROOT / "data" / "rdf" / "inferred.ttl")
    cat = Counter()
    for s, p, o in g:
        ps, os_ = str(p), str(o)
        if p == RDF.type:
            if os_.startswith(V):
                cat["rule" if os_.endswith("CentenarianPerson") else "class"] += 1
            else:
                cat["alignment"] += 1
        elif not ps.startswith(V):
            cat["alignment"] += 1
        else:
            name = ps[len(V):]
            if name in RULES:
                cat["rule"] += 1
            elif name in TRANSITIVE:
                cat["transitive"] += 1
            elif name in CHAINS:
                cat["chain"] += 1
            else:
                cat["inverse_subproperty"] += 1
    facts = {
        "inferred_by_mechanism": dict(cat),
        "inferred_total": len(g),
        "reasoning": json.loads((ROOT / "data" / "rdf" / "reasoning_stats.json").read_text(encoding="utf8")),
        "consistency": json.loads((ROOT / "data" / "rdf" / "consistency_report.json").read_text(encoding="utf8"))["summary"],
        "shacl": json.loads((ROOT / "data" / "rdf" / "shacl_report.json").read_text(encoding="utf8"))["by_constraint"],
        "linking": {k: v for k, v in json.loads((ROOT / "linking" / "evaluation.json").read_text(encoding="utf8")).items()
                    if k != "false_positive_examples"},
    }
    (Path(__file__).parent / "facts.json").write_text(json.dumps(facts, ensure_ascii=False, indent=1), encoding="utf8")
    print(json.dumps(facts["inferred_by_mechanism"], indent=1), facts["inferred_total"])


if __name__ == "__main__":
    main()
