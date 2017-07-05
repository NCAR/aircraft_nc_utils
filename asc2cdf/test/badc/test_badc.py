#!/usr/bin/python
#
# To run this, type:
#	py.test test_badc.py
#
# Documentation for the QtTest Module:
# https://docs.python.org/2/library/unittest.html
#

import os
import re
import subprocess
import unittest

class TestBADC(unittest.TestCase):
    def setUp(self):
        os.system("../../asc2cdf -c -r 1000 CSET-HOLODEC-H2H_GV_20150722.csv.control badc.nc")
        os.system("ncdump badc.nc > badc.dump")
        os.system("../../asc2cdf -c -r 1000 CSET-HOLODEC-H2H_GV_20150722.alpha.csv srt.nc")
        os.system("ncdump srt.nc > srt.dump")

    def tearDown(self):
	os.system("rm badc.dump")
	os.system("rm badc.nc")
	os.system("rm srt.dump")
	os.system("rm srt.nc")

    def test_compare_with_control(self):
	# This test compares newly-generated files with "control" files that were generated
	# using the previous best version of asc2df.

	f = open("badc.dump","r")
	c = open("dump.control","r")
	for line in f:
	    cline = c.readline()
	    result = re.match(r".*DateConvertedFromASCII.*",line)
	    if result is None:
		self.assertEqual(cline,line)

    def test_compare_alpha_with_control(self):
	# This test compares newly-generated files with "control" files that were generated
	# using the previous best version of asc2df.

	f = open("srt.dump","r")
	c = open("srt.control","r")
	for line in f:
	    cline = c.readline()
	    result = re.match(r".*DateConvertedFromASCII.*",line)
	    if result is None:
		self.assertEqual(cline,line)

    def test_global_attributes(self):
	# read in global atts from NASA Ames file and ensure they all are written to netCDF
	# file
	a = open("CSET-HOLODEC-H2H_GV_20150722.csv.control","r")
	for line in a:
	    # Lines that start with a letter are all content we want to move to NetCDF atts
	    if re.match(r"^[A-Za-z].*",line) is not None:
		if re.match(r".* = .*",line) is not None:
		    # Found key/value pair. These become NetCDF global atts
		    key,value = line.split(" = ")
		    pattern = value.rstrip()
		elif re.match(r"^Time.*",line) is None: # Skip Time - it is handled differently
		    pattern=line
		    
		#self.assertIsNotNone(subprocess.check_output("grep ".pattern." badc.dump"))
		command = ["grep",pattern,"badc.dump"]
		self.assertIsNotNone(subprocess.check_output(command))

    def test_alpha_atts(self):
	# read in global atts from NASA Ames file and ensure they all are written to netCDF
	# file
	a = open("CSET-HOLODEC-H2H_GV_20150722.alpha.csv","r")
	for line in a:
	    # Lines that start with a letter are all content we want to move to NetCDF atts
	    if re.match(r"^[A-Za-z].*",line) is not None:
		if re.match(r".* = .*",line) is not None:
		    # Found key/value pair. These become NetCDF global atts
		    key,value = line.split(" = ")
		    pattern = value.rstrip()
		elif re.match(r"^Time.*",line) is None: # Skip Time - it is handled differently
		    pattern=line
		    
		#self.assertIsNotNone(subprocess.check_output("grep ".pattern." badc.dump"))
		command = ["grep",pattern,"srt.dump"]
		self.assertIsNotNone(subprocess.check_output(command))


if __name__ == '__main__':
    unittest.main()
