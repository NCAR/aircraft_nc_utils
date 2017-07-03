#!/usr/bin/python
#
# To run this, type:
#	py.test test_rafCO.py
#
# Documentation for the QtTest Module:
# https://docs.python.org/2/library/unittest.html
#

import os
import re
import unittest

class Test100hz(unittest.TestCase):
    def test_compare_with_control(self):
        os.system("../../asc2cdf -m -d 2008-04-18 rafCO.txt rafCO.nc")
        os.system("ncdump rafCO.nc > rafCO.dump")
	os.system("diff rafCO.dump control.dump")

	f = open("rafCO.dump","r")
	c = open("control.dump","r")
	for line in f:
	    cline = c.readline()
	    result = re.match(r".*DateConvertedFromASCII.*",line)
	    if result is None:
	    	print line
		self.assertEqual(cline,line)

    def tearDown(self):
	os.system("rm rafCO.dump")
	os.system("rm rafCO.nc")

if __name__ == '__main__':
    unittest.main()
