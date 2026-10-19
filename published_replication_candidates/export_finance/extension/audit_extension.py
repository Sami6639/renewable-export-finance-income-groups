"""Gate-one OCI reconciliation. Run from any directory; no network or private TXF data."""
from pathlib import Path
import pandas as pd, numpy as np, json, hashlib, re
OUT=Path(__file__).resolve().parent
SRC=OUT.parent/'package/CenskowskyEtAl_ECA_ReplicationPackage'
f=SRC/'data/OCI Public Finance for Energy Database 2024.xlsx'
raw=pd.read_excel(f,sheet_name='Dataset')
cols=raw.columns.tolist()
raw['source_excel_row']=np.arange(len(raw))+2
raw['visible_normalized']=raw.visible.astype(str).str.strip().str.lower().eq('true')
d=raw[raw.visible_normalized].copy()
d['exact_duplicate_subsequent']=d.duplicated(cols)
d['exact_duplicate_group']=d.duplicated(cols,keep=False)
d['FY']=pd.to_numeric(d.FY,errors='coerce').astype('Int64')
d['approval_year']=d.date.astype(str).str.extract(r'((?:19|20)\d{2})')[0].astype('Int64')
d['nominal_original_usd']=pd.to_numeric(d.amountUSD,errors='coerce')
d['original_numeric']=pd.to_numeric(d.amountOriginal,errors='coerce')
d['xr_numeric']=pd.to_numeric(d.XR,errors='coerce')
d['fx_product_usd']=d.original_numeric*d.xr_numeric
d['amount_repaired_from_source_fx']=d.nominal_original_usd.isna() & d.fx_product_usd.notna()
d['nominal_usd']=d.nominal_original_usd
# Only the uniquely identified ECA missing observation is eligible for source-FX sensitivity.
d['nominal_usd_source_fx_sensitivity']=d.nominal_original_usd
repair=d.institutionKind.eq('Export Credit') & d.project.eq('Benarix Environmental Inc.') & d.FY.eq(2020) & d.nominal_original_usd.isna() & d.original_numeric.eq(500000) & d.xr_numeric.eq(.71309)
assert repair.sum()==1
d.loc[repair,'nominal_usd_source_fx_sensitivity']=d.loc[repair,'fx_product_usd']
d['fx_difference_usd']=d.nominal_original_usd-d.fx_product_usd
d['recipient_unallocable']=d.country.astype(str).str.contains('Global|Multiple|regional',case=False,regex=True)|d.country.isna()
d['aggregate_name_flag']=d.project.astype(str).str.contains('aggregate|annual total',case=False,regex=True)
d['provider']=d.institutionGroup
d['recipient_location']=d.country
d['instrument']=d.mechanism.astype(str).str.strip().str.title()
d['instrument_group']=np.select([d.instrument.eq('Loan'),d.instrument.eq('Guarantee')],['Loan','Guarantee'],default='Other or mixed')
d['exclusion_reason']=''
conditions=[(~d.institutionKind.eq('Export Credit'),'Not export credit'),(~d.FY.between(2013,2022),'Outside FY2013-2022'),(d.stage.eq('Electric Vehicles'),'Electric vehicles'),(d.sector.eq('Climate'),'Non-energy climate'),(d.stage.eq('Petrochemical'),'Petrochemical'),(d.institutionAbbr.isin(['BNDES','JICA']),'Development finance institution')]
flow=[]
mask=pd.Series(True,index=d.index)
flow.append({'step':'All visible entries','rows':int(mask.sum()),'nominal_usd':float(d.loc[mask,'nominal_usd'].sum())})
for cond,label in conditions:
 removed=mask&cond;d.loc[removed,'exclusion_reason']=label;mask&=~cond
 flow.append({'step':'After '+label,'rows':int(mask.sum()),'removed_rows':int(removed.sum()),'removed_nominal_usd':float(d.loc[removed,'nominal_usd'].sum()),'nominal_usd':float(d.loc[mask,'nominal_usd'].sum())})
d['main_sample']=mask
cpi_raw=pd.read_excel(SRC/'data/240918 IMF IFS - US CPI.xlsx',header=None)
cpi={int(cpi_raw.iloc[1,j]):float(cpi_raw.iloc[2,j])/float(cpi_raw.iloc[2,21]) for j in range(2,25)}
assert abs(cpi[2020]-1)<1e-12
assert max(abs(cpi[int(cpi_raw.iloc[1,j])]-float(cpi_raw.iloc[8,j])) for j in range(2,25))<1e-12
d['cpi_fy_2020']=d.FY.map(cpi).astype(float)
d['real2020_usd_once']=d.nominal_usd/d.cpi_fy_2020
# Published broad energy definitions. Grid has precedence to avoid overlap in extension.
d['published_ff']=d.category.eq('Fossil Fuel') & ~d.stage.eq('Transmission & Distribution')
d['published_re']=(d.category.eq('Clean')|d.sector.isin(['Hydro - Large','Hydro - Small','Hydro - large','Biomass','Biofuels','Renewables - Other'])) & ~d.sector.isin(['Climate','Fuel Cells + Hydrogen','Batteries']) & ~d.stage.eq('Transmission & Distribution')
d['published_grid']=d.sector.eq('Batteries')|d.stage.eq('Transmission & Distribution')
d['technology_group']=np.select([d.published_grid,d.published_ff,d.published_re],['Grid','Fossil','Renewable'],default='Other')
m=d[d.main_sample].copy();e=d[d.institutionKind.eq('Export Credit')].copy()
d.to_csv(OUT/'clean_all_entries_with_flags.csv',index=False)
m.to_csv(OUT/'clean_eca_main.csv',index=False)
pd.DataFrame(flow).to_csv(OUT/'sample_flow.csv',index=False)
pd.DataFrame({'year':list(cpi),'cpi_relative_2020':list(cpi.values())}).to_csv(OUT/'cpi_validated.csv',index=False)
for label,keys in [('annual',['FY']),('provider',['provider']),('annual_technology',['FY','technology_group']),('annual_instrument',['FY','instrument_group'])]:
 a=m.groupby(keys,dropna=False).agg(rows=('source_excel_row','size'),nominal_usd=('nominal_usd','sum'),real2020_usd_once=('real2020_usd_once','sum'),unallocable_rows=('recipient_unallocable','sum'),aggregate_named_rows=('aggregate_name_flag','sum'),duplicate_subsequent_rows=('exact_duplicate_subsequent','sum'),missing_usd_rows=('nominal_usd',lambda x: x.isna().sum())).reset_index()
 a.to_csv(OUT/(label+'_coverage.csv'),index=False)
assert abs(m.groupby('technology_group').nominal_usd.sum().sum()-m.nominal_usd.sum())<.01
checks=[]
for name,q in [('All ECA',e),('Main ECA',m),('Main drop subsequent exact copies',m[~m.exact_duplicate_subsequent]),('Main unknown recipient',m[m.recipient_unallocable]),('Main aggregate named',m[m.aggregate_name_flag])]:
 checks.append({'sample':name,'rows':len(q),'nominal_original_usd':q.nominal_original_usd.sum(),'nominal_usd_source_fx_sensitivity':q.nominal_usd_source_fx_sensitivity.sum(),'real2020_usd_once':q.real2020_usd_once.sum(),'exact_duplicate_subsequent_rows':int(q.exact_duplicate_subsequent.sum()),'unallocable_rows':int(q.recipient_unallocable.sum()),'missing_usd_rows':int(q.nominal_usd.isna().sum())})
pd.DataFrame(checks).to_csv(OUT/'coverage_reconciliation.csv',index=False)
e[e.amount_repaired_from_source_fx].to_csv(OUT/'missing_amount_source_repair.csv',index=False)
e[e.exact_duplicate_group].to_csv(OUT/'exact_duplicate_groups.csv',index=False)
e[e.fx_difference_usd.abs()>np.maximum(.01,e.nominal_original_usd.abs()*1e-6)].to_csv(OUT/'fx_reconciliation_exceptions.csv',index=False)
# Diagnostic emulation of deposited Element3 + Element5 SI Fig1, not extension convention.
p=d[d.institutionKind.eq('Export Credit') & ~d.stage.isin(['Electric Vehicles','Petrochemical']) & ~d.sector.eq('Climate') & ~d.approval_year.eq(2012) & ~d.institutionAbbr.isin(['BNDES','JICA'])].copy()
p['stata_id']=np.arange(len(p))+1
p['v_nominal_code']=p.nominal_original_usd
p.loc[p.stata_id.eq(2346),'v_nominal_code']=500000*.71309
factor=p.approval_year.map(cpi).astype(float).where(p.approval_year.between(2013,2022),1)
p['once_code']=p.v_nominal_code/factor
p['twice_code']=p.v_nominal_code/factor**2
# v_bn is created before second row-index correction at id2280, so SI totals use preceding value.
p.loc[p.stata_id.isin([386,619]),'published_grid']=False
pub=pd.read_excel(SRC/'SourceData_SupplementaryFigures.xlsx',sheet_name='SI_Fig_1',header=None)
records=[]
for row in range(2,13):
 year=pub.iloc[row,0]
 if not isinstance(year,(int,float)) or pd.isna(year):continue
 for j,typ in enumerate(['ff','re','grid'],start=1):
  q=p[p.approval_year.eq(int(year)) & ~p.provider.eq('Canada') & p['published_'+typ]]
  val=float(pub.iloc[row,j]);records.append({'year':int(year),'energy':typ,'published_usd2020_bn':val,'reconstructed_nominal_bn':q.v_nominal_code.sum()/1e9,'reconstructed_once_bn':q.once_code.sum()/1e9,'reconstructed_deposited_twice_bn':q.twice_code.sum()/1e9,'twice_minus_published_bn':q.twice_code.sum()/1e9-val})
comparison=pd.DataFrame(records);comparison.to_csv(OUT/'published_si_fig1_reconstruction.csv',index=False)
manifest={'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'source_rows':len(raw),'visible_rows':len(d),'source_columns':cols,'nonempty_source_columns':[c for c in cols if raw[c].notna().any()],'main_rows':len(m),'eca_raw_rows':len(e),'eca_duplicate_subsequent':int(e.exact_duplicate_subsequent.sum()),'main_duplicate_subsequent':int(m.exact_duplicate_subsequent.sum()),'eca_unknown_recipient':int(e.recipient_unallocable.sum()),'main_unknown_recipient':int(m.recipient_unallocable.sum()),'main_approval_fy_mismatch_rows':int(m.approval_year.ne(m.FY).sum()),'main_nonpositive_amount_rows':int(m.nominal_usd.le(0).sum()),'published_si_max_abs_twice_gap_bn':comparison.twice_minus_published_bn.abs().max(),'currency_definition':'USD nominal original; once-deflated derived using source IMF US CPI rebased to 2020 and FY','source_repository':'https://zenodo.org/records/14261240','source_article':'https://doi.org/10.1038/s41467-025-55981-0','source_workbook_user_guide_license':'CC BY-NC 4.0; package metadata CC BY-NC-SA 4.0, unresolved'}
(OUT/'audit_manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2));print(pd.DataFrame(checks).to_string(index=False));print(comparison.to_string(index=False))
