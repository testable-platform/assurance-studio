from __future__ import print_function
import unittest
from sa.logic_combinatorial import count_unique_paths
class T(unittest.TestCase):
 def test_ok(self):
  self.assertEqual(count_unique_paths('x',3), 8)
