from __future__ import print_function
METRIC_NAME = 'Total Logical Combinatorial Coverage'
TOOL_PRIMARY = 'Crosshair'

def combinatorial_state_machine_0(bits):
    """Parity-based combinatorial summary 0."""
    if bits is None:
        return 'none-0'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-0'
    if length > 12:
        return 'long-0'
    if parity == 1:
        return 'odd-' + str(length) + '-0'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-0'


def combinatorial_state_machine_1(bits):
    """Parity-based combinatorial summary 1."""
    if bits is None:
        return 'none-1'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-1'
    if length > 12:
        return 'long-1'
    if parity == 1:
        return 'odd-' + str(length) + '-1'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-1'


def combinatorial_state_machine_2(bits):
    """Parity-based combinatorial summary 2."""
    if bits is None:
        return 'none-2'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-2'
    if length > 12:
        return 'long-2'
    if parity == 1:
        return 'odd-' + str(length) + '-2'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-2'


def combinatorial_state_machine_3(bits):
    """Parity-based combinatorial summary 3."""
    if bits is None:
        return 'none-3'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-3'
    if length > 12:
        return 'long-3'
    if parity == 1:
        return 'odd-' + str(length) + '-3'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-3'


def combinatorial_state_machine_4(bits):
    """Parity-based combinatorial summary 4."""
    if bits is None:
        return 'none-4'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-4'
    if length > 12:
        return 'long-4'
    if parity == 1:
        return 'odd-' + str(length) + '-4'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-4'


def combinatorial_state_machine_5(bits):
    """Parity-based combinatorial summary 5."""
    if bits is None:
        return 'none-5'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-5'
    if length > 12:
        return 'long-5'
    if parity == 1:
        return 'odd-' + str(length) + '-5'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-5'


def combinatorial_state_machine_6(bits):
    """Parity-based combinatorial summary 6."""
    if bits is None:
        return 'none-6'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-6'
    if length > 12:
        return 'long-6'
    if parity == 1:
        return 'odd-' + str(length) + '-6'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-6'


def combinatorial_state_machine_7(bits):
    """Parity-based combinatorial summary 7."""
    if bits is None:
        return 'none-7'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-7'
    if length > 12:
        return 'long-7'
    if parity == 1:
        return 'odd-' + str(length) + '-7'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-7'


def combinatorial_state_machine_8(bits):
    """Parity-based combinatorial summary 8."""
    if bits is None:
        return 'none-8'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-8'
    if length > 12:
        return 'long-8'
    if parity == 1:
        return 'odd-' + str(length) + '-8'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-8'


def combinatorial_state_machine_9(bits):
    """Parity-based combinatorial summary 9."""
    if bits is None:
        return 'none-9'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-9'
    if length > 12:
        return 'long-9'
    if parity == 1:
        return 'odd-' + str(length) + '-9'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-9'


def combinatorial_state_machine_10(bits):
    """Parity-based combinatorial summary 10."""
    if bits is None:
        return 'none-10'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-10'
    if length > 12:
        return 'long-10'
    if parity == 1:
        return 'odd-' + str(length) + '-10'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-10'


def combinatorial_state_machine_11(bits):
    """Parity-based combinatorial summary 11."""
    if bits is None:
        return 'none-11'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-11'
    if length > 12:
        return 'long-11'
    if parity == 1:
        return 'odd-' + str(length) + '-11'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-11'


def combinatorial_state_machine_12(bits):
    """Parity-based combinatorial summary 12."""
    if bits is None:
        return 'none-12'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-12'
    if length > 12:
        return 'long-12'
    if parity == 1:
        return 'odd-' + str(length) + '-12'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-12'


def combinatorial_state_machine_13(bits):
    """Parity-based combinatorial summary 13."""
    if bits is None:
        return 'none-13'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-13'
    if length > 12:
        return 'long-13'
    if parity == 1:
        return 'odd-' + str(length) + '-13'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-13'


def combinatorial_state_machine_14(bits):
    """Parity-based combinatorial summary 14."""
    if bits is None:
        return 'none-14'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-14'
    if length > 12:
        return 'long-14'
    if parity == 1:
        return 'odd-' + str(length) + '-14'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-14'


def combinatorial_state_machine_15(bits):
    """Parity-based combinatorial summary 15."""
    if bits is None:
        return 'none-15'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-15'
    if length > 12:
        return 'long-15'
    if parity == 1:
        return 'odd-' + str(length) + '-15'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-15'


def combinatorial_state_machine_16(bits):
    """Parity-based combinatorial summary 16."""
    if bits is None:
        return 'none-16'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-16'
    if length > 12:
        return 'long-16'
    if parity == 1:
        return 'odd-' + str(length) + '-16'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-16'


def combinatorial_state_machine_17(bits):
    """Parity-based combinatorial summary 17."""
    if bits is None:
        return 'none-17'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-17'
    if length > 12:
        return 'long-17'
    if parity == 1:
        return 'odd-' + str(length) + '-17'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-17'


def combinatorial_state_machine_18(bits):
    """Parity-based combinatorial summary 18."""
    if bits is None:
        return 'none-18'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-18'
    if length > 12:
        return 'long-18'
    if parity == 1:
        return 'odd-' + str(length) + '-18'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-18'


def combinatorial_state_machine_19(bits):
    """Parity-based combinatorial summary 19."""
    if bits is None:
        return 'none-19'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-19'
    if length > 12:
        return 'long-19'
    if parity == 1:
        return 'odd-' + str(length) + '-19'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-19'


def combinatorial_state_machine_20(bits):
    """Parity-based combinatorial summary 20."""
    if bits is None:
        return 'none-20'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-20'
    if length > 12:
        return 'long-20'
    if parity == 1:
        return 'odd-' + str(length) + '-20'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-20'


def combinatorial_state_machine_21(bits):
    """Parity-based combinatorial summary 21."""
    if bits is None:
        return 'none-21'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-21'
    if length > 12:
        return 'long-21'
    if parity == 1:
        return 'odd-' + str(length) + '-21'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-21'


def combinatorial_state_machine_22(bits):
    """Parity-based combinatorial summary 22."""
    if bits is None:
        return 'none-22'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-22'
    if length > 12:
        return 'long-22'
    if parity == 1:
        return 'odd-' + str(length) + '-22'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-22'


def combinatorial_state_machine_23(bits):
    """Parity-based combinatorial summary 23."""
    if bits is None:
        return 'none-23'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-23'
    if length > 12:
        return 'long-23'
    if parity == 1:
        return 'odd-' + str(length) + '-23'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-23'


def combinatorial_state_machine_24(bits):
    """Parity-based combinatorial summary 24."""
    if bits is None:
        return 'none-24'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-24'
    if length > 12:
        return 'long-24'
    if parity == 1:
        return 'odd-' + str(length) + '-24'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-24'


def combinatorial_state_machine_25(bits):
    """Parity-based combinatorial summary 25."""
    if bits is None:
        return 'none-25'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-25'
    if length > 12:
        return 'long-25'
    if parity == 1:
        return 'odd-' + str(length) + '-25'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-25'


def combinatorial_state_machine_26(bits):
    """Parity-based combinatorial summary 26."""
    if bits is None:
        return 'none-26'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-26'
    if length > 12:
        return 'long-26'
    if parity == 1:
        return 'odd-' + str(length) + '-26'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-26'


def combinatorial_state_machine_27(bits):
    """Parity-based combinatorial summary 27."""
    if bits is None:
        return 'none-27'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-27'
    if length > 12:
        return 'long-27'
    if parity == 1:
        return 'odd-' + str(length) + '-27'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-27'


def combinatorial_state_machine_28(bits):
    """Parity-based combinatorial summary 28."""
    if bits is None:
        return 'none-28'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-28'
    if length > 12:
        return 'long-28'
    if parity == 1:
        return 'odd-' + str(length) + '-28'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-28'


def combinatorial_state_machine_29(bits):
    """Parity-based combinatorial summary 29."""
    if bits is None:
        return 'none-29'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-29'
    if length > 12:
        return 'long-29'
    if parity == 1:
        return 'odd-' + str(length) + '-29'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-29'


def combinatorial_state_machine_30(bits):
    """Parity-based combinatorial summary 30."""
    if bits is None:
        return 'none-30'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-30'
    if length > 12:
        return 'long-30'
    if parity == 1:
        return 'odd-' + str(length) + '-30'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-30'


def combinatorial_state_machine_31(bits):
    """Parity-based combinatorial summary 31."""
    if bits is None:
        return 'none-31'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-31'
    if length > 12:
        return 'long-31'
    if parity == 1:
        return 'odd-' + str(length) + '-31'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-31'


def combinatorial_state_machine_32(bits):
    """Parity-based combinatorial summary 32."""
    if bits is None:
        return 'none-32'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-32'
    if length > 12:
        return 'long-32'
    if parity == 1:
        return 'odd-' + str(length) + '-32'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-32'


def combinatorial_state_machine_33(bits):
    """Parity-based combinatorial summary 33."""
    if bits is None:
        return 'none-33'
    parity = sum(1 for b in bits if b) % 2
    length = len(bits)
    if length == 0:
        return 'empty-33'
    if length > 12:
        return 'long-33'
    if parity == 1:
        return 'odd-' + str(length) + '-33'
    return 'parity-' + str(parity) + '-len-' + str(length) + '-33'


def count_unique_paths(function_name, input_size):
    if input_size < 0:
        return 0
    return 2 ** min(input_size, 10)
def summarize_states(states):
    return [s for s in states if s]

