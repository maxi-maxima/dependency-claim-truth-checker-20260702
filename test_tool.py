import tempfile
import unittest
from pathlib import Path

from dependency_claim_truth_checker import check, evidence


class DependencyClaimTruthCheckerTests(unittest.TestCase):
    def test_zero_dependency_claim_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "README.md").write_text("Zero dependencies and works offline")
            (root / "requirements.txt").write_text("requests==2.0")
            result = check(root, root / "README.md")
        self.assertFalse(result["passed"])
        self.assertEqual(result["findings"][0]["claim"], "zero_dependencies")
        self.assertEqual(result["findings"][1]["claim"], "offline_first")

    def test_ignores_comments_options_and_version_specifiers(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "requirements.txt").write_text(
                "# requests==old\n-r base.txt\nhttpx>=0.27; python_version >= '3.9'\n"
            )
            deps, imports = evidence(root)
        self.assertEqual(deps, ["httpx"])
        self.assertEqual(imports, [])

    def test_reads_package_json_dependency_sections(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "package.json").write_text(
                '{"scripts":{"test":"node test.js"},"dependencies":{"chalk":"^5"},'
                '"devDependencies":{"vitest":"latest"}}'
            )
            deps, _ = evidence(root)
        self.assertEqual(deps, ["chalk", "vitest"])

    def test_reads_pyproject_dependencies(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "pyproject.toml").write_text(
                '[project]\ndependencies = ["rich>=13", "click"]\n'
            )
            deps, _ = evidence(root)
        self.assertEqual(deps, ["click", "rich"])

    def test_ignores_local_project_imports(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "tool.py").write_text("def run():\n    return True\n")
            (root / "test_tool.py").write_text("from tool import run\n")
            deps, imports = evidence(root)
        self.assertEqual(deps, [])
        self.assertEqual(imports, [])


if __name__ == "__main__":
    unittest.main()
