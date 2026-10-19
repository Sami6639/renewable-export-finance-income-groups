from audit_outcomes import *
a=pd.read_csv(O/'independent_allocation.csv');d=pd.read_csv(O/'independent_decomposition.csv');a=a[a.income_class.isin(C)];a['lower_observed_bound']=a.share_observed;a['upper_observed_bound']=(a.amount+a.unknown_amount)/a.observed_denominator
a=a.melt(id_vars=['scenario','geography','period','income_class'],value_vars=['amount','share_classified','share_observed','classified_denominator','observed_denominator','lower_observed_bound','upper_observed_bound'],var_name='outcome',value_name='value').rename(columns={'period':'target'}).assign(analysis='allocation')
d=d.melt(id_vars=['scenario','geography','pair','income_class'],value_vars=T,var_name='outcome',value_name='value').rename(columns={'pair':'target'}).assign(analysis='decomposition');z=pd.concat([a,d]);K=['analysis','geography','target','income_class','outcome'];lookup=z.set_index(['scenario']+K).value
checks=[]
def chk(x,y,label):
 x=np.asarray(x,float);y=np.asarray(y,float);assert np.allclose(x,y,equal_nan=True,atol=2e-5,rtol=1e-11),(label,np.nanmax(abs(x-y)));checks.append(dict(test=label,rows=x.size,max_error=float(np.nanmax(abs(x-y)))))
for filename in ['paired_factor_effects.csv','arithmetic_quarantine_paired_effects.csv']:
 f=R/'outputs'/filename
 if not f.exists():continue
 h=pd.read_csv(f)
 if filename.startswith('paired'):
  lo=h[['scenario_low']+K].rename(columns={'scenario_low':'scenario'});hi=h[['scenario_high']+K].rename(columns={'scenario_high':'scenario'});actual=h.effect
 else:
  lo=h[['matched_core_scenario']+K].rename(columns={'matched_core_scenario':'scenario'});hi=lo.copy();hi.scenario+='_Q1';actual=h.quarantine_minus_core
 ev=lookup.reindex(pd.MultiIndex.from_frame(hi)).to_numpy()-lookup.reindex(pd.MultiIndex.from_frame(lo)).to_numpy();chk(actual,ev,filename)
h=pd.read_csv(R/'outputs/anchored_factorial_interactions.csv');pv=z[~z.scenario.str.contains('_')].pivot(index=K,columns='scenario',values='value')
for (level,subset),g in h.groupby(['D_cube_level','factor_subset']):
 ex=np.zeros(len(g));idx=pd.MultiIndex.from_frame(g[K]);n=len(subset)
 for bits in itertools.product([0,1],repeat=n):
  fs=dict(A=0,O=0,G=0,D=0)
  for f,bit in zip(subset,bits):fs[f]=bit*(level if f=='D' else 1)
  sid=''.join(f+str(fs[f]) for f in 'AOGD');ex+=(-1)**(n-sum(bits))*pv[sid].reindex(idx).to_numpy()
 chk(g.interaction,ex,'interaction_'+str(level)+'_'+subset)
for filename in ['scenario_envelopes.csv','arithmetic_quarantine_envelopes.csv']:
 f=R/'outputs'/filename
 if not f.exists():continue
 h=pd.read_csv(f)
 for universe,g in h.groupby('universe'):
  mask={'core24':~z.scenario.str.contains('_'),'agreement12':z.scenario.str.endswith('_agreement'),'combined36':~z.scenario.str.endswith('_Q1'),'quarantine24':z.scenario.str.endswith('_Q1'),'core_plus_quarantine48':~z.scenario.str.endswith('_agreement')}[universe];v=z[mask].groupby(K).value.agg(['min','max','count','size']);idx=pd.MultiIndex.from_frame(g[K]);chk(g.minimum,v['min'].reindex(idx),universe+'_minimum');chk(g.maximum,v['max'].reindex(idx),universe+'_maximum');chk(g.undefined_cases,(v['size']-v['count']).reindex(idx),universe+'_undefined')
# Completion scalar envelope values reconstructed from the independent vertex tables.
a=pd.read_csv(O/'independent_completion_allocation.csv');d=pd.read_csv(O/'independent_completion_decomposition.csv');p=pd.read_csv(O/'independent_completion_provider_contributions.csv');vs=[]
for table,target,kind,cols in [(a,'period','allocation',['amount','share_classified','share_observed']),(d,'pair','decomposition',T),(p,'pair','provider_decomposition',T[1:])]:
 table=table[table.income_class.isin(C)].copy()
 if 'provider' not in table:table['provider']='__portfolio__'
 if kind=='provider_decomposition':table['provider_delta_pp']=table[T[1:]].sum(axis=1,min_count=4);cols=cols+['provider_delta_pp']
 v=table.melt(id_vars=['scenario','geography','vertex',target,'income_class','provider'],value_vars=cols,var_name='metric',value_name='value').rename(columns={target:'target'}).assign(target_type=kind);v.metric=v.metric.replace({'amount':'numerator_amount','share_classified':'targeted_completion_share'});vs.append(v)
v=pd.concat(vs);ck=['target_type','target','income_class','provider','metric']
for filename in ['completion_case_scalar_envelopes.csv','completion_union_scalar_envelopes.csv']:
 h=pd.read_csv(R/'outputs'/filename)
 if 'case_id' in h:
  keys=['scenario','geography']+ck;expected=v.groupby(keys).value.agg(['min','max']);h=h.rename(columns={'case_id':'scenario','panel':'geography'});idx=pd.MultiIndex.from_frame(h[keys]);chk(h.lower,expected['min'].reindex(idx),filename+'_lower');chk(h.upper,expected['max'].reindex(idx),filename+'_upper')
 else:
  for union,g in h.groupby('union_set'):
   vv=v if union.startswith('combined') else v[v.scenario.str.endswith('_agreement')] if union.startswith('agreement') else v[~v.scenario.str.endswith('_agreement')];keys=['geography']+ck;expected=vv.groupby(keys).value.agg(['min','max']);idx=pd.MultiIndex.from_frame(g.rename(columns={'panel':'geography'})[keys]);chk(g.lower,expected['min'].reindex(idx),union+'_lower');chk(g.upper,expected['max'].reindex(idx),union+'_upper')
pd.DataFrame(checks).to_csv(O/'envelope_effect_interaction_comparison.csv',index=False);print('Envelope, paired effects, all anchored interactions and completion envelope values independently verified',len(checks))
