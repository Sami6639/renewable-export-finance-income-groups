"""Only the three jointly frozen Dogger Bank records are quarantined; no recoding."""
from pathlib import Path
import pandas as pd,numpy as np
O=Path(__file__).resolve().parent
d=pd.read_csv(O/'clean_eca_income_mapped.csv')
flagged=[7410,8413,8034]
f=d[d.source_excel_row.isin(flagged)].copy();assert len(f)==3
assert f.country.eq('United Kingdom').all() and f.income_FY2013.eq('H').all() and f.FY.between(2020,2022).all()
assert abs(f.nominal_usd.sum()-4579950000)<.01
f['source_amount_basis']='Unresolved financing layer'
f.loc[f.source_excel_row.isin([7410,8413]),'source_amount_basis']='Official guaranteed-export-contract list amount, not verified loan principal'
f['source_basis_reference']='https://www.bpifrance.com/storage/sites/7/2023/05/Liste-contrats-garantis-2004-2022.zip'
f.loc[f.source_excel_row.eq(8034),'source_basis_reference']=f.loc[f.source_excel_row.eq(8034),'source']
f.to_csv(O/'dogger_bank_quarantine_source_ledger.csv',index=False)
d['window']=np.select([d.FY.between(2013,2015),d.FY.between(2020,2022)],['early','late'],default='excluded')
# France-only flagged rows are international. General same-country classification as frozen elsewhere.
providers={'Canada':'CAN','United States':'USA','Japan':'JPN','United Kingdom':'GBR','Korea':'KOR','Germany':'DEU','China':'CHN','Australia':'AUS','Italy':'ITA','Mexico':'MEX','India':'IND','France':'FRA','Russia':'RUS','South Africa':'ZAF','Indonesia':'IDN','Turkey':'TUR'}
d['provider_iso3']=d.provider.map(providers)
x=d[d.technology_group.eq('Renewable')&d.recipient_iso3.notna()&d.recipient_iso3.ne(d.provider_iso3)&d.window.ne('excluded')].copy()
rows=[]
for mode in ['Unaltered archive','All three Dogger records quarantined']:
 q=x if mode=='Unaltered archive' else x[~x.source_excel_row.isin(flagged)]
 for w in ['early','late']:
  a=q[q.window.eq(w)];known=a.income_FY2013.isin(['L','LM','UM','H']);total=a.nominal_usd.sum();alloc=a.loc[known,'nominal_usd'].sum();hi=a.loc[a.income_FY2013.eq('H'),'nominal_usd'].sum()
  rows.append({'scenario':mode,'window':w,'entries':len(a),'recorded_nominal_usd':total,'allocable_recorded_nominal_usd':alloc,'high_income_recorded_nominal_usd':hi,'high_share_allocable':hi/alloc,'missing_amount_entries':int(a.nominal_usd.isna().sum()),'amount_basis':'Mixed recorded source values; remainder not comprehensively validated financing principal'})
r=pd.DataFrame(rows);r.to_csv(O/'dogger_quarantine_endpoints.csv',index=False)
q=r.pivot(index='scenario',columns='window',values='high_share_allocable');q['delta_high_share']=q.late-q.early;q.to_csv(O/'dogger_quarantine_change_envelope.csv')
assert q.early.nunique()==1 and q.loc['All three Dogger records quarantined','late']<q.loc['Unaltered archive','late']
print(r.to_string(index=False));print(q.to_string())
