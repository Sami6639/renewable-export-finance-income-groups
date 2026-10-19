"""Verify saved influence exports using direct deletion and regrouping. Gates must pass."""
import json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import ROOT, CLASSES, SCENARIOS, TERMS, load, transform, panel
from influence import INFLUENCE_PANELS, PACKAGES
from run_revision import gate
gate()
start=time.monotonic();out=ROOT/'outputs/influence';report={'method':'Direct pandas regrouping after physically removing rows; independent explicit endpoint algebra; all-output closure/ledger/rank checks.'}
keys=['scenario','panel','unit_type','unit_id']
ledger=pd.read_csv(out/'influence_entity_ledger.csv.gz',dtype={'unit_id':str})
assert len(ledger)==42408 and not ledger.duplicated(keys).any()
assert len(ledger[ledger.unit_type=='record'])==572*72
assert set(ledger.scenario)=={s['scenario'] for s in SCENARIOS}
assert set(ledger.panel)==set(INFLUENCE_PANELS)
report['ledger_counts_by_type']=ledger.groupby('unit_type').size().to_dict()
report['ledger_status_counts']=ledger.groupby(['unit_type','deletion_status']).size().rename('count').reset_index().to_dict('records')
endpoints=pd.concat([pd.read_csv(out/f'{kind}_influence_endpoint.csv.gz',dtype={'unit_id':str}) for kind in ['record','provider','package']],ignore_index=True)
assert len(endpoints)==169632 and not endpoints.duplicated(keys+['income_class']).any()
max_closure=0
for phase in ['baseline','deleted','influence']:
 residual=endpoints[f'{phase}_delta_pp']-endpoints[[f'{phase}_{t}' for t in TERMS[1:]]].sum(axis=1,min_count=4)
 assert residual.abs().max()<1e-8
 max_closure=max(max_closure,float(residual.abs().max()))
 grouped=endpoints.groupby(keys)[[f'{phase}_{t}' for t in TERMS]].sum(min_count=4)
 assert grouped[f'{phase}_delta_pp'].abs().max()<1e-8
 assert grouped[f'{phase}_within_pp'].abs().max()<1e-8
 assert grouped[[f'{phase}_{t}' for t in ['composition_pp','entry_pp','exit_pp']]].sum(axis=1,min_count=3).abs().max()<1e-8
j=endpoints.merge(ledger[keys+['removed_observed_amount_usd','removed_endpoint_component_count']],on=keys,validate='many_to_one')
for zero in [j.removed_observed_amount_usd.eq(0),j.removed_endpoint_component_count.eq(0)]:
 assert j.loc[zero,[f'influence_{t}' for t in TERMS]].fillna(0).eq(0).all().all()
report['maximum_endpoint_identity_residual_pp']=max_closure

def direct(q):
 z=q[q.income.isin(CLASSES)]
 provider=sorted(z.provider_key.unique())
 def mat(years):
  g=z[z.analytical_year.isin(years)].groupby(['provider_key','income']).amount.sum().unstack('income',fill_value=0)
  return g.reindex(index=provider,columns=CLASSES,fill_value=0).fillna(0).to_numpy(float)
 a=mat([2013,2014,2015]);b=mat([2020,2021,2022]);pa=a.sum(1);pb=b.sum(1);va=pa.sum();vb=pb.sum()
 ep=np.full((4,5),np.nan)
 if va>0 and vb>0:
  wa=pa/va;wb=pb/vb
  ha=np.divide(a,pa[:,None],out=np.zeros_like(a),where=pa[:,None]>0)
  hb=np.divide(b,pb[:,None],out=np.zeros_like(b),where=pb[:,None]>0)
  common=(pa>0)&(pb>0);enter=(pa==0)&(pb>0);exit=(pa>0)&(pb==0)
  ep[:,0]=b.sum(0)/vb-a.sum(0)/va
  ep[:,1]=((ha[common]+hb[common])/2*(wb[common]-wa[common])[:,None]).sum(0)
  ep[:,2]=((wa[common]+wb[common])[:,None]/2*(hb[common]-ha[common])).sum(0)
  ep[:,3]=(wb[enter,None]*hb[enter]).sum(0)
  ep[:,4]=-(wa[exit,None]*ha[exit]).sum(0)
  ep*=100
 g=z.groupby(['analytical_year','income']).amount.sum().unstack('income',fill_value=0)
 amounts=g.reindex(index=range(2013,2023),columns=CLASSES,fill_value=0).fillna(0).to_numpy(float)
 classified=amounts.sum(1);observed=q.groupby('analytical_year').amount.sum().reindex(range(2013,2023),fill_value=0).to_numpy(float)
 shares={name:100*np.divide(amounts,den[:,None],out=np.full_like(amounts,np.nan),where=den[:,None]>0) for name,den in [('classified',classified),('observed',observed)]}
 return ep,shares
raw=load();d0=raw[raw.technology_group.eq('Renewable')]
expected=[];direct_count=0;max_direct_residual=0
indexed=endpoints.set_index(keys+['income_class'])
for s in SCENARIOS:
 d=transform(d0,s)
 entities=[('record',str(i),(i,)) for i in sorted({r for ids in PACKAGES.values() for r in ids})]
 entities += [('provider',str(p),tuple(g.source_excel_row)) for p,g in d.groupby('provider_key')]
 entities += [('package',name,ids) for name,ids in PACKAGES.items()]
 for geography in INFLUENCE_PANELS:
  q=panel(d,geography);base_ep,base_annual=direct(q)
  for kind,unit_id,ids in entities:
   deleted=q[~q.source_excel_row.isin(ids)]
   ep,annual=direct(deleted)
   found=indexed.loc[(s['scenario'],geography,kind,unit_id)].loc[CLASSES]
   for phase,values in [('baseline',base_ep),('deleted',ep),('influence',ep-base_ep)]:
    actual=found[[f'{phase}_{t}' for t in TERMS]].to_numpy()
    np.testing.assert_allclose(actual,values,atol=1e-8,rtol=1e-10,equal_nan=True)
    residual=np.abs(actual-values)
    if np.isfinite(residual).any(): max_direct_residual=max(max_direct_residual,float(np.nanmax(residual)))
   for yi,year in enumerate(range(2013,2023)):
    for k,c in enumerate(CLASSES):
     r=dict(scenario=s['scenario'],panel=geography,unit_type=kind,unit_id=unit_id,year=year,income_class=c)
     for scope in ['classified','observed']:
      r[f'baseline_share_{scope}_pp']=base_annual[scope][yi,k]
      r[f'deleted_share_{scope}_pp']=annual[scope][yi,k]
      r[f'influence_share_{scope}_pp']=annual[scope][yi,k]-base_annual[scope][yi,k]
     expected.append(r)
   direct_count+=1
report['direct_regrouping_entity_checks']=direct_count
report['maximum_direct_endpoint_residual_pp']=max_direct_residual
expected=pd.DataFrame(expected)
annual_cols=keys+['year','income_class']+[f'{phase}_share_{scope}_pp' for phase in ['baseline','deleted','influence'] for scope in ['classified','observed']]
annual_count=0;selected_count=0;max_annual_residual=0
for kind in ['record','provider','package']:
 for chunk in pd.read_csv(out/f'{kind}_influence_annual.csv.gz',dtype={'unit_id':str},usecols=annual_cols,chunksize=40000):
  annual_count+=len(chunk)
  grouped=chunk.groupby(keys+['year'])[[f'{phase}_share_classified_pp' for phase in ['baseline','deleted','influence']]].sum(min_count=4)
  for phase in ['baseline','deleted']:
   v=grouped[f'{phase}_share_classified_pp'].dropna()
   assert np.allclose(v,100,atol=1e-8,rtol=0)
  assert grouped.influence_share_classified_pp.abs().max()<1e-8
  comparison=chunk.merge(expected,on=keys+['year','income_class'],suffixes=('_saved','_direct'),validate='one_to_one')
  selected_count+=len(comparison)
  for field in annual_cols[len(keys)+2:]:
   a=comparison[field+'_saved'];b=comparison[field+'_direct']
   np.testing.assert_allclose(a,b,atol=1e-8,rtol=1e-10,equal_nan=True)
   if len(a) and (a-b).notna().any(): max_annual_residual=max(max_annual_residual,float((a-b).abs().max()))
assert annual_count==1696320 and selected_count==len(expected)
report['annual_rows_validated']=annual_count;report['direct_annual_class_rows_checked']=selected_count;report['maximum_direct_annual_residual_pp']=max_annual_residual
rank=pd.read_csv(out/'influence_rankings.csv.gz',dtype={'unit_id':str})
concentration=pd.read_csv(out/'influence_concentration.csv')
assert len(rank)==42408*7 and len(concentration)==72*3*7
assert not rank.duplicated(keys+['metric']).any()
for identity,g in rank[rank.ranking_status.eq('ranked')].groupby(['scenario','panel','unit_type','metric']):
 h=g.sort_values('rank');assert h['rank'].tolist()==list(range(1,len(h)+1))
 assert h.max_absolute_influence_pp.is_monotonic_decreasing
 assert h.summed_absolute_influence_pp.ge(h.max_absolute_influence_pp-1e-10).all()
 q=concentration
 for field,value in zip(['scenario','panel','unit_type','metric'],identity):q=q[q[field]==value]
 c=q.iloc[0]
 for n in [1,5]:
  if h.summed_absolute_influence_pp.sum()>0:
   np.testing.assert_allclose(c[f'top_{n}_share_summed_absolute_influence'],h.head(n).summed_absolute_influence_pp.sum()/h.summed_absolute_influence_pp.sum(),atol=1e-12)
  else:assert pd.isna(c[f'top_{n}_share_summed_absolute_influence'])
report['ranking_rows_validated']=len(rank);report['concentration_rows_validated']=len(concentration)
report['ranking_status_counts']=rank.ranking_status.value_counts().to_dict()
report['partially_undefined_ranked_vector_count']=int(((rank.ranking_status=='ranked') & (rank.undefined_vector_cell_count>0)).sum())
report['all_undefined_deletion_vector_count']=int((rank.ranking_status=='all_vector_cells_undefined').sum())
report['status']='PASS';report['runtime_seconds']=time.monotonic()-start
(ROOT/'audit/influence_export_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
