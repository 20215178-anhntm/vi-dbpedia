"""Package the paper for Overleaf (forward-slash paths):  python make_zip.py"""
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
files = ["main.tex", "references.bib", "neurips_2024.sty", "latexmkrc", "README.md"] + sorted(
    f"figures/{p.name}" for p in (HERE / "figures").iterdir())
with zipfile.ZipFile(HERE / "ViDBpedia_overleaf.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for f in files:
        z.write(HERE / f, f)
print("\n".join(zipfile.ZipFile(HERE / "ViDBpedia_overleaf.zip").namelist()))
