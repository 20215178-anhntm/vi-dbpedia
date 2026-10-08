"""Step 4 - Interlink ViDBpedia with the English DBpedia (5-star Linked Data).

Two complementary link generators:

A. Interlanguage links (high precision): Wikipedia's vi->en language links
   give dbr:<English title>. Every candidate is verified against the DBpedia SPARQL
   endpoint and DBpedia redirects are followed to the canonical resource.

B. Silk-style link discovery (for entities WITHOUT a language link):
   blocking   - candidate DBpedia resources whose English label equals one of several
                label variants (original, without diacritics, "Battle of ...", "... dynasty",
                "... province", ...)
   comparison - Jaro-Winkler on diacritic-folded labels, birth/start year agreement,
                type compatibility (vidbo class <-> dbo class)
   aggregation- weighted average; type mismatch is a veto
   filter     - score >= ACCEPT  -> owl:sameAs ; REVIEW <= score < ACCEPT -> review file
   The same rule is expressed as a Silk Link Specification in linking/silk_vidbpedia_dbpedia.xml.

   The matcher is EVALUATED on entities that do have a language link (ground truth),
   pretending the link is unknown, which gives precision / recall / F1.

Outputs: data/rdf/links_dbpedia_interlanguage.ttl, data/rdf/links_dbpedia_silk.ttl,
         linking/review_candidates.tsv, linking/evaluation.json

Usage:   python src/link.py [--eval-sample 1500]
"""
import argparse
import hashlib
import json
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path

import requests
from rapidfuzz.distance import JaroWinkler
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS
from unidecode import unidecode

sys.path.insert(0, str(Path(__file__).parent))
from extract import VIDBO, VIDBR, iri_part, res  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RDF_DIR = ROOT / "data" / "rdf"
LINK_DIR = ROOT / "linking"
LINK_DIR.mkdir(exist_ok=True)
DBR = Namespace("http://dbpedia.org/resource/")
DBO = Namespace("http://dbpedia.org/ontology/")
ENDPOINT = "https://dbpedia.org/sparql"
ACCEPT, REVIEW = 0.88, 0.75

_s = requests.Session()
_s.headers.update({"User-Agent": "ViDBpediaStudentProject/1.0 (educational)",
                   "Accept": "application/sparql-results+json"})


CACHE = LINK_DIR / "cache"
CACHE.mkdir(exist_ok=True)
FAILED = []
STATE = {"consecutive_failures": 0, "down": False}


def sparql(q, tries=4):
    """POST a query to DBpedia; successful answers are cached on disk, failures are remembered.

    After 3 consecutive failed queries the endpoint is considered down and only the cache is used,
    so that an outage of the public endpoint does not stall the pipeline for hours."""
    f = CACHE / (hashlib.sha1(q.encode("utf8")).hexdigest() + ".json")
    if f.exists():
        return json.loads(f.read_text(encoding="utf8"))
    if STATE["down"]:
        FAILED.append(q)
        return None
    for i in range(tries):
        try:
            r = _s.post(ENDPOINT, data={"query": q}, timeout=(15, 120))
            if r.status_code == 200:
                rows = r.json()["results"]["bindings"]
                f.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf8")
                STATE["consecutive_failures"] = 0
                return rows
        except Exception:
            pass
        time.sleep(5 * (i + 1))
    print("  ! query failed", q[:120], file=sys.stderr)
    FAILED.append(q)
    STATE["consecutive_failures"] += 1
    if STATE["consecutive_failures"] >= 3:
        STATE["down"] = True
        print("  ! DBpedia endpoint unreachable - continuing with cached answers only", file=sys.stderr)
    return None


def lit(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def dbr(title):
    return DBR[iri_part(title)]


# ------------------------------------------------------------------ load local data

TYPE_ORDER = ["MilitaryConflict", "AdministrativeUnit", "State", "Dynasty", "Region", "WrittenWork",
              "Person", "Place"]
COMPATIBLE = {  # vidbo class -> acceptable dbo classes
    "Person": {"Person", "Royalty", "Monarch", "MilitaryPerson", "Politician", "Writer", "OfficeHolder", "Agent"},
    "MilitaryConflict": {"MilitaryConflict", "Event", "SocietalEvent"},
    "AdministrativeUnit": {"Place", "PopulatedPlace", "AdministrativeRegion", "Settlement", "City", "Town",
                           "Village", "Region", "Province"},
    "State": {"Country", "Place", "PopulatedPlace", "FormerCountry", "Agent", "Organisation"},
    "Dynasty": {"Family", "Country", "Agent", "Organisation", "Place", "PopulatedPlace"},
    "Region": {"Place", "PopulatedPlace", "Region", "AdministrativeRegion"},
    "WrittenWork": {"WrittenWork", "Work", "Book", "Poem"},
    "Place": {"Place", "PopulatedPlace", "Settlement", "City", "NaturalPlace", "Building", "ArchitecturalStructure"},
}


def load_entities():
    """title -> {cls, year, en} from the extracted RDF (types incl. a light RDFS closure)."""
    pages = [json.loads(l) for l in (ROOT / "data" / "raw" / "pages.jsonl").open(encoding="utf8")]
    g = Graph()
    for n in ("instance_types", "mappingbased_literals", "tenures"):
        g.parse(RDF_DIR / f"{n}.ttl")
    onto = Graph().parse(ROOT / "ontology" / "vidbo.ttl")
    sup = {}
    for c in onto.subjects(RDF.type, OWL.Class):
        sup[c] = set(onto.transitive_objects(c, RDFS.subClassOf))
    ents = {}
    for p in pages:
        if "disambiguation" in p.get("pageprops", {}):
            continue
        s = res(p["title"])
        classes = set()
        for c in g.objects(s, RDF.type):
            classes |= {str(x).rsplit("/", 1)[-1] for x in sup.get(c, {c})}
        if g.value(s, VIDBO.hasReign) or g.value(s, VIDBO.holdsOffice):
            classes.add("Person")
        cls = next((c for c in TYPE_ORDER if c in classes), None)
        year = None
        for yp in (VIDBO.birthYear, VIDBO.startYear, VIDBO.foundingYear):
            v = g.value(s, yp)
            if v is not None:
                try:
                    year = int(str(v))
                except ValueError:
                    pass
                break
        en = p["langlinks"][0]["title"] if p.get("langlinks") else None
        ents[p["title"]] = {"cls": cls, "year": year, "en": en}
    return ents


# ------------------------------------------------------------------ A. interlanguage links

def verify_interlanguage(ents):
    """Check existence on DBpedia and follow DBpedia redirects."""
    cand = {t: e["en"] for t, e in ents.items() if e["en"]}
    titles = sorted(set(cand.values()))
    exists, redirect = set(), {}

    def old_cache(values):
        """Answers of an earlier query version (wikiPageID-based) still give the redirects."""
        q = f"""SELECT ?s ?r ?typed WHERE {{ VALUES ?s {{ {values} }}
              OPTIONAL {{ ?s <http://dbpedia.org/ontology/wikiPageRedirects> ?r }}
              OPTIONAL {{ ?s <http://dbpedia.org/ontology/wikiPageID> ?typed }} }}"""
        f = CACHE / (hashlib.sha1(q.encode("utf8")).hexdigest() + ".json")
        return json.loads(f.read_text(encoding="utf8")) if f.exists() else None

    def check(chunk):
        values = " ".join(f"<{dbr(t)}>" for t in chunk)
        # the current DBpedia release has no dbo:wikiPageID, so existence = "has an rdfs:label"
        rows = sparql(f"""SELECT ?s ?r ?label WHERE {{ VALUES ?s {{ {values} }}
              OPTIONAL {{ ?s <http://dbpedia.org/ontology/wikiPageRedirects> ?r }}
              OPTIONAL {{ ?s <http://www.w3.org/2000/01/rdf-schema#label> ?label }} }}""")
        if rows is None:
            for b in old_cache(values) or []:
                if "r" in b:
                    redirect[b["s"]["value"]] = b["r"]["value"]
            return False
        for b in rows:
            s = b["s"]["value"]
            if "r" in b:
                redirect[s] = b["r"]["value"]
            elif "label" in b:
                exists.add(s)
        return True

    B = 80
    failed = []
    for i in range(0, len(titles), B):
        chunk = titles[i:i + B]
        if not check(chunk):
            failed.append(chunk)
        if (i // B) % 25 == 0:
            print(f"  verified {i + len(chunk):,}/{len(titles):,}", flush=True)
    unverified = set()
    for chunk in failed:  # second chance, in smaller pieces, after the endpoint had time to recover
        if not STATE["down"]:
            time.sleep(20)
        for j in range(0, len(chunk), 20):
            if not check(chunk[j:j + 20]):
                unverified.update(str(dbr(t)) for t in chunk[j:j + 20])
    g = Graph()
    g.bind("owl", OWL), g.bind("vidbr", VIDBR), g.bind("dbr", DBR)
    stat = Counter()
    for t, en in cand.items():
        u = str(dbr(en))
        if u in redirect:
            u = redirect[u]
            stat["followed_redirect"] += 1
        elif u in unverified:
            # DBpedia unreachable: keep the link (DBpedia derives its URIs from the same English title)
            stat["unverified_endpoint_down"] += 1
        elif u not in exists:
            stat["missing_in_dbpedia"] += 1
            continue
        g.add((res(t), OWL.sameAs, URIRef(u)))
        stat["linked"] += 1
    g.serialize(RDF_DIR / "links_dbpedia_interlanguage.ttl", format="turtle", encoding="utf-8")
    print("interlanguage:", dict(stat))
    return g, stat


# ------------------------------------------------------------------ B. Silk-style matcher

def fold(s):
    s = re.sub(r"\s*\(.*?\)\s*", " ", s)
    return re.sub(r"\s+", " ", unidecode(s).lower()).strip()


def variants(title, cls):
    base = re.sub(r"\s*\(.*?\)\s*$", "", title).strip()
    v = [title, base, unidecode(title), unidecode(base)]
    if cls == "MilitaryConflict":
        for pre in ("Trận ", "Hải chiến ", "Trận chiến "):
            if base.startswith(pre):
                rest = base[len(pre):]
                v += [f"Battle of {rest}", f"Battle of {unidecode(rest)}"]
                paren = re.search(r"\((\d{3,4})\)", title)
                if paren:
                    v += [f"Battle of {rest} ({paren.group(1)})"]
        if base.startswith("Chiến dịch "):
            rest = base[len("Chiến dịch "):]
            v += [f"{rest} campaign", f"{rest} Campaign", f"Operation {rest}", f"Battle of {rest}"]
        if base.startswith("Khởi nghĩa "):
            rest = base[len("Khởi nghĩa "):]
            v += [f"{rest} uprising", f"{rest} Uprising", f"{rest} rebellion"]
    if cls in ("Dynasty", "State") and base.startswith("Nhà "):
        rest = base[4:]
        v += [f"{rest} dynasty", f"{unidecode(rest)} dynasty"]
    if cls == "AdministrativeUnit":
        v += [f"{base} province", f"{base} Province", f"{base} district", f"{base} District",
              f"{base} (ward)", f"{base} commune", f"{base}, Vietnam", f"{base} City"]
    out = []
    for x in v:
        if x and x not in out:
            out.append(x)
    return out


def candidates(batch):
    """batch: list of (title, cls) -> {title: [ {uri,label,types,year} ]}"""
    var2title = {}
    for t, cls in batch:
        for v in variants(t, cls):
            var2title.setdefault(v, set()).add(t)
    values = " ".join(lit(v) + "@en" for v in var2title)
    rows = sparql(f"""SELECT ?s ?l ?t ?y WHERE {{
        VALUES ?l {{ {values} }}
        ?s <http://www.w3.org/2000/01/rdf-schema#label> ?l .
        FILTER NOT EXISTS {{ ?s <http://dbpedia.org/ontology/wikiPageRedirects> ?x }}
        FILTER NOT EXISTS {{ ?s <http://dbpedia.org/ontology/wikiPageDisambiguates> ?d }}
        OPTIONAL {{ ?s a ?t . FILTER(STRSTARTS(STR(?t), "http://dbpedia.org/ontology/")) }}
        OPTIONAL {{ ?s <http://dbpedia.org/ontology/birthYear>|<http://dbpedia.org/ontology/foundingYear> ?y }}
        OPTIONAL {{ ?s <http://dbpedia.org/ontology/birthDate>|<http://dbpedia.org/ontology/date> ?y }}
    }}""")
    found = {}
    for b in rows or []:
        lab = b["l"]["value"]
        uri = b["s"]["value"]
        for t in var2title.get(lab, ()):
            c = found.setdefault(t, {}).setdefault(uri, {"uri": uri, "label": lab, "types": set(), "year": None})
            if "t" in b:
                c["types"].add(b["t"]["value"].rsplit("/", 1)[-1])
            if "y" in b and c["year"] is None:
                m = re.match(r"-?\d{1,4}", b["y"]["value"])
                if m:
                    c["year"] = int(m.group(0))
    return {t: list(d.values()) for t, d in found.items()}


def score(title, ent, cand):
    lab = JaroWinkler.similarity(fold(title), fold(cand["label"]))
    if ent["cls"] and cand["types"]:
        if not (COMPATIBLE.get(ent["cls"], set()) & cand["types"]):
            return 0.0, "type-veto"
        typ = 1.0
    else:
        typ = 0.5
    if ent["year"] is not None and cand["year"] is not None:
        diff = abs(ent["year"] - cand["year"])
        if diff > 2 and ent["cls"] == "Person":
            return 0.0, "year-veto"
        yr = 1.0 if diff == 0 else 0.7 if diff <= 2 else 0.2
    else:
        yr = 0.6
    return round(0.55 * lab + 0.25 * typ + 0.20 * yr, 4), f"label={lab:.2f} type={typ} year={yr}"


def match(items, ents):
    """items: titles -> {title: (best_uri, score, explanation)}"""
    res_ = {}
    B = 40
    for i in range(0, len(items), B):
        batch = [(t, ents[t]["cls"]) for t in items[i:i + B]]
        cands = candidates(batch)
        for t, _ in batch:
            best = None
            for c in cands.get(t, []):
                sc, why = score(t, ents[t], c)
                if not best or sc > best[1]:
                    best = (c["uri"], sc, why)
            if best:
                res_[t] = best
        if (i // B) % 20 == 0:
            print(f"  matched {i + len(batch):,}/{len(items):,}", flush=True)
    return res_


def evaluate(ents, interlinks, n):
    """Run the matcher on entities whose true link is known."""
    truth = {}
    for s, o in interlinks.subject_objects(OWL.sameAs):
        truth[str(s)] = str(o)
    failed_before = len(FAILED)
    pool = [t for t, e in ents.items() if e["cls"] and str(res(t)) in truth]
    random.Random(42).shuffle(pool)
    sample = pool[:n]
    pred = match(sample, ents)
    tp = fp = 0
    by_cls = Counter()
    errors = []
    for t in sample:
        gold = truth[str(res(t))]
        if t in pred and pred[t][1] >= ACCEPT:
            if pred[t][0] == gold:
                tp += 1
                by_cls[ents[t]["cls"] + "_tp"] += 1
            else:
                fp += 1
                by_cls[ents[t]["cls"] + "_fp"] += 1
                errors.append((t, pred[t][0], gold, pred[t][1]))
        by_cls[ents[t]["cls"] + "_n"] += 1
    p = tp / (tp + fp) if tp + fp else 0
    r = tp / len(sample) if sample else 0
    f1 = 2 * p * r / (p + r) if p + r else 0
    ev = {"sample_size": len(sample), "threshold": ACCEPT, "true_positives": tp, "false_positives": fp,
          "precision": round(p, 4), "recall": round(r, 4), "f1": round(f1, 4),
          "per_class": dict(by_cls), "false_positive_examples": errors[:25],
          "incomplete_because_endpoint_failed": len(FAILED) > failed_before}
    print("evaluation:", {k: v for k, v in ev.items() if k not in ("per_class", "false_positive_examples")})
    return ev


def main(eval_n):
    ents = load_entities()
    print(f"{len(ents):,} entities, {sum(1 for e in ents.values() if e['en']):,} with an English language link")
    inter, stat = verify_interlanguage(ents)
    ev = evaluate(ents, inter, eval_n)

    linked = {str(s) for s in inter.subjects(OWL.sameAs)}
    todo = [t for t, e in ents.items() if e["cls"] and str(res(t)) not in linked]
    print(f"silk-style matching for {len(todo):,} entities without a language link")
    pred = match(todo, ents)
    g = Graph()
    g.bind("owl", OWL), g.bind("vidbr", VIDBR), g.bind("dbr", DBR)
    review = []
    for t, (uri, sc, why) in pred.items():
        if sc >= ACCEPT:
            g.add((res(t), OWL.sameAs, URIRef(uri)))
        elif sc >= REVIEW:
            review.append((t, uri, sc, why))
    g.serialize(RDF_DIR / "links_dbpedia_silk.ttl", format="turtle", encoding="utf-8")
    with (LINK_DIR / "review_candidates.tsv").open("w", encoding="utf8") as f:
        f.write("vi_title\tdbpedia_uri\tscore\texplanation\n")
        for row in sorted(review, key=lambda r: -r[2]):
            f.write("\t".join(map(str, row)) + "\n")
    ev["interlanguage"] = dict(stat)
    ev["silk_candidates"] = len(todo)
    ev["silk_accepted"] = len(g)
    ev["silk_review"] = len(review)
    ev["failed_queries"] = len(FAILED)
    ev["endpoint_down_during_run"] = STATE["down"]
    (LINK_DIR / "evaluation.json").write_text(json.dumps(ev, ensure_ascii=False, indent=1), encoding="utf8")
    print(f"silk-style: {len(g)} accepted links, {len(review)} for manual review")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval-sample", type=int, default=1500)
    main(ap.parse_args().eval_sample)
