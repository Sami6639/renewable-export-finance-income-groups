import pandas as pd,numpy as np,pathlib,json,hashlib
base=pathlib.Path(__file__).resolve().parents[2];p=base/'package/CenskowskyEtAl_ECA_ReplicationPackage/data'
f=p/'OCI Public Finance for Energy Database 2024.xlsx'; d=pd.read_excel(f,sheet_name='Dataset'); original=d.columns.tolist();d['excel_row']=np.arange(len(d))+2
e=d.loc[d.institutionKind.eq('Export Credit')].copy();steps=[]
def tally(x): return dict(n=len(x),known_nominal_usd=float(x.amountUSD.sum(min_count=1)),missing_amount=int(x.amountUSD.isna().sum()))
steps.append({'stage':'ECA',**tally(e)})
for col,val in [('stage','Electric Vehicles'),('sector','Climate'),('stage','Petrochemical'),('institutionAbbr','BNDES'),('institutionAbbr','JICA')]:
 e=e[~e[col].eq(val)];steps.append({'stage':col+' != '+val,**tally(e)})
c=pd.read_excel(p/'240918 IMF IFS - US CPI.xlsx',header=None);ratios={int(c.iloc[1,j]):float(c.iloc[2,j])/float(c.iloc[2,21]) for j in range(2,25)}
assert ratios[2020]==1
# raw 2020 is col21 (2001 col2)
e['real2020']=e.amountUSD/e.FY.map(ratios)
dup=e.duplicated(original,keep='first');all_dup=e.duplicated(original,keep=False)
agg=e.project.str.contains('AGGREGATE|ANNUAL TOTAL',case=False,na=False)
un=e.country.str.contains('Global|Multiple|regional',case=False,na=False)
a=pd.to_numeric(e.amountOriginal,errors='coerce')*e.XR;ok=e.amountUSD.notna()&a.notna(); mismatch=ok&~np.isclose(e.amountUSD,a,rtol=1e-6,atol=.01)
r={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'sequential':steps,'primary':tally(e),'real2020_sum':float(e.real2020.sum()),'subsequent_exact_duplicate_rows':int(dup.sum()),'all_exact_duplicate_rows':int(all_dup.sum()),'subsequent_exact_duplicate_usd':float(e.loc[dup,'amountUSD'].sum()),'aggregate_named':tally(e[agg]),'unallocable_regex':tally(e[un]),'aggregate_outside_unallocable_regex':e.loc[agg&~un,['excel_row','country','project']].to_dict('records'),'fx_test_eligible':int(ok.sum()),'fx_mismatch_1e6relative_1centabsolute':e.loc[mismatch,['excel_row','amountUSD','amountOriginal','XR']].to_dict('records'),'missing_amount':e.loc[e.amountUSD.isna(),['excel_row','project','amountOriginal','XR']].to_dict('records'),'ratios':ratios}
pathlib.Path(__file__).with_name('source_recomputed.json').write_text(json.dumps(r,indent=2));e.groupby('FY').agg(n=('excel_row','size'),nominal=('amountUSD','sum'),real2020=('real2020','sum')).to_csv(pathlib.Path(__file__).with_name('annual_recomputed.csv'));print(json.dumps(r,indent=2))
