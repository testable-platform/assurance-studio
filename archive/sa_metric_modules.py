# ARCHIVED: superseded by lib/sa_generator.py
"""Backward-compatible shim — generation logic lives in lib.sa_generator."""

from __future__ import print_function

from lib.sa_generator import (  # noqa: F401
    METRIC_META,
    TARGET_GENERATORS,
    _stub_metric_module,
    n_functions,
)


def generate_module_content(module_key, variant):
    abbrev = METRIC_META[module_key][0]
    return TARGET_GENERATORS[module_key](variant, n_functions(abbrev))


def gen_metric_stub(module_key, metric_name, tool_primary):
    return _stub_metric_module(module_key)


def gen_bulk_empty(name):
    return "from __future__ import print_function\n" + '"""%s — placeholder module."""\n' % name
