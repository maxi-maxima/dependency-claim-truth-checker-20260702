#!/usr/bin/env python
import argparse, json, re
from pathlib import Path
CLAIMS=[('zero_dependencies', re.compile(r'zero dependencies|no dependencies|dependency-free', re.I)),('offline_first', re.compile(r'offline[- ]first|no network required|works offline', re.I))]
IMPORT=re.compile(r'^(?:import|from)\s+([a-zA-Z_][\w]*)', re.M)
STDLIB={'argparse','json','re','pathlib','sys','os','typing','hashlib','subprocess','tempfile','unittest'}
def package_files(root):
    p=Path(root); return [x for x in [p/'package.json',p/'requirements.txt',p/'pyproject.toml'] if x.exists()]
def evidence(root):
    deps=[]
    for f in package_files(root):
        txt=f.read_text(encoding='utf-8')
        if f.name=='requirements.txt': deps += [ln.strip() for ln in txt.splitlines() if ln.strip() and not ln.startswith('#')]
        else: deps += re.findall(r'["\']([A-Za-z0-9_.-]+)["\']\s*[:=]', txt)
    imports=[]
    for py in Path(root).rglob('*.py'):
        if '.git' in py.parts: continue
        imports += [m for m in IMPORT.findall(py.read_text(encoding='utf-8', errors='ignore')) if m not in STDLIB]
    return sorted(set(deps)), sorted(set(imports))
def check(root, readme):
    text=Path(readme).read_text(encoding='utf-8')
    claims=[name for name,rx in CLAIMS if rx.search(text)]
    deps, imports=evidence(root)
    findings=[]
    if 'zero_dependencies' in claims and (deps or imports): findings.append({'claim':'zero_dependencies','problem':'dependency evidence found','deps':deps,'imports':imports})
    if 'offline_first' in claims and re.search(r'\b(requests|httpx|fetch|curl|urllib)\b', '\n'.join(deps+imports), re.I): findings.append({'claim':'offline_first','problem':'network-capable dependency/import found'})
    return {'claims_found':claims,'dependency_files':deps,'third_party_imports':imports,'findings':findings,'passed':not findings}
def main(argv=None):
    p=argparse.ArgumentParser(description='Check README dependency/offline claims against dependency files and imports.')
    p.add_argument('root'); p.add_argument('--readme', default='README.md')
    a=p.parse_args(argv); print(json.dumps(check(a.root, Path(a.root)/a.readme), indent=2))
if __name__=='__main__': main()
