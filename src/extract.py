"""Step 3 - Transform collected Wikipedia pages into RDF (4-star Linked Data).

Reads   data/raw/pages.jsonl + mappings/infobox_mappings.yaml
Writes  data/rdf/*.ttl, split into DBpedia-like datasets:
        labels, instance_types, mappingbased_objects, mappingbased_literals,
        tenures, abstracts, article_categories, geo_coordinates, page_metadata,
        redirects, wikidata_links

Usage:  python src/extract.py
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import mwparserfromhell as mw
import yaml
from rdflib import RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import DCTERMS, FOAF, OWL, SKOS, PROV

sys.path.insert(0, str(Path(__file__).parent))
from parsers import (abstract_of, clean_text, fmt_year, norm_title, parse_date,  # noqa: E402
                     parse_number, parse_period, wikilinks_in)

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "data" / "raw" / "pages.jsonl"
OUT = ROOT / "data" / "rdf"
OUT.mkdir(parents=True, exist_ok=True)

BASE = "http://vi.dbpedia.example.org/"
VIDBO = Namespace(BASE + "ontology/")
VIDBR = Namespace(BASE + "resource/")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
WD = Namespace("http://www.wikidata.org/entity/")
WIKI = "https://vi.wikipedia.org/wiki/"

IRI_UNSAFE = re.compile(r'[\s<>"{}|\\^`#?%\[\]]')


def iri_part(title):
    t = title.replace(" ", "_")
    return IRI_UNSAFE.sub(lambda m: "%{:02X}".format(ord(m.group(0))), t)


def res(title):
    return VIDBR[iri_part(title)]


# ------------------------------------------------------------------ mappings

def _expand(props):
    out = {}
    for k, spec in (props or {}).items():
        for name in str(k).split("|"):
            out[name.strip().lower()] = spec
    return out


def load_mappings(path=ROOT / "mappings" / "infobox_mappings.yaml"):
    raw = yaml.safe_load(Path(path).read_text(encoding="utf8"))
    m = {"by_name": {}, "templates": {}}
    for key, t in raw["templates"].items():
        tm = {"key": key, "class": t["class"], "title_classes": t.get("title_classes", {}),
              "properties": _expand(t.get("properties"))}
        if "tenure" in t:
            tm["tenure"] = dict(t["tenure"], fields=_expand(t["tenure"]["fields"]))
        m["templates"][key] = tm
        for n in t["names"]:
            m["by_name"][n.strip().lower()] = tm
    m["admin_types"] = raw["admin_types"]
    m["first_level_cities"] = set(raw["first_level_cities"])
    m["category_types"] = raw["category_types"]
    m["royal_title_re"] = re.compile(raw["royal_title_regex"], re.I)
    names = sorted(m["by_name"], key=len, reverse=True)
    m["name_re"] = re.compile(r"\{\{\s*(?:" + "|".join(re.escape(n).replace(r"\ ", r"[ _]+") for n in names)
                              + r")\s*(?=\||\}\}|\n|<!--)", re.I)
    return m


def infobox_source(text, maps):
    """Cut the wikitext of the first mapped infobox (balanced {{ }}) out of an article.

    Parsing only this fragment is ~50x faster than parsing the whole article."""
    for m in maps["name_re"].finditer(text):
        depth, i, n = 0, m.start(), len(text)
        while i < n - 1:
            two = text[i:i + 2]
            if two == "{{":
                depth += 1
                i += 2
            elif two == "}}":
                depth -= 1
                i += 2
                if depth == 0:
                    return text[m.start():i]
            else:
                i += 1
    return None


def object_param_names(tm):
    names = {k for k, v in tm["properties"].items() if v.get("kind") == "object"}
    if "tenure" in tm:
        names |= {k for k, v in tm["tenure"]["fields"].items() if v.get("kind") == "object"}
    return names


def find_infobox(code, maps):
    for recursive in (False, True):
        for tpl in code.filter_templates(recursive=recursive):
            n = str(tpl.name).strip().replace("_", " ").lower()
            if n in maps["by_name"]:
                return tpl, maps["by_name"][n]
    return None


SUFFIX = re.compile(r"^(.*?)[\s_]*(\d+)$")


def split_param(name):
    """'tại vị 2' -> ('tại vị', '2'); 'combatant1' -> ('combatant', '1'); 'tên' -> ('tên', '')."""
    m = SUFFIX.match(name)
    if m and m.group(1):
        return m.group(1).strip(), m.group(2)
    return name, ""


def lookup(props, name):
    """Return (spec, group) for an infobox param name; exact name first, then numbered base."""
    if name in props:
        return props[name], ""
    base, num = split_param(name)
    if num and base in props:
        return props[base], num
    return None, None


# ------------------------------------------------------------------ extraction

class Extractor:
    def __init__(self):
        self.maps = load_mappings()
        self.alias = {}            # redirect title -> canonical title
        self.known = set()         # titles that we have pages for
        self.g = {n: Graph() for n in ("labels", "instance_types", "mappingbased_objects",
                                       "mappingbased_literals", "tenures", "abstracts",
                                       "article_categories", "geo_coordinates", "page_metadata",
                                       "redirects", "wikidata_links")}
        for g in self.g.values():
            for p, ns in (("vidbo", VIDBO), ("vidbr", VIDBR), ("geo", GEO), ("wd", WD), ("foaf", FOAF),
                          ("dct", DCTERMS), ("skos", SKOS), ("prov", PROV), ("owl", OWL)):
                g.bind(p, ns)
        self.stats = Counter()
        self.param_usage = defaultdict(Counter)

    def resolve(self, title):
        t = norm_title(title)
        seen = set()
        while t in self.alias and t not in seen:
            seen.add(t)
            t = self.alias[t]
        return t

    def obj(self, title):
        return res(self.resolve(title))

    # -------------------------------------------------------------- values
    def add_value(self, s, spec, value, tm, ctx):
        kind = spec.get("kind")
        prop = spec.get("prop")
        G_O, G_L = self.g["mappingbased_objects"], self.g["mappingbased_literals"]
        if kind == "object":
            links = wikilinks_in(value)
            if spec.get("max"):
                links = links[: spec["max"]]
            if spec.get("if_many") and len(links) > 2:
                # a place lies in ONE unit per level; a long list (a region listing its provinces)
                # names the units it CONTAINS
                prop = spec["if_many"]
            for t in links:
                o = self.obj(t)
                if o != s:
                    G_O.add((s, VIDBO[prop], o))
                    self.stats["object"] += 1
            return links
        if kind == "literal" or kind == "string":
            txt = clean_text(value)
            if txt and len(txt) <= 600:
                lit = Literal(txt, lang="vi") if kind == "literal" else Literal(txt)
                G_L.add((s, VIDBO[prop], lit))
                self.stats["literal"] += 1
            return txt
        if kind in ("date", "year"):
            d = parse_date(value)
            if not d:
                return None
            y, mo, da = d
            if kind == "date" and mo and da and y > 0:
                G_L.add((s, VIDBO[prop], Literal(f"{y:04d}-{mo:02d}-{da:02d}", datatype=XSD.date)))
            yp = spec.get("year_prop") or (prop if kind == "year" else None)
            if yp:
                G_L.add((s, VIDBO[yp], Literal(fmt_year(y), datatype=XSD.gYear)))
            self.stats["date"] += 1
            return d
        if kind in ("integer", "decimal"):
            n = parse_number(value, integer=(kind == "integer"))
            if n is not None and n >= 0:
                dt = XSD.integer if kind == "integer" else XSD.decimal
                G_L.add((s, VIDBO[prop], Literal(int(n) if kind == "integer" else n, datatype=dt)))
                self.stats["number"] += 1
            return n
        if kind == "period":
            start, end = parse_period(value)
            self.add_dates(s, start, end, spec.get("start_prop", "startDate"), spec.get("end_prop", "endDate"))
            return (start, end)
        if kind in ("lat", "long"):
            n = parse_number(clean_text(value).replace(",", "."), integer=False)
            if n is not None:
                self.g["geo_coordinates"].add((s, GEO[kind], Literal(n, datatype=XSD.float)))
            return n
        if kind == "adminType":
            return clean_text(value).lower()
        return None

    def add_dates(self, s, start, end, sp="startDate", ep="endDate"):
        G = self.g["mappingbased_literals"]
        for d, p, yp in ((start, sp, "startYear"), (end, ep, "endYear")):
            if not d:
                continue
            y, mo, da = d
            if mo and da and y > 0:
                G.add((s, VIDBO[p], Literal(f"{y:04d}-{mo:02d}-{da:02d}", datatype=XSD.date)))
            G.add((s, VIDBO[yp], Literal(fmt_year(y), datatype=XSD.gYear)))

    # -------------------------------------------------------------- page
    def page(self, p):
        title = p["title"]
        s = res(title)
        G = self.g
        wikitext = p["wikitext"]
        if "disambiguation" in p.get("pageprops", {}):
            self.stats["skipped_disambiguation"] += 1
            return
        self.stats["pages"] += 1

        # labels, metadata, provenance
        G["labels"].add((s, RDFS.label, Literal(title, lang="vi")))
        md = G["page_metadata"]
        md.add((s, FOAF.isPrimaryTopicOf, URIRef(WIKI + iri_part(title))))
        md.add((URIRef(WIKI + iri_part(title)), FOAF.primaryTopic, s))
        if p.get("pageid"):
            md.add((s, VIDBO.wikiPageID, Literal(p["pageid"], datatype=XSD.integer)))
        if p.get("revid"):
            md.add((s, VIDBO.wikiPageRevisionID, Literal(p["revid"], datatype=XSD.integer)))
            md.add((s, PROV.wasDerivedFrom, URIRef(f"{WIKI}{iri_part(title)}?oldid={p['revid']}")))
        qid = p.get("pageprops", {}).get("wikibase_item")
        if qid:
            G["wikidata_links"].add((s, OWL.sameAs, WD[qid]))
            G["wikidata_links"].add((s, VIDBO.wikidataID, Literal(qid)))
        ab = abstract_of(wikitext)
        if ab:
            G["abstracts"].add((s, VIDBO.abstract, Literal(ab, lang="vi")))
            G["abstracts"].add((s, RDFS.comment, Literal(ab.split(". ")[0].rstrip(".") + ".", lang="vi")))

        # categories -> dct:subject + category based typing
        for c in p.get("categories", []):
            ct = c["title"]
            cname = ct.split(":", 1)[1]
            cu = VIDBR[iri_part("Thể_loại:" + cname)]
            G["article_categories"].add((s, DCTERMS.subject, cu))
            G["article_categories"].add((cu, RDF.type, SKOS.Concept))
            G["article_categories"].add((cu, SKOS.prefLabel, Literal(cname, lang="vi")))
            for pat, cls in self.maps["category_types"].items():
                if pat in cname:
                    G["instance_types"].add((s, RDF.type, VIDBO[cls]))

        # coordinates from the API (primary coordinate of the article)
        for co in p.get("coordinates", []) or []:
            if co.get("primary") and co.get("globe", "earth") == "earth":
                G["geo_coordinates"].add((s, GEO.lat, Literal(co["lat"], datatype=XSD.float)))
                G["geo_coordinates"].add((s, GEO.long, Literal(co["lon"], datatype=XSD.float)))
                G["geo_coordinates"].add((s, RDF.type, GEO.SpatialThing))
                break

        # infobox
        src = infobox_source(wikitext, self.maps)
        hit = find_infobox(mw.parse(src), self.maps) if src else None
        if not hit:
            return
        tpl, tm = hit
        self.stats["infobox_" + tm["key"]] += 1
        G["instance_types"].add((s, RDF.type, VIDBO[tm["class"]]))
        G["page_metadata"].add((s, VIDBO.infoboxTemplate, Literal(str(tpl.name).strip())))
        for pat, cls in tm["title_classes"].items():
            if re.search(pat, title):
                G["instance_types"].add((s, RDF.type, VIDBO[cls]))
                break

        tenure_groups = defaultdict(dict)
        admin_type, admin_code = None, None
        person_dynasties = []
        for par in tpl.params:
            name = str(par.name).strip().lower()
            if not str(par.value).strip():
                continue
            spec, group = lookup(tm["properties"], name)
            if spec:
                self.param_usage[tm["key"]][name] += 1
                r = self.add_value(s, spec, par.value, tm, {})
                if spec.get("kind") == "adminType" and r and admin_type is None:
                    admin_type = r
                if spec.get("prop") == "adminCode" and r:
                    admin_code = re.sub(r"\D", "", r)
                if spec.get("prop") == "memberOfDynasty" and r:
                    person_dynasties += r
                continue
            if "tenure" in tm:
                spec, group = lookup(tm["tenure"]["fields"], name)
                if spec:
                    self.param_usage[tm["key"]][name] += 1
                    tenure_groups[group or "0"][name] = (spec, par.value)

        if admin_type is not None:
            self.admin_class(s, title, admin_type)
        elif tm["key"] == "vn_admin" and admin_code:
            # no unit type given: the length of the official code tells the level (2 / 3 / 5 digits)
            level = {2: 1, 3: 2, 5: 3}.get(len(admin_code))
            if level:
                self.g["mappingbased_literals"].add((s, VIDBO.adminLevel, Literal(level, datatype=XSD.integer)))
        if "tenure" in tm:
            self.tenures(s, title, tm, tenure_groups)

    def admin_class(self, s, title, t):
        G = self.g["instance_types"]
        t = re.sub(r"\s+", " ", t).strip()
        if t == "thành phố" and title.split(" (")[0] in self.maps["first_level_cities"]:
            t = "thành phố trực thuộc trung ương"
        for word, spec in sorted(self.maps["admin_types"].items(), key=lambda kv: -len(kv[0])):
            if t.startswith(word):
                G.add((s, RDF.type, VIDBO[spec["class"]]))
                self.g["mappingbased_literals"].add((s, VIDBO.adminLevel, Literal(spec["level"], datatype=XSD.integer)))
                return

    def tenures(self, person, title, tm, groups):
        cfg = tm["tenure"]
        G = self.g["tenures"]
        royal_re = self.maps["royal_title_re"]
        for gid, fields in sorted(groups.items()):
            pos_text, pos_links, start, end = None, [], None, None
            tenure_objects = []
            for name, (spec, value) in fields.items():
                k = spec.get("kind")
                if k == "object" and spec.get("attach") == "person":
                    self.add_value(person, spec, value, tm, {})
                elif k == "object":
                    tenure_objects.append((spec["prop"], wikilinks_in(value)))
                elif k == "literal":
                    pos_text = clean_text(value)
                    pos_links = wikilinks_in(value)
                elif k == "period":
                    start, end = parse_period(value)
                elif k == "start":
                    start = parse_date(value)
                elif k == "end":
                    end = parse_date(value)
            if not (pos_text or start or end):
                continue
            cls, link = cfg["class"], cfg["link"]
            if cls == "Reign" and pos_text and royal_re.search(pos_text):
                cls, link = "RoyalTitleTenure", "holdsRoyalTitle"
            t = res(f"{title}__{cls}_{gid}")
            G.add((t, RDF.type, VIDBO[cls]))
            G.add((person, VIDBO[link], t))
            G.add((t, RDFS.label, Literal(f"{cls} {gid} – {title}" + (f" ({pos_text})" if pos_text else ""), lang="vi")))
            if pos_text and len(pos_text) < 300:
                G.add((t, VIDBO.title, Literal(pos_text, lang="vi")))
            for l in pos_links:
                r = self.resolve(l)
                prop = VIDBO.tenureDynasty if (cls == "Reign" and r.startswith("Nhà ")) else VIDBO.position
                G.add((t, prop, res(r)))
            for prop, links in tenure_objects:
                for l in links:
                    G.add((t, VIDBO[prop], self.obj(l)))
            self.add_dates(t, start, end)
            self.stats["tenure_" + cls] += 1

    # -------------------------------------------------------------- range check
    def range_check(self):
        """DBpedia-style ontology range/domain check.

        An object triple whose subject (object) has an asserted class that is DISJOINT with the
        domain (range) of the property is moved to the dataset `mappingbased_objects_disjoint_range`,
        like DBpedia's "mappingbased-objects-disjoint-range". Example: the infobox of Lý Thái Tổ says
        that his predecessor is "Nhà Đinh" (a dynasty), but range(predecessor) = Person and Person ⊥ Group.
        """
        onto = Graph().parse(ROOT / "ontology" / "vidbo.ttl")
        sup = defaultdict(set)
        for a, b in onto.subject_objects(RDFS.subClassOf):
            sup[a].add(b)
        for a, b in onto.subject_objects(OWL.equivalentClass):
            sup[a].add(b), sup[b].add(a)
        for n, lst in onto.subject_objects(OWL.unionOf):
            for m in Collection(onto, lst):
                sup[m].add(n)

        def closure(c):
            seen, todo = {c}, [c]
            while todo:
                for d in sup.get(todo.pop(), ()):
                    if d not in seen:
                        seen.add(d)
                        todo.append(d)
            return {x for x in seen if isinstance(x, URIRef)}

        groups = [set(Collection(onto, onto.value(n, OWL.members))) for n in onto.subjects(RDF.type, OWL.AllDisjointClasses)]
        groups += [{a, b} for a, b in onto.subject_objects(OWL.disjointWith)]
        superprops = defaultdict(set)
        for a, b in onto.subject_objects(RDFS.subPropertyOf):
            superprops[a].add(b)

        inverse = defaultdict(set)
        for a, b in onto.subject_objects(OWL.inverseOf):
            inverse[a].add(b), inverse[b].add(a)
        other = {RDFS.domain: RDFS.range, RDFS.range: RDFS.domain}

        def constraint(p, kind):
            """domain/range of p, its super-properties, and (swapped) of their inverses."""
            out, todo, seen = set(), [p], set()
            while todo:
                q = todo.pop()
                if q in seen:
                    continue
                seen.add(q)
                out |= set(onto.objects(q, kind))
                for inv in inverse.get(q, ()):
                    out |= set(onto.objects(inv, other[kind]))
                todo.extend(superprops.get(q, ()))
            return {c for x in out if isinstance(x, URIRef) for c in closure(x)}

        def clash(classes, required):
            return any(len(g & classes) and len(g & required) and (g & classes) != (g & required) and
                       not ((g & classes) & (g & required)) for g in groups)

        types = defaultdict(set)
        for g in (self.g["instance_types"], self.g["tenures"]):
            for s, c in g.subject_objects(RDF.type):
                types[s] |= closure(c)
        bad = Graph()
        bad.bind("vidbo", VIDBO), bad.bind("vidbr", VIDBR)
        cache = {}
        for name in ("mappingbased_objects", "tenures"):
            g = self.g[name]
            for s, p, o in list(g):
                if p == RDF.type or not isinstance(o, URIRef):
                    continue
                if p not in cache:
                    cache[p] = (constraint(p, RDFS.domain), constraint(p, RDFS.range))
                dom, rng = cache[p]
                if (rng and o in types and clash(types[o], rng)) or (dom and s in types and clash(types[s], dom)):
                    g.remove((s, p, o))
                    bad.add((s, p, o))
        self.g["mappingbased_objects_disjoint_range"] = bad
        self.stats["disjoint_range_removed"] = len(bad)
        print(f"  range check: {len(bad):,} object triples moved to mappingbased_objects_disjoint_range", flush=True)

    # -------------------------------------------------------------- run
    def run(self):
        pages = [json.loads(l) for l in PAGES.open(encoding="utf8")]
        # de-duplicate (a page may be fetched in seed and expand passes)
        uniq = {}
        for p in pages:
            uniq[p["title"]] = p
        pages = list(uniq.values())
        red_file = PAGES.parent / "redirects.tsv"
        if red_file.exists():  # all redirects of the wiki, so that links to any alias resolve
            for line in red_file.open(encoding="utf8"):
                a, _, b = line.rstrip("\n").partition("\t")
                if b:
                    self.alias[a] = b
        for p in pages:
            self.known.add(p["title"])
            for r in p.get("redirected_from", []):
                self.alias[norm_title(r)] = p["title"]
                if len(p["redirected_from"]) <= 30:  # avoid flooding the redirects dataset
                    self.g["redirects"].add((res(r), VIDBO.wikiPageRedirects, res(p["title"])))
        print(f"{len(pages)} pages, {len(self.alias)} redirects", flush=True)
        for i, p in enumerate(pages, 1):
            try:
                self.page(p)
            except Exception as e:  # keep going; one broken infobox must not stop the pipeline
                self.stats["errors"] += 1
                print("ERROR", p["title"], repr(e)[:200], file=sys.stderr)
            if i % 2000 == 0:
                print(f"  {i}/{len(pages)}", flush=True)
        self.range_check()
        total = 0
        for name, g in self.g.items():
            g.serialize(OUT / f"{name}.ttl", format="turtle", encoding="utf-8")
            print(f"  {name:22s} {len(g):>9,} triples")
            total += len(g)
        print(f"TOTAL {total:,} triples")
        print(dict(self.stats))
        (OUT / "extraction_stats.json").write_text(json.dumps(
            {"stats": self.stats, "param_usage": {k: dict(v.most_common()) for k, v in self.param_usage.items()}},
            ensure_ascii=False, indent=1), encoding="utf8")


def referenced_labels():
    """rdfs:label for resources that are only REFERENCED (no article in the dataset): the URI is the
    Wikipedia title, so the label is recovered from it. Writes data/rdf/labels_referenced.ttl."""
    from urllib.parse import unquote
    labelled = {s for s in Graph().parse(OUT / "labels.ttl").subjects(RDFS.label, None)}
    g = Graph()
    g.bind("vidbr", VIDBR)
    for name in ("mappingbased_objects", "tenures"):
        for o in Graph().parse(OUT / f"{name}.ttl").objects():
            if isinstance(o, URIRef) and str(o).startswith(str(VIDBR)) and o not in labelled and "__" not in str(o):
                g.add((o, RDFS.label, Literal(unquote(str(o)[len(str(VIDBR)):]).replace("_", " "), lang="vi")))
    g.serialize(OUT / "labels_referenced.ttl", format="turtle", encoding="utf-8")
    print(f"  labels_referenced     {len(g):>9,} triples")


if __name__ == "__main__":
    if "--labels-only" in sys.argv:
        referenced_labels()
    else:
        Extractor().run()
        referenced_labels()
