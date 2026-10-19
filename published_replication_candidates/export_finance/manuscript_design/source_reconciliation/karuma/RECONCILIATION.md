# Karuma: evidence-only reconciliation of OCI rows 109 and 2253

Research date: 18 October 2026. No delivered files or source/analysis data were altered. This directory is a separate evidence supplement.

## Finding

**Strong evidence of duplicated reporting of one financing package, rather than two independent USD1.435bn commitments.** Two legally distinct facilities are real, but their amounts are USD789,337,275.36 and USD645,821,407.12, adding to USD1,435,158,682.48. Each OCI entry reports essentially the *entire sum*, not one component. Both OCI entries also cite the identical IJGlobal transaction, ID16091. Contract scans establish a 2013 EPC contract followed by loan agreements in 2014 and 2015; they do not establish a separate 2013 USD1.435bn loan.

This is a transaction-identity inference from primary financial terms plus archival provenance, not a finding that the publisher acknowledged a duplicate. Exact effective/closing dates and the original BU version were not independently recovered.

## Archive provenance (read from unchanged clean_eca_main.csv)

- Row109: FY2013, date2013-01-01, Loan, China Eximbank, Uganda, USD1,435,000,000, Karuma Hydroelectric Power Station. Its own description explicitly says the date is arbitrary and based on BU's 2013 listing; it mentions IJGlobal implying a March2015 loan agreement and reportedly not reaching financial close as of June2019.
- Row2253: FY2015, date2015-03-31, same provider/recipient/instrument and amount, Karuma Hydroelectric Power Plant (600MW).
- Both cite https://ijglobal.com/data/transaction/16091/karuma-hydroelectric-power-plant-600mw-ppp . The page was inaccessible in this research run; its present contents were not verified.
- Row109 additionally cites https://www.bu.edu/cgef/#/2013/Lender/Ex-Im-Bank . The current page returned no usable dataset text; historical 2013 coding was not reverified.
- Different project labels, entityKind values and dates explain why a literal exact-row deduplicator does not identify this relationship. They do not demonstrate independent finance.

## Primary documents inspected

### 1. Preferential Buyer Credit Loan Agreement: CHINA EXIMBANK PBC (2014)46 TOTAL No.(340)

Source discovery: AidData project30919, https://china.aiddata.org/projects/30919/ , Staff comments. Primary contract scan is hosted by a third party, not an official government host. Authenticity has not been independently certified; parties, terms and amounts are corroborated by UEGCL's official annual report.

Source URL: https://www.dropbox.com/s/znwu46a5h6vsclk/China%20EximBank%20Loan%20-%20Karuma%20Hydropower%20Dam%20and%20associated%20works%20Project%20PBC%20%282014%29%2046%20Total%20No%20340.pdf?dl=0

Downloaded same public URL with dl=1 to pbc_2014.pdf (46 pages). Relevant PNGs are retained and visually inspected. Printed p24 / PDF p26 visibly contains signatures for both parties, with names Maria Kiwanuka and Wang Zhi Jie.

- Cover, PDF page1: Government of Uganda (Ministry of Finance, Planning and Economic Development) as borrower; China Eximbank as lender. Handwritten date: “December 18, 2014”.
- Printed p3 / PDF p5, Article1 Commercial Contract definition: identifies the August16,2013 engineering/procurement/construction contract for the 600MW Karuma Hydropower Project and Karuma Interconnection Project, amended May6 and May15,2014; total USD1,688,421,979.39.
- Printed p7 / PDF p9, Article2.1: principal ceiling USD789,337,275.36.
- Same page Article2.4: finances no more than46.75% of that commercial-contract price. Short exact excerpt: “(46.75%) of the price of the Commercial Contract.”
- Same page Article2.2: fixed interest2%; management and commitment fees0.25%. Article2.3 specifies240 months maturity and84 months grace. These terms distinguish this facility from the BCL; they do not make it an extra full USD1.435bn package.

### 2. Buyer Credit Loan Agreement: Contract No.140302052015210069

Source URL: https://www.dropbox.com/s/rp79c47zockl9gi/China%20EximBank%20Loan%20-%20Karuma%20Hydropower%20Dam%20and%20associated%20works%20Project%20Contract%20No.%20140302052015210069.pdf?dl=0

Downloaded with dl=1 to bcl_2015.pdf (60 pages). Same third-party-host/provenance caveat as above.

- Printed p1 / PDF p3: handwritten agreement date “Feb, 20, 2015”; same lender and sovereign borrower; recital C finances38.25% of contract amount.
- Printed p2 / PDF p4: same August16,2013 EPC contract, same two May2014 addenda, same USD1,688,421,979.39 contract amount.
- Printed p9 / PDF p11, Article2.1: principal ceiling USD645,821,407.12. Article2.2 gives exact excerpt: “Percent (38.25%) of the Contract Amount.”
- Article2.3 on that page sets fifteen-year term from notice of commencement of disbursement period. Agreement date therefore must not automatically be called disbursement date or financial close.

### 3. Official UEGCL Annual Report2015, Note19(a), printed p66 / PDF p66

URL: https://uegcl.com/wp-content/uploads/2025/11/UEGCL-Annual-Report-For-the-18-Months-Ended-June-2015.pdf

Despite the URL filename, the document cover and accounts explicitly concern the year ended31December2015. Download retained as uegcl_2015.pdf and extracted text.

The note records precisely the same two sovereign-loan amounts and onward lending to UEGCL/UETCL for the Karuma dam plus associated transmission works/substations. It records an outstanding on-lent balance at31December2015 of USD63,690,304: that is an outstanding/disbursement measure, not the committed package total.

**Date discrepancy requiring disclosure:** the report calls the PBC agreement dated24November2014, whereas the scanned cover is18December2014. It agrees on BCL20February2015. Exact short quote: “the Buyer Credit Loan (BCL) Agreement dated February 20, 2015”. The discrepancy is within2014 and does not affect annual placement under agreement-year accounting. It should not be silently resolved by citing only the secondary database.

Official UEGCL2025 report, printed p163 / PDF p163, Note25(a), repeats the amounts and the November2014 PBC date: https://uegcl.com/wp-content/uploads/2026/01/UEGCL-Annual-Report-2025-Print-web.pdf . This was the prior audit's source. The independently retrieved2015 report provides contemporaneous corroboration.

### 4. Official Uganda Ministry of Finance Annual Budget Monitoring Report FY2013/14

Primary official URL: https://www.finance.go.ug/sites/default/files/archive-files/Publications/Annual%20Budget%20Monitoring%20Report%20FY2013-14_1.pdf

Alternate official URL: https://budget.finance.go.ug/sites/default/files/National%20Budget%20docs/Annual%20Budget%20Monitoring%20Report%20FY2013-14.pdf

Access limitation: full PDF requests timed out through web; direct first-host request returned403. The search engine returned substantial indexed passages, including printed p396 Karuma project review and p27 summary. Treat this as indexed-primary corroboration, not a locally verified page image.

Printed p396 says the financing agreement remained unfinalized at FY2013/14 end and links the low release to this delay. Short indexed excerpt: “the financing agreement had not yet been finalised.” It separately dates the EPC contract16August2013. This supports the distinction between construction/EPC activity and completed loan documentation. Do not reproduce the report's apparent EPC monetary-unit typographical errors as validated figures.

### 5. Official Uganda Finance debt report FY2014/15

URL: https://www.finance.go.ug/sites/default/files/archive-files/Publications/REPORT%20ON%20PUBLIC%20DEBT%20%28DOMESTIC%20AND%20EXTERNAL%20LOANS%29%20GUARANTEES%20OTHER%20FINANCIAL%20LIABILITIES%20AND%20GRANTS%20FOR%20FINANCIAL%20YEAR%202014-2015.pdf

Access limitation: indexed text only; full-file retrieval timed out / returned403. Printed p16 sections4.2.3–4.2.4 classify borrowing for Karuma and Isimba as FY2014/15 new loans, totaling aboutUSD1,917.7million across both projects. This does not alone establish a calendar-year2015 date for every Karuma tranche.

## Arithmetic and economic boundary

789,337,275.36 + 645,821,407.12 = 1,435,158,682.48.
46.75% + 38.25% =85%.
0.85 × 1,688,421,979.39 =1,435,158,682.4815 (rounding to cents matches facilities).
Each archive amount differs from this package by only158,682.48 (0.0111% of package), consistent with rounding toUSD1.435bn. Two archive entries sum toUSD2.870bn, nearly twice the documented85% financing package.

The shared contract includes hydropower *and transmission/interconnection*. This audit does not allocate the package's value between renewable generation and grid components. Sovereign loans and subsidiary/on-lent loans are financing layers; the on-lent balances should not be added as additional China Eximbank exposure.

## Recommended analytic handling, without editing existing files

1. Preserve the archive-reported baseline and deposit this relationship as a reviewed overlap group.
2. A minimal package-identity sensitivity can count the roundedUSD1.435bn once, retaining row2253 and excluding row109. Clearly label this an evidence-supported reconciliation scenario, not a verified March31 financial-close event. Reduction isUSD1.435bn nominal; both dates lie in the same2013–2015 window and recipient remainsUganda.
3. A more explicit *agreement-based* reconstruction replaces both records by the actual two facilities: USD789,337,275.36 in2014 andUSD645,821,407.12 in2015. This is preferable if the estimand is newly documented loan facilities. It changes record unit, precision, annual timing and deflation; it is not merely duplicate deletion. Date notes must retain the PBCNovember/December discrepancy. For window totals the replacement isUSD1,435,158,682.48, rather thanUSD2.870bn.
4. Do not call either scenario verified disbursements or financial-close accounting. A final effectiveness/disbursement-start notice, lender confirmation and original IJGlobal snapshot would be needed for that separate timing claim.
5. Confidence: high that these are two components of one documented package and that both archive rows carry the whole-package amount; strong but inferential that the archive contains temporal duplicate reporting. Lower confidence in exact archive-event dates and whether BU meant pledge, announcement, construction start or another date concept in2013.

## Remaining source gaps

- No original Parliament committee report or Hansard page from2015 was recovered. A scholarly paper references a2015 Committee on National Economy report, but not a verified accessible Karuma copy.
- AidData's claim of parliamentary ratification27February2015 differs from March2015 news accounts; neither is used here as the controlling primary date.
- No separate signedUSD1.435bn agreement from2013 was found. Absence alone is not proof; the positive same-contract/proportion evidence is the basis for reconciliation.
- No official Eximbank-hosted contract copy was found. The contract scans are primary documents accessed via AidData-linked public hosting, with official UEGCL corroboration.

## Extraction caution

The two agreement PDFs are image scans. Automated OCR can misread handwritten dates, so the factual dates and numeric amounts above were visually checked against the retained page PNGs. Any partial OCR files are navigation aids, not controlling evidence.
