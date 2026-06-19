"""Pure helpers for strength score comparison display."""

from __future__ import print_function

SCORE_CEILING = 99.5


def score_progress_display(prev, cur, ceiling=SCORE_CEILING):
    """Format prev->cur score progress for UI delta column."""
    if cur is None:
        return "—"
    try:
        cur_f = float(cur)
    except (TypeError, ValueError):
        return "—"
    if cur_f >= ceiling:
        return "maxed"
    if prev is None:
        return "—"
    try:
        prev_f = float(prev)
    except (TypeError, ValueError):
        return "—"
    delta = cur_f - prev_f
    if delta > 0:
        label = "+%.1f" % delta
    else:
        label = "%.1f" % delta
    if cur_f >= ceiling - 0.05:
        return "%s -> max" % label
    return label
