from __future__ import print_function
import unittest
from sa.decision_coverage import aggregate_decision_coverage
class T(unittest.TestCase):
 def test_empty(self):
  self.assertEqual(aggregate_decision_coverage([]), 1.0)
