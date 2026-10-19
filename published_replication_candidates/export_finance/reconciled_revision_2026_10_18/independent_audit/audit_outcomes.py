"""Independent raw-workbook outcome reconstruction; no producer imports."""
import pandas as pd,numpy as np,itertools,json,hashlib,openpyxl
from pathlib import Path
B=Path(__file__).resolve().parents[2];R=B/'reconciled_revision_2026_10_18';O=Path(__file__).resolve().parent
C=['L','LM','UM','H']; G=['all_locations','international_reporting','country_assigned_international','domestic']; P={**{str(y):[y] for y in range(2013,2023)},'early':[2013,2014,2015],'late':[2020,2021,2022]};PA=[('early','late')]+[(str(y),str(y+1)) for y in range(2013,2022)]
ISO=dict(zip(['Canada','United States','Japan','United Kingdom','Korea','Germany','China','Australia','Italy','Mexico','India','France','Russia','South Africa','Indonesia','Turkey'],['CAN','USA','JPN','GBR','KOR','DEU','CHN','AUS','ITA','MEX','IND','FRA','RUS','ZAF','IDN','TUR']))
T=['delta_pp','composition_pp','within_pp','entry_pp','exit_pp']
public=json.loads((R/'protocol/PUBLIC_PROTOCOL_INTEGRITY.json').read_text());assert hashlib.sha256((R/'protocol/ARITHMETIC_AMENDMENT.md').read_bytes()).hexdigest()==public['amendment_sha256']
d=pd.read_csv(B/'extension/clean_eca_income_mapped.csv');wb=openpyxl.load_workbook(B/'package/CenskowskyEtAl_ECA_ReplicationPackage/data/OCI Public Finance for Energy Database 2024.xlsx',read_only=True,data_only=True);rr=list(wb['Dataset'].values);raw=[dict(zip(rr[0],v)) for v in rr]
base=[]
for z in d[d.technology_group.eq('Renewable')].to_dict('records'):
 r=raw[int(z['source_excel_row'])-1];base.append(dict(id=int(z['source_excel_row']),a=float(r['amountUSD']) if r['amountUSD'] is not None else np.nan,y=int(r['FY']),p=z['provider'] if pd.notna(z['provider']) else 'Unknown provider',r=z['recipient_iso3'],c=z['income_FY2013'],c23=z['income_FY2023'],regional=False))
providers=sorted(set(r['p'] for r in base));pi={p:i for i,p in enumerate(providers)}
def records(a,o,g,d,overlay=False,q=False,vertex=None,fy23=False):
 out=[]
 for orig in base:
  r=orig.copy();i=r['id']
  if (o and i==109) or (d and i in ([7410,8413]+([8034] if d==2 else []))) or (q and i in [1976,8176,9180,9622]):continue
  if fy23:r['c']=r['c23']
  if a and i in [1907,1908]:r['a']=125e6 if i==1907 else 112.5e6
  if g and i in [1907,1908]:r.update(c=np.nan,r=np.nan,regional=True)
  if overlay and i==2253:
   for y,amt in [(2014,789337275.36),(2015,645821407.12)]:out.append(r|{'y':y,'a':amt})
  elif vertex is not None and i in [1907,1908]:
   for c,f in vertex.items():out.append(r|{'c':c,'a':r['a']*f})
  else:out.append(r)
 return out

def scope(rs,g):
 if g==G[0]:return rs
 out=[]
 for r in rs:
  known=pd.notna(r['r']) and r['p'] in ISO;international=known and r['r']!=ISO[r['p']];domestic=known and r['r']==ISO[r['p']]
  if (g==G[1] and (international or r['regional'])) or (g==G[2] and international) or (g==G[3] and domestic):out.append(r)
 return out

def evaluate(rs):
 alloc=[];dec=[];cells=[];mat={}
 for period,years in P.items():
  zz=[r for r in rs if r['y'] in years];m=np.zeros((len(providers),4));v=sum(r['a'] for r in zz if np.isfinite(r['a']));known=sum(r['a'] for r in zz if r['c'] in C and np.isfinite(r['a']));unknown=v-known
  for r in zz:
   if r['c'] in C and np.isfinite(r['a']):m[pi[r['p']],C.index(r['c'])]+=r['a']
  mat[period]=m
  for c in C+['Unknown']:
   sub=[r for r in zz if r['c']==c] if c!='Unknown' else [r for r in zz if r['c'] not in C];amt=sum(r['a'] for r in sub if np.isfinite(r['a']))
   alloc.append(dict(period=period,income_class=c,amount=amt,classified_denominator=known,observed_denominator=v,unknown_amount=unknown,share_classified=amt/known if known and c!='Unknown' else np.nan,share_observed=amt/v if v else np.nan,component_count=len(sub),source_row_count=len(set(r['id'] for r in sub)),missing_amount_count=sum(not np.isfinite(r['a']) for r in sub)))
 for e,l in PA:
  ma,mb=mat[e],mat[l];pa,pb=ma.sum(1),mb.sum(1);va,vb=pa.sum(),pb.sum();val=np.zeros((len(providers),4,4));delta=np.full(4,np.nan)
  if va and vb:
   delta=100*(mb.sum(0)/vb-ma.sum(0)/va)
   for p in range(len(providers)):
    if pa[p] and pb[p]:
     wa,wb=pa[p]/va,pb[p]/vb;ha,hb=ma[p]/pa[p],mb[p]/pb[p];val[p,:,0]=50*(ha+hb)*(wb-wa);val[p,:,1]=50*(wa+wb)*(hb-ha)
    elif pb[p]:val[p,:,2]=100*mb[p]/vb
    elif pa[p]:val[p,:,3]=-100*ma[p]/va
  else:val[:]=np.nan
  for k,c in enumerate(C):
   dec.append(dict(pair=e+'_to_'+l,income_class=c,**dict(zip(T,[delta[k],*val[:,k,:].sum(0)]))))
   for p,pname in enumerate(providers):cells.append(dict(pair=e+'_to_'+l,income_class=c,provider=pname,**dict(zip(T[1:],val[p,k]))))
 return pd.DataFrame(alloc),pd.DataFrame(dec),pd.DataFrame(cells),mat

def build():
 aa=[];dd=[];pp=[]
 for a,o,g,d in itertools.product(range(2),range(2),range(2),range(3)):
  s=f'A{a}O{o}G{g}D{d}'
  for overlay,q in [(False,False),(False,True)]+([(True,False)] if o else []):
   name=s+('_agreement' if overlay else '_Q1' if q else '');rs=records(a,o,g,d,overlay,q)
   for geo in G:
    av,dv,pv,_=evaluate(scope(rs,geo));meta={'scenario':name,'geography':geo}
    aa.append(av.assign(**meta));dd.append(dv.assign(**meta));pp.append(pv.assign(**meta))
 pd.concat(aa).to_csv(O/'independent_allocation.csv',index=False);pd.concat(dd).to_csv(O/'independent_decomposition.csv',index=False);pd.concat(pp).to_csv(O/'independent_provider_contributions.csv',index=False)
 print('Independent 60 case outputs saved',flush=True)

def compare(name,keys,metrics,filename=None):
 expected=pd.read_csv(O/('independent_'+name+'.csv')).set_index(keys);actual=pd.read_csv(R/'outputs'/(filename or name+'.csv')).set_index(keys);missing=actual.index.difference(expected.index);assert not len(missing),(name,missing);e=expected.loc[actual.index];results=[]
 for m in metrics:
  x,y=actual[m].to_numpy(float),e[m].to_numpy(float);assert np.array_equal(np.isnan(x),np.isnan(y)),(name,m,'NaN');err=np.nanmax(abs(x-y));assert np.allclose(x,y,equal_nan=True,atol=1e-5 if ('amount' in m or 'denominator' in m) else 1e-8,rtol=1e-12),(name,m,err);results.append({'file':filename or name,'metric':m,'rows':len(x),'max_absolute_error':float(err)})
 return results
if __name__=='__main__':build()
