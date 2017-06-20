#!/usr/bin/python
#
# To run this, type:
#	py.test test_ascav
#
# Documentation for the QtTest Module:
# https://docs.python.org/2/library/unittest.html
#

from ascav import ASCII_average, main
import unittest
import sys

class Test_ascav(unittest.TestCase):
    #def setUp(self):

    #def tearDown(self):

    #def test_transfer_header(self):

    #def test_avg_data(self):

    def test_assert(self):
	averager = ASCII_average(1,"BADC_CSV","test")
	assert (averager.rate  == 1)
	assert (averager.fileType  == "BADC_CSV")
	assert (averager.input_file  == "test")

if __name__ == '__main__':
    unittest.main()
