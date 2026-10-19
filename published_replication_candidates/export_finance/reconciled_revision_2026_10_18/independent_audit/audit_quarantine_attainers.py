import pandas as pd,numpy as np,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent
def read(name):return pd.read_csv(R/'outputs'/name,float_precision='round_trip')
a=read('arithmetic_quarantine_allocation.csv');d=read('arithmetic_quarantine_decomposition.csv');a=a[a.income_class.ne('Unknown')];a=a.melt(id_vars=['scenario','geography','period','income_class'],value_vars=['amount','share_classified','share_observed','classified_denominator','observed_denominator','lower_observed_bound','upper_observed_bound'],var_name='outcome',value_name='value').rename(columns={'period':'target'}).assign(analysis='allocation');d=d.melt(id_vars=['scenario','geography','pair','income_class'],value_vars=['delta_pp','composition_pp','within_pp','entry_pp','exit_pp'],var_name='outcome',value_name='value').rename(columns={'pair':'target'}).assign(analysis='decomposition');q=pd.concat([a,d]);core=read('all_scalar_outcomes.csv');core=core[core.case_set.eq('core')];K=['analysis','geography','target','income_class','outcome'];h=read('arithmetic_quarantine_envelopes.csv');errors=[]
for un,g in h.groupby('universe'):
 z=q if un=='quarantine24' else pd.concat([q,core]);groups=z.groupby(K)
 for r in g.to_dict('records'):
  v=groups.get_group(tuple(r[k] for k in K))
  for b,fn in [('min','min'),('max','max')]:
   expected=set(v.loc[v.value.eq(getattr(v.value,fn)()),'scenario']);actual=set(str(r[b+'_scenario_ids']).split(';'))
   if expected!=actual:errors.append({k:r[k] for k in K}|dict(universe=un,bound=b,missing=sorted(expected-actual),extra=sorted(actual-expected)))
report={'status':'failed' if errors else 'passed','rows':len(h),'errors':errors};(O/'quarantine_attainer_validation.json').write_text(json.dumps(report,indent=2));print('Q1 attainer discrepancies:',len(errors));assert not errors
