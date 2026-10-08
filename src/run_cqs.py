"""Run every competency-question query against the endpoint and write docs/cq_results.md.

    python src/run_cqs.py [--rows 12]
"""
import argparse
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from query import ENDPOINT, short, with_prefixes  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main(rows):
    out = ["# Kết quả các câu hỏi năng lực", "",
           f"Sinh tự động bởi `src/run_cqs.py` trên endpoint `{ENDPOINT}` ({time.strftime('%Y-%m-%d %H:%M')}).",
           f"Mỗi bảng chỉ in tối đa {rows} dòng đầu.", ""]
    summary = []
    for f in sorted((ROOT / "queries").glob("*.rq")):
        text = f.read_text(encoding="utf8")
        title = next(l.lstrip("# ").strip() for l in text.splitlines() if l.startswith("#"))
        t0 = time.time()
        try:
            r = requests.post(ENDPOINT, data={"query": with_prefixes(text)},
                              headers={"Accept": "application/sparql-results+json"}, timeout=300)
            r.raise_for_status()
            j = r.json()
            cols, res = j["head"]["vars"], j["results"]["bindings"]
            err = None
        except Exception as e:  # e.g. the federated query when DBpedia is unreachable
            cols, res, err = [], [], str(e)[:200]
        ms = int((time.time() - t0) * 1000)
        summary.append((f.stem, len(res), ms, err))
        out += [f"## {title}", "", f"`queries/{f.name}` — **{len(res)} kết quả**, {ms} ms", ""]
        if err:
            out += [f"> Lỗi: {err}", ""]
            continue
        out += ["```sparql", text.strip(), "```", ""]
        if res:
            out.append("| " + " | ".join("?" + c for c in cols) + " |")
            out.append("|" + "---|" * len(cols))
            for b in res[:rows]:
                cells = [short(b[c]["value"]).replace("|", "/").replace("\n", " ")[:90] if c in b else "" for c in cols]
                out.append("| " + " | ".join(cells) + " |")
            out.append("")
        print(f"{f.stem:42s} {len(res):6d} rows {ms:6d} ms {'ERR ' + err[:60] if err else ''}", flush=True)
    (ROOT / "docs" / "cq_results.md").write_text("\n".join(out), encoding="utf8")
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=12)
    if sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    main(ap.parse_args().rows)
