"""Restore large CSVs byte-for-byte without changing analytical calculations."""
from pathlib import Path
import gzip, hashlib, json
root = Path(__file__).resolve().parent
items = json.loads((root / 'COMPRESSED_OUTPUTS.json').read_text())
for item in items:
    source = root / item['compressed_path']
    target = root / item['path']
    compressed = source.read_bytes()
    if hashlib.sha256(compressed).hexdigest() != item['compressed_sha256']:
        raise SystemExit(f'Compressed checksum mismatch: {source.name}')
    data = gzip.decompress(compressed)
    if len(data) != item['bytes'] or hashlib.sha256(data).hexdigest() != item['sha256']:
        raise SystemExit(f'Restored checksum mismatch: {target.name}')
    if target.exists() and target.read_bytes() != data:
        raise SystemExit(f'Refusing to overwrite changed output: {target.name}')
    target.write_bytes(data)
print(f'Restored and verified {len(items)} large CSV outputs.')
