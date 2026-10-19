"""Run unchanged source-aware calculations with a portable package root."""
import argparse, pathlib, json, hashlib, subprocess, sys
p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent);p.add_argument('--verify-inputs',action='store_true');a=p.parse_args();root=a.root.resolve();base=root/'published_replication_candidates/export_finance';e=base/'extension'
if a.verify_inputs:
 for x in json.loads((e/'source_hashes.json').read_text())['inputs']:
  path=root/x['path']
  if not path.exists():raise SystemExit('Missing required input: '+str(path))
  if hashlib.sha256(path.read_bytes()).hexdigest()!=x['sha256']:raise SystemExit('Input SHA256 mismatch: '+str(path))
scripts=[e/(n+'.py') for n in ['audit_extension','prepare_income_mapping','decompose_allocation','technology_diagnostics','decompose_technology_geography','quarantine_flagged_source_rows','decompose_provider_only','decompose_provider_only_quarantine','plot_international_allocation']]
scripts += [e/'independent_audit'/(n+'.py') for n in ['recompute','recompute_si','recompute_decomposition','recompute_stratified','recompute_technology','recompute_provider_only','recompute_provider_only_quarantine']]
scripts += [base/'manuscript_design'/n for n in ['evidence/build_evidence.py','evidence/independent_audit/check_evidence.py','source_validation/build_validation.py','source_validation/write_audit.py','source_validation/finalize_validation.py']]
for script in scripts:
 print('Running',script.relative_to(root),flush=True);subprocess.run([sys.executable,str(script)],cwd=root,check=True)
print('All analysis and audit steps completed. Local raw extracts were generated; do not redistribute them by default.')
