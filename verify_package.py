"""Verify exact distributed bytes; optional influence parts may be absent."""
import argparse,pathlib,hashlib,json
p=argparse.ArgumentParser();p.add_argument('--require-all',action='store_true');a=p.parse_args();root=pathlib.Path(__file__).resolve().parent;m=json.loads((root/'MANIFEST.sha256.json').read_text());missing=[];bad=[]
for item in m['files']:
 f=root/item['path']
 if not f.exists():
  if a.require_all or item['part']=='core':bad.append(item['path']+' MISSING')
  else:missing.append(item['path'])
 elif hashlib.sha256(f.read_bytes()).hexdigest()!=item['sha256']:bad.append(item['path']+' HASH MISMATCH')
print(json.dumps({'status':'FAIL' if bad else 'PASS','files_checked':len(m['files'])-len(missing),'optional_missing':len(missing),'errors':bad},indent=2));raise SystemExit(bool(bad))
