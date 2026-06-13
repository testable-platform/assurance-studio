from __future__ import print_function
import unittest
from df.dead_data_identification import ddi_case_0

class TestBugPartial(unittest.TestCase):
    def test_one_case(self):
        self.assertTrue(ddi_case_0('x', True, 1, 3))
