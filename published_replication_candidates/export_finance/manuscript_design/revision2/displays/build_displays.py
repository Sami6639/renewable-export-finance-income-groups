from pathlib import Path
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import json, hashlib
import argparse
parser=argparse.ArgumentParser(); parser.add_argument('--source-dir',type=Path,default=Path(__file__).resolve().parents[3]/'reconciled_revision_2026_10_18'); args=parser.parse_args()
P=args.source_dir; O=P/'outputs'; D=Path(__file__).resolve().parent
assert json.loads((P/'independent_audit/FINAL_INDEPENDENT_AUDIT.json').read_text())['status']=='PASS'
def read(f): return pd.read_csv(O/f,float_precision='round_trip')
C=['L','LM','UM','H']; S=['A0O0G0D0','A1O1G1D1','A1O1G1D2']; names=['Archive reference','Source-informed:\ncontract exclusion','Source-informed:\nwhole-block exclusion']; cols=['#72777c','#17618c','#ba642a']; styles=[':','-','--']; marks=['o','s','^']; panel='international_reporting'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#292e32','text.color':'#292e32','axes.titleweight':'bold','pdf.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white'})
ledger=[]
def savecsv(df,f,source,filters):
 df.to_csv(D/f,index=False);ledger.append({'file':f,'source':source,'filters':filters,'rows':len(df),'columns':' | '.join(df.columns)})
def finish(fig,name):
 fig.savefig(D/(name+'.png'),dpi=240,bbox_inches='tight');fig.savefig(D/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
a=read('allocation.csv'); q=read('arithmetic_quarantine_allocation.csv'); de=read('decomposition.csv'); co=read('completion_case_scalar_envelopes.csv')
ann=a[(a.geography==panel)&a.income_class.isin(C)&a.period.str.fullmatch(r'20\d\d')].copy()
savecsv(ann,'SI_annual_Q0_core24_agreement12.csv','allocation.csv','international_reporting; known four classes; all ten annual periods; families retained in case_set')
savecsv(q[(q.geography==panel)&q.income_class.isin(C)&q.period.str.fullmatch(r'20\d\d')],'SI_annual_Q1_core24.csv','arithmetic_quarantine_allocation.csv','international_reporting; known four classes; all ten annual periods; separate Q1 family')
fa=ann[ann.scenario.isin(S)].copy();savecsv(fa,'figure1_annual_data.csv','allocation.csv','international_reporting; scenarios '+','.join(S)+'; all ten annual periods; four classes')
fig,axs=plt.subplots(2,2,figsize=(10,7.2),sharex=True,sharey=True)
for ax,cl,tag in zip(axs.flat,C,['a','b','c','d']):
 for s,n,c,st,m in zip(S,names,cols,styles,marks):
  z=fa[(fa.scenario==s)&(fa.income_class==cl)].sort_values('period');ax.plot(z.period.astype(int),z.share_classified*100,color=c,ls=st,marker=m,ms=3.7,lw=1.65,label=n)
 ax.set_title(f'{tag}  '+{'L':'Low income','LM':'Lower-middle income','UM':'Upper-middle income','H':'High income'}[cl],loc='left',fontsize=11);ax.set_ylim(0,100);ax.set_xticks([2013,2015,2017,2019,2022]);ax.grid(axis='y',color='#e2e5e7',lw=.6)
for ax in axs[:,0]:ax.set_ylabel('Classified amount share (%)')
for ax in axs[-1,:]:ax.set_xlabel('Archive fiscal year')
fig.legend(*axs.flat[0].get_legend_handles_labels(),loc='upper center',ncol=3,frameon=False,bbox_to_anchor=(.5,1.015));fig.subplots_adjust(top=.92,hspace=.29,wspace=.14);finish(fig,'Figure_1_annual_allocation')
end=de[(de.geography==panel)&(de.pair=='early_to_late')&de.scenario.isin(S)].copy();levels=a[(a.geography==panel)&a.scenario.isin(S)&a.income_class.isin(C)&a.period.isin(['early','late'])].copy()
savecsv(end,'figure2_endpoint_changes.csv','decomposition.csv','international_reporting; early_to_late; three named cases; four classes')
savecsv(levels,'figure2_nominal_levels.csv','allocation.csv','international_reporting; early/late; three named cases; four classes')
fig,axs=plt.subplots(1,2,figsize=(11,5.4),sharey=True)
for k,(s,n,c,m) in enumerate(zip(S,names,cols,marks)):
 for j,cl in enumerate(C):
  yy=j+(k-1)*.20;z=end[(end.scenario==s)&(end.income_class==cl)].iloc[0];axs[0].scatter(z.delta_pp,yy,c=c,marker=m,s=45,zorder=3)
  axs[0].annotate(f'{z.delta_pp:+.2f}',(z.delta_pp,yy),xytext=(5 if z.delta_pp>=0 else -5,0),textcoords='offset points',ha='left' if z.delta_pp>=0 else 'right',va='center',fontsize=8.3)
  zz=levels[(levels.scenario==s)&(levels.income_class==cl)].set_index('period');early=zz.loc['early','amount']/1e9;late=zz.loc['late','amount']/1e9
  axs[1].plot([early,late],[yy,yy],color=c,lw=1.5);axs[1].scatter(early,yy,facecolors='white',edgecolors=c,marker=m,s=42,zorder=3);axs[1].scatter(late,yy,color=c,marker=m,s=42,zorder=3)
axs[0].set_yticks(range(4),['Low','Lower-middle','Upper-middle','High']);axs[0].invert_yaxis();axs[0].axvline(0,c='#6d7479',lw=.8);axs[0].set_xlim(-44,52);axs[0].set_xlabel('Classified share change (percentage points)');axs[0].set_title('a  Pooled endpoint changes',loc='left',fontsize=11)
axs[1].set_xlim(left=0);axs[1].set_xlabel('Pooled nominal recorded amount (USD billions)');axs[1].set_title('b  Early (open) and late (filled) amounts',loc='left',fontsize=11)
for ax in axs:ax.grid(axis='x',color='#e2e5e7',lw=.6);ax.set_axisbelow(True)
fig.legend([Line2D([],[],color=c,marker=m,ls='') for c,m in zip(cols,marks)],names,loc='upper center',ncol=3,frameon=False);fig.subplots_adjust(top=.85,bottom=.13,wspace=.14);finish(fig,'Figure_2_endpoint_changes_and_levels')
h=end[end.income_class=='H'].copy();reg=co[(co.panel==panel)&co.case_id.isin(S[1:])&(co.target_type=='decomposition')&(co.target=='early_to_late')&(co.income_class=='H')].copy()
savecsv(h,'figure3_H_accounting.csv','decomposition.csv','international_reporting; early_to_late; H; three named cases')
savecsv(reg,'figure3_H_regional_outer_envelopes.csv','completion_case_scalar_envelopes.csv','international_reporting; early_to_late decomposition; H; A1O1G1D1/D2; Q0 only')
fig,axs=plt.subplots(1,2,figsize=(11,5.3),gridspec_kw={'width_ratios':[1.5,1]})
terms=['delta_pp','composition_pp','within_pp','entry_pp','exit_pp']
for k,(s,n,c,m) in enumerate(zip(S,names,cols,marks)):
 z=h[h.scenario==s].iloc[0]
 for j,t in enumerate(terms):
  y=j+(k-1)*.2;axs[0].scatter(z[t],y,color=c,marker=m,s=45,zorder=3)
  if s in S[1:]:
   r=reg[(reg.case_id==s)&(reg.metric==t)].iloc[0];axs[0].plot([r.lower,r.upper],[y,y],color=c,lw=2.2)
axs[0].set_yticks(range(5),['Total change','Provider composition','Within-provider','Entry','Exit']);axs[0].invert_yaxis();axs[0].set_title('a  Additive accounting components',loc='left',fontsize=11)
for k,(s,c,m) in enumerate(zip(S[1:],cols[1:],marks[1:])):
 z=h[h.scenario==s].iloc[0];r=reg[(reg.case_id==s)&(reg.metric=='within_pp')].iloc[0]
 axs[1].plot([r.lower,r.upper],[k,k],color=c,lw=3);axs[1].scatter(z.within_pp,k,color=c,marker=m,s=60,zorder=4)
 axs[1].text(z.within_pp,k-.18,f'{z.within_pp:+.2f}',ha='center',fontsize=11,color=c)
 axs[1].text(-.35,k+.22,f'Outer envelope: {r.lower:+.2f} to {r.upper:+.2f}',ha='center',fontsize=9)
axs[1].set_yticks([0,1],['Contract\nexclusion','Whole-block\nexclusion']);axs[1].set_ylim(1.55,-.55);axs[1].set_xlim(-2.7,2);axs[1].set_title('b  Within-provider term, enlarged',loc='left',fontsize=11)
for ax in axs:ax.axvline(0,c='#6d7479',lw=.8);ax.grid(axis='x',color='#e2e5e7',lw=.6);ax.set_axisbelow(True);ax.set_xlabel('Percentage points')
fig.legend([Line2D([],[],color=c,marker=m,ls='') for c,m in zip(cols,marks)],names,loc='upper center',ncol=3,frameon=False);fig.subplots_adjust(top=.84,bottom=.13,wspace=.36);finish(fig,'Figure_3_H_provider_accounting')
# Three compact main tables. Values are selections or unit formatting of frozen outputs.
t1=levels[levels.income_class=='L'][['scenario','period','classified_denominator','observed_denominator','unknown_amount']].copy();savecsv(t1,'SI_scope_and_denominators.csv','allocation.csv','international_reporting; three named cases; early/late; denominator fields identical across classes')
env=read('scenario_envelopes.csv');qe=read('arithmetic_quarantine_envelopes.csv')
t2=pd.concat([env[(env.universe.isin(['core24','agreement12']))&(env.analysis=='decomposition')&(env.geography==panel)&(env.target=='early_to_late')&(env.outcome=='delta_pp')],qe[(qe.universe=='quarantine24')&(qe.analysis=='decomposition')&(qe.geography==panel)&(qe.target=='early_to_late')&(qe.outcome=='delta_pp')]],ignore_index=True)
savecsv(t2,'Table_2_separate_family_share_envelopes.csv','scenario_envelopes.csv; arithmetic_quarantine_envelopes.csv','international_reporting; endpoint delta_pp; separate core24/agreement12/quarantine24; four classes')
pkg=read('influence/package_influence_endpoint.csv.gz');rr=read('influence/record_influence_endpoint.csv.gz');rr.unit_id=rr.unit_id.astype(str)
t3=pd.concat([pkg[(pkg.scenario=='A1O1G1D1')&(pkg.panel==panel)&pkg.income_class.isin(['L','H'])],rr[(rr.scenario=='A1O1G1D1')&(rr.panel==panel)&(rr.unit_id=='8129')&rr.income_class.isin(['L','H'])]],ignore_index=True)
savecsv(t3,'Table_3_record_and_package_influence.csv','influence/package_influence_endpoint.csv.gz; influence/record_influence_endpoint.csv.gz','A1O1G1D1; international_reporting; three frozen packages plus Guinea record8129; L/H')
# Complete provenance-bearing supplements are data exports, not extra manuscript display tables.
savecsv(de[(de.geography==panel)&(de.pair=='early_to_late')],'SI_Q0_all_endpoint_accounting.csv','decomposition.csv','international_reporting; all core24 and agreement12; endpoint; four classes')
qd=read('arithmetic_quarantine_decomposition.csv');savecsv(qd[(qd.geography==panel)&(qd.pair=='early_to_late')],'SI_Q1_all_endpoint_accounting.csv','arithmetic_quarantine_decomposition.csv','international_reporting; Q1 24; endpoint; four classes')
savecsv(co[(co.panel==panel)&(co.target_type=='decomposition')&(co.target=='early_to_late')],'SI_Q0_regional18_endpoint_envelopes.csv','completion_case_scalar_envelopes.csv','international_reporting; all 18 Q0 source cases separately; four classes; endpoint components')
pe=read('paired_factor_effects.csv');savecsv(pe[(pe.geography==panel)&(pe.analysis=='decomposition')&(pe.target=='early_to_late')],'SI_documented_source_contrasts.csv','paired_factor_effects.csv','international_reporting; endpoint; all factors/backgrounds; separate from deletion influence')
le=read('influence/influence_entity_ledger.csv.gz');savecsv(le[(le.scenario=='A1O1G1D1')&(le.panel==panel)&((le.unit_type=='package')|((le.unit_type=='record')&(le.unit_id.astype(str)=='8129')))],'SI_influence_membership_and_amounts.csv','influence/influence_entity_ledger.csv.gz','A1O1G1D1; international_reporting; displayed deletion entities; amount and membership audit')

def table_pdf(frame,labels,title,note,name,width=11):
 fig,ax=plt.subplots(figsize=(width,1.8+.34*len(frame)));ax.axis('off');ax.set_title(title,loc='left',pad=18,fontsize=12)
 tb=ax.table(cellText=frame.values,colLabels=labels,loc='upper center',cellLoc='left',colLoc='left');tb.auto_set_font_size(False);tb.set_fontsize(9);tb.scale(1,2.15)
 for (r,c),cell in tb.get_celld().items():
  cell.set_edgecolor('#d8dde0');cell.set_linewidth(.4)
  if r==0:cell.set_facecolor('#edf1f3');cell.set_text_props(weight='bold')
 ax.text(0,-.15,note,transform=ax.transAxes,fontsize=8,va='top');finish(fig,name)
x=t1.copy();x['scenario']=x.scenario.map(dict(zip(S,['Archive','D1','D2'])));x['period']=x.period.map({'early':'2013–15','late':'2020–22'})
for col in x.columns[2:]:x[col]=x[col].map(lambda v:f'{v/1e9:.3f}')
table_pdf(x,['Case','Period','Classified, USD bn','Observed, USD bn','Unclassified, USD bn'],'Table 1. International reporting scope and denominators','Fixed FY2013 income. Known-class shares divide by classified observed amounts.\nObserved includes unknown-income amounts. Missing amounts are excluded, never replaced by zero.','SI_scope_and_denominators')
x=t2[['universe','income_class','minimum','maximum','defined_cases','undefined_cases']].copy();x.universe=x.universe.replace({'core24':'Core treatments','agreement12':'Agreement-year overlay','quarantine24':'Arithmetic-flag exclusions'})
for c in ['minimum','maximum']:x[c]=x[c].map(lambda v:f'{v:+.2f}')
table2_rows=x.values.tolist();x.universe=x.universe.str.replace('Agreement-year overlay','Agreement-year\noverlay',regex=False).str.replace('Arithmetic-flag exclusions','Arithmetic-flag\nexclusions',regex=False)
table_pdf(x,['Family','Income','Minimum, pp','Maximum, pp','Defined cases','Undefined cases'],'Table 2. Endpoint share changes across separate case families','Finite treatment envelopes, not confidence intervals; no probability weighting.\nArithmetic-flag exclusions jointly omit four rows; agreement and regional families do not cross this stress.','Table_2_separate_family_share_envelopes')
x=t3[['unit_id','income_class','baseline_delta_pp','deleted_delta_pp','influence_delta_pp']].copy();x.unit_id=x.unit_id.replace({'8129':'Souapiti/Kaleta, Guinea','Standard Bank 1907/1908':'Standard Bank credit line','Karuma 109/2253':'Karuma hydropower','Dogger 7410/8034/8413':'Dogger Bank wind'})
for c in x.columns[2:]:x[c]=x[c].map(lambda v:f'{v:+.2f}')
table3_rows=x.values.tolist()
table_pdf(x,['Deleted entity','Income','Baseline, pp','After deletion, pp','Deletion minus base, pp'],'Table 3. Record and package influence: source-informed contract exclusion','The Guinea package is corroborated at approximately USD1.72bn, including development and restructuring.\nDeletion changes denominators and support; these diagnostics do not recommend trimming or measure causal effects.','Table_3_record_and_package_influence',width=12)
import textwrap
operations=pd.DataFrame([
 ['A: amount','1907; 1908','Direct loan USD125m; combined support USD237.5m. Guarantee USD112.5m is derived by subtraction.','A1 retains two instruments at USD125m and USD112.5m; assumes same-operation scope and additivity. A0 retains USD1.25bn each.'],
 ['O: overlap','109; 2253','Two signed contracts total approximately USD1.435bn for the same EPC package; strong overlap inference.','O1 removes row109 and retains row2253 at USD1.435bn, archive FY2015. Agreement years form a separate overlay.'],
 ['G: country role','1907; 1908','South Africa is intermediary location; documented intended project region is Sub-Saharan Africa.','G1 retains observed amounts in the international reporting portfolio, but removes them from classified income and country-assigned scope.'],
 ['D: financial basis','7410; 8413; 8034','Rows7410/8413 trace to guaranteed export-contract values; row8034 remains an unresolved financing-layer amount.','D1 excludes rows7410/8413 and retains row8034; D2 excludes all three. Neither is certified principal or a true-exposure bound.']
],columns=['operation','source_excel_rows','evidence_and_status','approved_treatment'])
savecsv(operations,'Table_1_source_operations.csv','protocol/REVISED_ANALYSIS_FREEZE_V2_PENDING_APPROVAL_2026-10-18.md, section3','Exact approved operation definitions; evidence qualifiers retained; no new operations')
fig,ax=plt.subplots(figsize=(12,6));ax.axis('off');ax.set_title('Table 1. Source evidence and approved operations',loc='left',pad=18,fontsize=12)
wrapped=operations[['operation','evidence_and_status','approved_treatment']].copy();wrapped.operation=['Standard Bank amount','Karuma overlap','Standard Bank geography','Dogger Bank basis'];wrapped.evidence_and_status=wrapped.evidence_and_status.str.replace('Rows7410/8413 trace to','Two entries trace to',regex=False).str.replace('row8034','a third entry',regex=False);wrapped.approved_treatment=['Use USD125m direct loan and USD112.5m derived guarantee; retain both instruments. The archive records USD1.25bn each.','Retain one USD1.435bn package in archive FY2015. Signed-contract years are a separate overlay.','Retain observed cross-border regional support; exclude from classified-income denominator and country-assigned subset.','Contract exclusion removes two export-contract entries, retaining an unresolved financing entry. Whole-block exclusion removes all three.']
table1_rows=wrapped.values.tolist()
for c,w in zip(wrapped.columns,[19,43,43]):wrapped[c]=wrapped[c].map(lambda t:'\n'.join(textwrap.wrap(t,w)))
tb=ax.table(cellText=wrapped.values,colLabels=['Source operation','Evidence and qualification','Treatment'],colWidths=[.18,.41,.41],loc='upper center',cellLoc='left',colLoc='left');tb.auto_set_font_size(False);tb.set_fontsize(9)
for (r,c),cell in tb.get_celld().items():
 cell.set_edgecolor('#d8dde0');cell.set_linewidth(.4);cell.set_height(.095 if r==0 else .205)
 if r==0:cell.set_facecolor('#edf1f3');cell.set_text_props(weight='bold')
ax.text(0,-.02,'Source-informed cases combine the amount, overlap and geography operations with one of the two financial-basis exclusions.\nThe archive is a reference reconstruction; treatments are not equally plausible estimates of true finance exposure.',transform=ax.transAxes,fontsize=9,va='top');finish(fig,'Table_1_source_operations')
for fn in ['Table_1_scope_and_denominators.csv','Table_1_scope_and_denominators.png','Table_1_scope_and_denominators.pdf','SI_scope_and_denominators.png','SI_scope_and_denominators.pdf']:
 (D/fn).unlink(missing_ok=True)
(D/'table_data.json').write_text(json.dumps({'table1':table1_rows,'table2':table2_rows,'table3':table3_rows},indent=2))
pd.DataFrame(ledger).to_csv(D/'VALUE_LEDGER.csv',index=False)
hashes={str(p.relative_to(O)):hashlib.sha256(p.read_bytes()).hexdigest() for p in O.rglob('*.csv*')};(D/'SOURCE_HASHES.json').write_text(json.dumps(hashes,indent=2))
print('Created',len(list(D.iterdir())),'files')
