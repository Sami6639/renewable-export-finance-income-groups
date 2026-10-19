from pathlib import Path
import pandas as pd, numpy as np,json,hashlib
O=Path(__file__).resolve().parent
H=O.parents[2]/'renewable_finance_recovery/financial_transition_panel/raw/income_history.xlsx'
h=pd.read_excel(H,sheet_name='Country Analytical History',header=None)
assert h.iloc[4,26]=='FY13' and h.iloc[5,26]==2011
assert h.iloc[4,36]=='FY23' and h.iloc[5,36]==2021
hist=h.iloc[6:,[0,1,26,36]].copy();hist.columns=['iso3','wb_name','income_FY2013','income_FY2023'];hist=hist[hist.iso3.notna()];hist.wb_name=hist.wb_name.str.strip()
for c in ['income_FY2013','income_FY2023']:hist[c]=hist[c].where(hist[c].isin(['L','LM','UM','H']))
d=pd.read_csv(O/'clean_eca_main.csv')
alias={'Bahamas':'BHS','Congo,the Democratic Republic of the':'COD',"Cote d'Ivoire":'CIV','Czech Republic':'CZE','Egypt':'EGY','Hong Kong':'HKG','Iran':'IRN','Kyrgyzstan':'KGZ',"Lao People's Democratic Republic":'LAO','Micronesia,Federated States of':'FSM','Occupied Palestinian Territories':'PSE','Russia':'RUS','Slovakia':'SVK','South Korea':'KOR','Taiwan':'TWN','Turkey':'TUR','Venezuela':'VEN','Yemen':'YEM'}
lookup=hist.set_index('wb_name').iso3.to_dict()
lookup.update(alias)
locations=d[['country','CC','recipient_unallocable']].drop_duplicates().copy()
locations['recipient_iso3']=locations.country.str.strip().map(lookup).where(~locations.recipient_unallocable)
locations['mapping_method']=locations.country.str.strip().map(lambda x:'Explicit name alias' if x in alias else 'Exact WB country name')
locations.loc[locations.recipient_unallocable,'mapping_method']='Unallocable geography'
locations=locations.merge(hist,left_on='recipient_iso3',right_on='iso3',how='left',validate='many_to_one').drop(columns='iso3')
iso=pd.read_excel(O.parent/'package/CenskowskyEtAl_ECA_ReplicationPackage/data/240801 ISO3-ISO2-codes.xlsx',sheet_name='iso3iso2',keep_default_na=False)
iso_lookup=iso.set_index('Alpha-2 code')['Alpha-3 code'].to_dict();iso_lookup['UK']='GBR';iso_lookup['XK']='XKX'
locations['iso3_from_raw_CC']=locations.CC.map(iso_lookup).where(locations.CC.notna() & locations.CC.ne(''))
locations['raw_CC_name_conflict']=locations.recipient_iso3.notna()&locations.iso3_from_raw_CC.notna()&locations.recipient_iso3.ne(locations.iso3_from_raw_CC)
assert locations.loc[~locations.recipient_unallocable,'recipient_iso3'].notna().all()
locations.to_csv(O/'recipient_mapping_review.csv',index=False)
merged=d.merge(locations[['country','CC','recipient_iso3','income_FY2013','income_FY2023','raw_CC_name_conflict']],on=['country','CC'],how='left',validate='many_to_one')
# Resolve source-name/code conflicts by verified evidence, never automatic name precedence.
merged['recipient_iso3_name_candidate']=merged.recipient_iso3
merged['unresolved_geography_conflict']=merged.source_excel_row.isin([5377,9697])
merged.loc[merged.unresolved_geography_conflict,['recipient_iso3','income_FY2013','income_FY2023']]=np.nan
israel=hist[hist.iso3.eq('ISR')].iloc[0]
verified=merged.source_excel_row.eq(578)
assert verified.sum()==1
merged.loc[verified,'recipient_iso3']='ISR'
for fy in [2013,2023]:merged.loc[verified,f'income_FY{fy}']=israel[f'income_FY{fy}']
ledger=merged[merged.raw_CC_name_conflict][['source_excel_row','project','country','CC','recipient_iso3_name_candidate','recipient_iso3','income_FY2013','income_FY2023','unresolved_geography_conflict']].copy()
ledger['resolution_evidence']='Unresolved competing name/code location; retained unknown'
ledger.loc[ledger.source_excel_row.eq(578),'resolution_evidence']='Verified primary EXIM report identifies $44.8m guarantee for plant in Ramla, Israel: https://www.exim.gov/news/ex-im-bank-approves-45-million-finance-export-turbine-products-israel'
ledger.to_csv(O/'recipient_conflict_correction_ledger.csv',index=False)
for fy in [2013,2023]:merged[f'income_unknown_FY{fy}']=merged[f'income_FY{fy}'].isna();merged[f'known_geography_unclassified_FY{fy}']=~merged.recipient_unallocable & ~merged.unresolved_geography_conflict & merged[f'income_FY{fy}'].isna()
merged.to_csv(O/'clean_eca_income_mapped.csv',index=False)
metadata={'source':'https://ddh-openapi.worldbank.org/resources/DR0095334/download','source_sha256':hashlib.sha256(H.read_bytes()).hexdigest(),'worksheet':'Country Analytical History','principal_fixed_column':'AA = FY13 (2011 GNI); classification effective July2012–June2013','sensitivity_fixed_column':'AK = FY23 (2021 GNI); classification effective July2022–June2023','classification_use':'Each classification held fixed across all observation years; FY13 principal, FY23 sensitivity','unmapped_known_geography_labels':int(locations.loc[~locations.recipient_unallocable,'recipient_iso3'].isna().sum()),'raw_CC_name_conflict_entries':int(merged.raw_CC_name_conflict.sum()),'known_geography_unclassified_FY2013_entries':int(merged.known_geography_unclassified_FY2013.sum()),'known_geography_unclassified_FY2023_entries':int(merged.known_geography_unclassified_FY2023.sum()),'unresolved_geography_conflict_entries':int(merged.unresolved_geography_conflict.sum()),'verified_row578_israel_correction':True,'outcome_comparisons_run':False}
(O/'income_mapping_freeze.json').write_text(json.dumps(metadata,indent=2));print(json.dumps(metadata,indent=2));print(locations[locations.raw_CC_name_conflict].to_string(index=False));print(locations[(~locations.recipient_unallocable)&(locations.income_FY2013.isna()|locations.income_FY2023.isna())].to_string(index=False))
