from audit_outcomes import *
checks=[]
# Verify every source-operation ledger against independent inclusion/values.
for file,q in [('transformation_lineage.csv',False),('arithmetic_quarantine_transformation_lineage.csv',True)]:
 z=pd.read_csv(R/'outputs'/file);n=0
 for sid,g in z[z.source_excel_row.isin([r['id'] for r in base])].groupby('scenario'):
  a,o,gg,d=map(int,[sid[1],sid[3],sid[5],sid[7]]);rs=records(a,o,gg,d,'_agreement' in sid,q);e=pd.DataFrame(rs);act=g[g.included]
  for i,h in act.groupby('source_excel_row'):
   ex=e[e.id.eq(i)];assert len(h)==len(ex);assert np.allclose(sorted(h.amount),sorted(ex.a),equal_nan=True);assert sorted(h.analytical_year)==sorted(ex.y)
  assert set(act.source_excel_row)==set(e.id);n+=len(g)
 checks.append({'test':file,'rows':n,'status':'passed'})
# Disjoint joint coverage independently from individual source rows, all core/overlay/Q panels.
for filename,q in [('coverage_joint.csv',False),('arithmetic_quarantine_coverage_joint.csv',True)]:
 z=pd.read_csv(R/'outputs'/filename);n=0
 for (sid,geo),g in z.groupby(['scenario','geography']):
  a,o,gg,d=map(int,[sid[1],sid[3],sid[5],sid[7]]);rs=scope(records(a,o,gg,d,'_agreement' in sid,q),geo)
  expected={}
  for r in rs:
   status='source_verified_cross_border_region' if r['regional'] else 'assigned_country' if pd.notna(r['r']) else 'otherwise_unresolved'
   for period,years in P.items():
    if r['y'] not in years:continue
    key=(period,r['p'] in ISO,status,r['c'] in C);v=expected.setdefault(key,[0.,0,0]);v[1]+=1
    if np.isfinite(r['a']):v[0]+=r['a']
    else:v[2]+=1
  for row in g.itertuples():
   v=expected.get((str(row.period),row.provider_known,row.recipient_status,row.income_known),[0,0,0]);assert np.isclose(row.observed_amount,v[0],atol=1e-5,rtol=1e-12);assert row.component_count==v[1];assert row.missing_amount_count==v[2];n+=1
 checks.append({'test':filename,'rows':n,'status':'passed'})
# FY2023 uses same operations and separately frozen classification.
aa=[];dd=[]
for a,o,g,d in itertools.product(range(2),range(2),range(2),range(3)):
 sid=f'A{a}O{o}G{g}D{d}'
 for geo in G:
  av,dv,_,_=evaluate(scope(records(a,o,g,d,fy23=True),geo));aa.append(av.assign(scenario=sid,geography=geo));dd.append(dv.assign(scenario=sid,geography=geo))
for filename,ex,keys,cols in [('secondary_FY2023_endpoint_allocation.csv',pd.concat(aa),['scenario','geography','period','income_class'],['amount','share_classified','share_observed']),('secondary_FY2023_endpoint_decomposition.csv',pd.concat(dd),['scenario','geography','pair','income_class'],T)]:
 act=pd.read_csv(R/'outputs'/filename).set_index(keys);exp=ex.set_index(keys).loc[act.index];assert np.allclose(act[cols],exp[cols],atol=1e-5,rtol=1e-12,equal_nan=True);checks.append({'test':filename,'rows':len(act),'status':'passed'})
# Exact attainer membership is checked against independently validated saved scalar values
# to avoid platform-rounding ties changing their machine-equality interpretation.
z=pd.read_csv(R/'outputs/all_scalar_outcomes.csv');q=pd.read_csv(R/'outputs/arithmetic_quarantine_all_scalar_outcomes.csv') if (R/'outputs/arithmetic_quarantine_all_scalar_outcomes.csv').exists() else None
K=['analysis','geography','target','income_class','outcome']
for file in ['scenario_envelopes.csv']:
 h=pd.read_csv(R/'outputs'/file)
 for universe,g in h.groupby('universe'):
  selected=z if universe=='combined36' else z[z.case_set.eq('core' if universe=='core24' else 'agreement')];groups=selected.groupby(K)
  for row in g.to_dict('records'):
   v=groups.get_group(tuple(row[k] for k in K));assert set(str(row['min_scenario_ids']).split(';'))==set(v.loc[v.value.eq(v.value.min()),'scenario']);assert set(str(row['max_scenario_ids']).split(';'))==set(v.loc[v.value.eq(v.value.max()),'scenario'])
 checks.append({'test':'exact_core_overlay_extremum_attainers','rows':len(h),'status':'passed'})
pd.DataFrame(checks).to_csv(O/'lineage_coverage_secondary_validation.csv',index=False);print(pd.DataFrame(checks).to_string(index=False))
