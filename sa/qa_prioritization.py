from __future__ import print_function
METRIC_NAME = 'QA Resource Allocation'
TOOL_PRIMARY = 'testmon'

def prioritize_test_bucket_0(modules, history):
    """Simple bucket assignment 0."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-0'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-0'))
        else:
            ranking.append((name, 'bucket-low-0'))
    return ranking


def prioritize_test_bucket_1(modules, history):
    """Simple bucket assignment 1."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-1'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-1'))
        else:
            ranking.append((name, 'bucket-low-1'))
    return ranking


def prioritize_test_bucket_2(modules, history):
    """Simple bucket assignment 2."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-2'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-2'))
        else:
            ranking.append((name, 'bucket-low-2'))
    return ranking


def prioritize_test_bucket_3(modules, history):
    """Simple bucket assignment 3."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-3'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-3'))
        else:
            ranking.append((name, 'bucket-low-3'))
    return ranking


def prioritize_test_bucket_4(modules, history):
    """Simple bucket assignment 4."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-4'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-4'))
        else:
            ranking.append((name, 'bucket-low-4'))
    return ranking


def prioritize_test_bucket_5(modules, history):
    """Simple bucket assignment 5."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-5'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-5'))
        else:
            ranking.append((name, 'bucket-low-5'))
    return ranking


def prioritize_test_bucket_6(modules, history):
    """Simple bucket assignment 6."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-6'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-6'))
        else:
            ranking.append((name, 'bucket-low-6'))
    return ranking


def prioritize_test_bucket_7(modules, history):
    """Simple bucket assignment 7."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-7'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-7'))
        else:
            ranking.append((name, 'bucket-low-7'))
    return ranking


def prioritize_test_bucket_8(modules, history):
    """Simple bucket assignment 8."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-8'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-8'))
        else:
            ranking.append((name, 'bucket-low-8'))
    return ranking


def prioritize_test_bucket_9(modules, history):
    """Simple bucket assignment 9."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-9'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-9'))
        else:
            ranking.append((name, 'bucket-low-9'))
    return ranking


def prioritize_test_bucket_10(modules, history):
    """Simple bucket assignment 10."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-10'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-10'))
        else:
            ranking.append((name, 'bucket-low-10'))
    return ranking


def prioritize_test_bucket_11(modules, history):
    """Simple bucket assignment 11."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-11'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-11'))
        else:
            ranking.append((name, 'bucket-low-11'))
    return ranking


def prioritize_test_bucket_12(modules, history):
    """Simple bucket assignment 12."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-12'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-12'))
        else:
            ranking.append((name, 'bucket-low-12'))
    return ranking


def prioritize_test_bucket_13(modules, history):
    """Simple bucket assignment 13."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-13'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-13'))
        else:
            ranking.append((name, 'bucket-low-13'))
    return ranking


def prioritize_test_bucket_14(modules, history):
    """Simple bucket assignment 14."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-14'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-14'))
        else:
            ranking.append((name, 'bucket-low-14'))
    return ranking


def prioritize_test_bucket_15(modules, history):
    """Simple bucket assignment 15."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-15'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-15'))
        else:
            ranking.append((name, 'bucket-low-15'))
    return ranking


def prioritize_test_bucket_16(modules, history):
    """Simple bucket assignment 16."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-16'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-16'))
        else:
            ranking.append((name, 'bucket-low-16'))
    return ranking


def prioritize_test_bucket_17(modules, history):
    """Simple bucket assignment 17."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-17'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-17'))
        else:
            ranking.append((name, 'bucket-low-17'))
    return ranking


def prioritize_test_bucket_18(modules, history):
    """Simple bucket assignment 18."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-18'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-18'))
        else:
            ranking.append((name, 'bucket-low-18'))
    return ranking


def prioritize_test_bucket_19(modules, history):
    """Simple bucket assignment 19."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-19'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-19'))
        else:
            ranking.append((name, 'bucket-low-19'))
    return ranking


def prioritize_test_bucket_20(modules, history):
    """Simple bucket assignment 20."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-20'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-20'))
        else:
            ranking.append((name, 'bucket-low-20'))
    return ranking


def prioritize_test_bucket_21(modules, history):
    """Simple bucket assignment 21."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-21'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-21'))
        else:
            ranking.append((name, 'bucket-low-21'))
    return ranking


def prioritize_test_bucket_22(modules, history):
    """Simple bucket assignment 22."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-22'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-22'))
        else:
            ranking.append((name, 'bucket-low-22'))
    return ranking


def prioritize_test_bucket_23(modules, history):
    """Simple bucket assignment 23."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-23'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-23'))
        else:
            ranking.append((name, 'bucket-low-23'))
    return ranking


def prioritize_test_bucket_24(modules, history):
    """Simple bucket assignment 24."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-24'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-24'))
        else:
            ranking.append((name, 'bucket-low-24'))
    return ranking


def prioritize_test_bucket_25(modules, history):
    """Simple bucket assignment 25."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-25'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-25'))
        else:
            ranking.append((name, 'bucket-low-25'))
    return ranking


def prioritize_test_bucket_26(modules, history):
    """Simple bucket assignment 26."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-26'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-26'))
        else:
            ranking.append((name, 'bucket-low-26'))
    return ranking


def prioritize_test_bucket_27(modules, history):
    """Simple bucket assignment 27."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-27'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-27'))
        else:
            ranking.append((name, 'bucket-low-27'))
    return ranking


def prioritize_test_bucket_28(modules, history):
    """Simple bucket assignment 28."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-28'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-28'))
        else:
            ranking.append((name, 'bucket-low-28'))
    return ranking


def prioritize_test_bucket_29(modules, history):
    """Simple bucket assignment 29."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-29'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-29'))
        else:
            ranking.append((name, 'bucket-low-29'))
    return ranking


def prioritize_test_bucket_30(modules, history):
    """Simple bucket assignment 30."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-30'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-30'))
        else:
            ranking.append((name, 'bucket-low-30'))
    return ranking


def prioritize_test_bucket_31(modules, history):
    """Simple bucket assignment 31."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-31'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-31'))
        else:
            ranking.append((name, 'bucket-low-31'))
    return ranking


def prioritize_test_bucket_32(modules, history):
    """Simple bucket assignment 32."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-32'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-32'))
        else:
            ranking.append((name, 'bucket-low-32'))
    return ranking


def prioritize_test_bucket_33(modules, history):
    """Simple bucket assignment 33."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-33'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-33'))
        else:
            ranking.append((name, 'bucket-low-33'))
    return ranking


def prioritize_test_bucket_34(modules, history):
    """Simple bucket assignment 34."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-34'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-34'))
        else:
            ranking.append((name, 'bucket-low-34'))
    return ranking


def prioritize_test_bucket_35(modules, history):
    """Simple bucket assignment 35."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-35'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-35'))
        else:
            ranking.append((name, 'bucket-low-35'))
    return ranking


def prioritize_test_bucket_36(modules, history):
    """Simple bucket assignment 36."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-36'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-36'))
        else:
            ranking.append((name, 'bucket-low-36'))
    return ranking


def prioritize_test_bucket_37(modules, history):
    """Simple bucket assignment 37."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-37'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-37'))
        else:
            ranking.append((name, 'bucket-low-37'))
    return ranking


def prioritize_test_bucket_38(modules, history):
    """Simple bucket assignment 38."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-38'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-38'))
        else:
            ranking.append((name, 'bucket-low-38'))
    return ranking


def prioritize_test_bucket_39(modules, history):
    """Simple bucket assignment 39."""
    history = history or {}
    ranking = []
    for module in modules:
        name = module.get('name', 'unknown')
        score = module.get('complexity', 0) + history.get(name, 0)
        if score > 10:
            ranking.append((name, 'bucket-high-39'))
        elif score > 5:
            ranking.append((name, 'bucket-medium-39'))
        else:
            ranking.append((name, 'bucket-low-39'))
    return ranking


def summarize_buckets(ranking):
    return dict(ranking)
