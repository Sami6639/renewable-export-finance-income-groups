"""Pure accounting functions. Importing this module never computes archive outcomes."""
from pathlib import Path
import itertools
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent
CLASSES=['L','LM','UM','H']
PANELS=['all_locations','international_reporting','country_assigned_international','domestic']
PERIODS={**{str(y):(y,) for y in range(2013,2023)},'early':(2013,2014,2015),'late':(2020,2021,2022)}
PAIRS=[('early','late')]+[(str(y),str(y+1)) for y in range(2013,2022)]
PROVIDERS={'Canada':'CAN','United States':'USA','Japan':'JPN','United Kingdom':'GBR','Korea':'KOR','Germany':'DEU','China':'CHN','Australia':'AUS','Italy':'ITA','Mexico':'MEX','India':'IND','France':'FRA','Russia':'RUS','South Africa':'ZAF','Indonesia':'IDN','Turkey':'TUR'}
TERMS=['delta_pp','composition_pp','within_pp','entry_pp','exit_pp']
SCENARIOS=[dict(scenario=f'A{a}O{o}G{g}D{d}',A=a,O=o,G=g,D=d) for a,o,g,d in itertools.product(range(2),range(2),range(2),range(3))]

def load():
 d=pd.read_csv(BASE/'extension/clean_eca_income_mapped.csv')
 assert d.source_excel_row.is_unique and d.main_sample.all()
 return d

def transform(raw,s,overlay=False,income_year=2013):
 d=raw.copy(deep=True)
 d['component_id']='Excel'+d.source_excel_row.astype(str)
 d['amount']=d.nominal_usd
 d['analytical_year']=d.FY.astype(int)
 d['income']=d[f'income_FY{income_year}']
 d['recipient']=d.recipient_iso3
 d['provider_iso3']=d.provider.map(PROVIDERS)
 d['provider_key']=d.provider.fillna('Unknown provider')
 d['included']=True
 d['recipient_status']=np.where(d.recipient.notna(),'assigned_country','otherwise_unresolved')
 d['amount_basis']='archive-reported heterogeneous basis'
 d['evidence_id']='archive'
 d['evidence_type']='archive'
 d['reason']='unchanged'
 sb=d.source_excel_row.isin([1907,1908])
 if s['A']:
  d.loc[d.source_excel_row.eq(1907),'amount']=125e6
  d.loc[d.source_excel_row.eq(1908),'amount']=112.5e6
  d.loc[sb,'amount_basis']=['direct JBIC loan' if r==1907 else 'derived partial guarantee support' for r in d.loc[sb,'source_excel_row']]
  d.loc[sb,'evidence_id']='standard_bank_jbic_primary'
  d.loc[sb,'evidence_type']=['direct' if r==1907 else 'derived conditional subtraction' for r in d.loc[sb,'source_excel_row']]
  d.loc[sb,'reason']='A1 source support amounts'
 if s['O']:
  q=d.source_excel_row.eq(109);d.loc[q,'included']=False;d.loc[q,'reason']='O1 repeated Karuma package';d.loc[q,'evidence_id']='karuma_contracts';d.loc[q,'evidence_type']='source-supported reconciliation inference'
 if s['G']:
  d.loc[sb,['recipient','income']]=np.nan;d.loc[sb,'recipient_status']='source_verified_cross_border_region';d.loc[sb,'reason']=d.loc[sb,'reason']+'; G1 ultimate recipient unallocated'
 if s['D']:
  ids=[7410,8413]+([8034] if s['D']==2 else [])
  q=d.source_excel_row.isin(ids);d.loc[q,'included']=False;d.loc[q,'reason']='D'+str(s['D'])+' basis quarantine';d.loc[q,'evidence_id']='dogger_source_review'
 if overlay:
  assert s['O']==1
  q=d.source_excel_row.eq(2253);orig=d.loc[q].copy();assert len(orig)==1
  d=d.loc[~q].copy()
  for year,amt in [(2014,789337275.36),(2015,645821407.12)]:
   z=orig.copy();z['component_id']=f'Excel2253_agreement_{year}';z['analytical_year']=year;z['amount']=amt;z['amount_basis']='contracted lending: generation and interconnection';z['evidence_id']='karuma_signed_contracts';z['evidence_type']='direct';z['reason']='agreement-year overlay; calendar agreement year, not verified fiscal year';d=pd.concat([d,z],ignore_index=True)
 d['scenario']=s['scenario']+('_agreement' if overlay else '')
 return d

def panel(d,name, included=True):
 q=d.loc[d.included] if included else d
 known=q.provider_iso3.notna()&q.recipient.notna()
 intl=known&q.provider_iso3.ne(q.recipient)
 masks={'all_locations':np.ones(len(q),dtype=bool),'international_reporting':intl|q.recipient_status.eq('source_verified_cross_border_region'),'country_assigned_international':intl,'domestic':known&q.provider_iso3.eq(q.recipient)}
 return q.loc[masks[name]]

def allocate(q):
 rows=[];coverage=[];marginals=[]
 for period,years in PERIODS.items():
  z=q[q.analytical_year.isin(years)]
  known=z.income.isin(CLASSES);v=z.amount.sum();k=z.loc[known,'amount'].sum();u=z.loc[~known,'amount'].sum()
  for c in CLASSES+['Unknown']:
   a=z[z.income.eq(c)] if c!='Unknown' else z.loc[~known]
   n=a.amount.sum()
   rows.append(dict(period=period,income_class=c,amount=n,classified_denominator=k,observed_denominator=v,unknown_amount=u,share_classified=n/k if k and c!='Unknown' else np.nan,share_observed=n/v if v else np.nan,lower_observed_bound=n/v if v and c!='Unknown' else np.nan,upper_observed_bound=(n+u)/v if v and c!='Unknown' else np.nan,component_count=len(a),source_row_count=a.source_excel_row.nunique(),missing_amount_count=int(a.amount.isna().sum())))
  z=z.assign(provider_known=z.provider_iso3.notna(),income_known=known)
  for pk,rs,ik in itertools.product([False,True],['assigned_country','source_verified_cross_border_region','otherwise_unresolved'],[False,True]):
   a=z[z.provider_known.eq(pk)&z.recipient_status.eq(rs)&z.income_known.eq(ik)]
   coverage.append(dict(period=period,provider_known=pk,recipient_status=rs,income_known=ik,observed_amount=a.amount.sum(),component_count=len(a),missing_amount_count=int(a.amount.isna().sum())))
  for name,m in [('unknown_country',z.recipient.isna()),('known_country_unclassified_income',z.recipient.notna()&~z.income_known),('unknown_provider',~z.provider_known)]:
   a=z[m];marginals.append(dict(period=period,marginal=name,observed_amount=a.amount.sum(),component_count=len(a),overlap_warning='Marginal flags can overlap; do not sum.'))
  assert np.isclose(sum(r['amount'] for r in rows[-5:]),v,atol=.01)
  if k: assert abs(sum(r['share_classified'] for r in rows[-5:-1])-1)<1e-10
 return pd.DataFrame(rows),pd.DataFrame(coverage),pd.DataFrame(marginals)

def matrices(q):
 providers=sorted(q.provider_key.unique())
 out={}
 for period,years in PERIODS.items():
  z=q[q.analytical_year.isin(years)&q.income.isin(CLASSES)]
  m=z.pivot_table(index='provider_key',columns='income',values='amount',aggfunc='sum',fill_value=0).reindex(index=providers,columns=CLASSES,fill_value=0).to_numpy(float)
  assert np.all(m>=0),'Negative observed dollars require protocol review'
  out[period]=m
 return providers,out

def decompose_arrays(a,b):
 pa=a.sum(axis=1);pb=b.sum(axis=1);va=pa.sum();vb=pb.sum()
 if va<=0 or vb<=0: return np.full((len(pa),4,4),np.nan),np.full(4,np.nan),None
 wa=pa/va;wb=pb/vb;ha=np.divide(a,pa[:,None],out=np.zeros_like(a),where=pa[:,None]>0);hb=np.divide(b,pb[:,None],out=np.zeros_like(b),where=pb[:,None]>0)
 co=(pa>0)&(pb>0);en=(pa==0)&(pb>0);ex=(pa>0)&(pb==0)
 t=np.zeros((len(pa),4,4))
 t[co,:,0]=(ha[co]+hb[co])/2*(wb[co]-wa[co])[:,None]
 t[co,:,1]=(wa[co]+wb[co])[:,None]/2*(hb[co]-ha[co])
 t[en,:,2]=wb[en,None]*hb[en];t[ex,:,3]=-wa[ex,None]*ha[ex]
 delta=b.sum(axis=0)/vb-a.sum(axis=0)/va
 assert np.max(np.abs(t.sum(axis=(0,2))-delta))<1e-10
 assert abs(t[:,:,1].sum())<1e-10
 assert abs(t[:,:,[0,2,3]].sum())<1e-10
 support=dict(common_provider_count=int(co.sum()),entry_provider_count=int(en.sum()),exit_provider_count=int(ex.sum()),common_volume_share_early=wa[co].sum(),common_volume_share_late=wb[co].sum(),classified_denominator_early=va,classified_denominator_late=vb)
 return t*100,delta*100,(support,pa,pb,wa,wb,ha,hb)

def decomposition(q):
 providers,m=matrices(q);rows=[];cells=[]
 for early,late in PAIRS:
  t,delta,aux=decompose_arrays(m[early],m[late]);sums=t.sum(axis=0) if aux else np.full((4,4),np.nan)
  for k,c in enumerate(CLASSES):
   base=dict(pair=f'{early}_to_{late}',early=early,late=late,income_class=c,delta_pp=delta[k],**dict(zip(TERMS[1:],sums[k])))
   rows.append(base|({'status':'defined',**aux[0]} if aux else {'status':'undefined'}))
   for p,provider in enumerate(providers):
    cell=dict(pair=base['pair'],income_class=c,provider=provider,**dict(zip(TERMS[1:],t[p,k])))
    if aux:
     _,pa,pb,wa,wb,ha,hb=aux
     cell.update(provider_amount_early=pa[p],provider_amount_late=pb[p],weight_early=wa[p],weight_late=wb[p],within_share_early=ha[p,k] if pa[p] else np.nan,within_share_late=hb[p,k] if pb[p] else np.nan,support='common' if pa[p]>0 and pb[p]>0 else 'entry' if pb[p]>0 else 'exit' if pa[p]>0 else 'absent')
    cells.append(cell)
 return pd.DataFrame(rows),pd.DataFrame(cells)
