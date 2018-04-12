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
    def test_compare_with_control(self):
	os.system("../../asc2cdf -n -r 10 -g PVM10TO01.TXT.globalatts.control -a PVM_RF01_20080716_170129_10.ames.control PVM_RF01_20080716_170129_10.nc")
        os.system("ncdump PVM_RF01_20080716_170129_10.nc > ames.dump")
	os.system("diff ames.dump control.dump")

	f = open("ames.dump","r")
	c = open("control.dump","r")
	for line in f:
	    cline = c.readline()
	    result = re.match(r".*DateConvertedFromASCII.*",line)
	    if result is None:
	    	print line
		self.assertEqual(cline,line)

    def test_RAF_compare_with_control(self):
	os.system("../../asc2cdf -r 10 -g PVM10TO01.TXT.globalatts.control -a PVM_RF01_20080716_170129_10.ames.control PVM_RF01_20080716_170129_10.nc")
        os.system("ncdump PVM_RF01_20080716_170129_10.nc > RAFames.dump")
	os.system("diff RAFames.dump RAFcontrol.dump")

	f = open("RAFames.dump","r")
	c = open("RAFcontrol.dump","r")
	for line in f:
	    cline = c.readline()
	    result = re.match(r".*DateConvertedFromASCII.*",line)
	    if result is None:
	    	print line
		self.assertEqual(cline,line)

    def tearDown(self):
	os.system("rm ames.dump")
	os.system("rm RAFames.dump")



if __name__ == '__main__':
    unittest.main()
