from pathlib import Path
import pandas as pd,numpy as np,json
O=Path(__file__).resolve().parent.parent
x=pd.read_csv(O/'clean_eca_income_mapped.csv');c=pd.read_csv(O/'full_technology_geography_coverage.csv');changes=pd.read_csv(O/'full_technology_geography_changes.csv')
# Rebuild taxonomy from original source fields, independent of saved derived label.
def tech(r):
 if r['sector']=='Batteries' or r['stage']=='Transmission & Distribution':return 'Grid'
 if r['category']=='Fossil Fuel':return 'Fossil'
 if (r['category']=='Clean' or r['sector'] in ['Hydro - Large','Hydro - Small','Hydro - large','Biomass','Biofuels','Renewables - Other']) and r['sector'] not in ['Climate','Fuel Cells + Hydrogen','Batteries']:return 'Renewable'
 return 'Other'
assert (x.apply(tech,axis=1)==x.technology_group).all()
pmap={'Canada':'CAN','United States':'USA','Japan':'JPN','United Kingdom':'GBR','Korea':'KOR','Germany':'DEU','China':'CHN','Australia':'AUS','Italy':'ITA','Mexico':'MEX','India':'IND','France':'FRA','Russia':'RUS','South Africa':'ZAF','Indonesia':'IDN','Turkey':'TUR'}
for r in c.to_dict('records'):
 total=known=hi=unk=dollars=0.;n=missing=0
 for a in x.to_dict('records'):
  if a['FY'] not in ([2013,2014,2015] if r['window']=='early' else [2020,2021,2022]):continue
  if r['technology']!='All' and tech(a)!=r['technology']:continue
  if r['geography']!='All locations':
   if pd.isna(a['recipient_iso3']):continue
   same=a['recipient_iso3']==pmap[a['provider']]
   if (r['geography']=='Domestic')!=same:continue
  n+=1;missing+=pd.isna(a['nominal_usd']);v=a['nominal_usd'];dollars+=v if pd.notna(v) else 0
  v=1. if r['unit']=='Financing entries' else v
  if pd.isna(v):continue
  total+=v
  if a['income_FY2013'] in ['H','UM','LM','L']:
   known+=v
   if a['income_FY2013']=='H':hi+=v
  else:unk+=v
 for k,v in {'entries':n,'missing_usd_entries':missing,'reported_nominal_usd':dollars,'total_weight':total,'known_income_weight':known,'high_income_weight':hi,'unknown_income_weight':unk}.items():assert np.isclose(v,r[k],rtol=1e-12,atol=1e-5),(r,k,v)
 for k,v in {'high_share_known':hi/known if known else np.nan,'high_lower_observed_weight':hi/total if total else np.nan,'high_upper_observed_weight':(hi+unk)/total if total else np.nan}.items():assert np.isclose(v,r[k],equal_nan=True)
for r in changes.to_dict('records'):
 z=c[(c.technology==r['technology'])&(c.geography==r['geography'])&(c.unit==r['unit'])].set_index('window');e=z.loc['early'];l=z.loc['late']
 for k,v in {'delta_share_known':l.high_share_known-e.high_share_known,'delta_lower_observed_weight':l.high_lower_observed_weight-e.high_upper_observed_weight,'delta_upper_observed_weight':l.high_upper_observed_weight-e.high_lower_observed_weight}.items():assert np.isclose(v,r[k],equal_nan=True)
print('All',len(c),'endpoint rows and',len(changes),'change rows independently verified. Raw taxonomy rederived for all2908 rows.')
print(c.query("technology in ['Renewable','Fossil'] and geography=='Known international' and unit=='Nominal USD'").to_string(index=False))
print(changes.query("technology=='Renewable' and geography=='All locations' and unit=='Nominal USD'").to_string(index=False))
(O/'independent_audit/technology_check.json').write_text(json.dumps({'endpoint_rows':len(c),'change_rows':len(changes),'all_match':True,'taxonomy_source_rows':len(x)},indent=2))
