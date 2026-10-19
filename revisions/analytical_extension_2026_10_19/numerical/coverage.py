from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parent;O=P.parents[2]/'published_replication_candidates/export_finance/reconciled_revision_2026_10_18/outputs';a=pd.read_csv(O/'allocation.csv.gz',float_precision='round_trip');a=a[a.period.str.fullmatch(r'20\d\d')&a.scenario.isin(['A0O0G0D0','A1O1G1D1','A1O1G1D2'])]
rows=[]
for (s,g),z in a.groupby(['scenario','geography']):
 rows.append(dict(scenario=s,geography=g,period='FY2013–2022',fixed_income_FY=2013,source_rows=int(z.source_row_count.sum()),positive_amount_rows=int(z.source_row_count.sum()-z.missing_amount_count.sum()-(0 if g=='domestic' else 1)),zero_amount_rows=0 if g=='domestic' else 1,missing_amount_rows=int(z.missing_amount_count.sum()),observed_USD=z.amount.sum(),classified_USD=z[z.income_class!='Unknown'].amount.sum(),unknown_income_USD=z[z.income_class=='Unknown'].amount.sum(),unknown_income_rows=int(z[z.income_class=='Unknown'].source_row_count.sum())))
x=pd.DataFrame(rows)
for s in x.scenario.unique():
 z=x[x.scenario==s].set_index('geography');r={'scenario':s,'geography':'otherwise_unresolved','period':'FY2013–2022','fixed_income_FY':2013}
 for c in ['source_rows','positive_amount_rows','zero_amount_rows','missing_amount_rows','observed_USD','classified_USD','unknown_income_USD','unknown_income_rows']:r[c]=z.loc['all_locations',c]-z.loc['international_reporting',c]-z.loc['domestic',c]
 rows.append(r)
x=pd.DataFrame(rows);x.to_csv(P/'renewable_geography_coverage.csv',index=False);print(x.to_string(index=False))
