# Renewable Energy Export Finance: Income-Group Concentration and Provider Portfolios

Reproducibility materials for the revision-2 analysis of recorded renewable-energy export finance: income-group allocation, provider accounting, documented source scenarios, regional completion, and deterministic influence diagnostics.

## Start here

- [Reproduction instructions and interpretation limits](REPRODUCTION.md)
- [Scientific protocol](published_replication_candidates/export_finance/reconciled_revision_2026_10_18/protocol/ANALYSIS_PROTOCOL.md)
- [Output guide](published_replication_candidates/export_finance/reconciled_revision_2026_10_18/OUTPUT_GUIDE.md)
- [Revised tables and figures](published_replication_candidates/export_finance/manuscript_design/revision2/displays/)
- [Independent numerical audit](published_replication_candidates/export_finance/reconciled_revision_2026_10_18/independent_audit/FINAL_INDEPENDENT_AUDIT.json)

Code, compact outputs, displays, source-assessment ledgers and provenance are unpacked. Large CSVs are losslessly gzip-compressed; existing influence exports are also compressed. No Git LFS or companion ZIP download is needed. Preserve the directory structure.

From the repository root, using Python 3.12:

```sh
python verify_package.py --require-all
python unpack_outputs.py
python -m pip install -r requirements.txt
# Acquire the exact source inputs described in REPRODUCTION.md first.
python reproduce.py --root . --verify-inputs
```

The first command verifies shipped files. The second restores large CSVs byte-for-byte and verifies their original hashes. Run verification before replay: replay overwrites results and generates local source-row intermediates. `python reproduce.py --list-steps` lists the analysis commands without running them.

## Data and rights boundary

This package is input-dependent, not self-contained. Obtain the original publication archive from [Zenodo](https://zenodo.org/records/14261240) and the exact historical World Bank income workbook separately, using the paths and hashes in [REPRODUCTION.md](REPRODUCTION.md). If the required vintage is unavailable, full reproduction remains blocked. Source documentary judgments require evidence review beyond code execution.

Original workbooks, source PDF scans, full raw-row/text extracts, proprietary TXF data, the manuscript DOCX and private correspondence are excluded. Derived ledgers retain analytical values, source row identifiers and evidence references, not complete source datasets. Do not publish locally regenerated raw extracts by default.

The upstream archive declares CC BY-NC-SA while its OCI guide declares CC BY-NC. These conditions remain unresolved; this repository does not clear source licenses or grant unrestricted rights to upstream materials. No blanket repository license has been applied.

## Scientific scope

The outputs cover 24 core scenarios, 12 Karuma agreement-year overlays, 24 arithmetic-quarantine companions and 18 Q0-only regional-completion source cases. Regional completion and influence are Q0-only; Q1 is not crossed with overlays or completion. Prior evidence and source-validation folders are historical prerequisite work; the revised output directory and its independent audit are the current numerical authority.

Values are nominal USD unless explicitly labelled otherwise. Shares are proportions; `_pp` fields are percentage points. Provider refers to the source institution-group country. Finite scenario envelopes are not confidence intervals or universal bounds on true exposure. Recorded values are heterogeneous; results do not establish causality, physical project hosts, homogeneous principal or disjoint economic exposure.

## Integrity

`MANIFEST.sha256.json` describes this repository distribution. `COMPRESSED_OUTPUTS.json` records original and compressed hashes. `provenance/original_delivery_manifest.json` preserves the preceding three-part release manifest as historical provenance. Analysis code and numerical outputs are unchanged; packaging documentation and compression differ. SHA-256 checksums detect byte changes and are not digital signatures.
