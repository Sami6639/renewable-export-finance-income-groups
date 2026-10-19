Historical prerequisite analysis, superseded for revised interpretation by reconciled_revision_2026_10_18. Retained to document the preceding analysis and replay.

# Bounded renewable recipient-role and value-basis validation

18 October 2026. This audit does not alter source values, classification, inclusion, or outcome estimates.

## Selection frozen before source review

Using clean_eca_income_mapped.csv, select positive nominal_usd Renewable records with a known recipient ISO3 different from provider ISO3, separately for FY2013–2015 and FY2020–2022. Rank recorded nominal_usd descending, breaking ties by original source_excel_row ascending. Retain five in each window, irrespective of later discoveries. Income remains fixed FY2013; income does not enter selection. This is a targeted concentration audit, not a random validation sample or representative error-rate estimate. Raw country/provider names used in the initial preview produce the same ten records; the deposited implementation uses the existing ISO-based international definition.

Early: 1586, 109, 2253, 1907, 1908. Late: 7410, 8129, 8413, 9810, 9841. Preserve repeated projects and the different reported instruments. No replacement of flagged rows by smaller records.

## Scope and coverage

The ten audited entries carry $17,711,920,000 in recorded nominal dollars. Early five: $9,835,000,000 of $23,454,976,749 across 132 positive-dollar international renewable rows (41.9314%). Late five: $7,876,920,000 of $18,156,477,640.437286 across 173 rows (43.3835%). These are recorded-value coverage measures, not independently verified financial volumes.

Eight of the ten have official project-level evidence supporting the recorded host country; these carry $15,211,920,000 of recorded value. Two carry $2.5bn and identify a South African financial intermediary funding projects across Sub-Saharan countries. They are classified issuer-only/ambiguous, with the word issuer used as the requested category label; Standard Bank is specifically an intermediary borrower. The ultimate project-country distribution is unresolved.

Only two exact original-currency amounts were matched to official disclosure: Dogger Bank A/B EUR2.4bn and C EUR1.18bn, corresponding under archive FX to $4.05692bn. Those are guaranteed export-contract values, not verified direct-loan principal or agency exposure. None of the ten is certified here as an exact, independent, non-overlapping agency finance exposure with fully verified timing. Approximate lending corroboration must not be counted as exact entry validation.

## User Guide

The deposited OCI workbook, User Guide sheet, explicitly defines country as the country where the project is located. It defines amountUSD as amountOriginal multiplied by the exchange rate. This is the intended schema, not proof that each populated record follows it. The Standard Bank rows demonstrate why the intended country definition is insufficient for an unqualified physical-host estimand.

## Material findings

- Standard Bank, rows1907/1908: official JBIC Annual Report2015, printed p45 (PDF page47), describes a South Africa-based bank credit line supporting projects in various Sub-Saharan countries. Source country is intermediary location; ultimate locations are not allocated. Each archive row has original USD125m, XR1, and amountUSD $1.25bn, an internal tenfold conversion discrepancy. The original release was inaccessible. The annual report passage does not establish exact loan share, partial guarantee coverage, or replacement value. The discrepancy is not permission to divide both observations by ten or treat the guarantee as equal to lender principal.
- Karuma, rows109/2253: both record $1.435bn in different years for the same named Ugandan project. The official UEGCL annual report describes two 2014/2015 loan agreements totaling $1,435,158,682.48. It corroborates lending scale and host but does not establish two distinct packages corresponding to both archive entries. Possible announcement/closing duplication remains unresolved; do not automatically deduplicate.
- Kirchner/Cepernic, row1586: Argentine government sources corroborate Santa Cruz host and a $4.71435bn credit agreement; the archive records $4.465bn as Guarantee. Exact guarantor exposure and boundary remain unresolved.
- Dogger rows7410/8413: reuse the retained official BPI audit rather than repeat downloads. Exact contract values are matched. Additional A/B row8034 is outside this fixed top ten and retained as a previously documented potential financing-layer overlap, not silently excluded.
- Souapiti/Kaleta, row8129: official builder evidence supports Guinea host; the exact combined $1.72bn CEXIM facility is not independently reconciled.
- Angola, row9810: official EXIM June2023 announcement supports Angola host and >$900m direct lending for two plants, initially announced in2022. It does not verify archive FY2022 $1.3bn or justify substituting the later approval.
- Neom, row9841: official project sponsor confirms Saudi host and an Euler Hermes tranche at2023 close, but not the exact FY2022 $800m guarantee.

The independently identified fossil Trinidad-and-Tobago/UK issue is not part of this renewable validation and is not counted as evidence of renewable-country error.

## Deterministic text screening

All 570 positive-dollar renewable rows in FY2013–2022 were screened, carrying $69,905,103,037.43729. Country names and ISO aliases come from the deposited ISO workbook, dataset country-to-ISO mappings, and an explicit finite extra-alias dictionary. The entire dictionary is deposited. Search fields are project, projectInstitutionName, projectDesc, and entity. Whole-word/phrase boundary matching is case-insensitive for long names and case-sensitive for ISO codes/short aliases. A match to an ISO3 different from recorded recipient_iso3 triggers review. Source URLs, provider and institution fields are not searched because they predictably name publishers/providers rather than host locations. This is text screening of the available content, not geocoding.

227 rows carrying $29,503,412,215 triggered review. Many matches refer to exporter, bank, corporate owner, incidental country, or ambiguous ISO abbreviation. Short codes can coincide with ordinary uppercase text; nested country names may also trigger. No match is evidence of a correct host and a flag is not proof of a wrong host. All match fields, literal aliases and mapped ISO codes are retained. Only the fixed top-ten records receive source-reviewed classifications here; all remaining560 stay unresolved, regardless of flag. This conservative disposition avoids falsely claiming all570 were source-validated. Regional wording such as Sub-Sahara is not itself a country alias, so the concentration audit detects an intermediary problem the country-name trigger alone can miss.

## Gate and manuscript recommendation

The gate for an unqualified physical-project-host allocation claim fails. The defensible estimand is the allocation of archive-reported values across archive-reported recipient-country income groups, with fixed FY2013 classification. Do not call these homogeneous finance commitments, new direct lending, disbursements, ultimate-country flows, or distinct agency exposure. Report the source limitations alongside the central results and preserve already-authorized sensitivities; do not silently recode outcomes. A full physical-host or reconciled-exposure estimand would require additional transaction-level documentation beyond this bounded validation.

## Reproduction

Run build_validation.py, write_audit.py, then finalize_validation.py in this directory. The first script regenerates the frozen selection, dictionary, screening and initial coverage; the second preserves the manual official-source assessment; the last merges reviewed statuses and records file hashes. Source registry uses paraphrases (no copied web quotations). This distribution includes compact derived ledgers/screens, not original source strings or full raw fields. Running these scripts after separately obtaining the inputs regenerates full local audit tables, including fixed_top10_raw.csv; these locally generated extracts must not be redistributed by default. Official source URLs and locators appear in official_source_registry.csv. The prior BPI audit report is included under extension/independent_audit; original PDFs are excluded and must be obtained separately. No source record has been edited.
