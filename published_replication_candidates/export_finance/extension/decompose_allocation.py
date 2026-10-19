"""Prespecified gate-two exact accounting, no estimation or model selection."""
from pathlib import Path
import pandas as pd,numpy as np,json
O=Path(__file__).resolve().parent
d=pd.read_csv(O/'clean_eca_income_mapped.csv')
d['window']=np.select([d.FY.between(2013,2015),d.FY.between(2020,2022)],['early','late'],default='excluded')
d=d[d.window.ne('excluded')].copy()
# Provider joins remain separate from recipient joins.
providers={'Canada':'CAN','United States':'USA','Japan':'JPN','United Kingdom':'GBR','Korea':'KOR','Germany':'DEU','China':'CHN','Australia':'AUS','Italy':'ITA','Mexico':'MEX','India':'IND','France':'FRA','Russia':'RUS','South Africa':'ZAF','Indonesia':'IDN','Turkey':'TUR'}
d['provider_iso3']=d.provider.map(providers);assert d.provider_iso3.notna().all()
d['domestic']=d.recipient_iso3.eq(d.provider_iso3)&d.recipient_iso3.notna()
d['international_known']=d.recipient_iso3.ne(d.provider_iso3)&d.recipient_iso3.notna()
d['portfolio']=np.select([d.aggregate_name_flag,d.instrument.eq('Loan'),d.instrument.eq('Guarantee')],['Aggregate residual','Loan','Guarantee'],default='Other instrument')
d['entry_count']=1.0
d['real2020_source_fx_sensitivity']=d.nominal_usd_source_fx_sensitivity/d.cpi_fy_2020
# Count-based support includes zero or missing-amount entries. Dollar support requires positive amount.
variants=[('primary_nominal',2013,'nominal_usd','all'),('fixed_FY2023',2023,'nominal_usd','all'),('once_deflated',2013,'real2020_usd_once','all'),('drop_exact_copies',2013,'nominal_usd','dedup'),('entry_counts',2013,'entry_count','all'),('international_known',2013,'nominal_usd','international'),('domestic',2013,'nominal_usd','domestic'),('leave_largest_entry_each_window',2013,'nominal_usd','largest'),('documented_source_fx',2013,'nominal_usd_source_fx_sensitivity','all')]
d.loc[d.groupby('window').nominal_usd.idxmax(),['source_excel_row','window','FY','provider','project','nominal_usd','aggregate_name_flag','income_FY2013']].to_csv(O/'largest_entry_sensitivity_exclusions.csv',index=False)
rows=[];summaries=[];cell_outputs=[]
for name,fy,amount,restriction in variants:
 x=d.copy()
 if restriction=='dedup':x=x[~x.exact_duplicate_subsequent]
 if restriction=='international':x=x[x.international_known]
 if restriction=='domestic':x=x[x.domestic]
 if restriction=='largest':x=x.drop(x.groupby('window')[amount].idxmax())
 x['weight']=x[amount]
 x['income_known']=x[f'income_FY{fy}'].isin(['L','LM','UM','H'])
 x['is_high']=x[f'income_FY{fy}'].eq('H')
 for portfolio in ['All','Loan','Guarantee','Other instrument','Aggregate residual']:
  q=x if portfolio=='All' else x[x.portfolio.eq(portfolio)]
  sums={}
  for window in ['early','late']:
   a=q[q.window.eq(window)]
   total=a.weight.sum();known=a.loc[a.income_known,'weight'].sum();hi=a.loc[a.is_high,'weight'].sum();unk=a.loc[~a.income_known,'weight'].sum()
   sums[window]={'total':total,'known':known,'hi':hi,'unknown':unk}
   summaries.append({'variant':name,'fixed_income_FY':fy,'portfolio':portfolio,'window':window,'units':'entries' if amount=='entry_count' else 'USD2020' if 'real2020' in amount else 'USD nominal','entries':len(a),'observed_weight':total,'allocable_weight':known,'high_income_weight':hi,'unknown_income_weight':unk,'missing_source_usd_entries':int(a.nominal_usd.isna().sum()),'high_share_allocable':hi/known if known else np.nan,'high_lower_known_amount_bound':hi/total if total else np.nan,'high_upper_known_amount_bound':(hi+unk)/total if total else np.nan,'unknown_income_weight_share':unk/total if total else np.nan})
  if sums['early']['known']<=0 or sums['late']['known']<=0:continue
  a=q[q.income_known & q.weight.gt(0)].copy();a['hi_weight']=a.weight*a.is_high
  keys=['provider','technology_group','portfolio']
  c=a.groupby(keys+['window']).agg(weight=('weight','sum'),hi=('hi_weight','sum')).reset_index()
  early=c[c.window.eq('early')].drop(columns='window').set_index(keys);late=c[c.window.eq('late')].drop(columns='window').set_index(keys)
  cc=early.join(late,lsuffix='_early',rsuffix='_late',how='outer')
  cc['support']=np.select([cc.weight_early.notna()&cc.weight_late.notna(),cc.weight_early.isna()],['common','entry'],default='exit')
  for win in ['early','late']:
   cc['w_'+win]=cc['weight_'+win].fillna(0)/sums[win]['known'];cc['h_'+win]=cc['hi_'+win]/cc['weight_'+win]
  common=cc.support.eq('common')
  cc['composition']=0.;cc['within']=0.;cc['entry']=0.;cc['exit']=0.
  cc.loc[common,'composition']=(cc.loc[common,'h_early']+cc.loc[common,'h_late'])/2*(cc.loc[common,'w_late']-cc.loc[common,'w_early'])
  cc.loc[common,'within']=(cc.loc[common,'w_early']+cc.loc[common,'w_late'])/2*(cc.loc[common,'h_late']-cc.loc[common,'h_early'])
  cc.loc[cc.support.eq('entry'),'entry']=cc.w_late*cc.h_late
  cc.loc[cc.support.eq('exit'),'exit']=-cc.w_early*cc.h_early
  delta=sums['late']['hi']/sums['late']['known']-sums['early']['hi']/sums['early']['known']
  terms=cc[['composition','within','entry','exit']].sum()
  residual=delta-terms.sum();assert abs(residual)<1e-12
  rows.append({'variant':name,'portfolio':portfolio,'delta_high_share':delta,**terms.to_dict(),'closure_residual':residual,'common_cells':int(common.sum()),'entry_cells':int(cc.support.eq('entry').sum()),'exit_cells':int(cc.support.eq('exit').sum()),'common_allocable_share_early':cc.loc[common,'w_early'].sum(),'common_allocable_share_late':cc.loc[common,'w_late'].sum()})
  cc=cc.reset_index();cc['variant']=name;cc['analysis_portfolio']=portfolio;cell_outputs.append(cc)
pd.DataFrame(summaries).to_csv(O/'allocation_coverage_bounds.csv',index=False)
pd.DataFrame(rows).to_csv(O/'allocation_decomposition.csv',index=False)
pd.concat(cell_outputs,ignore_index=True).to_csv(O/'allocation_cell_accounting.csv',index=False)
# All observed-volume endpoint bounds imply exact change bounds; unknown missing dollar volumes remain unbounded.
b=pd.DataFrame(summaries);bb=[]
for (var,port),g in b.groupby(['variant','portfolio']):
 e=g[g.window.eq('early')].iloc[0];l=g[g.window.eq('late')].iloc[0]
 bb.append({'variant':var,'portfolio':port,'delta_high_share_lower_known_amount_bound':l.high_lower_known_amount_bound-e.high_upper_known_amount_bound,'delta_high_share_upper_known_amount_bound':l.high_upper_known_amount_bound-e.high_lower_known_amount_bound,'missing_amount_entries_in_windows':e.missing_source_usd_entries+l.missing_source_usd_entries,'bound_scope':'Observed reported amounts only; missing source amount has no finite volume bound, except documented FX sensitivity or entry counts'})
pd.DataFrame(bb).to_csv(O/'allocation_change_bounds.csv',index=False)
print(pd.DataFrame(rows).query("variant=='primary_nominal'").to_string(index=False));print(b.query("variant=='primary_nominal'").to_string(index=False));print(pd.DataFrame(rows).query("portfolio=='All'").to_string(index=False))
