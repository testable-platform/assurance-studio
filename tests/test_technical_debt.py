from __future__ import print_function
import unittest
from sa.technical_debt import debt_calculator_b0_v0
class T(unittest.TestCase):
 def test_ok(self):
  self.assertTrue(debt_calculator_b0_v0(100,0.1,2) >= 0)
