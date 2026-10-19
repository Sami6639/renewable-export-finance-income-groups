"""Independent stdlib-only verification. Does not import or execute evidence builder."""
import csv, json, math, hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent; O=HERE.parent; E=O.parent.parent/'extension'
def read(p):
 with p.open(newline='') as f: return list(csv.DictReader(f))
def num(s): return float(s) if s not in ('','nan','NaN',None) else math.nan
def total(rows,col):return math.fsum(num(r[col]) for r in rows if math.isfinite(num(r[col])))
def ratio(a,b):return a/b if b else math.nan
checks=0; errors=[]; max_amount_error=0

def equal(actual, expected, label):
 global checks,max_amount_error
 checks+=1;a=num(actual) if isinstance(actual,str) else actual
 if math.isnan(expected):ok=math.isnan(a)
 else:
  ok=math.isclose(a,expected,rel_tol=2e-13,abs_tol=1e-5 if abs(expected)>1 else 1e-13)
  if abs(expected)>1:max_amount_error=max(max_amount_error,abs(a-expected))
 if not ok:errors.append({'label':label,'actual':str(actual),'expected':str(expected)})
raw=read(E/'clean_eca_income_mapped.csv'); start_hash=hashlib.sha256((E/'clean_eca_income_mapped.csv').read_bytes()).hexdigest()
providers=dict(zip(['Canada','United States','Japan','United Kingdom','Korea','Germany','China','Australia','Italy','Mexico','India','France','Russia','South Africa','Indonesia','Turkey'],['CAN','USA','JPN','GBR','KOR','DEU','CHN','AUS','ITA','MEX','IND','FRA','RUS','ZAF','IDN','TUR']))
assert set(r['provider'] for r in raw)<=set(providers)
assert set(int(r['FY']) for r in raw)==set(range(2013,2023))
source=[r for r in raw if r['recipient_iso3'] and r['recipient_iso3']!=providers[r['provider']]]
classes=['H','UM','LM','L','Unclassified']; quarantined={7410,8034,8413}
assert {int(r['source_excel_row']) for r in source}&quarantined==quarantined
assert all(r['technology_group']=='Renewable' and r['income_FY2013']=='H' for r in source if int(r['source_excel_row']) in quarantined)
equal(total([r for r in source if int(r['source_excel_row']) in quarantined],'nominal_usd'),4579950000,'quarantine amount')
R=read(O/'income_class_annual_and_windows.csv'); C=read(O/'annual_and_window_coverage.csv')
assert len(R)==480 and len(C)==96
keys=['scenario','technology','period','monetary_basis']
def key(r):return tuple(r[k] for k in keys)
ci={key(r):r for r in C};ri={key(r)+(r['income_class'],):r for r in R}
assert len(ci)==96 and len(ri)==480
periods={str(y):[y] for y in range(2013,2023)}|{'early':[2013,2014,2015],'late':[2020,2021,2022]}
for scenario in ['Archive','Quarantine']:
 for tech in ['Renewable','Fossil']:
  for period,years in periods.items():
   a=[r for r in source if r['technology_group']==tech and int(r['FY']) in years and (scenario=='Archive' or int(r['source_excel_row']) not in quarantined)]
   known=[r for r in a if r['income_FY2013'] in classes[:4]]
   for basis,col in [('Nominal USD','nominal_usd'),('Once-deflated 2020 USD','real2020_usd_once')]:
    k=(scenario,tech,period,basis); c=ci[k];assert c['fixed_income_FY']=='2013'
    v=total(a,col);kv=total(known,col);h=total([r for r in known if r['income_FY2013']=='H'],col);un=total([r for r in a if r not in known],col)
    expected={'observed_usd':v,'classified_usd':kv,'high_usd':h,'non_high_usd':kv-h,'unclassified_usd':un,'entries':len(a),'classified_entries':len(known),'missing_amount_entries':sum(not math.isfinite(num(r[col])) for r in a),'amount_income_coverage':ratio(kv,v),'entry_income_coverage':ratio(len(known),len(a)),'high_share_classified':ratio(h,kv)}
    for field,val in expected.items():equal(c[field],val,str(k)+field)
    for cl in classes:
     b=[r for r in a if (r['income_FY2013']==cl if cl!='Unclassified' else r['income_FY2013'] not in classes[:4])];r=ri[k+(cl,)];assert r['fixed_income_FY']=='2013';amount=total(b,col)
     expected={'amount_usd':amount,'entries':len(b),'missing_amount_entries':sum(not math.isfinite(num(x[col])) for x in b),'observed_usd_denominator':v,'classified_usd_denominator':kv,'all_entries_denominator':len(a),'classified_entries_denominator':len(known),'amount_share_observed':ratio(amount,v),'amount_share_classified':ratio(amount,kv) if cl!='Unclassified' else math.nan,'entry_share_all':ratio(len(b),len(a)),'entry_share_classified':ratio(len(b),len(known)) if cl!='Unclassified' else math.nan}
     for field,val in expected.items():equal(r[field],val,str(k)+(cl,).__str__()+field)
    equal(math.fsum(num(ri[k+(cl,)]['amount_usd']) for cl in classes),v,str(k)+'class sum')
# CPI is checked on every frozen row, not re-estimated or deflated again.
cpi={int(r['year']):num(r['cpi_relative_2020']) for r in read(E/'cpi_validated.csv')}
for r in raw:
 equal(r['real2020_usd_once'],num(r['nominal_usd'])/cpi[int(r['FY'])],r['source_excel_row']+' once deflation')
endpoint_checks=0
for scenario,fn in [('Archive','provider_only_endpoints.csv'),('Quarantine','provider_only_quarantine_endpoints.csv')]:
 for r in read(E/fn):
  if r['geography']=='Known international' and r['technology'] in ['Renewable','Fossil']:
   n=ci[(scenario,r['technology'],r['window'],'Nominal USD')]
   for new,old in [('entries','entries'),('missing_amount_entries','missing_source_usd_entries'),('observed_usd','observed_weight'),('classified_usd','allocable_weight'),('high_usd','high_weight'),('unclassified_usd','unknown_weight'),('high_share_classified','high_share')]:equal(n[new],num(r[old]),fn+new);endpoint_checks+=1
# The main tables must be unchanged selections of audited inputs.
for out,src in [('table1_data_coverage.csv','full_technology_geography_coverage.csv'),('table2_allocation_comparators.csv','full_technology_geography_changes.csv')]:
 expected=[r for r in read(E/src) if r['unit']=='Nominal USD']; actual=read(O/out)
 assert len(expected)==len(actual)
 for a,b in zip(actual,expected):
  for field,val in b.items():
   try: equal(a[field],num(val),out+field)
   except ValueError: assert a[field]==val
# Verify both provider-accounting selections and source endpoint table.
expected=[]
for scenario,fn in [('Archive','provider_only_decomposition.csv'),('Quarantine','provider_only_quarantine_decomposition.csv')]:
 expected += [r|{'scenario':scenario} for r in read(E/fn) if r['technology']=='Renewable' and r['geography']=='Known international']
for out,ex in [('table3_provider_country_scenarios.csv',expected),('table4_source_scenario_endpoints.csv',[r for r in C if r['technology']=='Renewable' and r['period'] in ['early','late'] and r['monetary_basis']=='Nominal USD'])]:
 actual=read(O/out); assert len(actual)==len(ex)
 for a,b in zip(actual,ex):
  for field,val in b.items():
   try:equal(a[field],num(val),out+field)
   except ValueError:assert a[field]==val
# Fixed pooled windows sum annual numerators and counts, not annual shares.
for k,c in ci.items():
 if k[2] not in ['early','late']:continue
 for field in ['observed_usd','classified_usd','high_usd','non_high_usd','unclassified_usd','entries','classified_entries','missing_amount_entries']:
  equal(c[field],math.fsum(num(ci[(k[0],k[1],str(y),k[3])][field]) for y in periods[k[2]]),'pooled annual sum '+str(k)+field)
assert start_hash==hashlib.sha256((E/'clean_eca_income_mapped.csv').read_bytes()).hexdigest()
result={'status':'PASS' if not errors else 'FAIL','independent_method':'Python standard-library csv reader, row filters, math.fsum; no import or execution of builder; no fitted models or changed classifications','checks':checks,'errors':errors,'max_absolute_numeric_difference_above_one':max_amount_error,'class_rows':len(R),'coverage_rows':len(C),'prior_endpoint_cells_checked':endpoint_checks,'known_international_records':len(source),'all_source_records':len(raw),'unclassified_known_international_records':sum(r['income_FY2013'] not in classes[:4] for r in source),'missing_nominal_known_international_records':sum(not math.isfinite(num(r['nominal_usd'])) for r in source),'source_sha256':start_hash,'quarantine_rows':sorted(quarantined),'scope':'FY2013–2022 Renewable/Fossil, fixed FY2013 income, nominal and once-deflated 2020 USD; early FY2013–15 and late FY2020–22','interpretation':'Recorded heterogeneous values by reported recipient countries. Missing amounts counted but excluded from numeric sums; an empty class sum is an accounting zero, not an imputed missing amount. Unclassified conditional-classified shares are intentionally undefined (blank).','chart_input_review':'Builder inspected: figures 1 and SI use complete annual grid; figure 2 uses nominal full-technology/geography changes; figure 3 uses previously audited provider decomposition; figure 4 uses nominal renewable pooled endpoints. USD/1e9 for bn; fractions*100 for shares and percentage points. No new model or recoding found.','bridge_status':'Reviewed separately in documentary_review.json'}
(HERE/'annual_income_audit.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps(result,indent=2));assert not errors
