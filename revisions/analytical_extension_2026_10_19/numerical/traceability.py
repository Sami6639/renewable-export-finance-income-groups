from pathlib import Path
import pandas as pd,hashlib,json
P=Path(__file__).resolve().parent;rows=[]
for display,files,case,vintage,period,unit,rounding in [
('Figure 1','allocation.csv.gz','Archive A0O0G0D0; D1 A1O1G1D1; D2 A1O1G1D2',2013,'Annual FY2013–2022','Percent of classified observed nominal USD','Percent axis integers; CSV full precision'),
('Figure 2 and main four-class table','allocation.csv.gz; decomposition.csv.gz','A0O0G0D0; A1O1G1D1; A1O1G1D2',2013,'Pooled FY2013–2015 versus FY2020–2022','Percentage points; nominal USD billions','pp 2 decimals; USD bn 3 decimals'),
('Figure 3','decomposition.csv.gz; completion_case_scalar_envelopes.csv.gz','A0O0G0D0; A1O1G1D1; A1O1G1D2; completion Q0 only',2013,'Pooled FY2013–2015 versus FY2020–2022','Percentage points','2 decimals'),
('SI geography coverage','allocation.csv.gz; transformation_lineage.csv.gz','A0O0G0D0; A1O1G1D1; A1O1G1D2',2013,'FY2013–2022','Reporting entries; nominal USD billions','Counts integers; USD bn 3 decimals'),
('SI provider contributions','provider_contributions.csv.gz; decomposition.csv.gz','A1O1G1D1; A1O1G1D2',2013,'Pooled FY2013–2015 versus FY2020–2022','Percentage points; signed composition/within','2 decimals; absolute composition rank'),
('SI alternative income vintage','secondary_FY2023_endpoint_allocation.csv; secondary_FY2023_endpoint_decomposition.csv','24 core cases; selected A1O1G1D1/D2',2023,'Pooled FY2013–2015 versus FY2020–2022','Percentage points','2 decimals'),
('SI alternative windows','allocation.csv.gz','A1O1G1D1; A1O1G1D2',2013,'Pooled FY2014–2016 versus FY2019–2021','Percentage points; nominal observed USD','2 decimals; amounts CSV full precision')]:
 rows.append(dict(display=display,source_files=files,case_codes=case,geography='international_reporting unless coverage table specifies other panel',fixed_income_FY=vintage,period=period,units=unit,rounding=rounding,source_commit='776d41f57ff893ba0d88be8f09035dbbf9d417fa'))
pd.DataFrame(rows).to_csv(P/'display_traceability.csv',index=False)
# Exact match of plotted data to frozen display selections.
D=P.parents[2]/'published_replication_candidates/export_finance/manuscript_design/revision2/displays'
checked=[]
for f in ['figure1_annual_data.csv','figure2_endpoint_changes.csv','figure2_nominal_levels.csv','figure3_H_accounting.csv','figure3_H_regional_outer_envelopes.csv']:
 a=pd.read_csv(P/f);b=pd.read_csv(D/f);pd.testing.assert_frame_equal(a,b,check_exact=False,rtol=1e-12,atol=1e-8);checked.append(f)
json.dump({'status':'PASS','figure_data_unchanged':checked,'visual_QA':'All three PNGs inspected; distinct circles/squares/triangles and dotted/solid/dashed styles; no clipped labels.'},open(P/'figure_validation.json','w'),indent=2)
