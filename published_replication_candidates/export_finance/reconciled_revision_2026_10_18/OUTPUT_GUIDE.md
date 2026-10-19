# Output guide and interpretation limits

The original input and provisional delivery remain unchanged. Monetary amounts are observed nominal USD on mixed archive/source bases, never certified common exposure or principal.

## Case families

- Core:24 A/O/G/D cases; IDs A0O0G0D0 through A1O1G1D2.
- Agreement overlay:12 O1 cases with `_agreement` suffix; two Karuma contracted-lending components at calendar agreement years2014/2015, with other rows still archive FY.
- Arithmetic quarantine:24 matched cases with `_Q1` suffix; four fixed additional arithmetic-flagged rows jointly excluded. These are a separate stress family, not inferred corrected amounts.
- Regional completion:12 G1 core plus6 G1 agreement cases, with four vertices each. Q0 only. These are unrestricted-income outer envelopes for the stipulated Standard Bank completion simplex, not bounds over actual eligible countries or total finance exposure.

## Principal tables

- `allocation.csv`: all36 core/overlay cases × four scopes ×12 annual/pooled periods × five income statuses. Known classes L/LM/UM/H and Unknown are kept separately. Share fields are proportions; observed and classified denominators are explicit. Missing amounts remain missing, with missing counts retained.
- `decomposition.csv`: every four-class endpoint and adjacent-year identity, terms in percentage points. Entry and exit are separate. All provider contributions and support are in `provider_contributions.csv`.
- `coverage_joint.csv`: exhaustive disjoint provider-known × recipient-status × income-known cells. `coverage_marginals.csv` flags overlap and must not be summed together.
- `endpoints.csv`: classified-share changes, observed-share changes and conditional unknown-income change bounds. Four separate marginal upper bounds are not jointly attainable; completed income shares lie on the sum-to-one simplex. Bounds condition on observed amounts and portfolio membership; missing amounts and unidentified international rows are not covered.
- `scenario_envelopes.csv`: separate core24, agreement12 and combined36 extrema, exact attaining cases and undefined counts. These are finite treatment envelopes, not confidence intervals.
- `paired_factor_effects.csv`, `factor_effect_ranges.csv`: every background-specific binary/three-level contrast, without averaging or scenario probabilities.
- `anchored_factorial_interactions.csv`: all15 nonempty subsets in each D0/D1 and D0/D2 cube. Exact anchored arithmetic differences, not causal interactions or tests.
- `arithmetic_quarantine_*.csv`: complete Q1 family, all matched Q1−Q0 effects, and separately labelled quarantine24/core-plus-quarantine48 envelopes. No Q1 auxiliary grid is implied.
- `secondary_FY2023_endpoint_*.csv`: complete core24 endpoint classification sensitivity, separate from primary FY2013.
- `completion_*.csv`: complete vertices, class and provider accounting, denominators/support, exact case hull/union scalar envelopes and numerical verification. Marginal extremes cannot generally occur together; source-case hulls are unioned, never convex-mixed.
- `influence/`: all core24 record/provider/package deletions and ledgers, annual share vectors, endpoint components, rankings, concentration and distinct top-recorded-dollar shares. Influence ranks are deterministic diagnostics, not evidence for trimming or sampling uncertainty.

## Validation

The archive and whole-Dogger corners reproduce prior audited values. Every primary and Q1 accounting identity closes to below3×10⁻¹⁴ percentage points. All operation orders, original raw fields and missingness, geography mass movements, and nonrenewable values are checked. The whole-archive arithmetic ledger includes2908 rows,2904 eligible arithmetic comparisons and34 material flags. Four additional Renewable flags were reviewed before revised outcomes and handled only by the approved fixed Q1 block.

Independent audit reports live in `independent_audit/`. Execution assertions are not a substitute for that independent review.
