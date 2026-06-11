from __future__ import print_function
import unittest
from sa.execution_path_integrity import evaluate_path_integrity
class T(unittest.TestCase):
 def test_ok(self):
  self.assertTrue(evaluate_path_integrity(1,'fast',{}))
