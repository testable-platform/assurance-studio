#!/usr/bin/env python3
# ARCHIVED: superseded by lib/sa_validate.py + notebooks/01_generate_and_validate.ipynb
"""
Assert validations for generated SA metric branches.

Each of the four fixed branch types (Bug, BugFX, TCC, CC) has a dedicated
assert function that checks naming, config, target-module variant, stubs,
tests, and tooling layout.
"""

from __future__ import print_function

import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))

from sa_metrics import (  # noqa: E402
    ABBREV_TO_MODULE,
    BRANCH_TYPES,
    SA_METRICS,
    branch_name,
    parse_metrics_arg,
)

TCC_CONFIG_FILES = (".coveragerc", "setup.cfg", "pytest.ini", ".testmondata.ini")
SA_MODULE_KEYS = [row[0] for row in SA_METRICS]
STUB_MIN_LINES = 25
STUB_MAX_LINES = 70
FULL_TEST_MIN_METHODS = {"TDI": 1, "QRA": 1, "DOV": 12}
FORBIDDEN_MARKERS = ("TOOL_MODE", "-tcc-", "fallback-cc-", "if False:", "phantom")

# Per-metric fingerprints in the *target* module source for each variant.
N_FUNCTIONS = 20

BUG_TARGET_MARKERS = {
    "execution_path_integrity": lambda s: "legacy-" in s and s.count("def route_handler_") >= N_FUNCTIONS,
    "decision_coverage": lambda s: "escalated-" in s and s.count("def decision_case_") >= N_FUNCTIONS,
    "condition_coverage": lambda s: "edge-" in s and s.count("def condition_check_") >= N_FUNCTIONS,
    "logic_combinatorial": lambda s: "overflow-" in s and s.count("def combinatorial_state_machine_") >= N_FUNCTIONS,
    "technical_debt": lambda s: "return -1.0" in s and s.count("def debt_calculator_") >= N_FUNCTIONS,
    "qa_prioritization": lambda s: "critical" in s and s.count("def prioritize_test_bucket_") >= N_FUNCTIONS,
}

TCC_TARGET_MARKERS = {
    "execution_path_integrity": lambda s: "audit-strict-" in s and s.count("def route_handler_") >= N_FUNCTIONS,
    "decision_coverage": lambda s: "disabled-" in s and "OUTCOME_LOOKUP" not in s,
    "condition_coverage": lambda s: "alt-" in s and s.count("def condition_check_") >= N_FUNCTIONS,
    "logic_combinatorial": lambda s: s.count("if idx % 2") >= 1 and s.count("def combinatorial_state_machine_") >= N_FUNCTIONS,
    "technical_debt": lambda s: "year % 2" in s and s.count("def debt_calculator_") >= N_FUNCTIONS,
    "qa_prioritization": lambda s: "high-history" in s and s.count("def prioritize_test_bucket_") >= N_FUNCTIONS,
}

CC_TARGET_MARKERS = {
    "execution_path_integrity": lambda s: "ROUTE_LABELS" in s and s.count("def route_handler_") >= N_FUNCTIONS,
    "decision_coverage": lambda s: "OUTCOME_LOOKUP" in s and "DECISION_TABLE" not in s,
    "condition_coverage": lambda s: "neutral-" in s and s.count("def condition_check_") >= N_FUNCTIONS,
    "logic_combinatorial": lambda s: "parity-" in s and s.count("def combinatorial_state_machine_") >= N_FUNCTIONS,
    "technical_debt": lambda s: "multiplier" in s and s.count("def debt_calculator_") >= N_FUNCTIONS,
    "qa_prioritization": lambda s: "bucket-" in s and s.count("def prioritize_test_bucket_") >= N_FUNCTIONS,
}

CONFIG_RE = {
    "BRANCH_TYPE": re.compile(r"^BRANCH_TYPE\s*=\s*'([^']+)'", re.M),
    "TARGET_METRIC_ABBREV": re.compile(r"^TARGET_METRIC_ABBREV\s*=\s*'([^']+)'", re.M),
    "PYTHON_VERSION": re.compile(r"^PYTHON_VERSION\s*=\s*'([^']+)'", re.M),
    "LANGUAGE": re.compile(r"^LANGUAGE\s*=\s*'([^']+)'", re.M),
    "TESTING_TYPE": re.compile(r"^TESTING_TYPE\s*=\s*'([^']+)'", re.M),
}


class BranchValidationError(AssertionError):
    pass


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _line_count(path):
    return len(_read(path).splitlines())


def _parse_config(root):
    cfg_path = os.path.join(root, "sa", "config.py")
    assert os.path.isfile(cfg_path), "missing sa/config.py"
    text = _read(cfg_path)
    out = {}
    for key, pattern in CONFIG_RE.items():
        m = pattern.search(text)
        assert m, "config.py missing %s" % key
        out[key] = m.group(1)
    return out


def _count_test_methods(tests_dir):
    if not os.path.isdir(tests_dir):
        return 0, []
    total = 0
    files = []
    for fn in os.listdir(tests_dir):
        if not fn.endswith(".py") or fn == "__init__.py":
            continue
        path = os.path.join(tests_dir, fn)
        text = _read(path)
        n = len(re.findall(r"^\s+def test_", text, re.M))
        total += n
        files.append((fn, n))
    return total, files


def _target_module_path(root, abbrev):
    module_key = ABBREV_TO_MODULE[abbrev]
    return os.path.join(root, "sa", "%s.py" % module_key), module_key


def _assert_no_forbidden(root):
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            text = _read(os.path.join(dirpath, fn))
            for marker in FORBIDDEN_MARKERS:
                assert marker not in text, "forbidden marker %r in %s" % (
                    marker, os.path.relpath(os.path.join(dirpath, fn), root))


def _assert_stubs(root, target_module_key):
    for key in SA_MODULE_KEYS:
        path = os.path.join(root, "sa", "%s.py" % key)
        assert os.path.isfile(path), "missing sa/%s.py" % key
        if key == target_module_key:
            continue
        lines = _line_count(path)
        assert STUB_MIN_LINES <= lines <= STUB_MAX_LINES, (
            "non-target module sa/%s.py should be a modest stub (%d-%d lines), got %d"
            % (key, STUB_MIN_LINES, STUB_MAX_LINES, lines)
        )


def _assert_common(root, abbrev, branch_type, version, language="python"):
    expected_name = branch_name(abbrev, branch_type, version)
    actual_name = os.path.basename(os.path.normpath(root))
    assert actual_name == expected_name, "folder name %r != expected %r" % (actual_name, expected_name)

    cfg = _parse_config(root)
    assert cfg["BRANCH_TYPE"] == branch_type, "BRANCH_TYPE=%r expected %r" % (cfg["BRANCH_TYPE"], branch_type)
    assert cfg["TARGET_METRIC_ABBREV"] == abbrev, "TARGET_METRIC_ABBREV=%r expected %r" % (
        cfg["TARGET_METRIC_ABBREV"], abbrev)
    assert cfg["PYTHON_VERSION"] == version, "PYTHON_VERSION=%r expected %r" % (cfg["PYTHON_VERSION"], version)
    if language:
        assert cfg.get("LANGUAGE") == language, "LANGUAGE=%r expected %r" % (cfg.get("LANGUAGE"), language)
    assert cfg["TESTING_TYPE"] == "Structural Analysis"

    target_path, target_key = _target_module_path(root, abbrev)
    assert os.path.isfile(target_path), "missing target module %s" % target_path
    _assert_stubs(root, target_key)
    return cfg, _read(target_path), target_key


def assert_bug_branch(root, abbrev, version="2.6", language="python"):
    """Bug: defects only in target module; partial tests; no TCC tooling."""
    _, target_src, target_key = _assert_common(root, abbrev, "Bug", version, language)

    marker = BUG_TARGET_MARKERS[target_key]
    assert marker(target_src), (
        "Bug target sa/%s.py missing expected defect markers for %s" % (target_key, abbrev)
    )
    _assert_no_forbidden(root)

    for name in TCC_CONFIG_FILES:
        assert not os.path.isfile(os.path.join(root, name)), "Bug branch must not include %s" % name

    test_count, test_files = _count_test_methods(os.path.join(root, "tests"))
    smoke = [f for f, _ in test_files if "_smoke" in f]
    assert not smoke, "Bug branch must not use smoke-only tests"
    if abbrev in ("EPI", "TDI"):
        assert test_count <= 1, "Bug %s expects at most one weak test, got %d" % (abbrev, test_count)
    else:
        assert 1 <= test_count <= 2, "Bug %s expects partial tests (1-2), got %d in %s" % (
            abbrev, test_count, test_files)

    target_lines = _line_count(_target_module_path(root, abbrev)[0])
    assert target_lines > 100, "Bug target module should be large (defect-heavy), got %d lines" % target_lines


def assert_bugfx_branch(root, abbrev, version="2.6", language="python"):
    """BugFX: fixed target module; full tests; clean variant (no defect markers)."""
    _, target_src, target_key = _assert_common(root, abbrev, "BugFX", version, language)

    marker = BUG_TARGET_MARKERS[target_key]
    assert not marker(target_src), (
        "BugFX target sa/%s.py still contains Bug defect markers" % target_key
    )
    _assert_no_forbidden(root)

    for name in TCC_CONFIG_FILES:
        assert not os.path.isfile(os.path.join(root, name)), "BugFX must not include %s" % name

    test_count, test_files = _count_test_methods(os.path.join(root, "tests"))
    min_tests = FULL_TEST_MIN_METHODS.get(abbrev, 2)
    assert test_count >= min_tests, "BugFX expects full test suite (>=%d methods), got %d in %s" % (
        min_tests, test_count, test_files)
    smoke = [f for f, _ in test_files if "_smoke" in f]
    assert not smoke, "BugFX must not use smoke-only tests"


def assert_tcc_branch(root, abbrev, version="2.6", language="python"):
    """TCC: tool configs + TOOL_MODE target module + tool-oriented tests."""
    _, target_src, target_key = _assert_common(root, abbrev, "TCC", version, language)

    marker = TCC_TARGET_MARKERS[target_key]
    assert marker(target_src), (
        "TCC target sa/%s.py missing expected branch-ladder style for %s" % (target_key, abbrev)
    )
    _assert_no_forbidden(root)

    for name in TCC_CONFIG_FILES:
        path = os.path.join(root, name)
        assert os.path.isfile(path), "TCC branch missing required file %s" % name

    req = _read(os.path.join(root, "requirements.txt"))
    for pkg in ("coverage", "radon", "testmon"):
        assert pkg in req, "TCC requirements.txt must list %s" % pkg

    test_count, test_files = _count_test_methods(os.path.join(root, "tests"))
    min_tests = FULL_TEST_MIN_METHODS.get(abbrev, 2)
    assert test_count >= min_tests, "TCC expects full tool-oriented tests (>=%d), got %d in %s" % (
        min_tests, test_count, test_files)
    smoke = [f for f, _ in test_files if "_smoke" in f]
    assert not smoke, "TCC must not use smoke-only tests"


def assert_cc_branch(root, abbrev, version="2.6", language="python"):
    """CC: general clean target module; smoke test only; no tool configs."""
    _, target_src, target_key = _assert_common(root, abbrev, "CC", version, language)

    marker = CC_TARGET_MARKERS[target_key]
    assert marker(target_src), (
        "CC target sa/%s.py missing table/lookup clean-code style for %s" % (target_key, abbrev)
    )
    bug_marker = BUG_TARGET_MARKERS[target_key]
    assert not bug_marker(target_src), "CC target must not contain Bug defect markers"
    _assert_no_forbidden(root)

    for name in TCC_CONFIG_FILES:
        assert not os.path.isfile(os.path.join(root, name)), "CC must not include %s" % name

    tests_dir = os.path.join(root, "tests")
    test_count, test_files = _count_test_methods(tests_dir)
    min_tests = FULL_TEST_MIN_METHODS.get(abbrev, 12)
    assert test_count >= min_tests, "CC expects full parametrized tests (>=%d), got %d in %s" % (
        min_tests, test_count, test_files)
    smoke = [f for f, _ in test_files if "_smoke" in f]
    assert not smoke, "CC must not use smoke-only tests"


TYPE_ASSERTERS = {
    "Bug": assert_bug_branch,
    "BugFX": assert_bugfx_branch,
    "TCC": assert_tcc_branch,
    "CC": assert_cc_branch,
}


def validate_branch(root, abbrev=None, branch_type=None, version="2.6", language="python"):
    """
    Run the type-specific assert validator for one build folder.
    abbrev / branch_type inferred from folder name when omitted.
    Returns (branch_name, branch_type) on success; raises BranchValidationError on failure.
    """
    folder = os.path.basename(os.path.normpath(root))
    parts = folder.split("_")
    if abbrev is None or branch_type is None:
        assert len(parts) >= 4 and parts[0] == "SA", "cannot parse branch folder: %s" % folder
        abbrev = abbrev or parts[1]
        branch_type = branch_type or parts[2]
        if version == "2.6" and len(parts) >= 4:
            version = parts[3]

    assert branch_type in TYPE_ASSERTERS, "unknown branch type %r" % branch_type
    try:
        TYPE_ASSERTERS[branch_type](root, abbrev, version, language)
    except AssertionError as exc:
        raise BranchValidationError("%s / %s: %s" % (folder, branch_type, exc)) from exc
    return folder, branch_type


def validate_build(metrics="all", version="2.6", language="python", build_dir="build", root=None):
    """
    Validate all generated branches under build_dir.
    Returns list of (branch_name, branch_type) for successes.
    """
    repo_root = root or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out = []
    failures = []
    for abbrev in parse_metrics_arg(metrics):
        for bt in BRANCH_TYPES:
            bname = branch_name(abbrev, bt, version)
            path = os.path.join(repo_root, build_dir, bname)
            if not os.path.isdir(path):
                failures.append((bname, "build folder missing: %s" % path))
                continue
            try:
                validate_branch(path, abbrev, bt, version, language)
                out.append((bname, bt))
            except BranchValidationError as exc:
                failures.append((bname, str(exc)))

    if failures:
        lines = ["Branch validation failed (%d):" % len(failures)]
        for name, msg in failures:
            lines.append("  - %s: %s" % (name, msg))
        raise BranchValidationError("\n".join(lines))
    return out


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Assert-validate generated SA metric branches")
    parser.add_argument("--metrics", default="all")
    parser.add_argument("--version", default="2.6")
    parser.add_argument("--language", default="python")
    parser.add_argument("--build-dir", default="build")
    parser.add_argument("--branch", help="Validate one build folder name or path")
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if args.branch:
        path = args.branch
        if not os.path.isdir(path):
            path = os.path.join(repo_root, args.build_dir, args.branch)
        name, bt = validate_branch(path, version=args.version, language=args.language)
        print("OK  %s (%s)" % (name, bt))
        return 0

    results = validate_build(args.metrics, args.version, args.language, args.build_dir, repo_root)
    for name, bt in results:
        print("OK  %s (%s)" % (name, bt))
    print("\nAll %d branches passed validation." % len(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
