from audit_outcomes import *
aa=[];dd=[];pp=[];validation=[]
for a,o,d in itertools.product(range(2),range(2),range(3)):
 for overlay in [False,True] if o else [False]:
  sid=f'A{a}O{o}G1D{d}'+('_agreement' if overlay else '')
  for geo in G[:2]:
   evals={}
   for vertex in C+['interior']:
    fractions={c:.25 for c in C} if vertex=='interior' else {vertex:1.}
    rs=scope(records(a,o,1,d,overlay,vertex=fractions),geo);av,dv,pv,m=evaluate(rs);evals[vertex]=(av,dv,pv,m)
    if vertex!='interior':
     meta={'scenario':sid,'geography':geo,'vertex':vertex};aa.append(av.assign(**meta));dd.append(dv.assign(**meta));pp.append(pv.assign(**meta))
   for tab,cols in [(0,['amount','classified_denominator','share_classified','share_observed']),(1,T),(2,T[1:])]:
    expected=np.mean([evals[c][tab][cols].to_numpy() for c in C],axis=0);actual=evals['interior'][tab][cols].to_numpy();assert np.allclose(expected,actual,equal_nan=True,rtol=1e-12,atol=1e-5 if tab==0 else 1e-8);validation.append(dict(scenario=sid,geography=geo,test='independent_interior_mean',table=tab,max_error=float(np.nanmax(abs(expected-actual)))))
   U=237.5e6 if a else 2.5e9;mat=evals['L'][3];j=pi['Japan']
   for e,l in PA:
    ma,mb=mat[e],mat[l];pa,pb=ma[j].sum(),mb[j].sum();va,vb=ma.sum(),mb.sum();ie,il=int(2014 in P[e]),int(2014 in P[l]);wa,wb=pa/va,pb/vb
    co=pa>0 and pb>0;en=pa==0 and pb>0;ex=pa>0 and pb==0
    slope=[il/vb-ie/va,(wb-wa)*((ie/pa if pa else 0)+(il/pb if pb else 0))/2 if co else 0,(wa+wb)*((il/pb if pb else 0)-(ie/pa if pa else 0))/2 if co else 0,il/vb if en else 0,-ie/va if ex else 0]
    assert abs(sum(slope[1:])-slope[0])*U*100<1e-8
    for c in C:
     other=next(k for k in C if k!=c);v1=evals[c][1];v2=evals[other][1];mask=v1.pair.eq(e+'_to_'+l)&v1.income_class.eq(c);diff=v1.loc[mask,T].to_numpy()[0]-v2.loc[mask,T].to_numpy()[0];err=np.max(abs(diff-np.array(slope)*U*100));assert err<1e-8;validation.append(dict(scenario=sid,geography=geo,test='general_derivative',pair=e+'_to_'+l,income_class=c,max_error=err))
for name,rows in [('allocation',aa),('decomposition',dd),('provider_contributions',pp)]:pd.concat(rows).to_csv(O/('independent_completion_'+name+'.csv'),index=False)
pd.DataFrame(validation).to_csv(O/'independent_affine_validation.csv',index=False)
results=[]
for name,pfile,keys,cols,mapping in [
 ('allocation','allocations',['period','income_class'],['amount','classified_denominator','observed_denominator','unknown_amount','share_classified','share_observed'],{'numerator_amount':'amount','targeted_completion_denominator':'classified_denominator','other_unknown_income_amount':'unknown_amount','targeted_completion_share':'share_classified'}),
 ('decomposition','decompositions',['pair','income_class'],T,{}),('provider_contributions','provider_decompositions',['pair','income_class','provider'],T[1:],{})]:
 keys=['scenario','geography','vertex']+keys;exp=pd.read_csv(O/('independent_completion_'+name+'.csv')).set_index(keys);act=pd.read_csv(R/'outputs'/('completion_vertex_'+pfile+'.csv')).rename(columns={'case_id':'scenario','panel':'geography',**mapping}).set_index(keys);ex=exp.loc[act.index]
 for c in cols:
  x,y=act[c].to_numpy(),ex[c].to_numpy();err=np.nanmax(abs(x-y));assert np.allclose(x,y,equal_nan=True,atol=1e-5 if ('amount' in c or 'denominator' in c) else 1e-8,rtol=1e-12),(name,c,err);results.append(dict(table=name,metric=c,rows=len(x),max_error=err))
pd.DataFrame(results).to_csv(O/'completion_output_comparison.csv',index=False);print('All 18 case × 2 panel × 4 vertex outputs and independent interior/general derivative passed',flush=True)
