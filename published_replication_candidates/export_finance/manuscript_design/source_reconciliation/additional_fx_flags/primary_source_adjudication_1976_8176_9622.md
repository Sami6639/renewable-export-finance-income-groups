# Bounded primary-source adjudication: fixed rows 1976, 8176, 9622

Reviewed 18 October 2026. No outcome variables or model results examined; no input edits, automatic repairs, discrepancy thresholds, or new row selection.

## Row 1976: confirmed_range_original_lower_bound_and_usd_inconsistency; exact_point_unresolved

CAD 5–15 million range

CAD5m is consistent with the disclosed lower bound. USD470079 is inconsistent with that lower bound at supplied XR. A repair to USD4701000 would encode a lower-bound estimate, not a disclosed exact commitment. Do not change original to CAD500000. Range handling requires an explicit outcome-blind policy.

Source: https://www.edc.ca/content/dam/edc/en/corporate/disclosure/reporting/2014-individual-transactions.pdf

Locator: Page 19 (PDF index 18), 04-07-2014, United Kingdom, Comerica Bank (Endurance Wind Power Inc.), Guarantee; column header Range (Cdn.$).

## Row 8176: usd_loan_magnitude_supported; exact_amount_and_fx_basis_unresolved

US$32 million (A$41 million); table A$13.95m + A$13.60m + A$13.60m = A$41.15m equivalent

EFA and ADB support a US-dollar-denominated loan about US$32m. They do not establish exact US$32.15m or the VND738752210000 basis. Implied XR is 0.0000435193283550, which rounds to 0.000044 at six decimals, not displayed 0.000043; truncation or different rate basis remains possible, but not proved. Do not describe the residual as confirmed ordinary rounding. FY2020 may be fiscal start-year coding: official reporting period is 2020–2021, signing May2021, financial close Aug2021. Do not silently change FY without global convention.

Source: https://www.exportfinance.gov.au/media/ia4hq0br/exportfinanceaustralia_2020-2021_annualreportfinalonline.pdf

Locator: EFA annual report 2020–2021 p46 case study and pp103–104 facility table; table covers 1 July 2020–30 June 2021.

## Row 9622: unresolved_guarantee_amount_and_fx_basis

EUR1.6bn BASF total financial engagement disclosed by bank; not the ECA guarantee

Bank and transaction adviser confirm holdco/project financing context but neither corroborates EUR1.63m Euler Hermes guarantee or USD1.79m. No matching public ECA disclosure found in bounded official-source search. Implied USD/EUR 1.0981595092 differs from supplied 1.154. Cannot select rate or repair value without source basis. Do not replace the guarantee with EUR1.6bn private investment or infer thousandfold error.

Source: https://www.db.com/news/detail/20220509-lift-off-for-basf-wind-farm-project?language_id=1

Locator: Deutsche Bank 9 May2022, Deutsche Bank role section.

## Limits and decision implications

1976 now has a matched primary range disclosure, not a verified exact amount. 8176 has an independently corroborated USD loan magnitude, not an exact FX reconciliation. 9622 remains unresolved. These findings cannot constitute blanket clearance of all three numeric points. Protocol v3 should explicitly designate range treatment and unresolved-record treatment before any outcomes are run. Neither retaining nor excluding a record is silently authorized here.

Source access: EDC legacy ASPX disclosure returned an error, but the official archived PDF was accessible through indexed text. PDF screenshot calls for EDC and EFA returned cache errors; the findings use the official PDFs' extracted text and matching row/column labels. No IJGlobal access or paid-source bypass was attempted.
