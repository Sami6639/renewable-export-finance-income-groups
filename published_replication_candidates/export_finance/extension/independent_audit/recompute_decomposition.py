from pathlib import Path
from collections import defaultdict
import pandas as pd,numpy as np,json
O=Path(__file__).resolve().parent.parent
source=pd.read_csv(O/'clean_eca_income_mapped.csv');out=pd.read_csv(O/'allocation_decomposition.csv');bounds=pd.read_csv(O/'allocation_coverage_bounds.csv')
providers={'Canada':'CAN','United States':'USA','Japan':'JPN','United Kingdom':'GBR','Korea':'KOR','Germany':'DEU','China':'CHN','Australia':'AUS','Italy':'ITA','Mexico':'MEX','India':'IND','France':'FRA','Russia':'RUS','South Africa':'ZAF','Indonesia':'IDN','Turkey':'TUR'}
errors=[]
for result in out.to_dict('records'):
 variant=result['variant'];port=result['portfolio'];fy=2023 if variant=='fixed_FY2023' else 2013
 z=source[source.FY.isin([2013,2014,2015,2020,2021,2022])].copy()
 if variant=='drop_exact_copies':z=z[~z.exact_duplicate_subsequent]
 if variant in ['international_known','domestic']:
  domestic=z.recipient_iso3.eq(z.provider.map(providers));z=z[z.recipient_iso3.notna() & (domestic if variant=='domestic' else ~domestic)]
 if variant=='leave_largest_entry_each_window':
  z=z.drop([z[z.FY<=2015].nominal_usd.idxmax(),z[z.FY>=2020].nominal_usd.idxmax()])
 cells=[defaultdict(lambda:[0.,0.]),defaultdict(lambda:[0.,0.])];total=[0.,0.];known=[0.,0.];hi=[0.,0.];unknown=[0.,0.]
 for r in z.to_dict('records'):
  p='Aggregate residual' if r['aggregate_name_flag'] else r['instrument'] if r['instrument'] in ['Loan','Guarantee'] else 'Other instrument'
  if port!='All' and p!=port:continue
  t=int(r['FY']>=2020);v=1. if variant=='entry_counts' else r['real2020_usd_once'] if variant=='once_deflated' else r['nominal_usd_source_fx_sensitivity'] if variant=='documented_source_fx' else r['nominal_usd']
  if pd.isna(v):continue
  total[t]+=v;inc=r[f'income_FY{fy}']; high=inc=='H'
  if inc not in ['H','L','LM','UM']:unknown[t]+=v;continue
  known[t]+=v;hi[t]+=v*high
  if v<=0:continue
  key=(r['provider'],r['technology_group'],p);cells[t][key][0]+=v;cells[t][key][1]+=v*high
 terms=dict(composition=0.,within=0.,entry=0.,exit=0.);counts=dict(common_cells=0,entry_cells=0,exit_cells=0)
 for key in set(cells[0])|set(cells[1]):
  if key not in cells[0]:terms['entry']+=cells[1][key][1]/known[1];counts['entry_cells']+=1
  elif key not in cells[1]:terms['exit']-=cells[0][key][1]/known[0];counts['exit_cells']+=1
  else:
   a,b=cells[0][key],cells[1][key];w0=a[0]/known[0];w1=b[0]/known[1];h0=a[1]/a[0];h1=b[1]/b[0]
   terms['composition']+=(w1-w0)*(h0+h1)/2;terms['within']+=(h1-h0)*(w0+w1)/2;counts['common_cells']+=1
 for name,v in {**terms,**counts,'delta_high_share':hi[1]/known[1]-hi[0]/known[0]}.items():
  assert abs(v-result[name])<1e-11,(variant,port,name,v,result[name])
 for t,win in enumerate(['early','late']):
  expected=bounds[(bounds.variant==variant)&(bounds.portfolio==port)&(bounds.window==win)].iloc[0]
  for col,v in [('observed_weight',total[t]),('allocable_weight',known[t]),('high_income_weight',hi[t]),('unknown_income_weight',unknown[t])]:assert np.isclose(v,expected[col],rtol=1e-12,atol=1e-5),(variant,port,col)
print('Independently replayed',len(out),'decomposition rows and their endpoint coverage totals. All match.')
(O/'independent_audit/decomposition_check.json').write_text(json.dumps({'decomposition_rows_checked':len(out),'all_match':True,'max_term_tolerance':1e-11},indent=2))
