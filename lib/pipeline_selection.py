"""Shared filter helpers for CLI and Streamlit UI."""

from __future__ import print_function

from lib.registry import all_techniques, iter_branches, load_registry, parse_metrics_filter, parse_techniques_arg, parse_types_arg


def selection_summary(techniques="all", metrics="all", types=None, version="2.6", registry=None):
    branches = list(iter_branches(techniques, metrics, types, version, registry))
    return {
        "techniques": parse_techniques_arg(techniques, registry),
        "metrics_filter": metrics,
        "types": parse_types_arg(types, registry),
        "version": version,
        "branch_count": len(branches),
        "branches": [b[3] for b in branches],
    }


def technique_options(registry=None):
    reg = registry or load_registry()
    return [(t["technique_code"], "%s — %s" % (t["technique_code"], t.get("l2", ""))) for t in all_techniques(reg)]


def metric_options(technique_code, registry=None):
    reg = registry or load_registry()
    return parse_metrics_filter("all", technique_code, reg)


def branch_type_options(registry=None):
    reg = registry or load_registry()
    return parse_types_arg(None, reg)


def csv_from_list(items):
    if not items:
        return "all"
    if isinstance(items, str):
        return items
    return ",".join(items)
