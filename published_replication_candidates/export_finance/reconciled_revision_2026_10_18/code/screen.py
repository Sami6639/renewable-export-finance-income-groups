"""Full retained-population arithmetic consistency gate. Never repairs amounts."""
from core import *
import json,hashlib,sys

def run():
 from public_integrity import protocol_integrity
 h=protocol_integrity()['sha256']
 d=load();a=pd.to_numeric(d.amountOriginal,errors='coerce');x=pd.to_numeric(d.XR,errors='coerce');v=pd.to_numeric(d.amountUSD,errors='coerce')
 e=v-a*x;eligible=np.isfinite(a)&np.isfinite(x)&np.isfinite(v)
 tol=np.maximum(1,.01*np.maximum(abs(v),abs(a*x)))
 d['screen_original_numeric']=a;d['screen_xr_numeric']=x;d['screen_usd_numeric']=v;d['screen_product']=a*x;d['screen_residual']=e;d['screen_tolerance']=tol;d['screen_eligible']=eligible
 d['material_arithmetic_discrepancy']=eligible&(abs(e)>tol)
 d['usd_xr1_discrepancy']=d.currency.str.upper().eq('USD')&np.isclose(x,1,atol=1e-12,rtol=0)&(abs(v-a)>1)
 old=pd.read_csv(BASE/'extension/fx_reconciliation_exceptions.csv');d['in_old_fx_exception_file']=d.source_excel_row.isin(old.source_excel_row)
 d.to_csv(ROOT/'audit/arithmetic_consistency_all_rows.csv',index=False)
 d.loc[d.material_arithmetic_discrepancy|d.usd_xr1_discrepancy].to_csv(ROOT/'audit/arithmetic_flagged_rows.csv',index=False)
 summaries=[]
 for col in ['technology_group','provider','FY','income_FY2013']:
  for key,z in d.groupby(col,dropna=False):
   summaries.append(dict(grouping=col,group=key,rows=len(z),eligible=int(z.screen_eligible.sum()),missing_or_nonfinite=int((~z.screen_eligible).sum()),material_flags=int(z.material_arithmetic_discrepancy.sum()),usd_xr1_flags=int(z.usd_xr1_discrepancy.sum()),recorded_amount=z.nominal_usd.sum(),flagged_recorded_amount=z.loc[z.material_arithmetic_discrepancy|z.usd_xr1_discrepancy,'nominal_usd'].sum()))
 pd.DataFrame(summaries).to_csv(ROOT/'audit/arithmetic_summary.csv',index=False)
 new=d.loc[d.technology_group.eq('Renewable')&(d.material_arithmetic_discrepancy|d.usd_xr1_discrepancy)&~d.source_excel_row.isin([1907,1908])]
 gate=dict(protocol_sha256=h,screen_rows=len(d),material_rows=int(d.material_arithmetic_discrepancy.sum()),usd_xr1_rows=int(d.usd_xr1_discrepancy.sum()),additional_renewable_flagged_ids=new.source_excel_row.tolist(),status='STOP_REVIEW_ADDITIONAL_RENEWABLE_FLAGS' if len(new) else 'CLEAR')
 (ROOT/'audit/arithmetic_gate.json').write_text(json.dumps(gate,indent=2));print(json.dumps(gate,indent=2))
 if len(new):print(new[['source_excel_row','project','amountOriginal','XR','amountUSD','screen_residual','in_old_fx_exception_file']].to_string(index=False))
 return gate
if __name__=='__main__':run()
