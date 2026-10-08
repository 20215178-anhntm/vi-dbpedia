"""Check the ontology with the HermiT tableau reasoner (OWL 2 DL) on the hand-made Trần dynasty sample.

    python tests/test_hermit.py

Verifies that the ontology is consistent and that the expected facts are inferred.
(owlready2's HermiT bridge mishandles non-ASCII IRIs, so the sample IRIs are transliterated
for this test only; Protégé handles the original Vietnamese IRIs fine.)
"""
import sys
import tempfile
from pathlib import Path

import rdflib
from owlready2 import default_world, get_ontology, sync_reasoner
from unidecode import unidecode

ROOT = Path(__file__).resolve().parent.parent
R = "http://vi.dbpedia.example.org/resource/"
O = "http://vi.dbpedia.example.org/ontology/"

EXPECTED_TYPES = {
    "Tran_Nhan_Tong": {"VietnameseMonarch", "MonarchWarrior", "RoyalChild"},
    "Tran_Thanh_Tong": {"VietnameseMonarch", "RoyalChild"},
    "Tran_Thai_Tong": {"VietnameseMonarch"},
    "Tran_Anh_Tong": {"RoyalChild"},
    "Tran_Hung_Dao": {"MilitaryCommander"},
}
EXPECTED_VALUES = {
    ("Tran_Nhan_Tong", "memberOfDynasty"): "Nha_Tran",
    ("Tran_Anh_Tong", "memberOfDynasty"): "Nha_Tran",
    ("Tran_Nhan_Tong", "hasPaternalGrandfather"): "Tran_Thai_Tong",
    ("Tran_Nhan_Tong", "participatedIn"): "Chien_tranh_Nguyen_Mong-Dai_Viet_lan_3",
    ("Tran_Nhan_Tong", "bornWithin"): "Dai_Viet",
    ("Tran_Bach_Dang_1288", "tookPlaceWithin"): "Dai_Viet",
}


def fix(t):
    if isinstance(t, rdflib.URIRef) and str(t).startswith(R):
        return rdflib.URIRef(R + unidecode(str(t)[len(R):]).replace("(", "").replace(")", ""))
    return t


def main():
    g = rdflib.Graph()
    g.parse(ROOT / "ontology" / "vidbo.ttl")
    g.parse(ROOT / "ontology" / "examples" / "tran_dynasty_sample.ttl")
    g.remove((None, rdflib.OWL.imports, None))
    h = rdflib.Graph()
    for s, p, o in g:
        h.add((fix(s), p, fix(o)))
    tmp = Path(tempfile.mkdtemp()) / "merged.owl"
    h.serialize(tmp, format="xml")
    onto = get_ontology("file://" + str(tmp).replace("\\", "/")).load()
    with onto:
        sync_reasoner(infer_property_values=True, debug=0)
    ok = True
    for ind, classes in EXPECTED_TYPES.items():
        got = {c.name for c in default_world[R + ind].is_a if hasattr(c, "name")}
        miss = classes - got
        print(f"{'OK ' if not miss else 'FAIL'} {ind}: {sorted(got)}")
        ok &= not miss
    for (ind, prop), val in EXPECTED_VALUES.items():
        got = [x.name for x in default_world[O + prop][default_world[R + ind]]]
        print(f"{'OK ' if val in got else 'FAIL'} {ind} {prop} -> {got}")
        ok &= val in got
    inc = list(default_world.inconsistent_classes())
    print("unsatisfiable classes:", inc)
    ok &= not inc
    print("ALL PASSED" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
