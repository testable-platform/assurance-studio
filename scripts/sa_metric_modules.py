"""Metric-targeted SA module generators — bug vs clean for taxonomy differentiation."""

from __future__ import print_function

import textwrap

FUTURE = "from __future__ import print_function\n"


def _nest(depth, body_indent="    "):
    lines = []
    for i in range(depth):
        pad = body_indent * (i + 1)
        lines.append("%sif value > %d:\n" % (pad, i))
    lines.append("%s    result = 'deep-%d'\n" % (body_indent * depth, depth))
    for i in range(depth - 1, -1, -1):
        pad = body_indent * (i + 1)
        lines.append("%selse:\n" % pad)
        lines.append("%s    result = 'level-%d'\n" % (pad, i))
    return "\n".join(lines)


def _flat_if_chain(prefix, count=55):
    """Independent if branches — Radon CC > 50 per function (drives EPI FAIL via avg_ccn > 50)."""
    lines = []
    for i in range(count):
        lines.append("    if value == %d:" % i)
        lines.append("        return '%s-%d'" % (prefix, i))
    lines.append("    return '%s-default'" % prefix)
    return "\n".join(lines)


def gen_metric_stub(module_key, metric_name, tool_primary):
    """Non-target module — minimal CC stubs so tests/imports work but Radon stays low."""
    apis = {
        "execution_path_integrity": (
            "def evaluate_path_integrity(value, mode, flags):\n"
            "    return 'ok-%s' % value\n"
            "def route_handler_1(payload):\n"
            "    return 'ok'\n"
        ),
        "decision_coverage": (
            "def aggregate_decision_coverage(cases):\n"
            "    return 1.0\n"
            "def decision_case_0(state, enabled, retry_count):\n"
            "    return 'ok'\n"
        ),
        "condition_coverage": (
            "def condition_check_0(a, b, c, d, flag):\n"
            "    return 'ok'\n"
            "def validate_all_conditions(inputs):\n"
            "    return []\n"
        ),
        "logic_combinatorial": (
            "def count_unique_paths(function_name, input_size):\n"
            "    return 2 ** input_size\n"
            "def combinatorial_state_machine_0(bits):\n"
            "    return 'S0'\n"
        ),
        "technical_debt": (
            "def debt_calculator_b0_v0(amount, rate, years):\n"
            "    return float(amount)\n"
        ),
        "qa_prioritization": (
            "def prioritize_test_bucket_0(modules, history):\n"
            "    return []\n"
        ),
    }
    return FUTURE + (
        "METRIC_NAME = '%s'\n"
        "TOOL_PRIMARY = '%s'\n\n"
        "%s"
    ) % (metric_name, tool_primary, apis.get(module_key, ""))


def gen_epi_bug(route_handlers=70):
    helpers = []
    for n in range(1, route_handlers + 1):
        body = _flat_if_chain("route-%d" % n, count=80)
        helpers.append(
            "def route_handler_%d(payload):\n"
            "    value = payload.get('value', 0)\n"
            "%s\n" % (n, body)
        )
    head = (
        "def evaluate_path_integrity(value, mode, flags):\n"
        "%s\n"
        "    if mode == 'audit':\n"
        "        return suffix_token\n"
        "    return 'done'\n"
        % _flat_if_chain("epi", count=80)
    )
    hdr = FUTURE + "METRIC_NAME = 'Execution Path Integrity'\nTOOL_PRIMARY = 'Crosshair'\n\n"
    return hdr + head + "\n\n" + "\n\n".join(helpers)


def gen_epi_clean(route_handlers=12):
    helpers = []
    for n in range(1, route_handlers + 1):
        helpers.append(
            "def route_handler_%d(payload):\n"
            "    if not isinstance(payload, dict):\n"
            "        return 'invalid'\n"
            "    value = payload.get('value', 0)\n"
            "    if value < 0:\n"
            "        return 'negative'\n"
            "    return 'ok-%%s' %% value\n" % n
        )
    head = textwrap.dedent(
        '''
        def evaluate_path_integrity(value, mode, flags):
            if not isinstance(flags, dict):
                flags = {}
            if value < 0:
                return 'invalid'
            if mode == 'audit':
                return 'audit-%s' % value
            return 'ok-%s' % value
        '''
    ).strip()
    hdr = FUTURE + "METRIC_NAME = 'Execution Path Integrity'\nTOOL_PRIMARY = 'Crosshair'\n\n"
    return hdr + head + "\n\n" + "\n\n".join(helpers)


def gen_dov_bug(cases=45):
    funcs = []
    for i in range(cases):
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
    agg = (
        "def aggregate_decision_coverage(cases):\n"
        "    covered = sum(1 for c in cases if c.get('covered'))\n"
        "    total = len(cases)\n"
        "    return float(covered) / total\n"
    )
    return FUTURE + "METRIC_NAME = 'Decision Outcome Verification'\nTOOL_PRIMARY = 'Coverage.py'\n\n" + "\n\n".join(funcs) + "\n\n" + agg


def gen_dov_clean(cases=20):
    funcs = []
    for i in range(cases):
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
    )
    return FUTURE + "METRIC_NAME = 'Decision Outcome Verification'\nTOOL_PRIMARY = 'Coverage.py'\n\n" + "\n\n".join(funcs) + "\n\n" + agg


def gen_lsv_bug(checks=45):
    funcs = []
    for i in range(checks):
        funcs.append(
            "def condition_check_%d(a, b, c, d, flag):\n"
            "    if (a and b) or (c and not d) and flag:\n"
            "        return 'accept-%d'\n"
            "    if a or b and c:\n"
            "        return 'partial-%d'\n"
            "    return 'reject-%d'\n" % (i, i, i, i)
        )
    helper = (
        "def validate_all_conditions(inputs):\n"
        "    results = []\n"
        "    for idx, item in enumerate(inputs):\n"
        "        results.append(condition_check_0(\n"
        "            item.get('a'), item.get('b'), item.get('c'), item.get('d'), item.get('flag')))\n"
        "    return results, results[idx]\n"
    )
    return FUTURE + "METRIC_NAME = 'Logical Sub-expression Validation'\nTOOL_PRIMARY = 'Pymcdc'\n\n" + "\n\n".join(funcs) + "\n\n" + helper


def gen_lsv_clean(checks=20):
    funcs = []
    for i in range(checks):
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
    return FUTURE + "METRIC_NAME = 'Logical Sub-expression Validation'\nTOOL_PRIMARY = 'Pymcdc'\n\n" + "\n\n".join(funcs) + "\n\n" + helper


def gen_tlcc_bug(machines=35):
    lines = [FUTURE + "METRIC_NAME = 'Total Logical Combinatorial Coverage'\nTOOL_PRIMARY = 'Crosshair'\n\n"]
    for i in range(machines):
        lines.append("def combinatorial_state_machine_%d(bits):\n" % i)
        lines.append("    state = 'S0'\n")
        for b in range(12):
            lines.append("    if bits[%d]:\n" % (b % 4))
            lines.append("        state = state + 'A%d'\n" % b)
            lines.append("    else:\n")
            lines.append("        state = state + 'B%d'\n" % b)
        lines.append("    if len(bits) > 500:\n")
        lines.append("        state = ghost_state_marker\n")
        lines.append("    return state\n\n")
    lines.append("def count_unique_paths(function_name, input_size):\n    return input_size - input_size\n")
    return "".join(lines)


def gen_tlcc_clean(machines=15):
    lines = [FUTURE + "METRIC_NAME = 'Total Logical Combinatorial Coverage'\nTOOL_PRIMARY = 'Crosshair'\n\n"]
    for i in range(machines):
        lines.append(
            "def combinatorial_state_machine_%d(bits):\n"
            "    if not bits:\n"
            "        return 'S0'\n"
            "    state = 'S0'\n"
            "    for idx, bit in enumerate(bits):\n"
            "        if bit:\n"
            "            state = state + 'A'\n"
            "        else:\n"
            "            state = state + 'B'\n"
            "    return state\n\n" % i
        )
    lines.append("def count_unique_paths(function_name, input_size):\n    if input_size < 0:\n        return 0\n    return 2 ** input_size\n")
    return "".join(lines)


def gen_tdi_bug(blocks=70, variants=1):
    chunks = [FUTURE + "METRIC_NAME = 'Technical Debt Impact'\nTOOL_PRIMARY = 'Radon/Lizard'\n"]
    for block in range(blocks):
        for i in range(variants):
            body = _flat_if_chain("debt-%d-%d" % (block, i), count=80)
            chunks.append(
                ("def debt_calculator_b%d_v%d(amount, rate, years):\n"
                 "    value = amount + years\n"
                 "%s\n") % (block, i, body)
            )
    return "\n\n".join(chunks)


def gen_tdi_clean(blocks=15, variants=5):
    chunks = [FUTURE + "METRIC_NAME = 'Technical Debt Impact'\nTOOL_PRIMARY = 'Radon/Lizard'\n"]
    for block in range(blocks):
        for i in range(variants):
            chunks.append(
                "def debt_calculator_b%d_v%d(amount, rate, years):\n"
                "    if years < 0:\n"
                "        raise ValueError('invalid years')\n"
                "    total = float(amount)\n"
                "    for year in range(years):\n"
                "        total += total * rate\n"
                "    return max(total, 0.0)\n" % (block, i)
            )
    return "\n\n".join(chunks)


def gen_qra_bug(buckets=40):
    lines = [FUTURE + "METRIC_NAME = 'QA Resource Allocation'\nTOOL_PRIMARY = 'testmon'\n\n"]
    for i in range(buckets):
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
    return "".join(lines)


def gen_qra_clean(buckets=15):
    lines = [FUTURE + "METRIC_NAME = 'QA Resource Allocation'\nTOOL_PRIMARY = 'testmon'\n\n"]
    for i in range(buckets):
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


def gen_bulk_empty(name):
    return FUTURE + '"""%s — constants only; excluded from cyclomatic rollup."""\n\n' % name


MODULE_BUG_CLEAN = {
    "execution_path_integrity": (gen_epi_bug, gen_epi_clean),
    "decision_coverage": (gen_dov_bug, gen_dov_clean),
    "condition_coverage": (gen_lsv_bug, gen_lsv_clean),
    "logic_combinatorial": (gen_tlcc_bug, gen_tlcc_clean),
    "technical_debt": (gen_tdi_bug, gen_tdi_clean),
    "qa_prioritization": (gen_qra_bug, gen_qra_clean),
}


def generate_module_content(module_key, variant):
    bug_fn, clean_fn = MODULE_BUG_CLEAN[module_key]
    if variant == "bug":
        return bug_fn()
    return clean_fn()
