"""Step 2 - Collect Vietnamese Wikipedia articles from the official Wikimedia dumps.

Like the DBpedia Extraction Framework, we work on the XML dump instead of the live API
(the API is rate-limited to ~50 pages/minute for anonymous clients).

Inputs (data/dumps/, from https://dumps.wikimedia.org/viwiki/latest/):
    viwiki-latest-pages-articles.xml.bz2   article wikitext
    viwiki-latest-langlinks.sql.gz         interlanguage links  (-> English DBpedia)
    viwiki-latest-page_props.sql.gz        Wikidata QIDs, disambiguation flags

Pass 1 (seed):   articles transcluding a mapped infobox, or in a seed category.
Pass 2 (expand): articles linked from object-valued infobox fields of the seed
                 (parents, spouses, birth places, commanders, provinces, ...).
Redirects of the whole wiki are recorded so that links can be resolved.

Output: data/raw/pages.jsonl, data/raw/redirects.tsv

Usage:  python src/collect_dump.py [--max-expand 20000]
"""
import argparse
import bz2
import gzip
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import mwparserfromhell as mw

sys.path.insert(0, str(Path(__file__).parent))
from extract import find_infobox, infobox_source, load_mappings, lookup, object_param_names  # noqa: E402
from parsers import norm_title, wikilinks_in  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DUMPS = ROOT / "data" / "dumps"
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
XML = DUMPS / "viwiki-latest-pages-articles.xml.bz2"
LANGLINKS = DUMPS / "viwiki-latest-langlinks.sql.gz"
PAGEPROPS = DUMPS / "viwiki-latest-page_props.sql.gz"

SEED_CATEGORIES = ["Triều đại Việt Nam", "Vua Việt Nam", "Chúa Việt Nam", "Tỉnh của Việt Nam",
                   "Vùng của Việt Nam", "Anh hùng dân tộc Việt Nam", "Truyện thơ Nôm"]

CAT_RE = re.compile(r"\[\[\s*(?:Thể[ _]loại|Category)\s*:\s*([^\]|]+)", re.I)
COORD_RE = re.compile(r"\{\{\s*coord\s*\|([^{}]*)\}\}", re.I)


# ------------------------------------------------------------------ SQL dumps

def sql_tuples(path, pattern):
    """Stream tuples matching `pattern` from the INSERT statements of a gzipped MySQL dump."""
    rx = re.compile(pattern)
    with gzip.open(path, "rt", encoding="utf8", errors="replace") as f:
        for line in f:  # newer dumps put one tuple per line, older ones many tuples per INSERT line
            if line.startswith("(") or line.startswith("INSERT INTO"):
                yield from rx.finditer(line)


def unescape_sql(s):
    return re.sub(r"\\(.)", r"\1", s)


def load_langlinks():
    out = {}
    if not LANGLINKS.exists():
        return out
    for m in sql_tuples(LANGLINKS, r"\((\d+),'en','((?:[^'\\]|\\.)*)'\)"):
        out[int(m.group(1))] = unescape_sql(m.group(2))
    return out


def load_page_props():
    qid, disamb = {}, set()
    if not PAGEPROPS.exists():
        return qid, disamb
    for m in sql_tuples(PAGEPROPS, r"\((\d+),'(wikibase_item|disambiguation)','((?:[^'\\]|\\.)*)'"):
        pid = int(m.group(1))
        if m.group(2) == "wikibase_item":
            qid[pid] = m.group(3)
        else:
            disamb.add(pid)
    return qid, disamb


# ------------------------------------------------------------------ XML dump

def iter_pages():
    """Yield (ns, pageid, title, revid, redirect_target, text) for every page in the dump."""
    with bz2.open(XML, "rb") as f:
        ctx = ET.iterparse(f, events=("end",))
        ns_uri = None
        for event, el in ctx:
            tag = el.tag
            if ns_uri is None and tag.startswith("{"):
                ns_uri = tag[: tag.index("}") + 1]
            if tag != f"{ns_uri}page":
                continue
            ns = int(el.findtext(f"{ns_uri}ns"))
            title = el.findtext(f"{ns_uri}title")
            pid = int(el.findtext(f"{ns_uri}id"))
            red = el.find(f"{ns_uri}redirect")
            rev = el.find(f"{ns_uri}revision")
            revid = int(rev.findtext(f"{ns_uri}id")) if rev is not None else None
            text = rev.findtext(f"{ns_uri}text") if rev is not None else ""
            yield ns, pid, title, revid, (red.get("title") if red is not None else None), text or ""
            el.clear()


def parse_coord(text):
    """Primary {{Coord}} (display=title) of an article -> (lat, lon)."""
    for m in COORD_RE.finditer(text):
        body = m.group(1)
        if "title" not in body and "display" in body:
            continue
        parts = [p.strip() for p in body.split("|") if "=" not in p]
        try:
            hemis = [i for i, p in enumerate(parts) if p.upper() in ("N", "S", "E", "W")]
            if len(hemis) >= 2:
                lat_parts, lon_parts = parts[: hemis[0]], parts[hemis[0] + 1: hemis[1]]
                lat = sum(float(x) / 60 ** i for i, x in enumerate(lat_parts))
                lon = sum(float(x) / 60 ** i for i, x in enumerate(lon_parts))
                lat *= -1 if parts[hemis[0]].upper() == "S" else 1
                lon *= -1 if parts[hemis[1]].upper() == "W" else 1
            else:
                lat, lon = float(parts[0]), float(parts[1])
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon
        except (ValueError, IndexError):
            continue
    return None


def build_record(pid, title, revid, text, langlinks, qids, disamb):
    rec = {"title": title, "pageid": pid, "revid": revid, "wikitext": text,
           "categories": [{"title": "Thể loại:" + c.strip()} for c in CAT_RE.findall(text)],
           "pageprops": {}, "langlinks": []}
    if pid in qids:
        rec["pageprops"]["wikibase_item"] = qids[pid]
    if pid in disamb:
        rec["pageprops"]["disambiguation"] = ""
    if pid in langlinks:
        rec["langlinks"] = [{"lang": "en", "title": langlinks[pid]}]
    c = parse_coord(text)
    if c:
        rec["coordinates"] = [{"lat": c[0], "lon": c[1], "primary": True, "globe": "earth"}]
    return rec


def main(max_expand):
    t0 = time.time()
    maps = load_mappings()
    names = sorted(maps["by_name"], key=len, reverse=True)
    tpl_re = re.compile(r"\{\{\s*(?:" + "|".join(re.escape(n) for n in names) + r")\s*(?:\||\}\}|\n|<!--)", re.I)
    seed_cats = {c.lower() for c in SEED_CATEGORIES}

    print("loading langlinks / page_props ...", flush=True)
    langlinks = load_langlinks()
    qids, disamb = load_page_props()
    print(f"  {len(langlinks):,} en-langlinks, {len(qids):,} QIDs, {len(disamb):,} disambiguations "
          f"({time.time() - t0:.0f}s)", flush=True)

    # ---------- pass 1: seeds + redirects
    redirects = {}
    seeds = {}
    n = 0
    for ns, pid, title, revid, red, text in iter_pages():
        if ns != 0:
            continue
        n += 1
        if red:
            redirects[title] = norm_title(red)
            continue
        hit = tpl_re.search(text[:20000])
        if not hit:
            cats = {c.strip().lower() for c in CAT_RE.findall(text)}
            if not (cats & seed_cats):
                continue
        seeds[title] = build_record(pid, title, revid, text, langlinks, qids, disamb)
        seeds[title]["source"] = "seed"
        if n % 200000 == 0:
            print(f"  scanned {n:,} articles, {len(seeds):,} seeds ({time.time() - t0:.0f}s)", flush=True)
    print(f"pass 1: {n:,} articles scanned, {len(seeds):,} seed pages, {len(redirects):,} redirects "
          f"({time.time() - t0:.0f}s)", flush=True)

    def resolve(t):
        seen = set()
        while t in redirects and t not in seen:
            seen.add(t)
            t = redirects[t]
        return t

    # ---------- which pages are linked from object-valued infobox fields?
    wanted = Counter()
    for rec in seeds.values():
        src = infobox_source(rec["wikitext"], maps)
        hit = find_infobox(mw.parse(src), maps) if src else None
        if not hit:
            continue
        tpl, tm = hit
        obj_names = object_param_names(tm)
        for par in tpl.params:
            name = str(par.name).strip().lower()
            spec, _ = lookup({k: True for k in obj_names}, name)
            if spec:
                for link in wikilinks_in(par.value):
                    t = resolve(link)
                    if t not in seeds:
                        wanted[t] += 1
    expand = {t for t, _ in wanted.most_common(max_expand)}
    print(f"expand: {len(wanted):,} distinct linked titles, taking {len(expand):,}", flush=True)

    # ---------- pass 2: fetch expanded pages
    extra = {}
    for ns, pid, title, revid, red, text in iter_pages():
        if ns == 0 and not red and title in expand:
            extra[title] = build_record(pid, title, revid, text, langlinks, qids, disamb)
            extra[title]["source"] = "expand"
            if len(extra) == len(expand):
                break
    print(f"pass 2: {len(extra):,} expanded pages ({time.time() - t0:.0f}s)", flush=True)

    # ---------- write
    back = {}
    for a, b in redirects.items():
        back.setdefault(resolve(b), []).append(a)
    with (RAW / "pages.jsonl").open("w", encoding="utf8") as out:
        for rec in list(seeds.values()) + list(extra.values()):
            rec["redirected_from"] = back.get(rec["title"], [])
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
    with (RAW / "redirects.tsv").open("w", encoding="utf8") as out:
        for a, b in redirects.items():
            out.write(f"{a}\t{resolve(b)}\n")
    print(f"wrote {len(seeds) + len(extra):,} pages ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-expand", type=int, default=20000)
    main(ap.parse_args().max_expand)
