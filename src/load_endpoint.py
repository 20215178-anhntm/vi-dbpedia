"""Step 5a - Bulk-load all RDF into the Fuseki TDB2 store (named graphs), offline.

Run with the Fuseki server STOPPED:
    python src/load_endpoint.py
then start the endpoint:
    python src/serve.py           (Fuseki on :3030 + web UI on :5000)
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FUSEKI = ROOT / "endpoint" / "apache-jena-fuseki-5.6.0"
DB = ROOT / "endpoint" / "databases" / "vidbpedia"
RDF_DIR = ROOT / "data" / "rdf"
G = "http://vi.dbpedia.example.org/graph/"

GRAPHS = {
    "ontology": [ROOT / "ontology" / "vidbo.ttl"],
    "data": [RDF_DIR / f"{n}.ttl" for n in (
        "labels", "labels_referenced", "instance_types", "mappingbased_objects", "mappingbased_literals", "tenures", "abstracts",
        "article_categories", "geo_coordinates", "page_metadata", "redirects")],
    "inferred": [RDF_DIR / "inferred.ttl"],
    "links": [RDF_DIR / f"{n}.ttl" for n in ("wikidata_links", "links_dbpedia_interlanguage", "links_dbpedia_silk")],
}


def main():
    if DB.exists():
        shutil.rmtree(DB)
    DB.mkdir(parents=True)
    jar = FUSEKI / "fuseki-server.jar"
    for name, files in GRAPHS.items():
        files = [str(f) for f in files if f.exists()]
        if not files:
            continue
        print(f"loading graph <{G}{name}>: {len(files)} file(s)", flush=True)
        cmd = ["java", "-Xmx4G", "-cp", str(jar), "tdb2.tdbloader", "--loc", str(DB), f"--graph={G}{name}", *files]
        subprocess.run(cmd, check=True)
    print("done. Start the endpoint with: python src/serve.py")


if __name__ == "__main__":
    sys.exit(main())
