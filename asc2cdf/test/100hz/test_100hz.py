#!/usr/bin/python
#
# To run this, type:
#	py.test test_100hz.py
#
# Documentation for the QtTest Module:
# https://docs.python.org/2/library/unittest.html
#

import os
import re
import unittest

class Test100hz(unittest.TestCase):
    def test_compare_with_control(self):
	os.system("../../asc2cdf -r 100 -g TO05_MRLA3_100Hz.txt.globalatts -a MRLA3_RF05_20080728_010636_100.ames.control 100hz.nc")
        os.system("ncdump 100hz.nc > 100hz.dump")
	os.system("diff 100hz.dump dump.control")

	f = open("100hz.dump","r")
	c = open("dump.control","r")
	for line in f:
	    cline = c.readline()
	    result = re.match(r".*DateConvertedFromASCII.*",line)
	    if result is None:
	    	print line
		self.assertEqual(cline,line)

    def tearDown(self):
	os.system("rm 100hz.dump")
	os.system("rm 100hz.nc")

if __name__ == '__main__':
    unittest.main()
