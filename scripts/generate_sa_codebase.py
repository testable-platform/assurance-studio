#!/usr/bin/env python3
"""Generate large Structural Analysis Python 2.6 codebases for SA_* branches."""

from __future__ import print_function

import argparse
import os
import textwrap

FUTURE = "from __future__ import print_function\n"

METRICS = [
    ("execution_path_integrity", "Static Analysis Metric", "Execution Path Integrity", "Crosshair"),
    ("decision_coverage", "Decision Coverage", "Decision Outcome Verification", "Coverage.py"),
    ("condition_coverage", "Condition Coverage", "Logical Sub-expression Validation", "Pymcdc"),
    ("logic_combinatorial", "Logic Coverage Metric", "Total Logical Combinatorial Coverage", "Crosshair"),
    ("technical_debt", "Maintainability Analysis", "Technical Debt Impact", "Radon/Lizard"),
    ("qa_prioritization", "Test Prioritization", "QA Resource Allocation", "testmon"),
]

SCALE = {
    "route_handlers": 45,
    "decision_cases": 40,
    "condition_checks": 40,
    "state_machines": 28,
    "debt_blocks": 25,
    "debt_variants": 10,
    "qa_buckets": 35,
    "bulk_rules": 80,
    "bulk_signals": 60,
    "bulk_integrations": 50,
}


def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def write_file(root, rel, content):
    path = os.path.join(root, rel)
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    return path


def gen_init():
    return FUTURE + '"""Structural Analysis package for Python 2.6."""\n\n__version__ = \'2.0.0\'\n'


def gen_config(variant):
    tools = "\n".join(
        "    '%s': {'classification': '%s', 'metric': '%s', 'tool': '%s'}," % (m, c, met, t)
        for m, c, met, t in METRICS
    )
    variant_label = {"bugfx": "bugFX"}.get(variant, variant)
    return FUTURE + textwrap.dedent(
        '''
        """Runtime configuration for Structural Analysis modules."""
        PYTHON_VERSION = '2.6'
        BRANCH_VARIANT = '%(variant)s'
        TESTING_TYPE = 'Structural Analysis'
        METRIC_TOOL_MAP = {
        %(tools)s
        }
        DEFAULT_THRESHOLDS = {
            'cyclomatic_complexity_warn': 10,
            'cyclomatic_complexity_fail': 20,
            'maintainability_index_min': 65,
            'decision_coverage_min': 0.85,
            'condition_coverage_min': 0.80,
            'path_coverage_min': 0.75,
        }
        def get_tool_for_metric(metric_name):
            for entry in METRIC_TOOL_MAP.values():
                if entry['metric'] == metric_name:
                    return entry['tool']
            return None
        '''
    ) % {"variant": variant_label, "tools": tools}


def gen_models(variant):
    bug = variant == "bug"
    body = textwrap.dedent(
        '''
        class AnalysisRecord(object):
            def __init__(self, record_id, source_path, metric_name, score, status):
                self.record_id = record_id
                self.source_path = source_path
                self.metric_name = metric_name
                self.score = score
                self.status = status
                self.tags = []
            def add_tag(self, tag):
                if tag not in self.tags:
                    self.tags.append(tag)
            def is_passing(self):
                return self.status == 'pass'
            def summary(self):
                return '%s:%s score=%s status=%s' % (
                    self.record_id, self.metric_name, self.score, self.status)
        class RepositorySnapshot(object):
            def __init__(self, name, loc, language_version):
                self.name = name
                self.loc = loc
                self.language_version = language_version
                self.modules = []
                self.complexity_scores = {}
            def register_module(self, module_name, complexity):
                self.modules.append(module_name)
                self.complexity_scores[module_name] = complexity
            def total_complexity(self):
                total = 0
                for module_name in self.modules:
                    total += self.complexity_scores.get(module_name, 0)
                return total
            def average_complexity(self):
                if not self.modules:
                    return 0
                return float(self.total_complexity()) / len(self.modules)
        class WorkflowContext(object):
            def __init__(self, workflow_id, operator):
                self.workflow_id = workflow_id
                self.operator = operator
                self.steps_completed = []
                self.errors = []
                self.metadata = {}
            def mark_step(self, step_name):
                self.steps_completed.append(step_name)
            def add_error(self, message):
                self.errors.append(message)
            def has_errors(self):
                return len(self.errors) > 0
        '''
    )
    if bug:
        tail = textwrap.dedent(
            '''
            def build_default_tags(tags=[]):
                tags.append('generated')
                return tags
            '''
        )
    else:
        tail = textwrap.dedent(
            '''
            def build_default_tags(tags=None):
                if tags is None:
                    tags = []
                tags.append('generated')
                return tags
            '''
        )
    return FUTURE + body + tail


def gen_decision_tree_block(prefix, variant, start=0):
    bug = variant == "bug"
    lines = []
    indent = "    "
    for i in range(16):
        idx = start + i
        cond = "value == %d" % idx
        if i == 0:
            lines.append("%sif %s:\n" % (indent, cond))
        else:
            lines.append("%selif %s:\n" % (indent, cond))
        lines.append("%s    result = '%s-path-%d'\n" % (indent, prefix, idx))
        if bug and i == 7:
            lines.append("%s    return result\n" % indent)
            lines.append("%s    result = 'unreachable-%s'\n" % (indent, prefix))
        if bug and i == 11:
            lines.append("%selif value > 9999 and value < 0:\n" % indent)
            lines.append("%s    result = 'impossible-%s'\n" % (indent, prefix))
    lines.append("%selse:\n" % indent)
    lines.append("%s    result = '%s-default'\n" % (indent, prefix))
    return "\n".join(lines)


def gen_path_integrity(variant):
    bug = variant == "bug"
    body = gen_decision_tree_block("epi", variant)
    if bug:
        head = (
            "def evaluate_path_integrity(value, mode, flags):\n"
            "    result = 'unknown'\n"
            "    multiplier = flags.get('multiplier')\n"
            + body + "\n"
            "    if mode == 'audit':\n"
            "        result = result + suffix_token\n"
            "    return result\n"
        )
    else:
        head = (
            "def evaluate_path_integrity(value, mode, flags):\n"
            "    result = 'unknown'\n"
            "    if not isinstance(flags, dict):\n"
            "        flags = {}\n"
            + body + "\n"
            "    if mode == 'audit':\n"
            "        result = result + flags.get('suffix', '')\n"
            "    return result\n"
        )
    helpers = []
    for n in range(1, SCALE["route_handlers"] + 1):
        block = gen_decision_tree_block("route-%d" % n, variant, start=n * 20)
        if bug:
            helpers.append(
                "def route_handler_%d(payload):\n"
                "    value = payload.get('value', 0)\n"
                "    result = 'init'\n%s\n"
                "    return result\n" % (n, block)
            )
        else:
            helpers.append(
                "def route_handler_%d(payload):\n"
                "    if not isinstance(payload, dict):\n"
                "        return 'invalid'\n"
                "    value = payload.get('value', 0)\n"
                "    result = 'init'\n%s\n"
                "    return result\n" % (n, block)
            )
    hdr = FUTURE + 'METRIC_NAME = \'Execution Path Integrity\'\nTOOL_PRIMARY = \'Crosshair\'\n\n'
    return hdr + head + "\n\n" + "\n\n".join(helpers)


def gen_decision_coverage(variant):
    bug = variant == "bug"
    funcs = []
    for i in range(SCALE["decision_cases"]):
        if bug:
            funcs.append(
                "def decision_case_%d(state, enabled, retry_count):\n"
                "    outcome = 'pending'\n"
                "    if state == 'ready' and enabled:\n"
                "        outcome = 'started'\n"
                "    elif state == 'failed':\n"
                "        outcome = 'failed'\n"
                "    elif retry_count > 3:\n"
                "        outcome = 'retry-exhausted'\n"
                "    else:\n"
                "        outcome = 'unknown'\n"
                "    if False:\n"
                "        outcome = 'phantom-%d'\n"
                "    return outcome + '-%d'\n" % (i, i, i)
            )
        else:
            funcs.append(
                "def decision_case_%d(state, enabled, retry_count):\n"
                "    if state == 'ready' and enabled:\n"
                "        return 'started-%d'\n"
                "    if state == 'failed':\n"
                "        return 'failed-%d'\n"
                "    if retry_count > 3:\n"
                "        return 'retry-exhausted-%d'\n"
                "    return 'unknown-%d'\n" % (i, i, i, i, i)
            )
    agg = (
        "def aggregate_decision_coverage(cases):\n"
        "    if not cases:\n"
        "        return 1.0\n"
        "    covered = sum(1 for c in cases if c.get('covered'))\n"
        "    return float(covered) / len(cases)\n"
    ) if not bug else (
        "def aggregate_decision_coverage(cases):\n"
        "    covered = sum(1 for c in cases if c.get('covered'))\n"
        "    total = len(cases)\n"
        "    return float(covered) / total\n"
    )
    return FUTURE + "METRIC_NAME = 'Decision Outcome Verification'\nTOOL_PRIMARY = 'Coverage.py'\n\n" + "\n\n".join(funcs) + "\n\n" + agg


def gen_condition_coverage(variant):
    bug = variant == "bug"
    funcs = []
    for i in range(SCALE["condition_checks"]):
        if bug:
            funcs.append(
                "def condition_check_%d(a, b, c, d, flag):\n"
                "    if (a and b) or (c and not d) and flag:\n"
                "        return 'accept-%d'\n"
                "    if a or b and c:\n"
                "        return 'partial-%d'\n"
                "    return 'reject-%d'\n" % (i, i, i, i)
            )
        else:
            funcs.append(
                "def condition_check_%d(a, b, c, d, flag):\n"
                "    if flag and ((a and b) or (c and not d)):\n"
                "        return 'accept-%d'\n"
                "    if (a or b) and c:\n"
                "        return 'partial-%d'\n"
                "    return 'reject-%d'\n" % (i, i, i, i)
            )
    helper = (
        "def validate_all_conditions(inputs):\n"
        "    results = []\n"
        "    for item in inputs:\n"
        "        results.append(condition_check_0(\n"
        "            item.get('a'), item.get('b'), item.get('c'), item.get('d'), item.get('flag')))\n"
        "    return results\n"
    )
    if bug:
        helper = (
            "def validate_all_conditions(inputs):\n"
            "    results = []\n"
            "    for idx, item in enumerate(inputs):\n"
            "        results.append(condition_check_0(\n"
            "            item.get('a'), item.get('b'), item.get('c'), item.get('d'), item.get('flag')))\n"
            "    return results, results[idx]\n"
        )
    return FUTURE + "METRIC_NAME = 'Logical Sub-expression Validation'\nTOOL_PRIMARY = 'Pymcdc'\n\n" + "\n\n".join(funcs) + "\n\n" + helper


def gen_logic_combinatorial(variant):
    bug = variant == "bug"
    lines = [FUTURE + "METRIC_NAME = 'Total Logical Combinatorial Coverage'\nTOOL_PRIMARY = 'Crosshair'\n\n"]
    for i in range(SCALE["state_machines"]):
        lines.append("def combinatorial_state_machine_%d(bits):\n" % i)
        lines.append("    state = 'S0'\n")
        for b in range(10):
            lines.append("    if bits[%d]:\n" % (b % 4))
            lines.append("        state = state + 'A%d'\n" % b)
            lines.append("    else:\n")
            lines.append("        state = state + 'B%d'\n" % b)
        if bug:
            lines.append("    if len(bits) > 500:\n")
            lines.append("        state = ghost_state_marker\n")
        lines.append("    return state\n\n")
    if bug:
        lines.append("def count_unique_paths(function_name, input_size):\n    return input_size - input_size\n")
    else:
        lines.append("def count_unique_paths(function_name, input_size):\n    return 2 ** input_size\n")
    return "".join(lines)


def gen_technical_debt(variant):
    bug = variant == "bug"
    chunks = [FUTURE + "METRIC_NAME = 'Technical Debt Impact'\nTOOL_PRIMARY = 'Radon/Lizard'\n"]
    for block in range(SCALE["debt_blocks"]):
        for i in range(SCALE["debt_variants"]):
            if bug:
                chunks.append(
                    "def debt_calculator_b%d_v%d(amount, rate, years):\n"
                    "    total = amount\n"
                    "    for year in range(years):\n"
                    "        total = total + total * rate\n"
                    "        if year %% 2 == 0:\n"
                    "            total = total + 1\n"
                    "        else:\n"
                    "            total = total - 1\n"
                    "    if rate > 1:\n"
                    "        total = total * rate\n"
                    "    return total\n" % (block, i)
                )
            else:
                chunks.append(
                    "def debt_calculator_b%d_v%d(amount, rate, years):\n"
                    "    if years < 0:\n"
                    "        raise ValueError('invalid years')\n"
                    "    total = float(amount)\n"
                    "    for year in range(years):\n"
                    "        total += total * rate\n"
                    "        if year %% 2 == 0:\n"
                    "            total += 1\n"
                    "        else:\n"
                    "            total -= 1\n"
                    "    return max(total, 0.0)\n" % (block, i)
                )
    return "\n\n".join(chunks)


def gen_qa_prioritization(variant):
    bug = variant == "bug"
    lines = [FUTURE + "METRIC_NAME = 'QA Resource Allocation'\nTOOL_PRIMARY = 'testmon'\n\n"]
    for i in range(SCALE["qa_buckets"]):
        if bug:
            lines.append(
                "def prioritize_test_bucket_%d(modules, history):\n"
                "    ranking = []\n"
                "    for module in modules:\n"
                "        score = module.get('complexity', 0)\n"
                "        if score > 10:\n"
                "            ranking.append((module['name'], 'high'))\n"
                "        else:\n"
                "            ranking.append((module['name'], 'low'))\n"
                "    modules.append({'name': 'ghost-%d'})\n"
                "    return ranking\n\n" % (i, i)
            )
        else:
            lines.append(
                "def prioritize_test_bucket_%d(modules, history):\n"
                "    ranking = []\n"
                "    history = history or {}\n"
                "    for module in modules:\n"
                "        name = module.get('name', 'unknown')\n"
                "        score = module.get('complexity', 0) + history.get(name, 0)\n"
                "        bucket = 'high' if score > 10 else 'low'\n"
                "        ranking.append((name, bucket))\n"
                "    return ranking\n\n" % i
            )
    return "".join(lines)


def gen_bulk_module(name, prefix, count, variant):
    bug = variant == "bug"
    lines = [FUTURE + '"""Generated bulk module for structural complexity."""\n\n']
    for i in range(count):
        block = gen_decision_tree_block("%s-%d" % (prefix, i), variant, start=i * 15)
        if bug:
            lines.append(
                "def %s_handler_%d(ctx):\n"
                "    value = ctx.get('value', 0)\n"
                "    result = 'init'\n%s\n"
                "    if ctx.get('broken'):\n"
                "        result = result + broken_ref_%d\n"
                "    return result\n\n" % (prefix, i, block, i)
            )
        else:
            lines.append(
                "def %s_handler_%d(ctx):\n"
                "    if not isinstance(ctx, dict):\n"
                "        return 'invalid'\n"
                "    value = ctx.get('value', 0)\n"
                "    result = 'init'\n%s\n"
                "    return result\n\n" % (prefix, i, block)
            )
    return "".join(lines)


def gen_repository(variant):
    if variant == "bug":
        return FUTURE + textwrap.dedent(
            '''
            class AnalysisRepository(object):
                def __init__(self):
                    self._records = {}
                def save(self, record):
                    self._records[record.record_id] = record
                def get(self, record_id):
                    return self._records[record_id]
                def list_by_metric(self, metric_name):
                    results = []
                    for record in self._records.values():
                        if record.metric_name is metric_name:
                            results.append(record)
                    return results
            '''
        )
    return FUTURE + textwrap.dedent(
        '''
        class AnalysisRepository(object):
            def __init__(self):
                self._records = {}
            def save(self, record):
                self._records[record.record_id] = record
            def get(self, record_id):
                return self._records.get(record_id)
            def list_by_metric(self, metric_name):
                return [r for r in self._records.values() if r.metric_name == metric_name]
        '''
    )


def gen_workflow(variant):
    return FUTURE + textwrap.dedent(
        '''
        from sa.execution_path_integrity import METRIC_NAME as EPI_METRIC
        from sa.decision_coverage import METRIC_NAME as DC_METRIC
        from sa.condition_coverage import METRIC_NAME as CC_METRIC
        from sa.logic_combinatorial import METRIC_NAME as LC_METRIC
        from sa.technical_debt import METRIC_NAME as TD_METRIC
        from sa.qa_prioritization import METRIC_NAME as QA_METRIC

        class StructuralAnalysisWorkflow(object):
            def __init__(self, repository):
                self.repository = repository
            def run_all(self, snapshot):
                return [
                    {'metric': EPI_METRIC, 'modules': len(snapshot.modules)},
                    {'metric': DC_METRIC, 'modules': len(snapshot.modules)},
                    {'metric': CC_METRIC, 'modules': len(snapshot.modules)},
                    {'metric': LC_METRIC, 'modules': len(snapshot.modules)},
                    {'metric': TD_METRIC, 'total_cc': snapshot.total_complexity()},
                    {'metric': QA_METRIC, 'module_count': len(snapshot.modules)},
                ]
        '''
    )


def gen_reporting(variant):
    return FUTURE + textwrap.dedent(
        '''
        def format_metric_row(metric, classification, tool, score, status):
            return {'metric': metric, 'classification': classification, 'tool': tool, 'score': score, 'status': status}
        def render_text_report(rows):
            lines = ['Structural Analysis Report']
            for row in rows:
                lines.append('%(metric)s tool=%(tool)s score=%(score)s' % row)
            return '\\n'.join(lines)
        '''
    )


def gen_main(variant):
    return FUTURE + textwrap.dedent(
        '''
        from sa.config import BRANCH_VARIANT, TESTING_TYPE, PYTHON_VERSION, METRIC_TOOL_MAP
        from sa.models import RepositorySnapshot, WorkflowContext
        from sa.data_repository import AnalysisRepository
        from sa.workflow_orchestrator import StructuralAnalysisWorkflow
        from sa.reporting import format_metric_row, render_text_report

        def build_snapshot():
            snapshot = RepositorySnapshot('sa-python26', loc=12000, language_version=PYTHON_VERSION)
            for module_name in METRIC_TOOL_MAP.keys():
                snapshot.register_module(module_name, complexity=22)
            return snapshot

        def main():
            print('Branch:', BRANCH_VARIANT, 'Python:', PYTHON_VERSION, 'Type:', TESTING_TYPE)
            workflow = StructuralAnalysisWorkflow(AnalysisRepository())
            snapshot = build_snapshot()
            context = WorkflowContext('wf-001', 'qa-analyst')
            results = workflow.run_all(snapshot)
            rows = [format_metric_row(v['metric'], v['classification'], v['tool'], 75, 'pending')
                    for v in METRIC_TOOL_MAP.values()]
            print(render_text_report(rows))
            print('Results:', len(results), 'Errors:', len(context.errors))

        if __name__ == '__main__':
            main()
        '''
    )


def gen_readme(branch_name, variant):
    desc = {
        "bug": "intentional structural-analysis defects",
        "bugfx": "bug-fixed structural-analysis codebase",
        "tcc": "tool-based clean code (Crosshair, Coverage.py, Pymcdc, Radon/Lizard, testmon)",
        "cc": "general clean code",
    }[variant]
    table = "\n".join("| %s | %s | %s |" % (c, m, t) for _, c, m, t in METRICS)
    return "# %s\n\nPython 2.6 Structural Analysis — %s\n\n| Classification | Metric | Tool |\n|---|---|---|\n%s\n" % (
        branch_name, desc, table
    )


def gen_requirements(variant):
    if variant in ("tcc", "cc"):
        return "# SA Python 2.6\n coverage==3.7.1\nradon==1.4.2\npytest==2.6.4\ntestmon==0.4.5\n"
    return "# Tooling installed by Testable platform\n"


def gen_tests(variant):
    if variant not in ("tcc", "cc"):
        return {}
    t = FUTURE
    return {
        "tests/__init__.py": t,
        "tests/test_execution_path_integrity.py": t + "import unittest\nfrom sa.execution_path_integrity import evaluate_path_integrity\nclass T(unittest.TestCase):\n def test_ok(self):\n  self.assertTrue(evaluate_path_integrity(1,'fast',{}))\n",
        "tests/test_decision_coverage.py": t + "import unittest\nfrom sa.decision_coverage import aggregate_decision_coverage\nclass T(unittest.TestCase):\n def test_empty(self):\n  self.assertEqual(aggregate_decision_coverage([]), 1.0)\n",
        "tests/test_condition_coverage.py": t + "import unittest\nfrom sa.condition_coverage import condition_check_0\nclass T(unittest.TestCase):\n def test_ok(self):\n  self.assertEqual(condition_check_0(True,True,False,True,True), 'accept-0')\n",
        "tests/test_logic_combinatorial.py": t + "import unittest\nfrom sa.logic_combinatorial import count_unique_paths\nclass T(unittest.TestCase):\n def test_ok(self):\n  self.assertEqual(count_unique_paths('x',3), 8)\n",
        "tests/test_technical_debt.py": t + "import unittest\nfrom sa.technical_debt import debt_calculator_b0_v0\nclass T(unittest.TestCase):\n def test_ok(self):\n  self.assertTrue(debt_calculator_b0_v0(100,0.1,2) >= 0)\n",
        "tests/test_qa_prioritization.py": t + "import unittest\nfrom sa.qa_prioritization import prioritize_test_bucket_0\nclass T(unittest.TestCase):\n def test_ok(self):\n  self.assertTrue(prioritize_test_bucket_0([{'name':'a','complexity':1}], {}))\n",
    }


def gen_tool_configs(variant):
    if variant != "tcc":
        return {}
    return {
        ".coveragerc": "[run]\nbranch = True\nsource = sa\n",
        "setup.cfg": "[radon]\ncc_min = A\n",
        "pytest.ini": "[pytest]\ntestpaths = tests\n",
        ".testmondata.ini": "[testmon]\ndepth = module\n",
    }


def generate(root, variant, branch_name):
    ensure_dir(root)
    mapping = {
        "sa/__init__.py": gen_init(),
        "sa/config.py": gen_config(variant),
        "sa/models.py": gen_models(variant),
        "sa/execution_path_integrity.py": gen_path_integrity(variant),
        "sa/decision_coverage.py": gen_decision_coverage(variant),
        "sa/condition_coverage.py": gen_condition_coverage(variant),
        "sa/logic_combinatorial.py": gen_logic_combinatorial(variant),
        "sa/technical_debt.py": gen_technical_debt(variant),
        "sa/qa_prioritization.py": gen_qa_prioritization(variant),
        "sa/rules_engine.py": gen_bulk_module("rules", "rule", SCALE["bulk_rules"], variant),
        "sa/signal_processing.py": gen_bulk_module("signal", "signal", SCALE["bulk_signals"], variant),
        "sa/integration_hub.py": gen_bulk_module("integration", "integration", SCALE["bulk_integrations"], variant),
        "sa/data_repository.py": gen_repository(variant),
        "sa/workflow_orchestrator.py": gen_workflow(variant),
        "sa/reporting.py": gen_reporting(variant),
        "main.py": gen_main(variant),
        "README.md": gen_readme(branch_name, variant),
        "requirements.txt": gen_requirements(variant),
        "versions.txt": open(os.path.join(os.path.dirname(__file__), "..", "versions.txt"), encoding="utf-8").read(),
    }
    for rel, content in mapping.items():
        write_file(root, rel, content)
    for rel, content in gen_tool_configs(variant).items():
        write_file(root, rel, content)
    for rel, content in gen_tests(variant).items():
        write_file(root, rel, content)
    total = 0
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith(".py"):
                with open(os.path.join(dirpath, fn), encoding="utf-8") as fh:
                    total += sum(1 for _ in fh)
    print("Generated %s (%d python lines)" % (branch_name, total))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("variant", choices=["bug", "bugfx", "tcc", "cc", "all"])
    parser.add_argument("--out", default="build")
    args = parser.parse_args()
    names = {"bug": "SA_bug_2.6", "bugfx": "SA_bugFX_2.6", "tcc": "SA_TCC_2.6", "cc": "SA_CC_2.6"}
    variants = names.keys() if args.variant == "all" else [args.variant]
    for v in variants:
        generate(os.path.join(args.out, names[v]), v, names[v])


if __name__ == "__main__":
    main()
