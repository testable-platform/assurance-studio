from __future__ import print_function
import unittest

from sa.logic_combinatorial import combinatorial_state_machine_0

class TestBugPartial(unittest.TestCase):
    def test_partial_only(self):
        self.assertTrue(combinatorial_state_machine_0([True, False],))
