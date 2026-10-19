from audit_outcomes import *
F=R/'outputs/influence';checks=[]
packages={'Standard Bank 1907/1908':{1907,1908},'Karuma 109/2253':{109,2253},'Dogger 7410/8413/8034':{7410,8413,8034}}
# Read actual names without using membership as evidence.
ledger=pd.read_csv(F/'influence_entity_ledger.csv.gz',dtype={'unit_id':str});print(ledger[ledger.unit_type.eq('package')].unit_id.unique(),flush=True)
for label in ledger[ledger.unit_type.eq('package')].unit_id.unique():
 if 'Standard' in label:packages[label]={1907,1908}
 elif 'Karuma' in label:packages[label]={109,2253}
 elif 'Dogger' in label:packages[label]={7410,8413,8034}

def terms(m):
 # m shape unit×2×provider×class
 x,y=m[:,0],m[:,1];pa,pb=x.sum(2),y.sum(2);va,vb=pa.sum(1),pb.sum(1);wa=np.divide(pa,va[:,None],out=np.zeros_like(pa),where=va[:,None]!=0);wb=np.divide(pb,vb[:,None],out=np.zeros_like(pb),where=vb[:,None]!=0);ha=np.divide(x,pa[:,:,None],out=np.zeros_like(x),where=pa[:,:,None]!=0);hb=np.divide(y,pb[:,:,None],out=np.zeros_like(y),where=pb[:,:,None]!=0);common=(pa>0)&(pb>0);entry=(pa==0)&(pb>0);exit=(pa>0)&(pb==0)
 co=(50*(ha+hb)*(wb-wa)[:,:,None]*common[:,:,None]).sum(1);wi=(50*(wa+wb)[:,:,None]*(hb-ha)*common[:,:,None]).sum(1);en=(100*wb[:,:,None]*hb*entry[:,:,None]).sum(1);ex=(-100*wa[:,:,None]*ha*exit[:,:,None]).sum(1);delta=100*(y.sum(1)/vb[:,None]-x.sum(1)/va[:,None]);out=np.stack([delta,co,wi,en,ex],axis=2);out[(va==0)|(vb==0)]=np.nan;return out

cache={}
for (sid,geo),units in ledger.groupby(['scenario','panel']):
 a,o,g,d=map(int,[sid[1],sid[3],sid[5],sid[7]]);rs=scope(records(a,o,g,d),geo);keys=list(zip(units.unit_type,units.unit_id));N=len(keys);m=np.zeros((10,len(providers),4));obs=np.zeros(10);remove=np.zeros((N,10,len(providers),4));robs=np.zeros((N,10));index={key:i for i,key in enumerate(keys)}
 for r in rs:
  if not np.isfinite(r['a']):continue
  y=r['y']-2013;p=pi[r['p']];obs[y]+=r['a'];ki=C.index(r['c']) if r['c'] in C else None
  if ki is not None:m[y,p,ki]+=r['a']
  affected=[('record',str(r['id'])),('provider',r['p'])]+[('package',label) for label,ids in packages.items() if r['id'] in ids]
  for key in set(affected):
   if key not in index:continue
   n=index[key];robs[n,y]+=r['a']
   if ki is not None:remove[n,y,p,ki]+=r['a']
 remaining=m[None]-remove;endpoint=np.stack([remaining[:,:3].sum(1),remaining[:,7:].sum(1)],axis=1);baseterm=terms(np.stack([m[:3].sum(0),m[7:].sum(0)])[None])[0];deleted=terms(endpoint);classamt=remaining.sum(2);denom=classamt.sum(2);v=obs[None]-robs
 bclass=m.sum(1);bden=bclass.sum(1)
 with np.errstate(divide='ignore',invalid='ignore'):
  ac=100*classamt/denom[:,:,None];ao=100*classamt/v[:,:,None];bc=100*bclass/bden[:,None];bo=100*bclass/obs[:,None]
 cache[(sid,geo)]={'index':index,'deleted':deleted,'baseline':baseterm,'annual_classified':ac-bc[None],'annual_observed':ao-bo[None]}
print('Independent batched deletion outcomes ready',len(cache),flush=True)
for kind in ['record','provider','package']:
 for period in ['endpoint','annual']:
  f=F/f'{kind}_influence_{period}.csv.gz';count=0;maxerr=0
  for chunk in pd.read_csv(f,dtype={'unit_id':str},chunksize=100000):
   for (sid,geo),z in chunk.groupby(['scenario','panel'],sort=False):
    v=cache[(sid,geo)];ix=np.array([v['index'][(kind,u)] for u in z.unit_id]);ci=np.array([C.index(c) for c in z.income_class])
    if period=='endpoint':
     ex=v['deleted'][ix,ci]-v['baseline'][ci];act=z[['influence_'+t for t in T]].to_numpy();
    else:
     yi=z.year.to_numpy()-2013;ex=np.stack([v['annual_classified'][ix,yi,ci],v['annual_observed'][ix,yi,ci]],1);act=z[['influence_share_classified_pp','influence_share_observed_pp']].to_numpy()
    err=np.nanmax(abs(ex-act));maxerr=max(maxerr,float(err));assert np.allclose(ex,act,equal_nan=True,atol=1e-8,rtol=1e-10),(f,sid,geo,err);count+=len(z)
  checks.append(dict(file=f.name,rows=count,max_error_pp=maxerr));print(checks[-1],flush=True)
pd.DataFrame(checks).to_csv(O/'full_influence_comparison.csv',index=False)
