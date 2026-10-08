"""Start the ViDBpedia endpoint: Apache Jena Fuseki (port 3030) + the Flask web UI (port 5000).

    python src/serve.py            # both
    python src/serve.py --fuseki   # only Fuseki
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
ENDPOINT_DIR = ROOT / "endpoint"
JAR = ENDPOINT_DIR / "apache-jena-fuseki-5.6.0" / "fuseki-server.jar"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fuseki", action="store_true", help="only start Fuseki")
    a = ap.parse_args()
    fuseki = subprocess.Popen(["java", "-Xmx3G", "-jar", str(JAR), "--config=fuseki-config.ttl", "--port=3030"],
                              cwd=ENDPOINT_DIR)
    for _ in range(60):
        try:
            if requests.get("http://localhost:3030/$/ping", timeout=2).ok:
                break
        except requests.RequestException:
            time.sleep(1)
    print("Fuseki:  http://localhost:3030/#/dataset/vidbpedia/query   (SPARQL: http://localhost:3030/vidbpedia/sparql)")
    if a.fuseki:
        fuseki.wait()
        return
    print("Web UI:  http://127.0.0.1:5000/")
    try:
        subprocess.run([sys.executable, str(ROOT / "web" / "app.py")])
    finally:
        fuseki.terminate()


if __name__ == "__main__":
    main()
