from pathlib import Path
from collections import defaultdict
import pandas as pd,numpy as np,json
O=Path(__file__).resolve().parent.parent
src=pd.read_csv(O/'clean_eca_income_mapped.csv');out=pd.read_csv(O/'technology_allocation_decomposition.csv');ends=pd.read_csv(O/'technology_allocation_endpoints.csv')
assert len(out)==84 and len(ends)==168
assert out[['variant','technology','geography']].drop_duplicates().shape[0]==84
pmap={'Canada':'CAN','United States':'USA','Japan':'JPN','United Kingdom':'GBR','Korea':'KOR','Germany':'DEU','China':'CHN','Australia':'AUS','Italy':'ITA','Mexico':'MEX','India':'IND','France':'FRA','Russia':'RUS','South Africa':'ZAF','Indonesia':'IDN','Turkey':'TUR'}
selected=src[src.FY.isin([2013,2014,2015,2020,2021,2022])]
largest=[selected[selected.FY<=2015].nominal_usd.idxmax(),selected[selected.FY>=2020].nominal_usd.idxmax()]
for result in out.to_dict('records'):
 variant=result['variant'];fy=2023 if variant=='fixed_FY2023' else 2013
 z=selected.copy()
 if variant=='drop_exact_copies':z=z[~z.exact_duplicate_subsequent]
 if variant=='leave_largest_entry_each_window':z=z.drop(largest)
 z=z[z.technology_group.eq(result['technology'])]
 if result['geography']!='All locations':
  domestic=z.recipient_iso3.eq(z.provider.map(pmap));z=z[z.recipient_iso3.notna() & (domestic if result['geography']=='Domestic' else ~domestic)]
 cells=[defaultdict(lambda:[0.,0.]),defaultdict(lambda:[0.,0.])];tot=[0.,0.];known=[0.,0.];hi=[0.,0.];unk=[0.,0.];n=[0,0];missing=[0,0];nominal=[0.,0.]
 for r in z.to_dict('records'):
  t=int(r['FY']>=2020);n[t]+=1;missing[t]+=pd.isna(r['nominal_usd']);nominal[t]+=r['nominal_usd'] if pd.notna(r['nominal_usd']) else 0
  v=1. if variant=='entry_counts' else r['real2020_usd_once'] if variant=='once_deflated' else r['nominal_usd_source_fx_sensitivity'] if variant=='documented_source_fx' else r['nominal_usd']
  if pd.isna(v):continue
  tot[t]+=v;inc=r[f'income_FY{fy}']; high=inc=='H'
  if inc not in ['H','L','LM','UM']:unk[t]+=v;continue
  known[t]+=v;hi[t]+=v*high
  if v<=0:continue
  p='Aggregate residual' if r['aggregate_name_flag'] else r['instrument'] if r['instrument'] in ['Loan','Guarantee'] else 'Other instrument'
  key=(r['provider'],p);cells[t][key][0]+=v;cells[t][key][1]+=v*high
 for t,w in enumerate(['early','late']):
  rr=ends[(ends.variant==variant)&(ends.technology==result['technology'])&(ends.geography==result['geography'])&(ends.window==w)].iloc[0]
  expected=dict(entries=n[t],reported_nominal_usd=nominal[t],missing_source_usd_entries=missing[t],observed_weight=tot[t],allocable_weight=known[t],high_weight=hi[t],unknown_weight=unk[t],high_share=hi[t]/known[t] if known[t] else np.nan,lower_observed_weight_bound=hi[t]/tot[t] if tot[t] else np.nan,upper_observed_weight_bound=(hi[t]+unk[t])/tot[t] if tot[t] else np.nan)
  for k,v in expected.items():assert np.isclose(rr[k],v,rtol=1e-12,atol=1e-5,equal_nan=True),(variant,result['technology'],result['geography'],k)
 if min(known)<=0:
  assert result['status'].startswith('Undefined') and pd.isna(result['composition']);continue
 assert result['status']=='Defined'
 terms=dict(composition=0.,within=0.,entry=0.,exit=0.);counts=dict(common_cells=0,entry_cells=0,exit_cells=0);com=[0.,0.]
 for key in set(cells[0])|set(cells[1]):
  if key not in cells[0]:terms['entry']+=cells[1][key][1]/known[1];counts['entry_cells']+=1
  elif key not in cells[1]:terms['exit']-=cells[0][key][1]/known[0];counts['exit_cells']+=1
  else:
   a,b=cells[0][key],cells[1][key];w0=a[0]/known[0];w1=b[0]/known[1];h0=a[1]/a[0];h1=b[1]/b[0];com[0]+=w0;com[1]+=w1
   terms['composition']+=(w1-w0)*(h0+h1)/2;terms['within']+=(h1-h0)*(w0+w1)/2;counts['common_cells']+=1
 exp={**terms,**counts,'common_weight_share_early':com[0],'common_weight_share_late':com[1],'delta_high_share':hi[1]/known[1]-hi[0]/known[0],'delta_lower_observed_weight_bound':hi[1]/tot[1]-(hi[0]+unk[0])/tot[0],'delta_upper_observed_weight_bound':(hi[1]+unk[1])/tot[1]-hi[0]/tot[0]}
 for k,v in exp.items():assert abs(v-result[k])<1e-11,(variant,result['technology'],result['geography'],k)
print('PASS84 target rows,168 endpoints; undefined',sum(out.status!='Defined'),'all terms/support counts/coverage independently matched')
(O/'independent_audit/stratified_check.json').write_text(json.dumps({'target_rows':84,'endpoint_rows':168,'undefined_rows':int(sum(out.status!='Defined')),'all_match':True,'original_largest_source_rows':src.loc[largest,'source_excel_row'].tolist()},indent=2))
