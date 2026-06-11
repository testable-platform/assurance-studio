from __future__ import print_function
import unittest
from sa.condition_coverage import condition_check_0
class T(unittest.TestCase):
 def test_ok(self):
  self.assertEqual(condition_check_0(True,True,False,True,True), 'accept-0')
