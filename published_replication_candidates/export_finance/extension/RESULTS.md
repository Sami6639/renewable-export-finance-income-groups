Historical prerequisite analysis, superseded for revised interpretation by reconciled_revision_2026_10_18. Retained to document the preceding analysis and replay.

# What explains changes in recipient allocation of public export finance?
## A descriptive accounting extension using archived OCI data
18 October 2026. Source: Oil Change International's Public Finance for Energy Database, archived with Censkowsky et al., Nature Communications16,900(2025), https://doi.org/10.1038/s41467-025-55981-0 ; repository https://zenodo.org/records/14261240 .

## Financing-layer qualification under source review
The dominant France × “Loan” term is a **raw reported-mechanism label**, not verified direct ECA lending. Ten records identify BPI France and “Loan”; three Dogger Bank records account for $4.580 billion of the cell's $5.168 billion. Two concern Dogger Bank A/B in2020 ($2.695 billion and$0.523 billion), so distinct financing layers or overlap require source verification. Do not infer a shift from guarantees toward direct public lending or treat all listed amounts as distinct newly financed capital. Official BPI guaranteed-contract lists also match the two largest original amounts and identify their source basis as contract amounts, leaving finance-principal comparability unresolved. Raw records are unchanged; the complete ledger is `france_reported_loan_renewable_source_review.csv`.

## Renewable-finance finding in brief
Known international renewable recorded amounts show a high-income share increase from **10.90% to 51.24%**, while their reported nominal volume falls from **$23.455 billion to $18.156 billion**. The exploratory exact accounting assigns **+10.93 percentage points to joint provider/reported-mechanism composition, +5.76 to within-cell allocation, +25.29 to recorded cell entry and −1.64 to cell exit**. Recorded France × Loan entry dominates the support term. This is an accounting result, not evidence of newly active providers, causation or expanded financing access. The full technology comparison and independent audit appear below; all-energy results are a separate benchmark.

## Principal finding
Among recorded amounts with classifiable recipient income, high-income destinations' share increased from **36.56% in FY2013–2015 to50.89% in FY2020–2022**, a **14.33percentage-point increase**. A fixed World Bank FY2013 classification is used in both periods, preventing classification changes from mechanically creating this shift. Financing entries are the observed unit; recorded amounts are not disbursements, guarantee payouts or newly mobilized capital.

The exact joint provider × broad technology × reported-mechanism-portfolio accounting separates the increase into:

| Component | Percentage-point contribution |
|---|---:|
| Composition change among common cells | +5.06 |
| Within-common-cell recipient allocation | +2.20 |
| Entry of cells absent from the early window | +8.64 |
| Exit of cells absent from the late window | −1.58 |
| Total | +14.33 |

There are50 common cells,22 entering cells and20 exiting cells. Common cells cover88.55% and87.04% of allocable nominal volume in the early and late windows. Entry/exit describes positive-dollar cell support, not necessarily new providers, projects or recipient countries. The common-cell composition term is joint composition; it cannot be interpreted as a separate provider, technology or instrument effect. Technology groups are Fossil, Renewable, Grid and Other. Instrument portfolios are Loan, Guarantee, Other instrument and Aggregate residual.

## Why the pooled all-energy shift is not a general cross-border result
The predeclared known-international-only comparison is just **+1.34percentage points**; the domestic-only comparison is **+27.75points**. Domestic means recipient country equals provider country. Unknown locations remain outside both restricted comparisons. These sensitivities materially limit a claim about export finance flowing toward richer countries internationally. The main sample intentionally includes the archive's domestic entries, including Canada; the publication's OCI comparison excluded Canada.

## Coverage prevents a total-portfolio directional conclusion
Unknown recipient income accounts for23.89% of early and25.44% of late observed nominal volume. Most uncertainty is annual aggregate residual financing for Canada and Korea, explicitly net of known individual transactions. These amounts are retained.

Conditional on all reported dollar amounts, allocating all unknown volume away from or toward high-income recipients yields:

| Portfolio | Early high-income share range | Late high-income share range | Change range |
|---|---:|---:|---:|
| All |27.82–51.71%|37.94–63.38%|−13.77 to+35.56pp|
| Loan |41.05–41.29%|52.93–53.48%|+11.64 to+12.43pp|
| Guarantee |25.69–28.27%|46.70–46.89%|+18.43 to+21.20pp|
| Other instrument |87.54–95.61%|58.66–66.65%|−36.95 to−20.88pp|
| Aggregate residual |0–100%|0–100%|−100 to+100pp|

Thus, **the complete observed-volume portfolio's direction is not identified**, even though allocated shares rise. The aggregate residual portfolio has no classifiable recipients and no within-portfolio decomposition. These are bounds over known reported dollars, not confidence intervals. One late guarantee entry lacks amountUSD; its unknown volume has no finite amount bound from amountUSD alone. A separate source-supported CAD500,000×0.71309 reconstruction adds$356,545 and leaves the main conditional change essentially unchanged. We do not silently treat that missing amount as zero economic volume.

## Instrument differences
Within classified-recipient recorded amounts, loans rise from41.15% to53.22% high-income (+12.07pp), guarantees from26.37% to46.79% (+20.42pp), and Other instrument declines from95.23% to63.76% (−31.47pp). Loan within-common-cell allocation contributes−2.81pp while guarantee within-common-cell allocation contributes+11.71pp. Pooling instruments would conceal this distinction. Other instruments have only4.28% early common-cell coverage and37.44% late coverage, so their decline is mostly support turnover and should not be presented as a stable within-cell pattern.

## Prespecified sensitivities
All outcomes below are percentage-point changes in high-income share among classifiable recipients, with original windows unchanged:

| Variant | Change |
|---|---:|
| Primary nominal, fixed FY2013 |+14.33|
| Fixed FY2023 classification |+14.27|
| Once-deflated2020 USD |+13.41|
| Remove subsequent exact full-row copies |+14.42|
| Financing-entry counts |+26.05|
| Known international recipients only |+1.34|
| Domestic recipients only |+27.75|
| Remove largest nominal entry per window |+9.14|
| Documented missing-amount FX sensitivity |+14.33|

The largest-entry sensitivity removes Canada's FY2014 annual residual oil/gas aggregate ($8.097billion) and FY2022 Trans Mountain Corporation financing ($8.839billion). It is a predeclared leverage check, not a preferred sample. Entry counts are reporting-unit counts; annual aggregate entries and individual project entries are not equally granular opportunities, so their count-weighted result cannot measure project access.

## Added contribution and boundaries
This extension goes beyond another recipient-income chart by showing an exact accounting of joint portfolio composition, within-cell allocation and support turnover, alongside instrument distinctions, domestic/international sensitivity and observable-volume uncertainty bounds. It finds that the pooled all-energy conditional shift is not predominantly a within-cell change and that its cross-border interpretation is weak. The complete technology diagnostic below shows a different and much larger cross-border increase specifically for renewable finance. It also exposes how unallocated aggregate financing limits claims about the total portfolio.

This is descriptive accounting, not a policy-effect estimate or a causal explanation. The end window includes2020–2022 and is not a clean post-policy period. Provider coverage, reporting quality, aggregation, instruments, fiscal-year differences and concentration all matter. There are no regressions, tuned cutpoints or post-result sample searches. This archive has no interest rate, tenor, project return or guarantee-payout information and cannot support cost-of-capital or realized-risk claims. Novelty relative to the wider literature remains to be established; this is a bounded empirical extension, not a completed publication claim.

## Verification and reproduction
Run in order: `audit_extension.py`, `prepare_income_mapping.py`, `decompose_allocation.py`. The last script writes every prespecified variant, its bounds, cell-level contributions and exact closure residuals. Independent audit files are in `independent_audit/`. The classification mapping uses the official historical World Bank source https://ddh-openapi.worldbank.org/resources/DR0095334/download , FY13/2011-GNI and FY23/2021-GNI columns, not the stale metadata sheet. Source conflicts are explicit: row578 is Israel on verified EXIM evidence; row5377 and9697 remain unknown; FY23 Venezuela remains unclassified. Raw source fields and identifiers are preserved. Monetary data and source licenses are documented in `GATE_ONE_REPORT.md`.


## Renewable finance and complete technology diagnostic
This full stratification was requested after the first pooled result and is explicitly an additional descriptive diagnostic. Every existing broad technology category is reported, with unchanged windows, classifications and known-location restrictions. It does not relabel all energy as renewable.

| Technology | All-location high-income share change | Known international change | Domestic change |
|---|---:|---:|---:|
| All energy |+14.33 pp|+1.34 pp|+27.75 pp|
| Fossil |+4.82 pp|−20.91 pp|+29.06 pp|
| Renewable |+38.86 pp|+40.34 pp|+37.44 pp|
| Grid |−12.54 pp|−10.16 pp|−16.70 pp|
| Other, including nuclear |+69.33 pp|+60.24 pp|Not defined: no early domestic volume|

The renewable-specific result is therefore substantially stronger than the pooled all-energy cross-border result. Among known international renewable recorded amounts, high-income share rises from **10.90% to 51.24%**, a **40.34-point increase**. Reported international renewable volume falls from **$23.455 billion across 132 entries** to **$18.156 billion across 175 entries**. Shares and volume answer different questions; this does not establish lower-income project access or financing terms.

Across all renewable locations, high-income share rises **12.57%→51.44%**. Total observed renewable recorded amounts are **$24.321 billion / 151 entries** early and **$18.339 billion / 197 entries** late. Unknown-income amounts are **0.33% and 0.59%**, yielding an all-location observed-volume change bound of **+38.27 to +39.19 points**. The one missing amount is a renewable guarantee, so these remain conditional on reported dollars; the documented source-FX sensitivity is available separately. Domestic renewable volume falls from **$0.786 billion / 17 entries** to **$0.074 billion / 20 entries**; the domestic share increase occurs on a small, shrinking financing-volume base.

The complete dollar and financing-entry denominators, unknown coverage, endpoint bounds and change bounds for all categories are in `full_technology_geography_coverage.csv` and `full_technology_geography_changes.csv`. The reproducible addition is `technology_diagnostics.py`. No technology-specific decomposition or causal model is claimed from this diagnostic.

The volume/count distinction also matters in the prespecified main decomposition: loans' within-cell contribution is negative in dollar-weighted results but positive in financing-entry counts. This is reporting-entry allocation, not a count of independently identified projects or a measure of access. The joint accounting identifies arithmetic sources of a shift, not behavioral or causal mechanisms.

## Exploratory technology-specific accounting, independently verified
After the full technology diagnostic, a dated follow-on plan froze all four technologies × three geography scopes × seven originally specified measurement variants. All **84 targets** are reported: **77 defined decompositions and seven undefined Other/domestic comparisons** with no early allocable volume. The independent audit reproduced all 168 endpoints, defined accounting identities, support weights/counts and bounds. There were no additional periods, favored categories or model selection.

For known international renewable recorded amounts, the **+40.34-point** increase decomposes as:

| Provider × reported-mechanism-portfolio accounting term | Contribution |
|---|---:|
| Composition among common cells |+10.93 pp|
| Within-common-cell allocation |+5.76 pp|
| Recorded cell entry |+25.29 pp|
| Recorded cell exit |−1.64 pp|
| Total |+40.34 pp|

Common provider × portfolio cells cover 93.92% of early allocated renewable volume and 70.96% of late volume. The principal additional finding is that recorded cell support turnover and joint composition contribute much more than within-common-cell allocation. The within term holds provider and broad reported-mechanism portfolio fixed. It does not hold detailed renewable technology, recipient, borrower or project characteristics fixed. Entry means the cell has positive allocable reported volume in the late window and none in the early window; this may reflect source reporting and does not establish genuine first activity.

The full signed cell-contribution table is preserved, including zero and offsetting terms. Largest arithmetic contributions to the international renewable change are:

| Recorded provider × portfolio cell | Support | Composition | Within | Entry/exit | Net |
|---|---|---:|---:|---:|---:|
| France × Loan |Entry|0.00|0.00|+25.22|+25.22|
| Canada × Loan |Common|+13.63|−1.40|0.00|+12.23|
| Germany × Guarantee |Common|+4.13|+0.40|0.00|+4.53|
| Japan × Loan |Common|−1.23|−0.94|0.00|−2.17|
| China × Guarantee |Common|−5.10|+6.44|0.00|+1.34|

All entries in the last four columns are percentage points, not financing amounts. The France × Loan cell contains $5.168 billion in late known-international renewable volume; the archive has no positive early volume for that cell. This must not be called a new recipient-country or new-project effect. Further source investigation would be needed to distinguish new financing activity from expanded reporting coverage or changes in source instrument coding.

The renewable international change remains +40.01 pp using fixed FY2023 classes, +41.00 pp with once-deflated amounts, and +40.17 pp after exact-copy removal. Financing-entry weighting yields +25.86 pp and a much smaller +4.57 pp entry-cell term, showing that the dollar result is not interchangeable with reporting-entry allocation. The original whole-window largest-entry exclusions do not alter the international renewable result, because both removed entries are outside this stratum; this is not a renewable-specific concentration test.

Complete outputs: `technology_allocation_decomposition.csv`, `technology_allocation_endpoints.csv`, `technology_allocation_cells.csv`, and `technology_signed_cell_contributions_sorted.csv`. Reproduce with `decompose_technology_geography.py` after the preceding scripts. The comparison chart is `international_renewable_fossil_allocation.png` and a vector PDF version; it uses independently verified diagnostic endpoints and reports financing volume and coverage alongside shares.


## Source-basis sensitivity: what remains after quarantining the flagged block
The dated, audited source-sensitivity plan quarantines all three Dogger Bank records together (Excel7410,8413,8034), totalling **$4.57995 billion**, without recoding or deleting any other entry. This is a source-meaning check, not an assertion that the records are all invalid. Official BPI contract lists match the two largest original amounts (€2,400 million and €1,180 million), identify contract amounts, and do not verify them as loan principal. The additional A/B record's distinct financing layer or overlap remains unresolved.

| Known international renewable archive | Early window | Late window | High-income share change |
|---|---:|---:|---:|
| Unaltered recorded-value share |10.90%|51.24%|+40.34 pp|
| All three flagged records quarantined |10.90%|34.79%|+23.89 pp|
| Unaltered recorded nominal USD |$23.455 bn|$18.156 bn|Not a share measure|
| Quarantined recorded nominal USD |$23.455 bn|$13.577 bn|Not a share measure|
| Unaltered entries |132|175|Reporting units|
| Quarantined entries |132|172|Reporting units|

All three records are late high-income observations. Their zero-to-full inclusion therefore produces a **+23.89 to +40.34 percentage-point conditional-change envelope** over this flagged block. It is not a confidence interval, a population uncertainty bound, or a validation of all remaining records. The known missing amount remains missing. The remaining values should not be described collectively as verified loan principal, transferred public funds or additional investment.

## Provider-country-only accounting: robustness to reported mechanism labels
A second source-classification check retains every raw observation and changes only the cell definition to provider. The complete four-technology × three-geography grid contains 12 targets, with 11 defined and one undefined. International renewable endpoints remain exactly unchanged, but the allocation of the +40.34-point change is:

- Joint provider × reported-mechanism portfolio cells: +10.93 composition, +5.76 within, +25.29 entry, −1.64 exit
- Provider-country-only cells: +26.16 composition, +14.19 within-provider, 0.00 high-income entry/exit contribution

The recorded France Loan cell is an entering mechanism-labelled cell, while France already appears as a provider in the early renewable sample. Thus the large reported-mechanism support term cannot be interpreted as provider entry. The coarser within-provider term allows reported financing-mechanism, detailed-technology and borrower composition to change; it is a different estimand rather than a preferred causal model. Both exact accountings are valid arithmetic on the archive, but financial interpretation depends on source semantics.

The usable research contribution is therefore a source-aware comparative allocation study: distinguish conditional high-income concentration from total coverage, distinguish renewable and fossil patterns, expose support/composition dependence on cell definitions, and bound a concretely identified source-basis problem. The arithmetic is independently reproducible; the archive is not yet a fully validated homogeneous financial-volume panel.

## Final measurement interaction check and strongest supported conclusion
The final authorized diagnostic applies exactly the same three-record quarantine to the complete 12-target provider-country-only grid. Nonrenewable results are unchanged. For known international renewables, the conditional increase is **+23.89 pp = +23.10 pp provider-country composition +0.80 pp within-provider**, with zero high-income entry/exit contribution. The unaltered archive's +14.19 pp within-provider-country contribution falls sharply after quarantine. Therefore the magnitude of apparent within-provider-country reallocation is not robust to the documented amount-basis problem.

The strongest defensible conclusion is narrower: **the archive shows a higher high-income share of recorded international renewable values in the late window, including under joint quarantine of the flagged block, while the apparent within-provider driver is source-sensitive.** The remaining record values are not comprehensively validated homogeneous financial principal. The contrast with fossil allocation remains descriptively useful; causal policy effects, access gains, verified investment expansion and universal cost-of-capital claims are not established.

This final check is in `provider_only_quarantine_decomposition.csv`, `provider_only_quarantine_endpoints.csv` and `provider_only_quarantine_cells.csv`. Source-audit and arithmetic-audit conclusions must remain distinct. No additional analyses follow this gate without a new substantive justification and review.

Provider identity in these calculations is institutionGroup, the provider country. Multiple agencies from that country are pooled; within-country terms do not describe a fixed individual bank or agency.
