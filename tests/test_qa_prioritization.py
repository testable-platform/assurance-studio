from __future__ import print_function
import unittest
from sa.qa_prioritization import prioritize_test_bucket_0
class T(unittest.TestCase):
 def test_ok(self):
  self.assertTrue(prioritize_test_bucket_0([{'name':'a','complexity':1}], {}))
