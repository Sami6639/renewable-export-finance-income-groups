"""Prospective arithmetic-flag quarantine family; never an amount repair."""
from core import *
from run_revision import gate
from effects import long_outcomes,KEYS
import json,hashlib
IDS=[1976,8176,9180,9622]

def run():
 gate()
 from public_integrity import protocol_integrity
 protocol_integrity()
 gate_ids=json.loads((ROOT/'audit/arithmetic_gate.json').read_text())['additional_renewable_flagged_ids']
 independent_ids=json.loads((ROOT/'independent_audit/independent_gate_audit.json').read_text())['flagged_renewable_rows']
 assert sorted(gate_ids)==IDS and sorted(set(independent_ids)-{1907,1908})==IDS
 raw=load();aa=[];cc=[];mm=[];dd=[];pp=[];ll=[]
 pd.DataFrame([s|{'Q':1,'case_set':'arithmetic_flag_quarantine','quarantine_scenario':s['scenario']+'_Q1'} for s in SCENARIOS]).to_csv(ROOT/'protocol/arithmetic_quarantine_manifest.csv',index=False)
 for s in SCENARIOS:
  d=transform(raw,s);before=d.copy(deep=True);flag=d.source_excel_row.isin(IDS);d.loc[flag,'included']=False;d.loc[flag,'reason']='Q1 fixed arithmetic-flag quarantine; original amount retained';d.loc[flag,'evidence_id']='complete_arithmetic_gate';d.loc[flag,'evidence_type']='internal arithmetic discrepancy, no inferred principal correction';d['scenario']=s['scenario']+'_Q1';pd.testing.assert_frame_equal(d.loc[~flag,before.columns.drop('scenario')],before.loc[~flag,before.columns.drop('scenario')]);assert np.allclose(d.amount,before.amount,equal_nan=True);ll.append(d)
  for geo in PANELS:
   q=panel(d[d.technology_group.eq('Renewable')],geo)
   meta=dict(scenario=s['scenario']+'_Q1',matched_core_scenario=s['scenario'],case_set='arithmetic_flag_quarantine',Q=1,A=s['A'],O=s['O'],G=s['G'],D=s['D'],geography=geo,fixed_income_FY=2013)
   a,c,m=allocate(q);dec,p=decomposition(q)
   for target,z in [(aa,a),(cc,c),(mm,m),(dd,dec),(pp,p)]:target.append(z.assign(**meta))
 allocation=pd.concat(aa,ignore_index=True);decomp=pd.concat(dd,ignore_index=True)
 for name,parts in [('allocation',aa),('coverage_joint',cc),('coverage_marginals',mm),('decomposition',dd),('provider_contributions',pp),('transformation_lineage',ll)]:pd.concat(parts,ignore_index=True).to_csv(ROOT/f'outputs/arithmetic_quarantine_{name}.csv',index=False)
 qz=long_outcomes(allocation,decomp)
 core=pd.read_csv(ROOT/'outputs/all_scalar_outcomes.csv',float_precision='round_trip');core=core[core.case_set.eq('core')]
 qz['matched_core_scenario']=qz.scenario.str.replace('_Q1','',regex=False)
 j=qz.merge(core,left_on=['matched_core_scenario']+KEYS,right_on=['scenario']+KEYS,suffixes=('_quarantine','_core'),validate='one_to_one');j['quarantine_minus_core']=j.value_quarantine-j.value_core
 j.to_csv(ROOT/'outputs/arithmetic_quarantine_paired_effects.csv',index=False)
 envelopes=[]
 for universe,z in [('quarantine24',qz),('core_plus_quarantine48',pd.concat([qz,core]))]:
  for keys,g in z.groupby(KEYS):
   v=g.value;finite=v.dropna();lo=finite.min();hi=finite.max();sign=np.where(abs(finite)<(1e-10 if keys[-1].endswith('_pp') else 1e-12),0,np.sign(finite))
   envelopes.append(dict(zip(KEYS,keys))|dict(universe=universe,minimum=lo,maximum=hi,min_scenario_ids=';'.join(g.loc[v.eq(lo),'scenario']),max_scenario_ids=';'.join(g.loc[v.eq(hi),'scenario']),defined_cases=int(v.notna().sum()),undefined_cases=int(v.isna().sum()),stable_sign=('positive' if sign[0]>0 else 'negative' if sign[0]<0 else 'zero') if len(sign)==len(g) and len(set(sign))==1 else 'not_stable_or_undefined'))
 pd.DataFrame(envelopes).to_csv(ROOT/'outputs/arithmetic_quarantine_envelopes.csv',index=False)
 (ROOT/'audit/arithmetic_quarantine_scope.json').write_text(json.dumps(dict(removed_source_ids=IDS,cases=24,scope='FY2013 annual/window allocation and decomposition only; no Q1 influence, completion, FY2023, agreement overlays or interactions'),indent=2))
 print('Arithmetic quarantine family complete.')
if __name__=='__main__':run()
