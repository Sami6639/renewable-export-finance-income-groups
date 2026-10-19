from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
O=Path(__file__).resolve().parent
d=pd.read_csv(O/'full_technology_geography_coverage.csv');d=d[d.unit.eq('Nominal USD')]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(10.4,6.7));fig.subplots_adjust(left=.09,right=.97,top=.77,bottom=.32)
colors=['#136F63','#81939E'];width=.28
for i,tech in enumerate(['Renewable','Fossil']):
 for j,window in enumerate(['early','late']):
  r=d[(d.technology.eq(tech))&d.geography.eq('Known international')&d.window.eq(window)].iloc[0]
  x=i+(j-.5)*.34;y=r.high_share_known*100
  ax.bar(x,y,width,color=colors[j],label=['FY2013–2015','FY2020–2022'][j] if i==0 else None,zorder=3)
  ax.text(x,y+1.8,f'{y:.1f}%',ha='center',va='bottom',fontweight='bold',fontsize=12)
  ax.text(x,-9,f'${r.reported_nominal_usd/1e9:.2f}bn\n{int(r.entries)} entries',ha='center',va='top',fontsize=10,clip_on=False)
quarantine=pd.read_csv(O/'dogger_quarantine_endpoints.csv')
q=quarantine[(quarantine.scenario.eq('All three Dogger records quarantined'))&quarantine.window.eq('late')].iloc[0]
qy=q.high_share_allocable*100
ax.plot([.03,.31],[qy,qy],color='white',linewidth=2.2,zorder=5)
ax.text(.17,qy-2,f'{qy:.1f}%\nthree flagged rows\nquarantined',ha='center',va='top',fontsize=9,color='white',zorder=6)
ax.set_xticks([0,1],['Renewable','Fossil']);ax.tick_params(axis='x',pad=7,length=0)
ax.set_ylim(0,60);ax.set_yticks([0,20,40,60]);ax.yaxis.set_major_formatter(PercentFormatter());ax.set_ylabel('High-income share of known international volume',fontsize=10)
ax.grid(axis='y',alpha=.18,zorder=0);ax.legend(frameon=False,loc='upper right')
fig.text(.09,.95,'Recipient allocation differs sharply by technology',fontsize=19,fontweight='bold',ha='left')
fig.text(.09,.90,'Known international recorded support values · fixed World Bank FY2013 income classes',fontsize=11,color='#46545D')
fig.text(.09,.85,'Descriptive comparison; amount basis and reported financing mechanisms require qualification.',fontsize=11,color='#46545D')
fig.text(.09,.17,'Coverage: unknown-income volume in all-location portfolios',fontsize=10,fontweight='bold')
fig.text(.09,.135,'Renewable: 0.33% early / 0.59% late.  Fossil: 30.40% early / 35.99% late.',fontsize=10)
fig.text(.09,.095,'Recorded support values mix source bases. Quarantining three Dogger records leaves $13.58bn late renewable.\nOne renewable amount is missing. Domestic/unresolved locations excluded; entries are not projects.',fontsize=9,color='#46545D')
fig.text(.09,.035,'Source: OCI archive, Zenodo 14261240; Censkowsky et al. (2025), DOI 10.1038/s41467-025-55981-0.',fontsize=8,color='#46545D')
fig.savefig(O/'international_renewable_fossil_allocation.png',dpi=180,facecolor='white');fig.savefig(O/'international_renewable_fossil_allocation.pdf',facecolor='white')
