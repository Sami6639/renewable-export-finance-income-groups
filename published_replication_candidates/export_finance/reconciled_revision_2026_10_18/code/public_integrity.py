"""Verify public protocol bytes and fixed arithmetic-flag membership."""
from core import ROOT
import hashlib,json

def protocol_integrity():
    m=json.loads((ROOT/'protocol/PUBLIC_PROTOCOL_INTEGRITY.json').read_text())
    for key,name in [('sha256','ANALYSIS_PROTOCOL.md'),('amendment_sha256','ARITHMETIC_AMENDMENT.md')]:
        assert hashlib.sha256((ROOT/'protocol'/name).read_bytes()).hexdigest()==m[key]
    return m
