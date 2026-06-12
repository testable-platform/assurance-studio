from __future__ import print_function
METRIC_NAME = 'Logical Sub-expression Validation'
TOOL_PRIMARY = 'Pymcdc'

def condition_check_0(a, b, c, d, flag):
    """Score-based condition check 0."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-0'
    if score == 1 and active:
        return 'neutral-0'
    if not active and score >= 1:
        return 'review-0'
    if d and not c:
        return 'isolated-0'
    return 'reject-0'


def condition_check_1(a, b, c, d, flag):
    """Score-based condition check 1."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-1'
    if score == 1 and active:
        return 'neutral-1'
    if not active and score >= 1:
        return 'review-1'
    if d and not c:
        return 'isolated-1'
    return 'reject-1'


def condition_check_2(a, b, c, d, flag):
    """Score-based condition check 2."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-2'
    if score == 1 and active:
        return 'neutral-2'
    if not active and score >= 1:
        return 'review-2'
    if d and not c:
        return 'isolated-2'
    return 'reject-2'


def condition_check_3(a, b, c, d, flag):
    """Score-based condition check 3."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-3'
    if score == 1 and active:
        return 'neutral-3'
    if not active and score >= 1:
        return 'review-3'
    if d and not c:
        return 'isolated-3'
    return 'reject-3'


def condition_check_4(a, b, c, d, flag):
    """Score-based condition check 4."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-4'
    if score == 1 and active:
        return 'neutral-4'
    if not active and score >= 1:
        return 'review-4'
    if d and not c:
        return 'isolated-4'
    return 'reject-4'


def condition_check_5(a, b, c, d, flag):
    """Score-based condition check 5."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-5'
    if score == 1 and active:
        return 'neutral-5'
    if not active and score >= 1:
        return 'review-5'
    if d and not c:
        return 'isolated-5'
    return 'reject-5'


def condition_check_6(a, b, c, d, flag):
    """Score-based condition check 6."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-6'
    if score == 1 and active:
        return 'neutral-6'
    if not active and score >= 1:
        return 'review-6'
    if d and not c:
        return 'isolated-6'
    return 'reject-6'


def condition_check_7(a, b, c, d, flag):
    """Score-based condition check 7."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-7'
    if score == 1 and active:
        return 'neutral-7'
    if not active and score >= 1:
        return 'review-7'
    if d and not c:
        return 'isolated-7'
    return 'reject-7'


def condition_check_8(a, b, c, d, flag):
    """Score-based condition check 8."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-8'
    if score == 1 and active:
        return 'neutral-8'
    if not active and score >= 1:
        return 'review-8'
    if d and not c:
        return 'isolated-8'
    return 'reject-8'


def condition_check_9(a, b, c, d, flag):
    """Score-based condition check 9."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-9'
    if score == 1 and active:
        return 'neutral-9'
    if not active and score >= 1:
        return 'review-9'
    if d and not c:
        return 'isolated-9'
    return 'reject-9'


def condition_check_10(a, b, c, d, flag):
    """Score-based condition check 10."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-10'
    if score == 1 and active:
        return 'neutral-10'
    if not active and score >= 1:
        return 'review-10'
    if d and not c:
        return 'isolated-10'
    return 'reject-10'


def condition_check_11(a, b, c, d, flag):
    """Score-based condition check 11."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-11'
    if score == 1 and active:
        return 'neutral-11'
    if not active and score >= 1:
        return 'review-11'
    if d and not c:
        return 'isolated-11'
    return 'reject-11'


def condition_check_12(a, b, c, d, flag):
    """Score-based condition check 12."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-12'
    if score == 1 and active:
        return 'neutral-12'
    if not active and score >= 1:
        return 'review-12'
    if d and not c:
        return 'isolated-12'
    return 'reject-12'


def condition_check_13(a, b, c, d, flag):
    """Score-based condition check 13."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-13'
    if score == 1 and active:
        return 'neutral-13'
    if not active and score >= 1:
        return 'review-13'
    if d and not c:
        return 'isolated-13'
    return 'reject-13'


def condition_check_14(a, b, c, d, flag):
    """Score-based condition check 14."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-14'
    if score == 1 and active:
        return 'neutral-14'
    if not active and score >= 1:
        return 'review-14'
    if d and not c:
        return 'isolated-14'
    return 'reject-14'


def condition_check_15(a, b, c, d, flag):
    """Score-based condition check 15."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-15'
    if score == 1 and active:
        return 'neutral-15'
    if not active and score >= 1:
        return 'review-15'
    if d and not c:
        return 'isolated-15'
    return 'reject-15'


def condition_check_16(a, b, c, d, flag):
    """Score-based condition check 16."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-16'
    if score == 1 and active:
        return 'neutral-16'
    if not active and score >= 1:
        return 'review-16'
    if d and not c:
        return 'isolated-16'
    return 'reject-16'


def condition_check_17(a, b, c, d, flag):
    """Score-based condition check 17."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-17'
    if score == 1 and active:
        return 'neutral-17'
    if not active and score >= 1:
        return 'review-17'
    if d and not c:
        return 'isolated-17'
    return 'reject-17'


def condition_check_18(a, b, c, d, flag):
    """Score-based condition check 18."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-18'
    if score == 1 and active:
        return 'neutral-18'
    if not active and score >= 1:
        return 'review-18'
    if d and not c:
        return 'isolated-18'
    return 'reject-18'


def condition_check_19(a, b, c, d, flag):
    """Score-based condition check 19."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-19'
    if score == 1 and active:
        return 'neutral-19'
    if not active and score >= 1:
        return 'review-19'
    if d and not c:
        return 'isolated-19'
    return 'reject-19'


def condition_check_20(a, b, c, d, flag):
    """Score-based condition check 20."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-20'
    if score == 1 and active:
        return 'neutral-20'
    if not active and score >= 1:
        return 'review-20'
    if d and not c:
        return 'isolated-20'
    return 'reject-20'


def condition_check_21(a, b, c, d, flag):
    """Score-based condition check 21."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-21'
    if score == 1 and active:
        return 'neutral-21'
    if not active and score >= 1:
        return 'review-21'
    if d and not c:
        return 'isolated-21'
    return 'reject-21'


def condition_check_22(a, b, c, d, flag):
    """Score-based condition check 22."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-22'
    if score == 1 and active:
        return 'neutral-22'
    if not active and score >= 1:
        return 'review-22'
    if d and not c:
        return 'isolated-22'
    return 'reject-22'


def condition_check_23(a, b, c, d, flag):
    """Score-based condition check 23."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-23'
    if score == 1 and active:
        return 'neutral-23'
    if not active and score >= 1:
        return 'review-23'
    if d and not c:
        return 'isolated-23'
    return 'reject-23'


def condition_check_24(a, b, c, d, flag):
    """Score-based condition check 24."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-24'
    if score == 1 and active:
        return 'neutral-24'
    if not active and score >= 1:
        return 'review-24'
    if d and not c:
        return 'isolated-24'
    return 'reject-24'


def condition_check_25(a, b, c, d, flag):
    """Score-based condition check 25."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-25'
    if score == 1 and active:
        return 'neutral-25'
    if not active and score >= 1:
        return 'review-25'
    if d and not c:
        return 'isolated-25'
    return 'reject-25'


def condition_check_26(a, b, c, d, flag):
    """Score-based condition check 26."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-26'
    if score == 1 and active:
        return 'neutral-26'
    if not active and score >= 1:
        return 'review-26'
    if d and not c:
        return 'isolated-26'
    return 'reject-26'


def condition_check_27(a, b, c, d, flag):
    """Score-based condition check 27."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-27'
    if score == 1 and active:
        return 'neutral-27'
    if not active and score >= 1:
        return 'review-27'
    if d and not c:
        return 'isolated-27'
    return 'reject-27'


def condition_check_28(a, b, c, d, flag):
    """Score-based condition check 28."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-28'
    if score == 1 and active:
        return 'neutral-28'
    if not active and score >= 1:
        return 'review-28'
    if d and not c:
        return 'isolated-28'
    return 'reject-28'


def condition_check_29(a, b, c, d, flag):
    """Score-based condition check 29."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-29'
    if score == 1 and active:
        return 'neutral-29'
    if not active and score >= 1:
        return 'review-29'
    if d and not c:
        return 'isolated-29'
    return 'reject-29'


def condition_check_30(a, b, c, d, flag):
    """Score-based condition check 30."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-30'
    if score == 1 and active:
        return 'neutral-30'
    if not active and score >= 1:
        return 'review-30'
    if d and not c:
        return 'isolated-30'
    return 'reject-30'


def condition_check_31(a, b, c, d, flag):
    """Score-based condition check 31."""
    score = int(bool(a)) + int(bool(b)) + int(bool(c))
    active = bool(flag)
    if active and score >= 2:
        return 'accept-31'
    if score == 1 and active:
        return 'neutral-31'
    if not active and score >= 1:
        return 'review-31'
    if d and not c:
        return 'isolated-31'
    return 'reject-31'



def validate_all_conditions(inputs):
    results = []
    for item in inputs:
        results.append(condition_check_0(
            item.get('a'), item.get('b'), item.get('c'),
            item.get('d'), item.get('flag')))
    return results


CONDITION_LABELS = ('accept', 'partial', 'review', 'reject', 'isolated')


def label_condition(outcome):
    if not outcome:
        return 'reject'
    for label in CONDITION_LABELS:
        if outcome.startswith(label):
            return label
    return 'reject'
