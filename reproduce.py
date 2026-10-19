"""Portable input-dependent replay of prerequisite and revised analyses."""
import argparse,subprocess,sys,pathlib
p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);p.add_argument('--verify-inputs',action='store_true');p.add_argument('--skip-prerequisites',action='store_true');p.add_argument('--skip-influence',action='store_true');p.add_argument('--list-steps',action='store_true');a=p.parse_args();root=a.root.resolve();r=root/'published_replication_candidates/export_finance/reconciled_revision_2026_10_18'
steps=[]
if not a.skip_prerequisites:
 steps.append([sys.executable,str(root/'reproduce_prerequisites.py'),'--root',str(root)]+(['--verify-inputs'] if a.verify_inputs else []))
for s in ['code/screen.py','independent_audit/verify_raw_screen.py','code/run_revision.py','code/quarantine.py','code/completion.py']:
 steps.append([sys.executable,str(r/s)])
if not a.skip_influence:steps.append([sys.executable,str(r/'code/influence.py'),'--arithmetic-screen-cleared'])
for s in ['audit_outcomes','compare_core','audit_envelopes','audit_completion','audit_completion_attainers','audit_quarantine_attainers','audit_identities_bounds','audit_metadata']:
 steps.append([sys.executable,str(r/'independent_audit'/f'{s}.py')])
if not a.skip_influence:
 steps.extend([[sys.executable,str(r/'independent_audit/audit_reporting_summaries.py')],[sys.executable,str(r/'code/verify_influence_exports.py')],[sys.executable,str(r/'independent_audit/audit_influence.py')]])
display=root/'published_replication_candidates/export_finance/manuscript_design/revision2/displays/build_displays.py'
if display.exists() and (r/'outputs/influence/influence_rankings.csv.gz').exists():steps.extend([[sys.executable,str(display)],[sys.executable,str(display.parent/'assemble_display_metadata.py')]])
for cmd in steps:
 print(' '.join(cmd),flush=True)
 if not a.list_steps:subprocess.run(cmd,cwd=root,check=True)
