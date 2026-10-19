from pathlib import Path
import pandas as pd,json,hashlib
O=Path(__file__).resolve().parent
s=pd.read_csv(O/'all_positive_renewable_text_screen.csv');t=pd.read_csv(O/'top10_source_audit_ledger.csv')
for _,r in t.iterrows():
 m=s.source_excel_row.eq(r.source_excel_row);s.loc[m,'screen_classification']=r.host_classification;s.loc[m,'screen_note']=r.audit_note
s.to_csv(O/'all_positive_renewable_text_screen.csv',index=False);s[s.country_conflict_trigger].to_csv(O/'country_conflict_triggers.csv',index=False)
z=json.loads((O/'screen_summary.json').read_text());z['reviewed_host_supported_rows']=8;z['reviewed_host_supported_recorded_usd']=float(t.loc[t.host_classification.eq('source-supported host'),'nominal_usd'].sum());z['reviewed_issuer_ambiguous_rows']=2;z['reviewed_issuer_ambiguous_recorded_usd']=2500000000;z['exact_original_currency_amount_match_rows']=2;z['exact_original_currency_match_archive_converted_usd']=4056920000;z['exact_independent_distinct_finance_exposure_verified_rows']=0
(O/'screen_summary.json').write_text(json.dumps(z,indent=2))
(O/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in O.iterdir() if p.is_file() and p.name!='manifest.json'},indent=2))
print(t[['source_excel_row','host_classification','amount_verification']].to_string(index=False));print(s.groupby('screen_classification').nominal_usd.agg(['count','sum']))
