"""Shared generation constants and helpers for all languages."""

from __future__ import print_function

MIN_LOC = 2500
BASE_STRENGTH_FLOOR = 4
DEFAULT_N_FUNCTIONS = 72
VARIANT_MAP = {"Bug": "bug", "BugFX": "bugfx", "TCC": "tcc", "CC": "cc"}


def _raw_strength(strength):
    try:
        return max(0, int(strength or 0))
    except (TypeError, ValueError):
        return 0


def effective_strength(strength):
    """Floor only brand-new branches (strength 0); regeneration keeps raw strength."""
    s = _raw_strength(strength)
    if s <= 0:
        return BASE_STRENGTH_FLOOR
    return s


def scaled_n_functions(base_n, strength):
    s = _raw_strength(strength)
    if s <= 0:
        s = BASE_STRENGTH_FLOOR
    return min(180, base_n + s * 4)


def scaled_test_count(n_fn, branch_type, strength):
    if branch_type == "Bug":
        return 1
    s = effective_strength(strength)
    ratio = min(1.0, 0.55 + 0.11 * (s - BASE_STRENGTH_FLOOR))
    target = int(round(n_fn * ratio))
    return max(16, min(n_fn, target))


def variant_marker(variant, idx, strength):
    if variant == "bug":
        return "escalated-%d" % idx
    if variant == "bugfx":
        return "resolved-%d" % idx
    if variant == "tcc":
        return ("disabled-%d" % idx) if idx % 2 else ("audit-strict-%d" % idx)
    return "neutral-%d" % idx
