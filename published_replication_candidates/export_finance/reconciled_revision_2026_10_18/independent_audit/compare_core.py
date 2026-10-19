from audit_outcomes import *
results=[]
for prefix in ['', 'arithmetic_quarantine_']:
 for name,keys,metrics in [('allocation',['scenario','geography','period','income_class'],['amount','classified_denominator','observed_denominator','unknown_amount','share_classified','share_observed','component_count','source_row_count','missing_amount_count']),('decomposition',['scenario','geography','pair','income_class'],T),('provider_contributions',['scenario','geography','pair','income_class','provider'],T[1:])]:
  f=prefix+name+'.csv'
  if (R/'outputs'/f).exists():results+=compare(name,keys,metrics,f)
pd.DataFrame(results).to_csv(O/'core_output_comparison.csv',index=False);print(pd.DataFrame(results).to_string(index=False))
# Compare historical published corners directly to independent four-class output.
x=pd.read_csv(O/'independent_decomposition.csv');hist=[]
for sid,file in [('A0O0G0D0','provider_only_decomposition.csv'),('A0O0G0D2','provider_only_quarantine_decomposition.csv')]:
 old=pd.read_csv(B/'extension'/file);old=old[old.variant.eq('primary_nominal')&old.technology.eq('Renewable')&old.fixed_income_FY.eq(2013)]
 for label,geo in [('All locations',G[0]),('Known international',G[1]),('Domestic',G[3])]:
  z=old[old.geography.eq(label)];new=x[x.scenario.eq(sid)&x.geography.eq(geo)&x.pair.eq('early_to_late')&x.income_class.eq('H')]
  if len(z):
   for om,nm in zip(['delta_high_share','composition','within','entry','exit'],T):
    e=abs(float(z.iloc[0][om])*100-float(new.iloc[0][nm]));assert e<1e-8,(sid,label,om,e);hist.append(dict(scenario=sid,geography=geo,metric=nm,error_pp=e))
pd.DataFrame(hist).to_csv(O/'historical_corner_comparison.csv',index=False);print('Historical original and D2 corners reproduced',len(hist))
