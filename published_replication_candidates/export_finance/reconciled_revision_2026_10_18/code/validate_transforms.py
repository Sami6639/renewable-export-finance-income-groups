"""Transformation invariants; invoked only after execution-gate clearance."""
from core import *

def run(raw):
 checks=[]
 untouched=raw[~raw.source_excel_row.isin([109,2253,1907,1908,7410,8413,8034])]
 for s in SCENARIOS:
  d=transform(raw,s)
  assert len(d)==len(raw) and d.source_excel_row.is_unique
  pd.testing.assert_frame_equal(d[raw.columns].reset_index(drop=True),raw.reset_index(drop=True))
  u=d[d.source_excel_row.isin(untouched.source_excel_row)]
  assert np.allclose(u.amount,u.nominal_usd,equal_nan=True) and u.included.all()
  if s['G']:
   b=transform(raw,s|{'G':0});u=d[d.source_excel_row.isin([1907,1908])].amount.sum()
   for name in ['all_locations','international_reporting']:
    p0=panel(b,name);p1=panel(d,name)
    assert np.isclose(p0.amount.sum(),p1.amount.sum(),atol=.01)
    assert np.isclose(p0.loc[p0.income.isin(CLASSES),'amount'].sum()-p1.loc[p1.income.isin(CLASSES),'amount'].sum(),u,atol=.01)
   assert np.isclose(panel(b,'country_assigned_international').amount.sum()-panel(d,'country_assigned_international').amount.sum(),u,atol=.01)
  if s['O']:
   o=transform(raw,s,True)
   assert len(o)==len(d)+1
   assert o.loc[o.source_excel_row.eq(2253),'component_id'].nunique()==2
   assert np.isclose(o.loc[o.source_excel_row.eq(2253),'amount'].sum(),1435158682.48,atol=.001)
   assert not o.loc[o.source_excel_row.eq(109),'included'].any()
  # Each operation updates disjoint logical fields or conjunctively excludes rows.
  # Independently apply them in every order and compare the analytical columns.
  for order in itertools.permutations('AOGD'):
   t=transform(raw,dict(A=0,O=0,G=0,D=0,scenario=s['scenario']))
   for f in order:
    if f=='A' and s['A']:
     t.loc[t.source_excel_row.eq(1907),'amount']=125e6;t.loc[t.source_excel_row.eq(1908),'amount']=112.5e6
    if f=='O' and s['O']:t.loc[t.source_excel_row.eq(109),'included']=False
    if f=='G' and s['G']:
     z=t.source_excel_row.isin([1907,1908]);t.loc[z,['recipient','income']]=np.nan;t.loc[z,'recipient_status']='source_verified_cross_border_region'
    if f=='D' and s['D']:t.loc[t.source_excel_row.isin([7410,8413]+([8034] if s['D']==2 else [])),'included']=False
   cols=['amount','included','recipient','income','recipient_status','analytical_year']
   pd.testing.assert_frame_equal(t[cols],d[cols])
  checks.append(dict(scenario=s['scenario'],raw_preserved=True,untouched_rows_preserved=True,all_24_operation_orders_equal=True,geography_mass_conserved=True))
 pd.DataFrame(checks).to_csv(ROOT/'audit/transformation_invariants.csv',index=False)
