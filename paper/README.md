# Report (NeurIPS preprint layout, Overleaf)

Same form as the group's earlier report (`Group5_...Fraud Detection.pdf`): single column, NeurIPS 2024 style with the
`preprint` option, numbered sections with bold paragraph heads, listings, a contributions table; references come last.

Fonts: STIX Two Text/Math and Source Code Pro (both in TeX Live, so they work on Overleaf); they render Vietnamese
diacritics correctly. No "Preprint" footer.

Files: `main.tex`, `references.bib`, `neurips_2024.sty` (official NeurIPS 2024 style, unmodified; `main.tex` empties
its footer notice), `figures/` (PDF vector figures + 2 screenshots), `latexmkrc`.
The previous IEEE two-column version is kept in `old/` (not part of the Overleaf zip).

## Upload to Overleaf
1. Overleaf → **New Project → Upload Project** → choose `ViDBpedia_overleaf.zip`.
2. The bundled `latexmkrc` selects **XeLaTeX** automatically (needed for Vietnamese characters).
   If Overleaf still uses pdfLaTeX: **Menu → Compiler → XeLaTeX**, then Recompile.
3. `main.pdf` in this folder is the compiled preview (15 pages; references are the last section; the limit is 15).
   Adding text will push it over the limit.

Code listings: characters above U+00FF (ầ, ệ, Đ, …) are wrapped in `(*…*)` escapes, because `listings` under
XeLaTeX would otherwise move them to the start of the word. Keep this when editing a listing.

The member roles in "Contributions of Team Members" match slide 26 of the deck; change both if the real split differs.

## Rebuild figures
`python ../presentation/make_figures.py` regenerates `figures/*.pdf` from `../presentation/facts.json`
(`python ../presentation/collect_facts.py` refreshes the numbers from `data/rdf/`).
