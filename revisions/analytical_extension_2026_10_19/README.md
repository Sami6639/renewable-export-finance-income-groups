# Revised manuscript analytical extension

This folder contains the additional summaries, shifted-window comparison and display outputs used in the revised manuscript and Supplementary Information. It extends the archived source outputs at commit `776d41f57ff893ba0d88be8f09035dbbf9d417fa`. The original source-dependent pipeline and its rights restrictions remain applicable.

## Reproduction from the repository root

```sh
python verify_package.py --require-all
python -m pip install -r revisions/analytical_extension_2026_10_19/requirements.txt
python revisions/analytical_extension_2026_10_19/numerical/extend.py
python revisions/analytical_extension_2026_10_19/numerical/coverage.py
python revisions/analytical_extension_2026_10_19/numerical/build_revised_figures.py --source-dir published_replication_candidates/export_finance/reconciled_revision_2026_10_18
python revisions/analytical_extension_2026_10_19/numerical/traceability.py
python revisions/analytical_extension_2026_10_19/numerical/complete_traceability.py
```

Run the two traceability scripts in the displayed order each time. These scripts reaggregate public outputs; they do not reconstruct source transactions. They overwrite this extension's numerical outputs. Verify shipped hashes before rerunning. Matplotlib PDF metadata can vary between runs even when figures and numerical results are identical.

## Added outputs and document mapping

- `numerical/FY2023_all24_decomposition.csv`: complete 24-case alternative fixed 2023 income-classification endpoint decomposition for the international portfolio (96 rows).
- `numerical/FY2023_selected.csv`: archive reference and two source-informed cases, including all four classes.
- `numerical/FY2023_ranges.csv`: full-grid minimum and maximum changes by class.
- `numerical/alternative_windows.csv`: two source-informed cases, four classes, pooled 2014–2016 versus 2019–2021, retaining the fixed 2013 income classification.
- `numerical/display_traceability.csv`: all main and supplementary display mappings. Supplementary Table S10 combines the selected classification comparison and shifted-window comparison; these are separate analyses, not a factorial cross.
- Other numerical CSVs contain endpoint nominal levels, geography coverage, provider contributions and three revised figure datasets.
- `verification/release_alignment.json` records checks against the supplied manuscript and Supplementary Information, input commit and numerical regeneration.
- `verification/release_file_map.csv` links every extension file to its repository-relative path and SHA-256 hash.

Technical file names retain the archive's `FY2023` identifier for traceability. The primary and alternate classifications are held fixed across observation years. Classification-vintage and shifted-window tests do not imply additional years of observations, a causal effect, or full reconstruction from original source workbooks.

## Scope and rights

No original workbook, report, source scan, manuscript or private correspondence is included. All added CSVs are derived from already-public analytical outputs. Original source rights are not expanded. The earlier receipts in `verification/` document historical private-extension validation; `release_alignment.json` is the current package-alignment receipt. Until this package is actually committed, this folder remains a prepared publication update, not a verified live GitHub release.
