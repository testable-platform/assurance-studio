from __future__ import print_function
METRIC_NAME = 'Decision Outcome Verification'
TOOL_PRIMARY = 'Coverage.py'

def decision_case_0(state, enabled, retry_count, priority):
    """Branch-ladder decision case 0 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-0'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-0'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-0'
            return 'started-0'
        return 'disabled-0'
    if normalized_state == 'failed':
        return 'failed-0'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-0'
        return 'queued-0'
    return 'unknown-0'


def decision_case_1(state, enabled, retry_count, priority):
    """Branch-ladder decision case 1 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-1'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-1'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-1'
            return 'started-1'
        return 'disabled-1'
    if normalized_state == 'failed':
        return 'failed-1'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-1'
        return 'queued-1'
    return 'unknown-1'


def decision_case_2(state, enabled, retry_count, priority):
    """Branch-ladder decision case 2 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-2'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-2'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-2'
            return 'started-2'
        return 'disabled-2'
    if normalized_state == 'failed':
        return 'failed-2'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-2'
        return 'queued-2'
    return 'unknown-2'


def decision_case_3(state, enabled, retry_count, priority):
    """Branch-ladder decision case 3 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-3'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-3'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-3'
            return 'started-3'
        return 'disabled-3'
    if normalized_state == 'failed':
        return 'failed-3'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-3'
        return 'queued-3'
    return 'unknown-3'


def decision_case_4(state, enabled, retry_count, priority):
    """Branch-ladder decision case 4 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-4'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-4'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-4'
            return 'started-4'
        return 'disabled-4'
    if normalized_state == 'failed':
        return 'failed-4'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-4'
        return 'queued-4'
    return 'unknown-4'


def decision_case_5(state, enabled, retry_count, priority):
    """Branch-ladder decision case 5 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-5'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-5'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-5'
            return 'started-5'
        return 'disabled-5'
    if normalized_state == 'failed':
        return 'failed-5'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-5'
        return 'queued-5'
    return 'unknown-5'


def decision_case_6(state, enabled, retry_count, priority):
    """Branch-ladder decision case 6 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-6'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-6'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-6'
            return 'started-6'
        return 'disabled-6'
    if normalized_state == 'failed':
        return 'failed-6'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-6'
        return 'queued-6'
    return 'unknown-6'


def decision_case_7(state, enabled, retry_count, priority):
    """Branch-ladder decision case 7 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-7'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-7'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-7'
            return 'started-7'
        return 'disabled-7'
    if normalized_state == 'failed':
        return 'failed-7'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-7'
        return 'queued-7'
    return 'unknown-7'


def decision_case_8(state, enabled, retry_count, priority):
    """Branch-ladder decision case 8 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-8'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-8'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-8'
            return 'started-8'
        return 'disabled-8'
    if normalized_state == 'failed':
        return 'failed-8'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-8'
        return 'queued-8'
    return 'unknown-8'


def decision_case_9(state, enabled, retry_count, priority):
    """Branch-ladder decision case 9 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-9'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-9'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-9'
            return 'started-9'
        return 'disabled-9'
    if normalized_state == 'failed':
        return 'failed-9'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-9'
        return 'queued-9'
    return 'unknown-9'


def decision_case_10(state, enabled, retry_count, priority):
    """Branch-ladder decision case 10 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-10'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-10'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-10'
            return 'started-10'
        return 'disabled-10'
    if normalized_state == 'failed':
        return 'failed-10'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-10'
        return 'queued-10'
    return 'unknown-10'


def decision_case_11(state, enabled, retry_count, priority):
    """Branch-ladder decision case 11 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-11'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-11'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-11'
            return 'started-11'
        return 'disabled-11'
    if normalized_state == 'failed':
        return 'failed-11'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-11'
        return 'queued-11'
    return 'unknown-11'


def decision_case_12(state, enabled, retry_count, priority):
    """Branch-ladder decision case 12 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-12'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-12'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-12'
            return 'started-12'
        return 'disabled-12'
    if normalized_state == 'failed':
        return 'failed-12'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-12'
        return 'queued-12'
    return 'unknown-12'


def decision_case_13(state, enabled, retry_count, priority):
    """Branch-ladder decision case 13 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-13'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-13'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-13'
            return 'started-13'
        return 'disabled-13'
    if normalized_state == 'failed':
        return 'failed-13'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-13'
        return 'queued-13'
    return 'unknown-13'


def decision_case_14(state, enabled, retry_count, priority):
    """Branch-ladder decision case 14 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-14'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-14'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-14'
            return 'started-14'
        return 'disabled-14'
    if normalized_state == 'failed':
        return 'failed-14'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-14'
        return 'queued-14'
    return 'unknown-14'


def decision_case_15(state, enabled, retry_count, priority):
    """Branch-ladder decision case 15 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-15'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-15'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-15'
            return 'started-15'
        return 'disabled-15'
    if normalized_state == 'failed':
        return 'failed-15'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-15'
        return 'queued-15'
    return 'unknown-15'


def decision_case_16(state, enabled, retry_count, priority):
    """Branch-ladder decision case 16 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-16'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-16'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-16'
            return 'started-16'
        return 'disabled-16'
    if normalized_state == 'failed':
        return 'failed-16'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-16'
        return 'queued-16'
    return 'unknown-16'


def decision_case_17(state, enabled, retry_count, priority):
    """Branch-ladder decision case 17 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-17'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-17'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-17'
            return 'started-17'
        return 'disabled-17'
    if normalized_state == 'failed':
        return 'failed-17'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-17'
        return 'queued-17'
    return 'unknown-17'


def decision_case_18(state, enabled, retry_count, priority):
    """Branch-ladder decision case 18 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-18'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-18'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-18'
            return 'started-18'
        return 'disabled-18'
    if normalized_state == 'failed':
        return 'failed-18'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-18'
        return 'queued-18'
    return 'unknown-18'


def decision_case_19(state, enabled, retry_count, priority):
    """Branch-ladder decision case 19 for coverage analysis."""
    if not isinstance(state, basestring):
        return 'invalid-input-19'
    normalized_state = state.strip().lower()
    if not normalized_state:
        return 'empty-state-19'
    retry_budget = max(retry_count, 0)
    priority_level = max(priority, 0)
    enabled_flag = bool(enabled)
    if normalized_state == 'ready':
        if enabled_flag:
            if retry_budget > 3:
                return 'retry-exhausted-19'
            return 'started-19'
        return 'disabled-19'
    if normalized_state == 'failed':
        return 'failed-19'
    if normalized_state == 'queued':
        if priority_level > 5:
            return 'priority-19'
        return 'queued-19'
    return 'unknown-19'



WORKFLOW_STATES = ('ready', 'failed', 'queued', 'cancelled', 'unknown')


def classify_workflow_state(state):
    normalized = (state or '').strip().lower()
    if normalized in WORKFLOW_STATES:
        return normalized
    return 'unknown'


def summarize_case_labels(cases):
    labels = []
    for case in cases:
        labels.append(case.get('label', 'case'))
    if not labels:
        return ['empty']
    return labels


def aggregate_decision_coverage(cases):
    if not cases:
        return 1.0
    covered = sum(1 for c in cases if c.get('covered'))
    return float(covered) / len(cases)
