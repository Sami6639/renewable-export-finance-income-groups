from audit_outcomes import *
# Vertex outputs have already been independently reconstructed; validate exact
# floating-equality attainers against these saved verified vectors.
parts=[]
for file,target,kind,cols in [('allocations','period','allocation',['numerator_amount','targeted_completion_share','share_observed']),('decompositions','pair','decomposition',T),('provider_decompositions','pair','provider_decomposition',['provider_delta_pp']+T[1:])]:
 z=pd.read_csv(R/'outputs'/('completion_vertex_'+file+'.csv'));z=z[z.income_class.isin(C)]
 if 'provider' not in z:z['provider']='__portfolio__'
 v=z.melt(id_vars=['case_id','case_family','panel','vertex',target,'income_class','provider'],value_vars=cols,var_name='metric',value_name='value').rename(columns={target:'target'}).assign(target_type=kind);parts.append(v)
v=pd.concat(parts);K=['panel','target_type','target','income_class','provider','metric'];results=[]
for file in ['completion_case_scalar_envelopes.csv','completion_union_scalar_envelopes.csv']:
 h=pd.read_csv(R/'outputs'/file)
 for label,rows in h.groupby('case_id' if 'case_id' in h else 'union_set'):
  vv=v[v.case_id.eq(label)] if 'case_id' in h else v if label.startswith('combined') else v[v.case_family.eq('core_G1' if label.startswith('core') else 'agreement_G1')];groups=vv.groupby(K)
  for row in rows.to_dict('records'):
   g=groups.get_group(tuple(row[k] for k in K));ids=g.vertex if 'case_id' in h else g.case_id+'::'+g.vertex
   for bound,fn in [('lower','min'),('upper','max')]:
    val=getattr(g.value,fn)();expected=set(ids[g.value.eq(val)]);assert expected==set(json.loads(row[bound+'_attaining_case_vertices']))
   assert row['undefined_vertex_count']==g.value.isna().sum()
 results.append(dict(file=file,rows=len(h),status='passed'))
pd.DataFrame(results).to_csv(O/'completion_attainer_validation.csv',index=False);print(results)
