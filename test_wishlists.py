# Test cases can be run with either of the following:
# python -m unittest discover
# nosetests -v --rednose --nologcapture

import unittest
import logging
import json
from flask_api import status    # HTTP Status Codes
import wishlists

######################################################################
#  T E S T   C A S E S
######################################################################
class TestWishlists(unittest.TestCase):

    def setUp(self):
        # Only log criticl errors

        # Set up the test database

        pass

    def tearDown(self):
        # Retrace back to status before tests
        pass

    def test_index(self):
        # Test Index pages
        pass




######################################################################
# Utility functions
######################################################################


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()