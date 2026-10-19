from pathlib import Path
import pandas as pd,numpy as np,json,hashlib
P=Path(__file__).resolve().parent; O=P.parents[2]/'published_replication_candidates/export_finance/reconciled_revision_2026_10_18/outputs'
def read(f):return pd.read_csv(O/f,float_precision='round_trip')
S=['A0O0G0D0','A1O1G1D1','A1O1G1D2']; C=['L','LM','UM','H']; checks=[]
a=read('allocation.csv.gz'); d=read('decomposition.csv.gz'); p=read('provider_contributions.csv.gz')
a=a[(a.geography=='international_reporting')&a.income_class.isin(C)];d=d[(d.geography=='international_reporting')&(d.pair=='early_to_late')];p=p[(p.geography=='international_reporting')&(p.pair=='early_to_late')]
rows=[]
for cl in C:
 r={'class':cl}
 for s,name in zip(S,['Archive','D1','D2']):
  z=a[(a.scenario==s)&(a.income_class==cl)&a.period.isin(['early','late'])].set_index('period');delta=100*(z.loc['late','amount']/z.loc['late','classified_denominator']-z.loc['early','amount']/z.loc['early','classified_denominator'])
  assert abs(delta-d[(d.scenario==s)&(d.income_class==cl)].iloc[0].delta_pp)<1e-9
  r[name+'_change_pp']=delta
  for t in ['early','late']:
   r[name+'_'+t+'_USD_bn']=z.loc[t,'amount']/1e9;r[name+'_'+t+'_share_percent']=100*z.loc[t,'amount']/z.loc[t,'classified_denominator']
 rows.append(r)
pd.DataFrame(rows).to_csv(P/'four_class_main_results.csv',index=False)
a[(a.scenario.isin(S))&a.period.isin(['early','late'])].to_csv(P/'endpoint_levels_provenance.csv',index=False)
# Independently recompute provider identity from disclosed weights and within shares.
for _,r in p.iterrows():
 if r.support=='common':
  co=100*(r.weight_late-r.weight_early)*(r.within_share_late+r.within_share_early)/2
  wi=100*(r.weight_late+r.weight_early)*(r.within_share_late-r.within_share_early)/2
  assert abs(co-r.composition_pp)<1e-8 and abs(wi-r.within_pp)<1e-8
for (s,cl),g in p.groupby(['scenario','income_class']):
 z=d[(d.scenario==s)&(d.income_class==cl)].iloc[0]
 for term in ['composition_pp','within_pp','entry_pp','exit_pp']:assert abs(g[term].sum()-z[term])<1e-8
 assert abs(g[['composition_pp','within_pp','entry_pp','exit_pp']].to_numpy().sum()-z.delta_pp)<1e-8
h=p[(p.scenario.isin(S[1:]))&(p.income_class=='H')].copy();h['absolute_composition_rank']=h.groupby('scenario').composition_pp.transform(lambda x:x.abs().rank(ascending=False,method='first'));h.sort_values(['scenario','absolute_composition_rank']).to_csv(P/'provider_H_ranked_full.csv',index=False);h[h.absolute_composition_rank<=5].sort_values(['scenario','absolute_composition_rank']).to_csv(P/'provider_H_top5.csv',index=False)
cancel=[]
for s,g in h.groupby('scenario'):
 cancel.append({'scenario':s,'positive_within_pp':g.loc[g.within_pp>0,'within_pp'].sum(),'negative_within_pp':g.loc[g.within_pp<0,'within_pp'].sum(),'net_within_pp':g.within_pp.sum(),'composition_pp':g.composition_pp.sum()})
pd.DataFrame(cancel).to_csv(P/'within_cancellation.csv',index=False)
# Alternate FY2023 fixed classification: verify from separate amount table
v=read('secondary_FY2023_endpoint_allocation.csv');vd=read('secondary_FY2023_endpoint_decomposition.csv');vd=vd[vd.geography=='international_reporting'];v=v[v.geography=='international_reporting']
for _,r in vd.iterrows():
 z=v[(v.scenario==r.scenario)&(v.income_class==r.income_class)].set_index('period');assert abs(100*(z.loc['late','amount']/z.loc['late','classified_denominator']-z.loc['early','amount']/z.loc['early','classified_denominator'])-r.delta_pp)<1e-8
vd.to_csv(P/'FY2023_all24_decomposition.csv',index=False);vd[vd.scenario.isin(S)].to_csv(P/'FY2023_selected.csv',index=False);vd.groupby('income_class').delta_pp.agg(['min','max']).to_csv(P/'FY2023_ranges.csv')
# New shifted endpoint test from verified published annual sufficient statistics.
alt=[]
for s in S[1:]:
 for cl in C:
  row={'scenario':s,'income_class':cl,'early_window':'FY2014–2016','late_window':'FY2019–2021','geography':'international_reporting','fixed_income_FY':2013}
  for name,years in [('early',['2014','2015','2016']),('late',['2019','2020','2021'])]:
   z=a[(a.scenario==s)&(a.income_class==cl)&a.period.isin(years)];assert len(z)==3
   row[name+'_amount']=z.amount.sum();row[name+'_denominator']=z.classified_denominator.sum();row[name+'_share_percent']=100*z.amount.sum()/z.classified_denominator.sum()
  row['delta_pp']=row['late_share_percent']-row['early_share_percent'];alt.append(row)
alt=pd.DataFrame(alt);alt.to_csv(P/'alternative_windows.csv',index=False)
# Independent checks: annual amounts across four classes reproduce denominators; original pooling matches existing endpoints.
for (s,period),g in a.groupby(['scenario','period']):assert abs(g.amount.sum()-g.classified_denominator.iloc[0])<.001
for s in S:
 for cl in C:
  for label,years in [('early',['2013','2014','2015']),('late',['2020','2021','2022'])]:
   z=a[(a.scenario==s)&(a.income_class==cl)&a.period.isin(years)];r=a[(a.scenario==s)&(a.income_class==cl)&(a.period==label)].iloc[0];assert abs(z.amount.sum()-r.amount)<.001;assert abs(z.classified_denominator.sum()-r.classified_denominator)<.001
json.dump({'status':'PASS','checks':['all provider core and agreement contributions recomputed from weights and within shares','all provider sums match aggregate components','all four-class annual amounts close to classified denominators','original endpoint sums reproduced from annual amounts','all FY2023 endpoint deltas recomputed from nominal levels'],'source_commit':'776d41f57ff893ba0d88be8f09035dbbf9d417fa','source_hashes':{f:hashlib.sha256((O/f).read_bytes()).hexdigest() for f in ['allocation.csv.gz','decomposition.csv.gz','provider_contributions.csv.gz','secondary_FY2023_endpoint_allocation.csv','secondary_FY2023_endpoint_decomposition.csv']}},open(P/'verification.json','w'),indent=2)
print(pd.DataFrame(rows).to_string(index=False));print(pd.DataFrame(cancel).to_string(index=False));print(vd[vd.scenario.isin(S)][['scenario','income_class','delta_pp','composition_pp','within_pp']].to_string(index=False));print(alt[['scenario','income_class','delta_pp']].to_string(index=False));print(h[h.absolute_composition_rank<=5][['scenario','provider','composition_pp','within_pp']].to_string(index=False))
