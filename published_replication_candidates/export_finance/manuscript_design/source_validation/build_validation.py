from pathlib import Path
import pandas as pd, re,json,hashlib,unicodedata
O=Path(__file__).resolve().parent; B=O.parent.parent; P=B/'extension/clean_eca_income_mapped.csv';d=pd.read_csv(P)
providers={'Canada':'CAN','United States':'USA','Japan':'JPN','United Kingdom':'GBR','Korea':'KOR','Germany':'DEU','China':'CHN','Australia':'AUS','Italy':'ITA','Mexico':'MEX','India':'IND','France':'FRA','Russia':'RUS','South Africa':'ZAF','Indonesia':'IDN','Turkey':'TUR'}
d['international']=d.recipient_iso3.notna()&d.recipient_iso3.ne(d.provider.map(providers))
s=d[d.FY.between(2013,2022)&d.technology_group.eq('Renewable')&d.nominal_usd.gt(0)].copy()
top=pd.concat([s[s.FY.between(a,b)&s.international].sort_values(['nominal_usd','source_excel_row'],ascending=[False,True],kind='stable').head(5).assign(window=w,rank=lambda x:range(1,len(x)+1)) for a,b,w in [(2013,2015,'early'),(2020,2022,'late')]])
top.to_csv(O/'fixed_top10_raw.csv',index=False)
iso=pd.read_excel(B/'package/CenskowskyEtAl_ECA_ReplicationPackage/data/240801 ISO3-ISO2-codes.xlsx',sheet_name='iso3iso2')
alias=[]
for _,r in iso.iterrows():
 for val,typ in [(r['Country'],'country_name'),(r['Alpha-3 code'],'ISO3_uppercase'),(r['Alpha-2 code'],'ISO2_uppercase')]:
  if isinstance(val,str):alias.append((val,r['Alpha-3 code'],typ))
for _,r in d[['country','recipient_iso3']].dropna().drop_duplicates().iterrows():alias.append((r['country'],r['recipient_iso3'],'dataset_country_name'))
for code,names in {'GBR':['UK','U.K.','United Kingdom','Britain','Great Britain','England','Scotland','Wales','Northern Ireland','Royaume-Uni'],'USA':['US','U.S.','USA','United States','United States of America'],'KOR':['South Korea','Republic of Korea'],'CIV':['Ivory Coast','Côte d’Ivoire'],'TUR':['Türkiye','Turkey'],'COD':['DR Congo','Democratic Republic of the Congo'],'COG':['Republic of the Congo'],'ZAF':['South Africa'],'CHN':['PRC','China']}.items():
 for n in names:alias.append((n,code,'documented_extra_alias'))
alias=sorted(set(alias));pd.DataFrame(alias,columns=['alias','iso3','type']).to_csv(O/'country_alias_dictionary.csv',index=False)
fields=['project','projectInstitutionName','projectDesc','entity']
def screen(r):
 hits=[]
 for f in fields:
  t=str(r[f]) if pd.notna(r[f]) else ''
  for a,c,k in alias:
   flags=0 if (k.startswith('ISO') or len(a)<=3) else re.I
   if re.search(r'(?<!\w)'+re.escape(a)+r'(?!\w)',t,flags):hits.append((f,a,c))
 other=sorted({c for _,_,c in hits if c!=r.recipient_iso3})
 return pd.Series({'text_country_matches':json.dumps(hits,ensure_ascii=False),'other_country_iso3':';'.join(other),'country_conflict_trigger':bool(other),'screen_classification':'unresolved','screen_note':'Text matches are review triggers only; foreign names may identify exporter, lender, owner, service territory, or incidental mention. No match is not validation.'})
s=pd.concat([s,s.apply(screen,axis=1)],axis=1)
s.to_csv(O/'all_positive_renewable_text_screen.csv',index=False)
s[s.country_conflict_trigger].to_csv(O/'country_conflict_triggers.csv',index=False)
summary={'input_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'screen_rows':len(s),'screen_nominal_usd':s.nominal_usd.sum(),'flag_rows':int(s.country_conflict_trigger.sum()),'flag_nominal_usd':s.loc[s.country_conflict_trigger,'nominal_usd'].sum(),'top_rows':len(top),'top_nominal_usd':top.nominal_usd.sum(),'windows':{}}
for a,b,w in [(2013,2015,'early'),(2020,2022,'late')]:
 q=s[s.FY.between(a,b)&s.international];t=top[top.window.eq(w)];summary['windows'][w]={'international_positive_rows':len(q),'international_positive_usd':q.nominal_usd.sum(),'audited_rows':len(t),'audited_recorded_usd':t.nominal_usd.sum(),'recorded_value_coverage':t.nominal_usd.sum()/q.nominal_usd.sum()}
(O/'screen_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
