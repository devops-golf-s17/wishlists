
# Test cases can be run with either of the following:
# python -m unittest discover
# nosetests -v --rednose --nologcapture

import unittest
from persistence import DatabaseEngine

class WishlistTestCase(unittest.TestCase):
	def setUp(self):
		self.db=DatabaseEngine()
    
	def tearDown(self):
		self.db=None
    
if __name__ == '__main__':
	unittest.main()
