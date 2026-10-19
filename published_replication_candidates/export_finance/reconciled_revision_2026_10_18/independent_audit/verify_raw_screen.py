"""Independent gate-only audit. Does not calculate revised allocation outcomes."""
from pathlib import Path
import openpyxl,pandas as pd,numpy as np,json,hashlib
B=Path(__file__).resolve().parents[2]
O=Path(__file__).resolve().parent
R=O.parent
D=pd.read_csv(B/'extension/clean_eca_income_mapped.csv')
W=openpyxl.load_workbook(B/'package/CenskowskyEtAl_ECA_ReplicationPackage/data/OCI Public Finance for Energy Database 2024.xlsx',read_only=True,data_only=True)
rows=list(W['Dataset'].iter_rows(values_only=True));head=rows[0]
errors=[];out=[]
for _,r in D.iterrows():
 raw=dict(zip(head,rows[int(r.source_excel_row)-1]));z={'source_excel_row':int(r.source_excel_row)}
 for k in ['amountOriginal','amountUSD','XR','FY']:
  a=pd.to_numeric(raw[k],errors='coerce');b=pd.to_numeric(r[k],errors='coerce')
  if not ((pd.isna(a) and pd.isna(b)) or np.isclose(a,b,rtol=1e-12,atol=1e-6)):
   errors.append({'row':int(r.source_excel_row),'field':k,'raw':str(a),'clean':str(b)})
 a=pd.to_numeric(raw['amountOriginal'],errors='coerce');x=pd.to_numeric(raw['XR'],errors='coerce');u=pd.to_numeric(raw['amountUSD'],errors='coerce')
 eligible=np.isfinite(a) and np.isfinite(x) and np.isfinite(u)
 residual=u-a*x;threshold=max(1,.01*max(abs(u),abs(a*x))) if eligible else np.nan
 z.update(amount_original=a,xr=x,amount_usd=u,eligible=eligible,residual=residual,threshold=threshold,material_flag=bool(eligible and abs(residual)>threshold),currency=raw['currency'],technology_group=r.technology_group,provider=r.provider,FY=r.FY,income_FY2013=r.income_FY2013)
 out.append(z)
T=pd.DataFrame(out);T.to_csv(O/'workbook_independent_arithmetic_screen.csv',index=False)
report={'raw_numeric_disagreements':errors,'rows':len(T),'eligible':int(T.eligible.sum()),'flagged':int(T.material_flag.sum()),'flagged_renewable_rows':T.loc[T.material_flag&T.technology_group.eq('Renewable'),'source_excel_row'].tolist(),'protocol_sha256':hashlib.sha256((R/'protocol/ANALYSIS_PROTOCOL.md').read_bytes()).hexdigest(),'revised_outcomes_calculated':False}
(O/'independent_gate_audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not errors
