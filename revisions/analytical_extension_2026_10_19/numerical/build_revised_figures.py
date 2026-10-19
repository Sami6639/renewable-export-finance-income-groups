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
def read(f): return pd.read_csv((O/f) if (O/f).exists() else O/(f+'.gz'),float_precision='round_trip')
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
  axs[1].plot([early,late],[yy,yy],color=c,ls=styles[k],lw=1.5);axs[1].scatter(early,yy,facecolors='white',edgecolors=c,marker=m,s=42,zorder=3);axs[1].scatter(late,yy,color=c,marker=m,s=42,zorder=3)
axs[0].set_yticks(range(4),['Low','Lower-middle','Upper-middle','High']);axs[0].invert_yaxis();axs[0].axvline(0,c='#6d7479',lw=.8);axs[0].set_xlim(-44,52);axs[0].set_xlabel('Classified share change (percentage points)');axs[0].set_title('a  Pooled endpoint changes',loc='left',fontsize=11)
axs[1].set_xlim(left=0);axs[1].set_xlabel('Pooled nominal recorded amount (USD billions)');axs[1].set_title('b  Early (open) and late (filled) amounts',loc='left',fontsize=11)
for ax in axs:ax.grid(axis='x',color='#e2e5e7',lw=.6);ax.set_axisbelow(True)
fig.legend([Line2D([],[],color=c,marker=m,ls=st) for c,m,st in zip(cols,marks,styles)],names,loc='upper center',ncol=3,frameon=False);fig.subplots_adjust(top=.85,bottom=.13,wspace=.14);finish(fig,'Figure_2_endpoint_changes_and_levels')
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
   r=reg[(reg.case_id==s)&(reg.metric==t)].iloc[0];axs[0].plot([r.lower,r.upper],[y,y],color=c,ls=styles[k],lw=2.2)
axs[0].set_yticks(range(5),['Total change','Provider-country composition','Within-provider-country','Entry','Exit']);axs[0].invert_yaxis();axs[0].set_title('a  Additive accounting components',loc='left',fontsize=11)
for k,(s,c,m) in enumerate(zip(S[1:],cols[1:],marks[1:])):
 z=h[h.scenario==s].iloc[0];r=reg[(reg.case_id==s)&(reg.metric=='within_pp')].iloc[0]
 axs[1].plot([r.lower,r.upper],[k,k],color=c,ls=styles[k+1],lw=3);axs[1].scatter(z.within_pp,k,color=c,marker=m,s=60,zorder=4)
 axs[1].text(z.within_pp,k-.18,f'{z.within_pp:+.2f}',ha='center',fontsize=11,color=c)
 axs[1].text(-.35,k+.22,f'Outer envelope: {r.lower:+.2f} to {r.upper:+.2f}',ha='center',fontsize=9)
axs[1].set_yticks([0,1],['Contract\nexclusion','Whole-block\nexclusion']);axs[1].set_ylim(1.55,-.55);axs[1].set_xlim(-2.7,2);axs[1].set_title('b  Within-provider-country term',loc='left',fontsize=11)
for ax in axs:ax.axvline(0,c='#6d7479',lw=.8);ax.grid(axis='x',color='#e2e5e7',lw=.6);ax.set_axisbelow(True);ax.set_xlabel('Percentage points')
fig.legend([Line2D([],[],color=c,marker=m,ls=st) for c,m,st in zip(cols,marks,styles)],names,loc='upper center',ncol=3,frameon=False);fig.subplots_adjust(top=.84,bottom=.13,wspace=.36);finish(fig,'Figure_3_H_provider_accounting')
