#!/usr/bin/python
#
# To run this, type:
#	py.test test_ames.py
#
# Documentation for the QtTest Module:
# https://docs.python.org/2/library/unittest.html
#

import os
import re
import unittest

class Testames(unittest.TestCase):

    def test_hhmmss_compare_with_control(self):

	os.system("../../asc2cdf hhmmss.asc hhmmss.nc")
        os.system("ncdump hhmmss.nc > hhmmss.dump")
	os.system("diff hhmmss.dump hhmmss_control.dump")

	f = open("hhmmss.dump","r")
	c = open("hhmmss_control.dump","r")
	for line in f:
	    cline = c.readline()
	    result = re.match(r".*DateConvertedFromASCII.*",line)
	    if result is None:
	    	print line
		self.assertEqual(cline,line)

    def test_secondsSinceMidnight_compare_with_control(self):

	os.system("../../asc2cdf -m secondsSinceMidnight.asc secondsSinceMidnight.nc")
        os.system("ncdump secondsSinceMidnight.nc > secondsSinceMidnight.dump")
	os.system("diff secondsSinceMidnight.dump secondsSinceMidnight_control.dump")

	f = open("secondsSinceMidnight.dump","r")
	c = open("secondsSinceMidnight_control.dump","r")
	for line in f:
	    cline = c.readline()
	    result = re.match(r".*DateConvertedFromASCII.*",line)
	    if result is None:
	    	print line
		self.assertEqual(cline,line)

    def test_hhmmss_nocolon_compare_with_control(self):

	os.system("../../asc2cdf -: hhmmss_nocolon.asc hhmmss_nocolon.nc")
        os.system("ncdump hhmmss_nocolon.nc > hhmmss_nocolon.dump")
	os.system("diff hhmmss_nocolon.dump hhmmss_nocolon_control.dump")

	f = open("hhmmss_nocolon.dump","r")
	c = open("hhmmss_nocolon_control.dump","r")
	for line in f:
	    cline = c.readline()
	    result = re.match(r".*DateConvertedFromASCII.*",line)
	    if result is None:
	    	print line
		self.assertEqual(cline,line)

    def tearDown(self):
	os.system("rm hhmmss.dump")
	os.system("rm secondsSinceMidnight.dump")
	os.system("rm hhmmss_nocolon.dump")



if __name__ == '__main__':
    unittest.main()
