"""Step 3b - Reasoning: materialise the OWL 2 RL consequences of the ontology + a rule layer.

The reasoner is generic: it reads the axioms from ontology/vidbo.ttl and applies the
OWL 2 RL/RDF rules listed below until a fix-point is reached (forward chaining).

    schema   scm-sco, scm-eqc1/2, scm-spo, scm-eqp1/2       (class / property hierarchies)
    classes  cax-sco, cax-eqc1/2                             (type propagation)
             cls-int1, cls-int2, cls-uni                     (intersection / union)
             cls-svf1 (object & data), cls-hv1, cls-hv2      (someValuesFrom, hasValue)
    props    prp-dom, prp-rng, prp-spo1, prp-eqp1/2, prp-inv1/2, prp-symp, prp-trp, prp-spo2 (chains)
    checks   cax-dw / cax-adc (disjoint), prp-irp, prp-asyp, prp-fp on literals, prp-key duplicates
             (reported as inconsistencies instead of deriving owl:sameAs / owl:Nothing)

Rule layer (rules/*.rq, SPARQL CONSTRUCT) handles what OWL cannot express
(x != y, arithmetic, date comparison). OWL closure -> rules -> OWL closure.

Outputs: data/rdf/inferred.ttl              (only NEW triples)
         data/rdf/consistency_report.json  (violations found by the reasoner)
         data/rdf/reasoning_stats.json

Usage:   python src/reason.py
"""
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF, RDFS, XSD

ROOT = Path(__file__).resolve().parent.parent
RDF_DIR = ROOT / "data" / "rdf"
RULES = ROOT / "rules"
DATASETS = ["instance_types", "mappingbased_objects", "mappingbased_literals", "tenures"]


def rdf_list(g, node):
    return list(Collection(g, node)) if node is not None else []


class Ontology:
    """Compiled view of the TBox."""

    def __init__(self, g):
        self.g = g
        self.sub = defaultdict(set)        # class -> direct superclasses (incl. restriction nodes)
        self.subp = defaultdict(set)       # property -> direct superproperties
        self.inverse = defaultdict(set)
        self.symmetric, self.transitive = set(), set()
        self.irreflexive, self.asymmetric, self.functional = set(), set(), set()
        self.domain, self.range = defaultdict(set), defaultdict(set)
        self.chains = []                   # (p1, p2, p)
        self.intersections = {}            # node -> [members]
        self.svf, self.hv = {}, {}         # restriction -> (p, C) / (p, v)
        self.disjoint = []                 # list of member lists
        self.keys = {}                     # class -> [props]

        for c, d in g.subject_objects(RDFS.subClassOf):
            self.sub[c].add(d)
        for c, d in g.subject_objects(OWL.equivalentClass):
            self.sub[c].add(d), self.sub[d].add(c)
        for p, q in g.subject_objects(RDFS.subPropertyOf):
            self.subp[p].add(q)
        for p, q in g.subject_objects(OWL.equivalentProperty):
            self.subp[p].add(q), self.subp[q].add(p)
        for p, q in g.subject_objects(OWL.inverseOf):
            self.inverse[p].add(q), self.inverse[q].add(p)
        for kind, target in ((OWL.SymmetricProperty, self.symmetric), (OWL.TransitiveProperty, self.transitive),
                             (OWL.IrreflexiveProperty, self.irreflexive), (OWL.AsymmetricProperty, self.asymmetric),
                             (OWL.FunctionalProperty, self.functional)):
            target.update(g.subjects(RDF.type, kind))
        for p, c in g.subject_objects(RDFS.domain):
            self.domain[p].add(c)
        for p, c in g.subject_objects(RDFS.range):
            self.range[p].add(c)
        for p, lst in g.subject_objects(OWL.propertyChainAxiom):
            chain = rdf_list(g, lst)
            if len(chain) == 2:
                self.chains.append((chain[0], chain[1], p))
        for n, lst in g.subject_objects(OWL.intersectionOf):
            members = rdf_list(g, lst)
            self.intersections[n] = members
            for m in members:                        # cls-int2 as subclass axioms
                self.sub[n].add(m)
        for n, lst in g.subject_objects(OWL.unionOf):
            for m in rdf_list(g, lst):               # cls-uni
                self.sub[m].add(n)
        for r in g.subjects(RDF.type, OWL.Restriction):
            p = g.value(r, OWL.onProperty)
            if g.value(r, OWL.someValuesFrom) is not None:
                self.svf[r] = (p, g.value(r, OWL.someValuesFrom))
            if g.value(r, OWL.hasValue) is not None:
                self.hv[r] = (p, g.value(r, OWL.hasValue))
        for n in g.subjects(RDF.type, OWL.AllDisjointClasses):
            self.disjoint.append(rdf_list(g, g.value(n, OWL.members)))
        for a, b in g.subject_objects(OWL.disjointWith):
            self.disjoint.append([a, b])
        for c, lst in g.subject_objects(OWL.hasKey):
            self.keys[c] = rdf_list(g, lst)

        # inverse of a sub-property relation: if p ⊑ q and p inv p', q inv q' then p' ⊑ q'
        self.sup_closure = {c: self._closure(c, self.sub) for c in list(self.sub)}
        self.supp_closure = {p: self._closure(p, self.subp) for p in list(self.subp)}

    @staticmethod
    def _closure(x, edges):
        seen, todo = set(), [x]
        while todo:
            y = todo.pop()
            for z in edges.get(y, ()):
                if z not in seen:
                    seen.add(z)
                    todo.append(z)
        seen.discard(x)
        return seen

    def supers(self, c):
        return self.sup_closure.get(c, frozenset())

    def superprops(self, p):
        return self.supp_closure.get(p, frozenset())


class Reasoner:
    def __init__(self, onto):
        self.o = onto
        self.props = defaultdict(set)      # p -> {(s, o)}
        self.types = defaultdict(set)      # s -> {C}
        self.literal_props = set()

    def load(self, g):
        for s, p, o in g:
            if p == RDF.type:
                self.types[s].add(o)
            else:
                self.props[p].add((s, o))

    def add_type(self, s, c):
        if c not in self.types[s]:
            self.types[s].add(c)
            return 1
        return 0

    # ------------------------------------------------------------------ one round
    def round(self):
        o = self.o
        new = 0
        # prp-spo1 / prp-eqp
        for p in list(self.props):
            pairs = self.props[p]
            for q in o.superprops(p):
                before = len(self.props[q])
                self.props[q] |= pairs
                new += len(self.props[q]) - before
        # prp-inv
        for p in list(self.props):
            for q in o.inverse.get(p, ()):
                inv = {(b, a) for a, b in self.props[p] if not isinstance(b, Literal)}
                before = len(self.props[q])
                self.props[q] |= inv
                new += len(self.props[q]) - before
        # prp-symp
        for p in o.symmetric:
            pairs = self.props.get(p)
            if pairs:
                before = len(pairs)
                pairs |= {(b, a) for a, b in pairs}
                new += len(pairs) - before
        # prp-trp (full transitive closure)
        for p in o.transitive:
            pairs = self.props.get(p)
            if not pairs:
                continue
            succ = defaultdict(set)
            for a, b in pairs:
                succ[a].add(b)
            closure = set()
            for a in list(succ):
                seen, todo = set(), list(succ[a])
                while todo:
                    x = todo.pop()
                    if x in seen:
                        continue
                    seen.add(x)
                    todo.extend(succ.get(x, ()))
                closure |= {(a, x) for x in seen if x != a}
            before = len(pairs)
            pairs |= closure
            new += len(pairs) - before
        # prp-spo2 (property chains of length 2)
        for p1, p2, p in o.chains:
            by_s = defaultdict(set)
            for a, b in self.props.get(p2, ()):
                by_s[a].add(b)
            derived = {(x, z) for x, y in self.props.get(p1, ()) for z in by_s.get(y, ()) if x != z}
            before = len(self.props[p])
            self.props[p] |= derived
            new += len(self.props[p]) - before
        # prp-dom / prp-rng
        for p, pairs in list(self.props.items()):
            doms, rngs = o.domain.get(p, ()), o.range.get(p, ())
            if doms:
                for a, _ in pairs:
                    for c in doms:
                        new += self.add_type(a, c)
            if rngs:
                for _, b in pairs:
                    if not isinstance(b, Literal):
                        for c in rngs:
                            if not str(c).startswith(str(XSD)):
                                new += self.add_type(b, c)
        # cls-hv1 / cls-hv2
        for r, (p, v) in o.hv.items():
            for a, b in self.props.get(p, ()):
                if b == v or (isinstance(b, Literal) and isinstance(v, Literal) and b.eq(v)):
                    new += self.add_type(a, r)
            for s, ts in self.types.items():
                if r in ts and (s, v) not in self.props[p]:
                    self.props[p].add((s, v))
                    new += 1
        # cls-svf1 (object and datatype restrictions)
        for r, (p, c) in o.svf.items():
            for a, b in self.props.get(p, ()):
                if isinstance(b, Literal):
                    if b.datatype == c or c == RDFS.Literal:
                        new += self.add_type(a, r)
                elif c == OWL.Thing or c in self.types.get(b, ()):
                    new += self.add_type(a, r)
        # cax-sco / cax-eqc (type propagation through the class hierarchy)
        for s in list(self.types):
            ts = self.types[s]
            extra = set()
            for c in ts:
                extra |= o.supers(c)
            if not extra <= ts:
                new += len(extra - ts)
                ts |= extra
        # cls-int1 (all members of an intersection -> the intersection)
        for n, members in o.intersections.items():
            for s, ts in self.types.items():
                if n not in ts and all(m in ts for m in members):
                    ts.add(n)
                    new += 1
        return new

    def closure(self, label):
        t = time.time()
        total, i = 0, 0
        while True:
            i += 1
            n = self.round()
            total += n
            print(f"  [{label}] round {i}: +{n:,}", flush=True)
            if n == 0:
                break
        print(f"  [{label}] fix-point after {i} rounds, {time.time() - t:.0f}s", flush=True)
        return total

    def graph(self, named_only=True):
        g = Graph()
        for s, ts in self.types.items():
            if isinstance(s, BNode):
                continue
            for c in ts:
                if isinstance(c, URIRef):
                    g.add((s, RDF.type, c))
        for p, pairs in self.props.items():
            for a, b in pairs:
                if not isinstance(a, BNode) and not isinstance(b, BNode):
                    g.add((a, p, b))
        return g

    # ------------------------------------------------------------------ consistency
    def check(self):
        o = self.o
        report = defaultdict(list)
        for members in o.disjoint:
            ms = set(members)
            for s, ts in self.types.items():
                hit = sorted(str(m).rsplit("/", 1)[-1] for m in ms & ts)
                if len(hit) > 1:
                    report["disjoint_classes"].append({"individual": str(s), "classes": hit})
        for p in o.irreflexive:
            for a, b in self.props.get(p, ()):
                if a == b:
                    report["irreflexive"].append({"individual": str(a), "property": str(p)})
        # Transitive properties cannot be declared irreflexive in OWL 2 DL (non-simple), so cycles
        # (a locatedIn b locatedIn a) are detected here: they signal a wrongly oriented edge.
        for p in o.transitive:
            pairs = self.props.get(p, set())
            for a, b in pairs:
                if (b, a) in pairs and str(a) < str(b):
                    report["transitive_cycle"].append({"a": str(a), "b": str(b), "property": str(p).rsplit("/", 1)[-1]})
        for p in o.asymmetric:
            pairs = self.props.get(p, set())
            for a, b in pairs:
                if (b, a) in pairs and str(a) < str(b):
                    report["asymmetric"].append({"a": str(a), "b": str(b), "property": str(p)})
        for p in o.functional:
            vals = defaultdict(set)
            for a, b in self.props.get(p, ()):
                vals[a].add(b)
            for a, vs in vals.items():
                if len(vs) > 1:
                    kind = "functional_datatype" if all(isinstance(v, Literal) for v in vs) else "functional_object"
                    report[kind].append({"individual": str(a), "property": str(p).rsplit("/", 1)[-1],
                                         "values": sorted(map(str, vs))[:5]})
        for c, keys in o.keys.items():
            seen = defaultdict(list)
            members = [s for s, ts in self.types.items() if c in ts]
            for k in keys:
                vals = defaultdict(set)
                for a, b in self.props.get(k, ()):
                    vals[a].add(str(b))
                for s in members:
                    for v in vals.get(s, ()):
                        seen[v].append(str(s))
            for v, ss in seen.items():
                if len(ss) > 1:
                    report["has_key_duplicates"].append({"key": v, "individuals": ss[:5]})
        return report


def run_rules(r, base_graph):
    """Apply SPARQL CONSTRUCT rules on a compact graph with only the predicates they need."""
    V = "http://vi.dbpedia.example.org/ontology/"
    needed = {URIRef(V + n) for n in ("hasParent", "birthYear", "deathYear", "birthDate", "deathDate",
                                       "hasReign", "startYear", "endYear", "area", "population",
                                       "memberOfDynasty", "combatant", "tenureDynasty")}
    g = Graph()
    for p in needed:
        for a, b in r.props.get(p, ()):
            g.add((a, p, b))
    for s, ts in r.types.items():
        for c in ts:
            if isinstance(c, URIRef) and str(c) in (V + "Monarch", V + "MilitaryConflict", V + "Person"):
                g.add((s, RDF.type, c))
    out = Graph()
    stats = {}
    for f in sorted(RULES.glob("*.rq")):
        res = g.query(f.read_text(encoding="utf8"))
        n = 0
        for t in res:
            out.add(t)
            n += 1
        stats[f.stem] = n
        print(f"  rule {f.stem}: {n:,} triples", flush=True)
    return out, stats


def main():
    t0 = time.time()
    onto_g = Graph().parse(ROOT / "ontology" / "vidbo.ttl")
    onto = Ontology(onto_g)
    data = Graph()
    for n in DATASETS:
        data.parse(RDF_DIR / f"{n}.ttl")
    print(f"ontology {len(onto_g):,} triples, data {len(data):,} triples ({time.time() - t0:.0f}s)")

    r = Reasoner(onto)
    r.load(data)
    r.closure("OWL RL #1")
    rule_triples, rule_stats = run_rules(r, data)
    r.load(rule_triples)
    r.closure("OWL RL #2")

    full = r.graph()
    inferred = full - data
    inferred.bind("vidbo", "http://vi.dbpedia.example.org/ontology/")
    inferred.bind("vidbr", "http://vi.dbpedia.example.org/resource/")
    inferred.bind("dbo", "http://dbpedia.org/ontology/")
    inferred.serialize(RDF_DIR / "inferred.ttl", format="turtle", encoding="utf-8")

    by_pred = Counter()
    for s, p, o in inferred:
        key = str(o) if p == RDF.type else str(p)
        by_pred[key.replace("http://vi.dbpedia.example.org/ontology/", "vidbo:")
                   .replace("http://dbpedia.org/ontology/", "dbo:")] += 1
    report = r.check()
    summary = {k: len(v) for k, v in report.items()}
    (RDF_DIR / "consistency_report.json").write_text(json.dumps(
        {"summary": summary, "details": {k: v[:200] for k, v in report.items()}}, ensure_ascii=False, indent=1),
        encoding="utf8")
    stats = {"asserted": len(data), "inferred": len(inferred), "rules": rule_stats,
             "inferred_by_predicate_or_class": dict(by_pred.most_common(80)),
             "violations": summary, "seconds": round(time.time() - t0)}
    (RDF_DIR / "reasoning_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf8")
    print(f"asserted {len(data):,}  inferred {len(inferred):,}  ({time.time() - t0:.0f}s)")
    print("violations:", summary)
    for k, v in by_pred.most_common(30):
        print(f"   {v:>8,}  {k}")


if __name__ == "__main__":
    main()
