"""Frozen descriptive evidence assembly; no fitting, recoding, or new sample selection."""
from pathlib import Path
import hashlib,json,shutil,os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-evidence")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/evidence-cache")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent; E=O.parent.parent/'extension'
D=pd.read_csv(E/'clean_eca_income_mapped.csv')
P={'Canada':'CAN','United States':'USA','Japan':'JPN','United Kingdom':'GBR','Korea':'KOR','Germany':'DEU','China':'CHN','Australia':'AUS','Italy':'ITA','Mexico':'MEX','India':'IND','France':'FRA','Russia':'RUS','South Africa':'ZAF','Indonesia':'IDN','Turkey':'TUR'}
assert D.provider.map(P).notna().all()
D=D[D.recipient_iso3.notna() & D.recipient_iso3.ne(D.provider.map(P))].copy()
classes=['H','UM','LM','L','Unclassified']; rows=[]; coverage=[]
for scenario in ['Archive','Quarantine']:
 d=D if scenario=='Archive' else D[~D.source_excel_row.isin([7410,8034,8413])]
 for tech in ['Renewable','Fossil']:
  t=d[d.technology_group.eq(tech)]
  for period,years in [(str(y),[y]) for y in range(2013,2023)]+[('early',[2013,2014,2015]),('late',[2020,2021,2022])]:
   a=t[t.FY.isin(years)]; known=a.income_FY2013.isin(classes[:4])
   for basis,col in [('Nominal USD','nominal_usd'),('Once-deflated 2020 USD','real2020_usd_once')]:
    v=a[col].sum(); k=a.loc[known,col].sum(); h=a.loc[a.income_FY2013.eq('H'),col].sum(); u=a.loc[~known,col].sum()
    meta=dict(scenario=scenario,technology=tech,period=period,fixed_income_FY=2013,monetary_basis=basis)
    cv=meta|dict(observed_usd=v,classified_usd=k,high_usd=h,non_high_usd=k-h,unclassified_usd=u,entries=len(a),classified_entries=int(known.sum()),missing_amount_entries=int(a[col].isna().sum()),amount_income_coverage=k/v if v else np.nan,entry_income_coverage=known.mean() if len(a) else np.nan,high_share_classified=h/k if k else np.nan)
    coverage.append(cv)
    for cl in classes:
     b=a.loc[a.income_FY2013.eq(cl)] if cl!='Unclassified' else a.loc[~known]
     amount=b[col].sum()
     rows.append(meta|dict(income_class=cl,amount_usd=amount,entries=len(b),missing_amount_entries=int(b[col].isna().sum()),observed_usd_denominator=v,classified_usd_denominator=k,all_entries_denominator=len(a),classified_entries_denominator=int(known.sum()),amount_share_observed=amount/v if v else np.nan,amount_share_classified=amount/k if k and cl!='Unclassified' else np.nan,entry_share_all=len(b)/len(a) if len(a) else np.nan,entry_share_classified=len(b)/known.sum() if known.sum() and cl!='Unclassified' else np.nan))
R=pd.DataFrame(rows); C=pd.DataFrame(coverage)
R.to_csv(O/'income_class_annual_and_windows.csv',index=False); C.to_csv(O/'annual_and_window_coverage.csv',index=False)
# Exact agreement of pooled nominal results with independently audited endpoints.
for scenario,fn in [('Archive','provider_only_endpoints.csv'),('Quarantine','provider_only_quarantine_endpoints.csv')]:
 old=pd.read_csv(E/fn);old=old[old.geography.eq('Known international') & old.technology.isin(['Renewable','Fossil'])]
 new=C[C.scenario.eq(scenario)&C.monetary_basis.eq('Nominal USD')&C.period.isin(['early','late'])]
 j=new.merge(old,left_on=['technology','period'],right_on=['technology','window'],validate='one_to_one')
 for a,b in [('observed_usd','observed_weight'),('classified_usd','allocable_weight'),('high_usd','high_weight'),('high_share_classified','high_share')]:assert np.allclose(j[a],j[b],rtol=1e-12,atol=1e-5)
# Four main tables: existing audited quantities only, apart from complete class detail in SI.
T1=pd.read_csv(E/'full_technology_geography_coverage.csv');T1=T1[T1.unit.eq('Nominal USD')]
T1.to_csv(O/'table1_data_coverage.csv',index=False)
T2=pd.read_csv(E/'full_technology_geography_changes.csv');T2=T2[T2.unit.eq('Nominal USD')];T2.to_csv(O/'table2_allocation_comparators.csv',index=False)
T3=pd.concat([pd.read_csv(E/f).assign(scenario=s) for s,f in [('Archive','provider_only_decomposition.csv'),('Quarantine','provider_only_quarantine_decomposition.csv')]],ignore_index=True)
T3=T3[T3.technology.eq('Renewable')&T3.geography.eq('Known international')];T3.to_csv(O/'table3_provider_country_scenarios.csv',index=False)
T4=C[C.technology.eq('Renewable')&C.period.isin(['early','late'])&C.monetary_basis.eq('Nominal USD')];T4.to_csv(O/'table4_source_scenario_endpoints.csv',index=False)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
colors={'H':'#235789','UM':'#53A6A6','LM':'#E4B363','L':'#A85563','Unclassified':'#AAAAAA'}
def save(fig,n):
 fig.savefig(O/(n+'.png'),dpi=250,bbox_inches='tight');fig.savefig(O/(n+'.pdf'),bbox_inches='tight');plt.close(fig)
# Figure 1: complete annual numerator and denominator, four classes, two technologies.
fig,axs=plt.subplots(2,2,figsize=(11,7),sharex=True)
for j,tech in enumerate(['Renewable','Fossil']):
 a=R[R.scenario.eq('Archive')&R.technology.eq(tech)&R.monetary_basis.eq('Nominal USD')&~R.period.isin(['early','late'])].copy();a['year']=a.period.astype(int)
 p=a.pivot(index='year',columns='income_class',values='amount_usd').reindex(columns=classes)
 axs[0,j].stackplot(p.index,*[p[c]/1e9 for c in classes],colors=[colors[c] for c in classes],labels=classes,alpha=.9)
 axs[0,j].set(title=tech,ylabel='Recorded value (nominal USD bn)')
 c=C[C.scenario.eq('Archive')&C.technology.eq(tech)&C.monetary_basis.eq('Nominal USD')&~C.period.isin(['early','late'])].copy();years=c.period.astype(int)
 axs[1,j].plot(years,100*c.high_share_classified,'o-',color=colors['H'],label='Archive')
 q=C[C.scenario.eq('Quarantine')&C.technology.eq(tech)&C.monetary_basis.eq('Nominal USD')&~C.period.isin(['early','late'])]
 axs[1,j].plot(years,100*q.high_share_classified,'s--',color='#A85563',label='Three-row quarantine')
 axs[1,j].set(ylabel='High-income share (%)',xlabel='Fiscal year',ylim=(0,100),xticks=range(2013,2023));axs[1,j].tick_params(axis='x',rotation=45)
axs[0,0].legend(ncol=5,fontsize=8,loc='upper left');axs[1,0].legend(fontsize=8);fig.tight_layout();save(fig,'figure1_annual_allocation')
# Figure 2: complete technology/geography comparison.
fig,ax=plt.subplots(figsize=(9,5));techs=['All','Fossil','Renewable','Grid','Other']; geos=['All locations','Known international','Domestic']
for i,g in enumerate(geos):
 a=T2[T2.geography.eq(g)].set_index('technology').reindex(techs)
 ax.barh(np.arange(5)+(i-1)*.24,a.delta_share_known*100,height=.22,label=g)
ax.axvline(0,color='black',lw=.7);ax.set(yticks=range(5),yticklabels=['All energy']+techs[1:],xlabel='Change in high-income share (percentage points)');ax.legend(fontsize=9);ax.text(.99,.02,'Other/domestic: undefined (no early allocable value)',transform=ax.transAxes,ha='right',fontsize=8);fig.tight_layout();save(fig,'figure2_complete_comparators')
# Figure 3: already audited provider-only identity.
fig,ax=plt.subplots(figsize=(8,4.8));terms=['composition','within','entry','exit'];names=['Composition','Within provider country','Provider entry','Provider exit']
for i,s in enumerate(['Archive','Quarantine']):
 r=T3[T3.scenario.eq(s)].iloc[0];vals=[r[t]*100 for t in terms];bars=ax.bar(np.arange(4)+(i-.5)*.34,vals,width=.33,label=s,color=['#235789','#A85563'][i]);ax.bar_label(bars,fmt='%.2f',padding=3,fontsize=9)
ax.set(xticks=range(4),xticklabels=names,ylabel='Contribution (percentage points)',ylim=(-1,30));ax.legend();fig.tight_layout();save(fig,'figure3_provider_accounting')
# Figure 4: equal visibility to both source scenarios, levels and shares.
fig,axs=plt.subplots(1,2,figsize=(9,4.8)); labels=['Early\narchive','Late\narchive','Late\nquarantine'];sel=pd.concat([T4[(T4.scenario=='Archive')&(T4.period=='early')],T4[(T4.scenario=='Archive')&(T4.period=='late')],T4[(T4.scenario=='Quarantine')&(T4.period=='late')]])
x=np.arange(3);axs[0].bar(x,sel.high_usd/1e9,label='High income',color=colors['H']);axs[0].bar(x,sel.non_high_usd/1e9,bottom=sel.high_usd/1e9,label='Non-high-income',color=colors['UM']);axs[0].set(ylabel='Recorded value (nominal USD bn)',xticks=x,xticklabels=labels);axs[0].legend(fontsize=8)
b=axs[1].bar(x,100*sel.high_share_classified,color=['#235789','#235789','#A85563']);axs[1].bar_label(b,fmt='%.2f%%',padding=3);axs[1].set(ylabel='High-income share (%)',xticks=x,xticklabels=labels,ylim=(0,60));fig.tight_layout();save(fig,'figure4_source_scenarios')
# SI nominal and real full four-class paths; counts and coverage remain in complete CSVs.
for basis,slug in [('Nominal USD','nominal'),('Once-deflated 2020 USD','real2020')]:
 fig,axs=plt.subplots(2,2,figsize=(11,7),sharex=True)
 for i,s in enumerate(['Archive','Quarantine']):
  for j,t in enumerate(['Renewable','Fossil']):
   a=R[R.scenario.eq(s)&R.technology.eq(t)&R.monetary_basis.eq(basis)&~R.period.isin(['early','late'])].copy();a['year']=a.period.astype(int);p=a.pivot(index='year',columns='income_class',values='amount_usd').reindex(columns=classes)
   axs[i,j].stackplot(p.index,*[p[c]/1e9 for c in classes],colors=[colors[c] for c in classes],labels=classes);axs[i,j].set(title=f'{t}: {s}',ylabel=f'{basis} bn',xlabel='Fiscal year',xticks=range(2013,2023));axs[i,j].tick_params(axis='x',rotation=45)
 handles,labels=axs[0,0].get_legend_handles_labels();fig.legend(handles,labels,ncol=5,fontsize=9,loc='upper center',bbox_to_anchor=(.5,1.02));fig.tight_layout();save(fig,'si_full_income_path_'+slug)
# Machine-readable ledger: numbers carry their exact source, units and denominators.
ledger={'status':'Independent annual/class arithmetic audit passed; economic principal and physical-host interpretations not cleared: 10096 numeric checks, 480 class rows, 96 coverage rows, 56 prior endpoint cells; see independent_audit/annual_income_audit.json','scope':'Recorded known-international recipient-country allocation; fixed FY2013; source-described heterogeneous values','units':{'shares':'fractions, multiply by 100 for percent','accounting':'fractions, multiply by 100 for percentage points','amounts':'USD, monetary_basis column governs'},'source_hashes':{f:hashlib.sha256((E/f).read_bytes()).hexdigest() for f in ['clean_eca_income_mapped.csv','provider_only_decomposition.csv','provider_only_quarantine_decomposition.csv','full_technology_geography_changes.csv']},'renewable_endpoints':T4.to_dict('records'),'renewable_provider_accounting':T3.to_dict('records'),'all_technology_comparators':json.loads(T2.to_json(orient='records')),'complete_grid_files':['income_class_annual_and_windows.csv','annual_and_window_coverage.csv'],'quarantined_excel_rows':[7410,8034,8413],'quarantined_nominal_usd':4579950000}
(O/'values_ledger.json').write_text(json.dumps(ledger,indent=2,allow_nan=False))
print('Saved',len(R),'class rows;',len(C),'coverage rows. Endpoint reconciliation passed.')
