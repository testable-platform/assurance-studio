from __future__ import print_function
import unittest
from df.du_path_validation import dpv_case_0

class TestBugPartial(unittest.TestCase):
    def test_one_case(self):
        self.assertTrue(dpv_case_0('x', True, 1, 3))
