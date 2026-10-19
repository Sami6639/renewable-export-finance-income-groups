# Reproduction and interpretation

Before these steps, run `python verify_package.py --require-all` and `python unpack_outputs.py` from the repository root.

## Exact input acquisition
Download the publication archive at https://zenodo.org/records/14261240 (article https://doi.org/10.1038/s41467-025-55981-0). Save its original ZIP at ROOT/published_replication_candidates/export_finance/CenskowskyEtAl_ECA_ReplicationPackage.zip. Extract it so the README is ROOT/published_replication_candidates/export_finance/package/CenskowskyEtAl_ECA_ReplicationPackage/README.md. Obtain the historical World Bank income workbook at https://ddh-openapi.worldbank.org/resources/DR0095334/download and save it at ROOT/renewable_finance_recovery/financial_transition_panel/raw/income_history.xlsx.

Verify exact vintages against published_replication_candidates/export_finance/extension/source_hashes.json, including the OCI, CPI, ISO and supplementary-source workbooks inside the publication ZIP. Live URLs may return changed versions: do not substitute a later workbook after a hash mismatch. If the exact historical income file is unavailable, reproduction is blocked until that vintage is obtained. Official documentary sources are listed in manuscript_design/source_validation/official_source_registry.csv and manuscript_design/source_reconciliation below the export_finance directory. Their compact memos, URLs, locators, limitations and available hashes are included; complete hashes were not obtained for every external webpage.

The publication archive declares CC BY-NC-SA and the OCI embedded guide declares CC BY-NC. This distribution does not resolve that difference or grant unrestricted rights over upstream data. Respect source terms. Restricted TXF and the original Stata/R pipeline are outside this reproduction.

## Run
Python 3.12 was used. Create an isolated environment and install requirements.txt. From ROOT:

    python -m pip install -r requirements.txt
    python reproduce.py --root . --verify-inputs

The runner executes the 21 prerequisite analysis/audit steps, then the full arithmetic screen and independent screen, 24-case core/12-overlay analysis, 24 Q companions, regional completion, full influence, and independent revised checks. Use --list-steps to inspect commands; --skip-influence omits the computationally expensive influence generation and its checks; --skip-prerequisites is only for a directory where the 21 steps have already generated exact-vintage inputs. The full replay can take substantial time. No live web lookup is required once inputs are acquired.

Replay overwrites outputs and locally recreates excluded raw-row intermediates. Keep an unchanged repository checkout for verification; do not redistribute regenerated full-row extracts by default. Verify the shipped manifest before replay, not after it. Prior evidence/source-validation folders are explicitly historical prerequisite work, not current source reconciliation. The revised result authority is reconciled_revision_2026_10_18/outputs and its FINAL_INDEPENDENT_AUDIT.json; the audited analysis passed independent numerical reproduction. Packaging validation separately checks portability, unchanged scientific calculations, integrity and omission boundaries. Public protocol-integrity gates verify the scientific protocol without changing formulas; CODE_PROVENANCE.json records source and distributed code hashes.

## Interpretation
Values are nominal USD unless explicitly labelled otherwise. Share fields are proportions; _pp fields are percentage points. Provider denotes source institutionGroup country. Source entries and analytical components are distinct. Regional completion and influence are Q0-only; Q1 is not crossed with overlays or completion. Finite scenario envelopes are not confidence intervals or universal bounds on true exposure. Recorded values are heterogeneous; the audit does not establish causal effects, physical project hosts, homogeneous principal, or disjoint economic exposure. Read the public protocol and OUTPUT_GUIDE.md before using results.
