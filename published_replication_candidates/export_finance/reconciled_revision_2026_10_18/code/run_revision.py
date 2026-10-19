"""Reproduce the frozen finite sensitivity analysis. Screen clearance is mandatory."""
from core import *
import hashlib,json,platform,sys,shutil

def gate():
 from public_integrity import protocol_integrity
 a=protocol_integrity()
 g=json.loads((ROOT/'audit/arithmetic_gate.json').read_text())
 assert sorted(g['additional_renewable_flagged_ids'])==a['reviewed_source_ids']
 return a

def export_manifest(raw):
 pd.DataFrame(SCENARIOS).to_csv(ROOT/'protocol/scenario_manifest.csv',index=False)
 ledger=[]
 for s in SCENARIOS:
  for overlay in ([False,True] if s['O'] else [False]):
   d=transform(raw,s,overlay)
   cols=['scenario','source_excel_row','component_id','nominal_usd','amount','amount_basis','FY','analytical_year','country','recipient','recipient_status','included','income','provider','provider_iso3','evidence_id','evidence_type','reason']
   ledger.append(d[cols])
 pd.concat(ledger).to_csv(ROOT/'outputs/transformation_lineage.csv',index=False)


def run():
 approval=gate();raw=load();assert raw.nominal_usd.dropna().ge(0).all()
 export_manifest(raw)
 from validate_transforms import run as validate_run
 validate_run(raw)
 rows=[];cov=[];marg=[];dec=[];cells=[];secondary=[];secondary_alloc=[];controls=[]
 for s in SCENARIOS:
  for overlay in ([False,True] if s['O'] else [False]):
   d=transform(raw,s,overlay);sid=d.scenario.iloc[0];kind='agreement' if overlay else 'core'
   unchanged=d.loc[d.technology_group.ne('Renewable')]
   assert unchanged.included.all() and np.allclose(unchanged.amount,unchanged.nominal_usd,equal_nan=True)
   for panel_name in PANELS:
    q=panel(d[d.technology_group.eq('Renewable')],panel_name)
    meta=dict(scenario=sid,case_set=kind,geography=panel_name,fixed_income_FY=2013)
    a,c,m=allocate(q);r,t=decomposition(q)
    for target,z in [(rows,a),(cov,c),(marg,m),(dec,r),(cells,t)]:target.append(z.assign(**meta))
   if not overlay:
    d23=transform(raw,s,False,2023)
    for panel_name in PANELS:
     q=panel(d23[d23.technology_group.eq('Renewable')],panel_name);r,t=decomposition(q)
     secondary.append(r[r.pair.eq('early_to_late')].assign(scenario=sid,geography=panel_name,fixed_income_FY=2023))
     a23,_,_=allocate(q);secondary_alloc.append(a23[a23.period.isin(['early','late'])].assign(scenario=sid,geography=panel_name,fixed_income_FY=2023))
    for tech in ['Fossil','Grid','Other']:
     for panel_name in PANELS:
      q=panel(d[d.technology_group.eq(tech)],panel_name);a,_,_=allocate(q)
      controls.append(a.assign(scenario=sid,technology=tech,geography=panel_name))
 output={'allocation':rows,'coverage_joint':cov,'coverage_marginals':marg,'decomposition':dec,'provider_contributions':cells,'secondary_FY2023_endpoint_decomposition':secondary,'secondary_FY2023_endpoint_allocation':secondary_alloc,'nonrenewable_scope_controls':controls}
 for name,parts in output.items():pd.concat(parts,ignore_index=True).to_csv(ROOT/f'outputs/{name}.csv',index=False)
 allocation=pd.concat(rows);decom=pd.concat(dec)
 endpoint=[]
 for keys,z in allocation.groupby(['scenario','case_set','geography','fixed_income_FY','income_class']):
  e=z[z.period.eq('early')].iloc[0];l=z[z.period.eq('late')].iloc[0]
  endpoint.append(dict(zip(['scenario','case_set','geography','fixed_income_FY','income_class'],keys))|dict(delta_pp=100*(l.share_classified-e.share_classified),observed_share_delta_pp=100*(l.share_observed-e.share_observed),delta_lower_observed_bound_pp=100*(l.lower_observed_bound-e.upper_observed_bound),delta_upper_observed_bound_pp=100*(l.upper_observed_bound-e.lower_observed_bound),nominal_amount_change=l.amount-e.amount,early_classified_denominator=e.classified_denominator,late_classified_denominator=l.classified_denominator,early_observed_denominator=e.observed_denominator,late_observed_denominator=l.observed_denominator))
 pd.DataFrame(endpoint).to_csv(ROOT/'outputs/endpoints.csv',index=False)
 # Agreement overlays are paired to matching O1 cores, preserving separate timing conventions.
 for name,z,keys,values in [('allocation',allocation,['geography','period','income_class'],['amount','share_classified','share_observed','classified_denominator','observed_denominator']),('decomposition',decom,['geography','pair','income_class'],TERMS)]:
  ov=z[z.case_set.eq('agreement')].copy();ov['core_scenario']=ov.scenario.str.replace('_agreement','',regex=False)
  core=z[z.case_set.eq('core')]
  j=ov.merge(core,left_on=['core_scenario']+keys,right_on=['scenario']+keys,suffixes=('_overlay','_core'),validate='one_to_one')
  for v in values:j[v+'_difference']=j[v+'_overlay']-j[v+'_core']
  j.to_csv(ROOT/f'outputs/agreement_overlay_{name}_differences.csv',index=False)
 # Archive and D2 reproduce already-audited endpoints (the old known-international implementation has all provider mappings known).
 old=pd.read_csv(BASE/'extension/provider_only_endpoints.csv');old=old[old.technology.eq('Renewable')]
 comparisons=[]
 for geography,old_geo in [('all_locations','All locations'),('international_reporting','Known international'),('domestic','Domestic')]:
  for period in ['early','late']:
   n=allocation[(allocation.scenario=='A0O0G0D0')&(allocation.geography==geography)&(allocation.period==period)&(allocation.income_class=='H')].iloc[0]
   o=old[(old.geography==old_geo)&(old.window==period)].iloc[0]
   assert np.isclose(n.share_classified,o.high_share,atol=1e-12,equal_nan=True)
   assert np.isclose(n.observed_denominator,o.observed_weight,atol=.01)
   comparisons.append(dict(geography=geography,period=period,share_residual=n.share_classified-o.high_share,amount_residual=n.observed_denominator-o.observed_weight))
 oldq=pd.read_csv(BASE/'extension/provider_only_quarantine_endpoints.csv');oldq=oldq[oldq.technology.eq('Renewable')]
 for geography,old_geo in [('all_locations','All locations'),('international_reporting','Known international'),('domestic','Domestic')]:
  for period in ['early','late']:
   n=allocation[(allocation.scenario=='A0O0G0D2')&(allocation.geography==geography)&(allocation.period==period)&(allocation.income_class=='H')].iloc[0]
   o=oldq[(oldq.geography==old_geo)&(oldq.window==period)].iloc[0]
   assert np.isclose(n.share_classified,o.high_share,atol=1e-12,equal_nan=True)
   assert np.isclose(n.observed_denominator,o.observed_weight,atol=.01)
   comparisons.append(dict(scenario='A0O0G0D2',geography=geography,period=period,share_residual=n.share_classified-o.high_share,amount_residual=n.observed_denominator-o.observed_weight))
 pd.DataFrame(comparisons).to_csv(ROOT/'audit/archive_reproduction.csv',index=False)
 from effects import run as effects_run
 effects_run(allocation,decom)
 (ROOT/'audit/run_environment.json').write_text(json.dumps(dict(python=sys.version,numpy=np.__version__,pandas=pd.__version__,platform=platform.platform(),protocol_integrity=approval),indent=2))
 print('Core and agreement outputs complete.')
if __name__=='__main__':run()
