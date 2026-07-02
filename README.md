# Dependency Claim Truth Checker

## Pain point
Project READMEs often claim “zero dependencies”, “no network”, or “offline first”, but lockfiles and imports may contradict those claims.

## Why now
AI-generated READMEs and fast-moving open-source releases make lightweight evidence checks valuable for maintainers, reviewers, and security teams.

## Install / run
Requires Python 3.9+ and no runtime third-party packages.

```bash
python dependency_claim_truth_checker.py --help
```

## Example
Input:
```text
README: Zero dependencies. requirements.txt: requests==2.0
```

Command:
```bash
python dependency_claim_truth_checker.py examples/demo-project
```

Example output:
```json
{"claims_found": ["zero_dependencies"], "passed": false}
```

## Self-check
```bash
python -m unittest discover -v
```

## Roadmap
- Add more ecosystem-specific rules.
- Emit GitHub Actions annotations.
- Support SARIF/JSON Lines output for CI ingestion.

## License
MIT
