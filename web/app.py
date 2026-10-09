"""ViDBpedia web front-end (Flask).

  /                      home: statistics, search, example queries
  /sparql                SPARQL endpoint (proxy to Fuseki; HTML query editor when opened in a browser)
  /resource/<name>       Linked Data URI: 303 -> /page/<name> (HTML) or /data/<name>.<ext> (RDF)
  /ontology/<term>       same for ontology terms
  /page/<name>           human readable description of a resource (asserted vs. inferred facts)
  /data/<name>.ttl|.rdf|.jsonld|.nt   machine readable description
  /search?q=             label search
  /ontology              class hierarchy and properties of the vidbo ontology

Run:  python web/app.py  (needs Fuseki on http://localhost:3030, see src/serve.py)
"""
import os
import re
from pathlib import Path
from urllib.parse import unquote

import requests
from flask import Flask, Response, abort, redirect, render_template, request, url_for
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, RDF

ROOT = Path(__file__).resolve().parent.parent
FUSEKI = os.environ.get("VIDBPEDIA_FUSEKI", "http://localhost:3030/vidbpedia/sparql")
BASE = "http://vi.dbpedia.example.org/"
RES, ONT = BASE + "resource/", BASE + "ontology/"
GRAPH = BASE + "graph/"
PREFIXES = {
    "vidbr": RES, "vidbo": ONT, "dbr": "http://dbpedia.org/resource/", "dbo": "http://dbpedia.org/ontology/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#", "xsd": "http://www.w3.org/2001/XMLSchema#",
    "foaf": "http://xmlns.com/foaf/0.1/", "dct": "http://purl.org/dc/terms/", "skos": "http://www.w3.org/2004/02/skos/core#",
    "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#", "schema": "http://schema.org/", "wd": "http://www.wikidata.org/entity/",
    "prov": "http://www.w3.org/ns/prov#",
}
PREFIX_DECL = "\n".join(f"PREFIX {k}: <{v}>" for k, v in PREFIXES.items())
RDF_FORMATS = {"ttl": ("turtle", "text/turtle"), "rdf": ("xml", "application/rdf+xml"),
               "jsonld": ("json-ld", "application/ld+json"), "nt": ("nt", "application/n-triples")}

app = Flask(__name__)


# ------------------------------------------------------------------ helpers

def sparql(query, accept="application/sparql-results+json", timeout=60):
    r = requests.post(FUSEKI, data={"query": query}, headers={"Accept": accept}, timeout=timeout)
    r.raise_for_status()
    r.encoding = "utf-8"  # Fuseki sends text/turtle without a charset; requests would assume Latin-1
    return r


def select(query):
    return sparql(query).json()["results"]["bindings"]


def short(uri):
    for k, v in PREFIXES.items():
        if uri.startswith(v):
            return f"{k}:{uri[len(v):]}"
    return uri


def local_link(uri):
    if uri.startswith(RES):
        return url_for("page", name=uri[len(RES):])
    if uri.startswith(ONT):
        return url_for("ontology_term", term=uri[len(ONT):])
    return uri


def iri(name):
    return "<" + RES + name.replace(" ", "_").replace(">", "%3E") + ">"


app.jinja_env.globals.update(short=short, local_link=local_link)

_onto = None


def onto():
    """The vidbo ontology as an rdflib graph (small; parsed once), used to render anonymous class expressions."""
    global _onto
    if _onto is None:
        _onto = Graph().parse(ROOT / "ontology" / "vidbo.ttl")
    return _onto


def render_expr(node):
    """Description-logic notation for a class expression or property chain, e.g. Person ⊓ ∃hasReign.Reign."""
    g = onto()
    if isinstance(node, URIRef):
        s = short(str(node))
        return s[len("vidbo:"):] if s.startswith("vidbo:") else s
    if isinstance(node, Literal):
        return str(node)
    for op, sym in ((OWL.intersectionOf, " ⊓ "), (OWL.unionOf, " ⊔ ")):
        lst = g.value(node, op)
        if lst is not None:
            return sym.join(wrap(m) for m in Collection(g, lst))
    if (node, RDF.type, OWL.Restriction) in g:
        p = render_expr(g.value(node, OWL.onProperty))
        for pred, fmt in ((OWL.someValuesFrom, "∃{p}.{c}"), (OWL.allValuesFrom, "∀{p}.{c}")):
            c = g.value(node, pred)
            if c is not None:
                return fmt.format(p=p, c=wrap(c))
        v = g.value(node, OWL.hasValue)
        if v is not None:
            return f"∃{p}.{{{render_expr(v)}}}"
        for pred, sym in ((OWL.minQualifiedCardinality, "≥"), (OWL.maxQualifiedCardinality, "≤"),
                          (OWL.qualifiedCardinality, "="), (OWL.minCardinality, "≥"), (OWL.maxCardinality, "≤"),
                          (OWL.cardinality, "=")):
            n = g.value(node, pred)
            if n is not None:
                c = g.value(node, OWL.onClass)
                return f"{sym}{n} {p}" + (f".{wrap(c)}" if c is not None else "")
    c = g.value(node, OWL.complementOf)
    if c is not None:
        return "¬" + wrap(c)
    if g.value(node, RDF.first) is not None:          # an RDF list, e.g. a property chain
        return " ∘ ".join(render_expr(m) for m in Collection(g, node))
    return "[nút rỗng]"


def wrap(node):
    s = render_expr(node)
    return f"({s})" if isinstance(node, BNode) and (" ⊓ " in s or " ⊔ " in s) else s


def load_examples():
    ex = []
    for f in sorted((ROOT / "queries").glob("*.rq")):
        text = f.read_text(encoding="utf8")
        title = next((l.lstrip("# ").strip() for l in text.splitlines() if l.startswith("#")), f.stem)
        ex.append({"id": f.stem, "title": title, "query": text})
    return ex


# ------------------------------------------------------------------ routes

@app.route("/")
def home():
    stats = {}
    try:
        rows = select("""SELECT ?g (COUNT(*) AS ?n) WHERE { GRAPH ?g { ?s ?p ?o } } GROUP BY ?g""")
        stats["graphs"] = {r["g"]["value"].replace(GRAPH, ""): int(r["n"]["value"]) for r in rows}
        rows = select(PREFIX_DECL + """
            SELECT ?c (COUNT(DISTINCT ?s) AS ?n) WHERE { ?s a ?c . FILTER(STRSTARTS(STR(?c), STR(vidbo:))) }
            GROUP BY ?c ORDER BY DESC(?n) LIMIT 24""")
        stats["classes"] = [(r["c"]["value"], int(r["n"]["value"])) for r in rows]
    except Exception as e:  # endpoint not running
        stats["error"] = str(e)
    return render_template("home.html", stats=stats, examples=load_examples())


@app.route("/sparql", methods=["GET", "POST"])
def sparql_endpoint():
    q = request.values.get("query")
    wants_html = "text/html" in request.headers.get("Accept", "") and not request.values.get("format")
    if not q or (wants_html and request.values.get("ui", "1") == "1" and request.method == "GET" and not request.values.get("run")):
        return render_template("sparql.html", query=q or "", examples=load_examples())
    fmt = request.values.get("format") or request.headers.get("Accept", "application/sparql-results+json")
    if "html" in fmt:
        fmt = "application/sparql-results+json"
    if not re.search(r"^\s*PREFIX\s+vidbo:", q, re.I | re.M):
        q = PREFIX_DECL + "\n" + q
    try:
        r = sparql(q, accept=fmt, timeout=120)
    except requests.HTTPError as e:
        return Response(e.response.text, status=e.response.status_code, mimetype="text/plain")
    return Response(r.content, mimetype=r.headers.get("Content-Type", fmt),
                    headers={"Access-Control-Allow-Origin": "*"})


def negotiate(name, html_endpoint):
    accept = request.headers.get("Accept", "")
    for ext, (_, mime) in RDF_FORMATS.items():
        if mime in accept:
            return redirect(url_for("data", name=name, ext=ext), code=303)
    return redirect(url_for(html_endpoint, **({"name": name} if html_endpoint == "page" else {"term": name})), code=303)


@app.route("/resource/<path:name>")
def resource(name):
    return negotiate(name, "page")


@app.route("/data/<path:name>.<ext>")
def data(name, ext):
    if ext not in RDF_FORMATS:
        abort(404)
    fmt, mime = RDF_FORMATS[ext]
    base = ONT if name.startswith("ontology:") else RES
    name = name.split("ontology:", 1)[-1]
    uri = "<" + base + name + ">"
    r = sparql(f"CONSTRUCT {{ {uri} ?p ?o . ?s ?q {uri} }} WHERE {{ {{ {uri} ?p ?o }} UNION {{ ?s ?q {uri} }} }}",
               accept="text/turtle")
    g = Graph().parse(data=r.text, format="turtle")
    for k, v in PREFIXES.items():
        g.bind(k, v)
    return Response(g.serialize(format=fmt), content_type=f"{mime}; charset=utf-8")


@app.route("/page/<path:name>")
def page(name):
    uri = "<" + RES + name + ">"
    rows = select(f"""SELECT ?p ?o ?g WHERE {{ GRAPH ?g {{ {uri} ?p ?o }} }}""")
    if not rows:
        alt = select(f"""PREFIX vidbo: <{ONT}> SELECT ?t WHERE {{ {uri} vidbo:wikiPageRedirects ?t }}""")
        if alt:
            return redirect(local_link(alt[0]["t"]["value"]))
        abort(404)
    incoming = select(f"""SELECT ?s ?p ?label ?g WHERE {{ GRAPH ?g {{ ?s ?p {uri} }}
                          OPTIONAL {{ ?s <http://www.w3.org/2000/01/rdf-schema#label> ?label }}
                          FILTER(?p != <{ONT}wikiPageRedirects>) }} LIMIT 300""")
    labels = {}
    objs = [r["o"]["value"] for r in rows if r["o"]["type"] == "uri" and r["o"]["value"].startswith(RES)]
    if objs:
        values = " ".join(f"<{o}>" for o in set(objs[:400]))
        for r in select(f"""SELECT ?s ?l WHERE {{ VALUES ?s {{ {values} }} ?s <http://www.w3.org/2000/01/rdf-schema#label> ?l }}"""):
            labels[r["s"]["value"]] = r["l"]["value"]
    props = {}
    for r in rows:
        p = r["p"]["value"]
        o = r["o"]
        entry = {"value": o["value"], "type": o["type"], "lang": o.get("xml:lang"),
                 "datatype": o.get("datatype"), "graph": r["g"]["value"].replace(GRAPH, ""),
                 "label": labels.get(o["value"])}
        props.setdefault(p, []).append(entry)
    def first(p):
        v = props.get(p)
        return v[0]["value"] if v else None
    title = unquote(name).replace("_", " ")
    info = {
        "uri": RES + name, "title": title,
        "abstract": first(ONT + "abstract"),
        "lat": first("http://www.w3.org/2003/01/geo/wgs84_pos#lat"),
        "long": first("http://www.w3.org/2003/01/geo/wgs84_pos#long"),
        "wiki": first("http://xmlns.com/foaf/0.1/isPrimaryTopicOf"),
    }
    order = sorted(props, key=lambda p: (p != PREFIXES["rdf"] + "type", not p.startswith(ONT), short(p)))
    return render_template("page.html", info=info, props=props, order=order, incoming=incoming, name=name)


@app.route("/search")
def search():
    q = (request.args.get("q") or "").strip()
    results = []
    if q:
        safe = q.replace("\\", "").replace('"', "")
        results = select(PREFIX_DECL + f"""
            SELECT ?s ?label (SAMPLE(?c) AS ?cls) WHERE {{
              GRAPH <{GRAPH}data> {{ ?s rdfs:label ?label }}
              FILTER(CONTAINS(LCASE(STR(?label)), LCASE("{safe}")))
              FILTER NOT EXISTS {{ ?s a vidbo:Tenure }}   # reign/office nodes are reached from their person
              OPTIONAL {{ GRAPH <{GRAPH}data> {{ ?s a ?c }} }}
            }} GROUP BY ?s ?label ORDER BY STRLEN(STR(?label)) LIMIT 100""")
    return render_template("search.html", q=q, results=results)


@app.route("/ontology")
def ontology():
    classes = select(PREFIX_DECL + f"""
        SELECT ?c ?label ?super (COUNT(DISTINCT ?i) AS ?n) WHERE {{
          GRAPH <{GRAPH}ontology> {{ ?c a owl:Class . FILTER(isIRI(?c) && STRSTARTS(STR(?c), STR(vidbo:)))
             OPTIONAL {{ ?c rdfs:label ?label FILTER(lang(?label)="vi") }}
             OPTIONAL {{ ?c rdfs:subClassOf ?super FILTER(STRSTARTS(STR(?super), STR(vidbo:))) }} }}
          OPTIONAL {{ ?i a ?c }}
        }} GROUP BY ?c ?label ?super ORDER BY ?c""")
    props = select(PREFIX_DECL + f"""
        SELECT ?p ?type ?label (GROUP_CONCAT(DISTINCT ?ch; separator=", ") AS ?chars) WHERE {{
          GRAPH <{GRAPH}ontology> {{ ?p a ?type . FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty))
             FILTER(STRSTARTS(STR(?p), STR(vidbo:)))
             OPTIONAL {{ ?p rdfs:label ?label FILTER(lang(?label)="vi") }}
             OPTIONAL {{ ?p a ?ch FILTER(?ch IN (owl:TransitiveProperty, owl:SymmetricProperty, owl:FunctionalProperty,
                          owl:InverseFunctionalProperty, owl:IrreflexiveProperty, owl:AsymmetricProperty)) }} }}
        }} GROUP BY ?p ?type ?label ORDER BY ?type ?p""")
    return render_template("ontology.html", classes=classes, props=props)


@app.route("/ontology/<path:term>")
def ontology_term(term):
    accept = request.headers.get("Accept", "")
    for ext, (_, mime) in RDF_FORMATS.items():
        if mime in accept:
            return redirect(url_for("data", name="ontology:" + term, ext=ext), code=303)
    uri = "<" + ONT + term + ">"
    rows = select(f"SELECT ?p ?o ?g WHERE {{ GRAPH ?g {{ {uri} ?p ?o }} }}")
    usage = select(f"SELECT (COUNT(*) AS ?n) WHERE {{ {{ ?s {uri} ?o }} UNION {{ ?s a {uri} }} }}")
    props = {}
    for r in rows:
        props.setdefault(r["p"]["value"], []).append({"value": r["o"]["value"], "type": r["o"]["type"],
                                                      "lang": r["o"].get("xml:lang"), "datatype": r["o"].get("datatype"),
                                                      "graph": r["g"]["value"].replace(GRAPH, ""), "label": None})
    # anonymous class expressions / property chains: show them as formulas instead of blank nodes
    for p, entries in props.items():
        if any(e["type"] == "bnode" for e in entries):
            exprs = [render_expr(o) for o in onto().objects(URIRef(ONT + term), URIRef(p)) if isinstance(o, BNode)]
            named = [e for e in entries if e["type"] != "bnode"]
            props[p] = [{"value": x, "type": "expr", "graph": "ontology", "label": None, "lang": None, "datatype": None}
                        for x in exprs] + named
    info = {"uri": ONT + term, "title": "vidbo:" + term, "abstract": None, "lat": None, "long": None, "wiki": None,
            "usage": usage[0]["n"]["value"] if usage else 0}
    order = sorted(props, key=short)
    return render_template("page.html", info=info, props=props, order=order, incoming=[], name=term)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=False)
