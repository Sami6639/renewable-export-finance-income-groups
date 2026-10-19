# Revision 2 display guide

## Deliverables and placement

Exactly three main figures and three compact main tables. Use native editable tables from display_manifest.json; use PNGs for Word and vector PDFs for journal production. Caption and notes in the manifest are authoritative. Main figure width 6.4–6.7 inches; Figure 1 is about 5.5 inches high at this width, Figures 2–3 about 3.4 inches. Put Table 1 in source-reconciliation methods; Figure 1 at annual allocation; Figure 2 at pooled endpoint results; Table 2 after case-family robustness; Figure 3 at provider accounting/regional completion; Table 3 at concentration/influence. No original or earlier-revision files were edited.

## Scope and terminology

Primary scope is international reporting: known unequal provider/recipient countries plus specifically verified intended cross-border Standard Bank regional support. At source-informed geography, this differs from country-assigned international scope. South Africa is the recorded borrower/intermediary location, not an observed allocation of all ultimate projects. Provider is the institutionGroup country grouping, not an individual agency. The four fixed FY2013 classes are low, lower-middle, upper-middle and high income; unknown income is reported separately. Shares divide known-class observed amounts by their classified denominator. Pooled 2013–2015 / 2020–2022 shares are ratios of pooled dollars. Missing amounts remain excluded/missing, never zero-filled; undefined results remain undefined.

Main labels map to: archive reference=A0O0G0D0; source-informed contract exclusion=A1O1G1D1; source-informed whole-block exclusion=A1O1G1D2. This map is for SI and reproducibility. Named cases have unequal documentary standing and are not equally plausible estimates of truth.

## Exact value provenance

VALUE_LEDGER.csv lists each display dataset, original CSV, exact selection, row count and retained column set. SOURCE_HASHES.json records all frozen output CSV hashes. All plot positions are direct exported values, multiplied by 100 only for proportions-to-percent or divided by 1e9 only for USD-to-billions. No new statistical analyses, contrasts, hypotheses, corrections or scenarios were run. Table 1 is a prose transcription of approved protocol section 3 and source memos; Table 2 reads frozen envelope endpoints; Table 3 reads frozen deletion influence.

- Figure 1: allocation.csv, share_classified ×100; ten annual periods; named scenarios; four known classes; international_reporting. Full observed amounts, classified/observed denominators, unknown_amount, component/source-row/missing counts remain in data.
- Figure 2a: decomposition.csv, delta_pp, pair=early_to_late, same panel/scenarios/classes. Figure 2b: allocation.csv, amount/1e9, period=early/late. Missing amounts are not inferred as zero.
- Figure 3 points: decomposition.csv, delta_pp/composition_pp/within_pp/entry_pp/exit_pp, H endpoint, named scenarios. Segments: completion_case_scalar_envelopes.csv, lower/upper, target_type=decomposition, target=early_to_late, panel=international_reporting, income_class=H, case_id=A1O1G1D1/A1O1G1D2, metric matching the plotted term. These are exact scalar hull extrema, not CIs. They describe a targeted-completion denominator distinct from the uncompleted point. Exact attaining vertices remain in data.
- Table 2: scenario_envelopes.csv, universe=core24/agreement12; arithmetic_quarantine_envelopes.csv, universe=quarantine24; analysis=decomposition, target=early_to_late, outcome=delta_pp, geography=international_reporting, all four classes. minimum/maximum, attaining IDs, defined/undefined counts and signs preserved.
- Table 3: package_influence_endpoint.csv.gz and record_influence_endpoint.csv.gz; source-informed contract exclusion; international_reporting; L/H; three prespecified packages and Guinea record8129. baseline_delta_pp, deleted_delta_pp, influence_delta_pp are printed; full support/components are preserved. Entity ledger records removed amounts/membership. No source-operation effect is relabelled deletion influence.

## Complete families retained separately

SI_annual_Q0_core24_agreement12.csv retains 36 × 10 × 4 rows with case_set distinguishing 24 core and 12 agreement overlays. SI_annual_Q1_core24.csv retains 24 × 10 × 4 separate arithmetic-stress rows. Endpoint accounting files retain all four classes and all five accounting terms. SI_Q0_regional18_endpoint_envelopes.csv retains all 12 core G1 plus 6 agreement G1 cases; there is no arithmetic-stress regional grid. SI_documented_source_contrasts.csv preserves all paired factor/background contrasts separately from Table 3. Original full regional vertices and other panels remain in the frozen analysis bundle, not invented here.

## Reproduction

Run python build_displays.py --source-dir /path/to/reconciled_revision_2026_10_18 with pandas, numpy and matplotlib. The default source path resolves to the canonical sibling analysis directory. To avoid cache warnings on read-only hosts set MPLCONFIGDIR=/tmp/mpl and XDG_CACHE_HOME=/tmp/cache. Then run python assemble_display_metadata.py to regenerate captions and manifest; the shipped display_manifest.json is ready for direct use. No network or raw-data reanalysis is needed.

## Captions and table notes

### table1

Table 1. Source evidence and approved operations

The guarantee component is derived, conditional on same-operation scope and additivity; it is not a separately disclosed guarantee ceiling. Source-informed treatments differ in evidentiary status from archive retention and are not certified true finance exposure. Borrower location and intended project region have distinct roles. The SI scenario map gives exact row-level operations and source citations.

### table2

Table 2. Endpoint share changes across separate case families

International reporting portfolio, Renewable records, fixed FY2013 World Bank income classes. Archive fiscal years are retained; pooled endpoints are 2013–2015 and 2020–2022. Amounts are recorded nominal USD on heterogeneous archive/source financial bases. Missing amounts are excluded, not replaced by zero. Core treatments (24), agreement-year overlays (12) and arithmetic-flag exclusions (24) are separate finite families, not probability-weighted estimates or confidence intervals. The arithmetic stress excludes four additional rows jointly; it is not crossed with agreement timing or regional completion. Marginal extrema may be attained in different cases; full attaining cases remain in the CSV.

### table3

Table 3. Record and package influence: source-informed contract exclusion

International reporting portfolio, Renewable records, fixed FY2013 World Bank income classes. Archive fiscal years are retained; pooled endpoints are 2013–2015 and 2020–2022. Amounts are recorded nominal USD on heterogeneous archive/source financial bases. Missing amounts are excluded, not replaced by zero. Baseline is source-informed contract exclusion. Effects are deletion minus baseline share changes, with denominators and provider support recomputed in the already-approved influence outputs. Standard Bank has zero classified-share influence here because its regional amount is retained in observed totals but unallocated by income. The approximately USD1.72bn Guinea package is corroborated and includes Souapiti development and Kaleta restructuring; its influence does not establish an error or justify deletion. Source-treatment effects are reported separately in the SI and are not causal effects.

### figure1

Figure 1. Annual four-class allocation under the archive reference and two source-informed specifications. International reporting portfolio, Renewable records, fixed FY2013 World Bank income classes. Archive fiscal years are retained; pooled endpoints are 2013–2015 and 2020–2022. Amounts are recorded nominal USD on heterogeneous archive/source financial bases. Missing amounts are excluded, not replaced by zero. Lines show each class’s share of observed amounts with known recipient income for every year from 2013 through 2022; they are not smoothed trends. Source-informed contract exclusion removes the two Dogger export-contract entries; whole-block exclusion additionally removes the unresolved Dogger financing entry. Both apply the same amount, overlap and recipient-geography reconciliations. Standard Bank remains in observed international totals under its documented regional role but outside the classified denominator. Annual amounts, observed/classified denominators, unknown-income amounts and missingness counts accompany every plotted point in figure1_annual_data.csv.

### figure2

Figure 2. Pooled endpoint share changes and nominal amounts by income class. International reporting portfolio, Renewable records, fixed FY2013 World Bank income classes. Archive fiscal years are retained; pooled endpoints are 2013–2015 and 2020–2022. Amounts are recorded nominal USD on heterogeneous archive/source financial bases. Missing amounts are excluded, not replaced by zero. Panel a shows late-minus-early classified-share changes in percentage points. Panel b joins early (open) and late (filled) pooled nominal amounts; endpoints are sums across three years, not annual averages. Under both source-informed specifications, low-income amounts fall from USD3.013bn to USD2.785bn although their shares rise. Classified denominators (early/late, USD bn) are 23.455/18.156 for the archive, 19.520/14.100 for contract exclusion and 19.520/13.577 for whole-block exclusion. Source-informed early observed totals additionally include USD0.2375bn unallocated regional support; the late unknown-income amount is zero. Full coverage is retained in accompanying CSVs.

### figure3

Figure 3. High-income share-change accounting and Standard Bank regional-completion outer envelopes. International reporting portfolio, Renewable records, fixed FY2013 World Bank income classes. Archive fiscal years are retained; pooled endpoints are 2013–2015 and 2020–2022. Amounts are recorded nominal USD on heterogeneous archive/source financial bases. Missing amounts are excluded, not replaced by zero. Points show the classified-income accounting: provider-country composition, within-provider allocation, entry and exit sum to total change. Horizontal segments for the source-informed cases are exact case-specific regional-completion outer envelopes, not confidence intervals. Completion assigns only Standard Bank’s observed regional amount across the four-class simplex; it changes the denominator relative to the uncompleted classified-share point. It imposes no actual-country eligibility restrictions and is not a bound on total or true finance exposure. Componentwise extrema need not occur together. The enlarged within-provider panel retains the positive contract-exclusion versus negative whole-block contrast throughout the respective outer envelopes. Regional completion is restricted to the original population; the arithmetic-flag-exclusion family is separate.

