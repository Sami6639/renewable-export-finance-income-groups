"""Finite scenario envelopes, complete paired factor effects and anchored interactions."""
from core import *

def long_outcomes(allocation,decomposition):
 a=allocation[allocation.income_class.isin(CLASSES)].melt(id_vars=['scenario','case_set','geography','period','income_class'],value_vars=['amount','share_classified','share_observed','classified_denominator','observed_denominator','lower_observed_bound','upper_observed_bound'],var_name='outcome',value_name='value').rename(columns={'period':'target'})
 a['analysis']='allocation'
 d=decomposition.melt(id_vars=['scenario','case_set','geography','pair','income_class'],value_vars=TERMS,var_name='outcome',value_name='value').rename(columns={'pair':'target'});d['analysis']='decomposition'
 return pd.concat([a,d],ignore_index=True)

KEYS=['analysis','geography','target','income_class','outcome']
def run(allocation,decomposition):
 z=long_outcomes(allocation,decomposition);z.to_csv(ROOT/'outputs/all_scalar_outcomes.csv',index=False)
 env=[];rank=[]
 for universe in ['core24','agreement12','combined36']:
  q=z if universe=='combined36' else z[z.case_set.eq('core' if universe=='core24' else 'agreement')]
  for keys,g in q.groupby(KEYS,dropna=False):
   finite=g[g.value.notna()];lo=finite.value.min();hi=finite.value.max()
   sign=np.where(abs(finite.value)<(1e-10 if keys[-1].endswith('_pp') else 1e-12),0,np.sign(finite.value))
   env.append(dict(zip(KEYS,keys))|dict(universe=universe,minimum=lo,maximum=hi,min_scenario_ids=';'.join(finite.loc[finite.value.eq(lo),'scenario']),max_scenario_ids=';'.join(finite.loc[finite.value.eq(hi),'scenario']),defined_cases=len(finite),undefined_cases=len(g)-len(finite),stable_sign=('positive' if sign[0]>0 else 'negative' if sign[0]<0 else 'zero') if len(sign)==len(g) and len(set(sign))==1 else 'not_stable_or_undefined'))
  rkkeys=['analysis','geography','target','outcome']
  for keys,g in q.groupby(rkkeys):
   orders=[];undefined=0
   for sid,h in g.groupby('scenario'):
    v=h.set_index('income_class').value.reindex(CLASSES)
    if v.isna().any():undefined+=1;continue
    # Pairwise weak ordering, with tolerance only on percentage-point arithmetic.
    sig=[]
    for i,j in itertools.combinations(CLASSES,2):
     diff=v[i]-v[j];sig.append(f'{i}={j}' if diff==0 else f'{i}>{j}' if diff>0 else f'{i}<{j}')
    orders.append((sid,';'.join(sig)))
   rank.append(dict(zip(rkkeys,keys))|dict(universe=universe,stable_weak_order=len({o[1] for o in orders})==1 and undefined==0,weak_orders=' | '.join(sorted(set(o[1] for o in orders))),undefined_cases=undefined))
 pd.DataFrame(env).to_csv(ROOT/'outputs/scenario_envelopes.csv',index=False);pd.DataFrame(rank).to_csv(ROOT/'outputs/rank_stability.csv',index=False)
 core=z[z.case_set.eq('core')].merge(pd.DataFrame(SCENARIOS),on='scenario',validate='many_to_one')
 effects=[]
 for factor,contrasts in [('A',[(0,1)]),('O',[(0,1)]),('G',[(0,1)]),('D',[(0,1),(0,2),(1,2)])]:
  others=[f for f in 'AOGD' if f!=factor]
  for low,high in contrasts:
   left=core[core[factor].eq(low)];right=core[core[factor].eq(high)]
   j=left.merge(right,on=KEYS+others,suffixes=('_low','_high'),validate='one_to_one')
   for col in KEYS+others:j[col]=j[col]
   e=j[KEYS+others+['scenario_low','scenario_high']].copy();e['factor']=factor;e['contrast']=f'{factor}{high}-{factor}{low}';e['effect']=j.value_high-j.value_low;effects.append(e)
 eff=pd.concat(effects,ignore_index=True);eff.to_csv(ROOT/'outputs/paired_factor_effects.csv',index=False)
 er=[]
 for keys,g in eff.groupby(KEYS+['factor','contrast']):
  v=g.effect;er.append(dict(zip(KEYS+['factor','contrast'],keys))|dict(minimum=v.min(),maximum=v.max(),undefined_count=int(v.isna().sum()),min_backgrounds=';'.join(g.loc[v.eq(v.min()),'scenario_low']),max_backgrounds=';'.join(g.loc[v.eq(v.max()),'scenario_low'])))
 pd.DataFrame(er).to_csv(ROOT/'outputs/factor_effect_ranges.csv',index=False)
 inter=[];checks=[]
 pivot=core.pivot(index=KEYS,columns='scenario',values='value')
 for dlevel in [1,2]:
  interactions=[]
  for size in range(1,5):
   for subset in itertools.combinations('AOGD',size):
    val=pd.Series(0.,index=pivot.index)
    for bits in itertools.product([0,1],repeat=size):
     factors=dict(A=0,O=0,G=0,D=0)
     for f,b in zip(subset,bits):factors[f]=b*(dlevel if f=='D' else 1)
     sid=''.join(f+str(factors[f]) for f in 'AOGD')
     val=val+((-1)**(size-sum(bits)))*pivot[sid]
    interactions.append(val)
    out=val.rename('interaction').reset_index();out['D_cube_level']=dlevel;out['factor_subset']=''.join(subset);out['order']=size;inter.append(out)
  total=sum(interactions);target=pivot[f'A1O1G1D{dlevel}']-pivot['A0O0G0D0'];residual=total-target
  assert np.allclose(total,target,atol=1e-5,rtol=1e-10,equal_nan=True)
  ch=residual.rename('closure_residual').reset_index();ch['D_cube_level']=dlevel;checks.append(ch)
 pd.concat(inter).to_csv(ROOT/'outputs/anchored_factorial_interactions.csv',index=False);pd.concat(checks).to_csv(ROOT/'audit/interaction_closure.csv',index=False)
