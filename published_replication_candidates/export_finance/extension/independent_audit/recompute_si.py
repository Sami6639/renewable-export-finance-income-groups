exec(open(__file__.replace('recompute_si.py','recompute.py')).read().split("r={'sha256'")[0])
x=d.copy();x['year']=x.date.astype(str).str.extract(r'(20\d{2})')[0].astype(int)
x=x[x.institutionKind.eq('Export Credit') & ~x.stage.isin(['Electric Vehicles','Petrochemical']) & x.sector.ne('Climate') & x.year.ne(2012) & ~x.institutionAbbr.isin(['BNDES','JICA'])].copy()
x['id']=range(1,len(x)+1);x['v']=x.amountUSD;x.loc[x.id.eq(2346),'v']=356545
x['deflator']=x.year.map(ratios);x.loc[x.year.eq(2023),'deflator']=1
x['re']=x.category.eq('Clean')|x.sector.isin(['Hydro - Large','Hydro - Small','Hydro - large','Biomass','Biofuels','Renewables - Other']);x.loc[x.sector.isin(['Climate','Fuel Cells + Hydrogen','Batteries'])|x.stage.eq('Transmission & Distribution'),'re']=False
x['ff']=x.category.eq('Fossil Fuel')&x.stage.ne('Transmission & Distribution')
x['grid']=x.sector.eq('Batteries')|x.stage.eq('Transmission & Distribution');x.loc[x.id.isin([386,619]),'grid']=False
pub=pd.read_excel(p.parent/'SourceData_SupplementaryFigures.xlsx',sheet_name='SI_Fig_1',header=None)
rows=[]
for year in range(2013,2024):
 for j,t in enumerate(['ff','re','grid'],1):
  z=x[x.year.eq(year)&x.institutionGroup.ne('Canada')&x[t]]; ref=pub.iloc[year-2011,j]
  rows.append({'year':year,'energy':t,'published':ref,'once':sum(z.v/z.deflator)/1e9,'twice':sum(z.v/z.deflator**2)/1e9})
b=pd.DataFrame(rows);b['delta']=b.twice-b.published;b.to_csv(pathlib.Path(__file__).with_name('si_recomputed.csv'),index=False)
y=pd.read_csv(base/'extension/published_si_fig1_reconstruction.csv');assert np.allclose(b.twice,y.reconstructed_deposited_twice_bn,rtol=1e-12,atol=1e-12)
print('33 SI cells independently agree, max residual vs archived source in USD:',abs(b.delta).max()*1e9)
