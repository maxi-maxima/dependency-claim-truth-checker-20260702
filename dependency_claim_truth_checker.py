#!/usr/bin/env python
"""Check README dependency and offline claims against repository evidence."""

import argparse
import json
import re
from pathlib import Path

CLAIMS = [
    (
        "zero_dependencies",
        re.compile(r"zero dependencies|no dependencies|dependency-free", re.I),
    ),
    (
        "offline_first",
        re.compile(r"offline[- ]first|no network required|works offline", re.I),
    ),
]
IMPORT = re.compile(r"^(?:import|from)\s+([a-zA-Z_][\w]*)", re.M)
STDLIB = {
    "argparse",
    "collections",
    "dataclasses",
    "functools",
    "hashlib",
    "importlib",
    "itertools",
    "json",
    "math",
    "os",
    "pathlib",
    "re",
    "statistics",
    "subprocess",
    "sys",
    "tempfile",
    "typing",
    "unittest",
}
DEPENDENCY_FILES = ("package.json", "requirements.txt", "pyproject.toml")
NETWORK_NAMES = {"requests", "httpx", "aiohttp", "urllib3", "fetch", "curl"}
SKIP_DIRS = {".git", ".hg", ".svn", "__pycache__", ".venv", "venv", "node_modules"}


def package_files(root):
    p = Path(root)
    return [p / name for name in DEPENDENCY_FILES if (p / name).exists()]


def _strip_requirement(line):
    line = line.split("#", 1)[0].strip()
    if not line or line.startswith(("-", "--")):
        return ""
    return re.split(r"\s*(?:==|>=|<=|~=|!=|>|<|\[|;)\s*", line, maxsplit=1)[0].strip()


def _extract_pyproject_deps(text):
    deps = set()
    in_deps = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("dependencies") and "[" in line:
            in_deps = True
        if in_deps:
            deps.update(_strip_requirement(item) for item in re.findall(r'["\']([^"\']+)["\']', line))
            if "]" in line:
                in_deps = False
    return {dep for dep in deps if dep}


def _extract_package_json_deps(text):
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return set(re.findall(r'["\']([A-Za-z0-9_.-]+)["\']\s*:', text))
    deps = set()
    for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        values = data.get(section, {})
        if isinstance(values, dict):
            deps.update(values)
    return deps


def _is_skipped(path):
    return bool(SKIP_DIRS.intersection(path.parts))


def _local_module_names(root):
    names = set()
    for py in Path(root).rglob("*.py"):
        if _is_skipped(py):
            continue
        if py.name == "__init__.py":
            names.add(py.parent.name)
        else:
            names.add(py.stem)
    return names


def evidence(root):
    local_modules = _local_module_names(root)
    deps = []
    for dep_file in package_files(root):
        txt = dep_file.read_text(encoding="utf-8")
        if dep_file.name == "requirements.txt":
            deps += [dep for dep in (_strip_requirement(ln) for ln in txt.splitlines()) if dep]
        elif dep_file.name == "package.json":
            deps += sorted(_extract_package_json_deps(txt))
        elif dep_file.name == "pyproject.toml":
            deps += sorted(_extract_pyproject_deps(txt))

    imports = []
    for py in Path(root).rglob("*.py"):
        if _is_skipped(py):
            continue
        modules = IMPORT.findall(py.read_text(encoding="utf-8", errors="ignore"))
        imports += [
            module for module in modules if module not in STDLIB and module not in local_modules
        ]
    return sorted(set(deps)), sorted(set(imports))


def check(root, readme):
    text = Path(readme).read_text(encoding="utf-8")
    claims = [name for name, rx in CLAIMS if rx.search(text)]
    deps, imports = evidence(root)
    findings = []
    if "zero_dependencies" in claims and (deps or imports):
        findings.append(
            {
                "claim": "zero_dependencies",
                "problem": "dependency evidence found",
                "deps": deps,
                "imports": imports,
            }
        )
    network_evidence = sorted(set(deps + imports).intersection(NETWORK_NAMES))
    if "offline_first" in claims and network_evidence:
        findings.append(
            {
                "claim": "offline_first",
                "problem": "network-capable dependency/import found",
                "evidence": network_evidence,
            }
        )
    return {
        "claims_found": claims,
        "dependency_files": deps,
        "third_party_imports": imports,
        "findings": findings,
        "passed": not findings,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check README dependency/offline claims against dependency files and imports."
    )
    parser.add_argument("root")
    parser.add_argument("--readme", default="README.md")
    args = parser.parse_args(argv)
    print(json.dumps(check(args.root, Path(args.root) / args.readme), indent=2))


if __name__ == "__main__":
    main()
