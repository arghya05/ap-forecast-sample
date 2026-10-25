"""CI for ap_forecast: compile, unit tests, coverage gate (>= 90%), simple static checks. Exit 0 only when all pass.

SonarQube is not available locally; the static checks below stand in for it (unused imports via compile warnings are not
detected). Output is JSON on the last line for the agent spine to record.
"""
import ast
import compileall
import io
import json
import sys
import unittest
from pathlib import Path

import coverage

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
COVERAGE_MIN = 90.0


def static_checks():
    issues = []
    for path in sorted((SRC / "ap_forecast").glob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "id", "") in ("print", "eval", "exec"):
                issues.append(f"{path.name}:{node.lineno} uses {node.func.id}()")
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(f"{path.name}:{node.lineno} bare except")
        for i, line in enumerate(path.read_text().splitlines(), 1):
            if len(line) > 140:
                issues.append(f"{path.name}:{i} line longer than 140 characters")
    return issues


def main():
    result = {"compile": compileall.compile_dir(str(SRC), quiet=1, force=True)}
    sys.path.insert(0, str(SRC))
    cov = coverage.Coverage(source=[str(SRC / "ap_forecast")], data_file=None)
    cov.start()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
    stream = io.StringIO()
    run = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
    cov.stop()
    out = io.StringIO()
    total = cov.report(file=out, show_missing=True)
    result.update(tests_run=run.testsRun, failures=len(run.failures), errors=len(run.errors), coverage=round(total, 1),
                  coverage_report=out.getvalue(), test_output=stream.getvalue()[-3000:], static_issues=static_checks())
    result["passed"] = bool(result["compile"]) and run.wasSuccessful() and total >= COVERAGE_MIN and not result["static_issues"]
    print(json.dumps(result))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
