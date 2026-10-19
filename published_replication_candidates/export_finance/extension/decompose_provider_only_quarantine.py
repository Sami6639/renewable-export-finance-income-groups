"""Provider-only source-classification robustness; approved12-target grid, all raw rows retained."""
from pathlib import Path
import pandas as pd,numpy as np
O=Path(__file__).resolve().parent
d=pd.read_csv(O/'clean_eca_income_mapped.csv');d=d[~d.source_excel_row.isin([7410,8413,8034])].copy();d['window']=np.select([d.FY.between(2013,2015),d.FY.between(2020,2022)],['early','late'],default='excluded');d=d[d.window.ne('excluded')].copy()
providers={'Canada':'CAN','United States':'USA','Japan':'JPN','United Kingdom':'GBR','Korea':'KOR','Germany':'DEU','China':'CHN','Australia':'AUS','Italy':'ITA','Mexico':'MEX','India':'IND','France':'FRA','Russia':'RUS','South Africa':'ZAF','Indonesia':'IDN','Turkey':'TUR'}
d['provider_iso3']=d.provider.map(providers)
d['portfolio']=np.select([d.aggregate_name_flag,d.instrument.eq('Loan'),d.instrument.eq('Guarantee')],['Aggregate residual','Loan','Guarantee'],default='Other instrument');d['entry_count']=1.
exclude_largest=d.loc[d.groupby('window').nominal_usd.idxmax(),'source_excel_row'].tolist()
variants=[('primary_nominal',2013,'nominal_usd','all')]
rows=[];endpoints=[];cells=[]
for variant,fy,amount,restriction in variants:
 x=d.copy()
 if restriction=='dedup':x=x[~x.exact_duplicate_subsequent]
 if restriction=='largest':x=x[~x.source_excel_row.isin(exclude_largest)]
 x['weight']=x[amount];x['known']=x[f'income_FY{fy}'].isin(['L','LM','UM','H']);x['high']=x[f'income_FY{fy}'].eq('H')
 for technology in ['Fossil','Renewable','Grid','Other']:
  t=x[x.technology_group.eq(technology)]
  for geography in ['All locations','Known international','Domestic']:
   q=t
   if geography=='Known international':q=t[t.recipient_iso3.notna()&t.recipient_iso3.ne(t.provider_iso3)]
   if geography=='Domestic':q=t[t.recipient_iso3.notna()&t.recipient_iso3.eq(t.provider_iso3)]
   meta={'variant':variant,'technology':technology,'geography':geography,'fixed_income_FY':fy};win={}
   for w in ['early','late']:
    a=q[q.window.eq(w)];total=a.weight.sum();known=a.loc[a.known,'weight'].sum();hi=a.loc[a.high,'weight'].sum();unknown=a.loc[~a.known,'weight'].sum()
    z={'window':w,'entries':len(a),'reported_nominal_usd':a.nominal_usd.sum(),'missing_source_usd_entries':int(a.nominal_usd.isna().sum()),'observed_weight':total,'allocable_weight':known,'high_weight':hi,'unknown_weight':unknown,'high_share':hi/known if known else np.nan,'lower_observed_weight_bound':hi/total if total else np.nan,'upper_observed_weight_bound':(hi+unknown)/total if total else np.nan}
    win[w]=z;endpoints.append(meta|z)
   base=meta|{'delta_high_share':win['late']['high_share']-win['early']['high_share'],'delta_lower_observed_weight_bound':win['late']['lower_observed_weight_bound']-win['early']['upper_observed_weight_bound'],'delta_upper_observed_weight_bound':win['late']['upper_observed_weight_bound']-win['early']['lower_observed_weight_bound']}
   if min(win['early']['allocable_weight'],win['late']['allocable_weight'])<=0:
    rows.append(base|{'status':'Undefined: zero allocable weight in at least one window'});continue
   a=q[q.known&q.weight.gt(0)].copy();a['hi_weight']=a.weight*a.high
   c=a.groupby(['provider','window']).agg(weight=('weight','sum'),hi=('hi_weight','sum')).reset_index();es=c[c.window.eq('early')].drop(columns='window').set_index(['provider']);ls=c[c.window.eq('late')].drop(columns='window').set_index(['provider']);c=es.join(ls,lsuffix='_early',rsuffix='_late',how='outer')
   c['support']=np.select([c.weight_early.notna()&c.weight_late.notna(),c.weight_early.isna()],['common','entry'],default='exit')
   for w in ['early','late']:c['w_'+w]=c['weight_'+w].fillna(0)/win[w]['allocable_weight'];c['h_'+w]=c['hi_'+w]/c['weight_'+w]
   co=c.support.eq('common');c['composition']=0.;c['within']=0.;c['entry']=0.;c['exit']=0.
   c.loc[co,'composition']=(c.loc[co,'h_early']+c.loc[co,'h_late'])/2*(c.loc[co,'w_late']-c.loc[co,'w_early'])
   c.loc[co,'within']=(c.loc[co,'w_early']+c.loc[co,'w_late'])/2*(c.loc[co,'h_late']-c.loc[co,'h_early'])
   c.loc[c.support.eq('entry'),'entry']=c.w_late*c.h_late;c.loc[c.support.eq('exit'),'exit']=-c.w_early*c.h_early
   terms=c[['composition','within','entry','exit']].sum();res=base['delta_high_share']-terms.sum();assert abs(res)<1e-12
   rows.append(base|{'status':'Defined',**terms.to_dict(),'closure_residual':res,'common_cells':int(co.sum()),'entry_cells':int(c.support.eq('entry').sum()),'exit_cells':int(c.support.eq('exit').sum()),'common_weight_share_early':c.loc[co,'w_early'].sum(),'common_weight_share_late':c.loc[co,'w_late'].sum()})
   c=c.reset_index()
   for k,v in meta.items():c[k]=v
   cells.append(c)
r=pd.DataFrame(rows);e=pd.DataFrame(endpoints)
assert len(r)==12 and len(e)==24
# Principal endpoint equality against already-audited full diagnostic, before interpreting results.
old=pd.read_csv(O/'full_technology_geography_coverage.csv');old=old[old.unit.eq('Nominal USD')&old.technology.ne('All')];new=e[e.variant.eq('primary_nominal')]
j=new.merge(old,on=['technology','geography','window'],suffixes=('_new','_old'),validate='one_to_one')
assert len(j)==24
assert np.allclose(j.loc[j.technology.ne('Renewable'),'high_share'],j.loc[j.technology.ne('Renewable'),'high_share_known'],equal_nan=True,atol=1e-12)
assert np.allclose(j.loc[j.technology.ne('Renewable'),'reported_nominal_usd_new'],j.loc[j.technology.ne('Renewable'),'reported_nominal_usd_old'],atol=.001)
quarantine=pd.read_csv(O/'dogger_quarantine_endpoints.csv');quarantine=quarantine[quarantine.scenario.eq('All three Dogger records quarantined')]
check=e[e.technology.eq('Renewable')&e.geography.eq('Known international')].merge(quarantine,on='window',validate='one_to_one')
assert np.allclose(check.high_share,check.high_share_allocable,atol=1e-12)
r.to_csv(O/'provider_only_quarantine_decomposition.csv',index=False);e.to_csv(O/'provider_only_quarantine_endpoints.csv',index=False);all_cells=pd.concat(cells,ignore_index=True);all_cells.to_csv(O/'provider_only_quarantine_cells.csv',index=False)
all_cells['signed_total_contribution']=all_cells[['composition','within','entry','exit']].sum(axis=1);all_cells['absolute_total_contribution']=all_cells.signed_total_contribution.abs()
all_cells.sort_values(['variant','technology','geography','absolute_total_contribution'],ascending=[True,True,True,False]).to_csv(O/'provider_only_quarantine_signed_cell_contributions_sorted.csv',index=False)
print(r[r.variant.eq('primary_nominal')].to_string(index=False));print(r[r.technology.eq('Renewable')&r.geography.eq('Known international')].to_string(index=False))
