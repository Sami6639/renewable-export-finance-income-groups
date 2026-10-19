from audit_outcomes import *
F=R/'outputs/influence';rank=pd.read_csv(F/'influence_rankings.csv.gz',dtype={'unit_id':str});keys=['scenario','panel','unit_type','unit_id'];checks=[]
for kind in ['record','provider','package']:
 for period in ['endpoint','annual']:
  cols=T if period=='endpoint' else ['share_classified_pp','share_observed_pp'];z=pd.read_csv(F/f'{kind}_influence_{period}.csv.gz',dtype={'unit_id':str},usecols=keys+['influence_'+c for c in cols]);ab=z[['influence_'+c for c in cols]].abs();ab.columns=cols;z=pd.concat([z[keys],ab],axis=1);mx=z.groupby(keys)[cols].max();sm=z.groupby(keys)[cols].sum(min_count=1)
  for c in cols:
   metric=c if period=='endpoint' else 'annual_'+c;actual=rank[rank.unit_type.eq(kind)&rank.metric.eq(metric)].set_index(keys);x=mx[c].reindex(actual.index);y=sm[c].reindex(actual.index);assert np.allclose(x,actual.max_absolute_influence_pp,equal_nan=True,atol=1e-10);assert np.allclose(y,actual.summed_absolute_influence_pp,equal_nan=True,atol=1e-10)
  checks.append(dict(test=kind+'_'+period+'_ranking_scores',rows=len(z),status='passed'))
con=pd.read_csv(F/'influence_concentration.csv');groupkeys=['scenario','panel','unit_type','metric'];grouped=rank.groupby(groupkeys)
for row in con.to_dict('records'):
 z=grouped.get_group(tuple(row[k] for k in groupkeys));z=z[z.ranking_status.eq('ranked')].copy();z['tie']=z.unit_id.astype(int) if row['unit_type']=='record' else z.unit_id;z=z.sort_values(['max_absolute_influence_pp','tie'],ascending=[False,True]);assert list(z['rank'])==list(range(1,len(z)+1));total=z.summed_absolute_influence_pp.sum()
 for n in [1,5]:
  h=z.head(n);assert list(h.unit_id)==json.loads(row[f'top_{n}_unit_ids']);share=h.summed_absolute_influence_pp.sum()/total if total else np.nan;assert np.isclose(share,row[f'top_{n}_share_summed_absolute_influence'],equal_nan=True)
checks.append(dict(test='influence_rank_ties_and_concentrations',rows=len(con),status='passed'))
# Independent raw-record value concentration for each scenario and scope.
v=pd.read_csv(F/'endpoint_recorded_value_concentration.csv');orig={r['id']:r['a'] for r in base}
for row in v.to_dict('records'):
 sid=row['scenario'];a,o,g,d=map(int,[sid[1],sid[3],sid[5],sid[7]]);rs=scope(records(a,o,g,d),row['panel']);rs=[r for r in rs if r['y'] in P[row['period']]]
 vals=[(r['id'],orig[r['id']] if row['value_measure']=='original_recorded_nominal_usd' else r['a']) for r in rs];vals=sorted([(i,x) for i,x in vals if np.isfinite(x)],key=lambda v:(-v[1],v[0]));total=sum(x for i,x in vals)
 for n in [1,5]:
  assert [i for i,x in vals[:n]]==json.loads(row[f'top_{n}_source_excel_rows']);expected=sum(x for i,x in vals[:n])/total if total else np.nan;assert np.isclose(expected,row[f'top_{n}_recorded_value_share'],equal_nan=True)
checks.append(dict(test='raw_recorded_value_concentrations',rows=len(v),status='passed'))
# All source scenario sign and weak-rank summaries use independently validated values.
z=pd.read_csv(R/'outputs/all_scalar_outcomes.csv');K=['analysis','geography','target','income_class','outcome'];env=pd.read_csv(R/'outputs/scenario_envelopes.csv')
for universe,rows in env.groupby('universe'):
 v=z if universe=='combined36' else z[z.case_set.eq('core' if universe=='core24' else 'agreement')];groups=v.groupby(K)
 for r in rows.to_dict('records'):
  vals=groups.get_group(tuple(r[k] for k in K)).value;finite=vals.dropna();s=np.where(finite.abs()<(1e-10 if r['outcome'].endswith('_pp') else 1e-12),0,np.sign(finite));expected=('positive' if s[0]>0 else 'negative' if s[0]<0 else 'zero') if len(s)==len(vals) and len(set(s))==1 else 'not_stable_or_undefined';assert r['stable_sign']==expected
checks.append(dict(test='all_scenario_sign_summaries',rows=len(env),status='passed'))
ranks=pd.read_csv(R/'outputs/rank_stability.csv');RK=['analysis','geography','target','outcome']
for universe,rows in ranks.groupby('universe'):
 v=z if universe=='combined36' else z[z.case_set.eq('core' if universe=='core24' else 'agreement')];groups=v.groupby(RK)
 for r in rows.to_dict('records'):
  block=groups.get_group(tuple(r[k] for k in RK));orders=[];undefined=0
  for sid,h in block.groupby('scenario'):
   val=h.set_index('income_class').value
   if val.isna().any():undefined+=1;continue
   orders.append(tuple(np.sign(val[a]-val[b]) for a,b in itertools.combinations(C,2)))
  assert r['stable_weak_order']==(len(set(orders))==1 and undefined==0);assert r['undefined_cases']==undefined
checks.append(dict(test='all_weak_rank_summaries',rows=len(ranks),status='passed'))
pd.DataFrame(checks).to_csv(O/'reporting_summary_validation.csv',index=False);print(pd.DataFrame(checks).to_string(index=False))
