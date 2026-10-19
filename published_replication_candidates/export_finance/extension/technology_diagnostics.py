"""Authorized full stratification diagnostic added after main accounting; no selection."""
from pathlib import Path
import pandas as pd,numpy as np
O=Path(__file__).resolve().parent
d=pd.read_csv(O/'clean_eca_income_mapped.csv');d['window']=np.select([d.FY.between(2013,2015),d.FY.between(2020,2022)],['early','late'],default='excluded');d=d[d.window.ne('excluded')].copy()
providers={'Canada':'CAN','United States':'USA','Japan':'JPN','United Kingdom':'GBR','Korea':'KOR','Germany':'DEU','China':'CHN','Australia':'AUS','Italy':'ITA','Mexico':'MEX','India':'IND','France':'FRA','Russia':'RUS','South Africa':'ZAF','Indonesia':'IDN','Turkey':'TUR'}
d['provider_iso3']=d.provider.map(providers);d['income_known']=d.income_FY2013.isin(['L','LM','UM','H']);d['high']=d.income_FY2013.eq('H');d['entry_weight']=1
rows=[]
for tech in ['All','Fossil','Renewable','Grid','Other']:
 t=d if tech=='All' else d[d.technology_group.eq(tech)]
 for geography in ['All locations','Known international','Domestic']:
  q=t
  if geography=='Known international':q=t[t.recipient_iso3.notna()&t.recipient_iso3.ne(t.provider_iso3)]
  if geography=='Domestic':q=t[t.recipient_iso3.notna()&t.recipient_iso3.eq(t.provider_iso3)]
  for unit,weight in [('Nominal USD','nominal_usd'),('Financing entries','entry_weight')]:
   for window in ['early','late']:
    a=q[q.window.eq(window)];total=a[weight].sum();known=a.loc[a.income_known,weight].sum();hi=a.loc[a.high,weight].sum();unknown=a.loc[~a.income_known,weight].sum()
    rows.append({'technology':tech,'geography':geography,'unit':unit,'window':window,'entries':len(a),'reported_nominal_usd':a.nominal_usd.sum(),'missing_usd_entries':int(a.nominal_usd.isna().sum()),'total_weight':total,'known_income_weight':known,'high_income_weight':hi,'unknown_income_weight':unknown,'high_share_known':hi/known if known else np.nan,'unknown_weight_share':unknown/total if total else np.nan,'high_lower_observed_weight':hi/total if total else np.nan,'high_upper_observed_weight':(hi+unknown)/total if total else np.nan})
r=pd.DataFrame(rows);r.to_csv(O/'full_technology_geography_coverage.csv',index=False)
p=[]
for keys,a in r.groupby(['technology','geography','unit']):
 e=a[a.window.eq('early')].iloc[0];l=a[a.window.eq('late')].iloc[0]
 p.append(dict(zip(['technology','geography','unit'],keys))|{'early_share_known':e.high_share_known,'late_share_known':l.high_share_known,'delta_share_known':l.high_share_known-e.high_share_known,'delta_lower_observed_weight':l.high_lower_observed_weight-e.high_upper_observed_weight,'delta_upper_observed_weight':l.high_upper_observed_weight-e.high_lower_observed_weight,'early_entries':e.entries,'late_entries':l.entries,'early_reported_nominal_usd':e.reported_nominal_usd,'late_reported_nominal_usd':l.reported_nominal_usd,'early_unknown_weight_share':e.unknown_weight_share,'late_unknown_weight_share':l.unknown_weight_share})
p=pd.DataFrame(p);p.to_csv(O/'full_technology_geography_changes.csv',index=False);print(p[p.unit.eq('Nominal USD')].to_string(index=False))
