"""Run the whole ViDBpedia pipeline (after the dumps are in data/dumps/).

    python run_pipeline.py              # collect -> extract -> reason -> validate -> link -> load
    python run_pipeline.py --from reason
    python run_pipeline.py --skip link  # e.g. without Internet access
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = [
    ("collect", ["src/collect_dump.py"]),
    ("extract", ["src/extract.py"]),
    ("reason", ["src/reason.py"]),
    ("validate", ["src/validate.py"]),
    ("link", ["src/link.py"]),
    ("load", ["src/load_endpoint.py"]),
    ("test", ["tests/test_parsers.py"]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start", choices=[s for s, _ in STEPS], default="collect")
    ap.add_argument("--skip", nargs="*", default=[])
    a = ap.parse_args()
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    names = [s for s, _ in STEPS]
    for name, cmd in STEPS[names.index(a.start):]:
        if name in a.skip:
            continue
        t0 = time.time()
        print(f"\n=== {name} ===", flush=True)
        r = subprocess.run([sys.executable, "-u", *cmd], cwd=ROOT, env=env)
        if r.returncode:
            sys.exit(f"step '{name}' failed (exit {r.returncode})")
        print(f"=== {name} done in {time.time() - t0:.0f}s ===", flush=True)
    print("\nAll done. Start the endpoint with: python src/serve.py")


if __name__ == "__main__":
    main()
