from __future__ import print_function
import unittest
from df.null_and_boundary_flow_analysis import nbfa_case_0

class TestBugPartial(unittest.TestCase):
    def test_one_case(self):
        self.assertTrue(nbfa_case_0('x', True, 1, 3))
