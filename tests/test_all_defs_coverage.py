from __future__ import print_function
import unittest
from df.all_defs_coverage import deco_case_0

class TestBugPartial(unittest.TestCase):
    def test_one_case(self):
        self.assertTrue(deco_case_0('x', True, 1, 3))
