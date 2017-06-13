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
import subprocess
import unittest

class Test100hz(unittest.TestCase):
    def test_compare_with_control(self):
	# This test compares newly-generated files with "control" files that were generated
	# using the previous best version of asc2df.
	os.system("../../asc2cdf -r 100 -g TO05_MRLA3_100Hz.txt.globalatts -a MRLA3_RF05_20080728_010636_100.ames.control 100hz.nc")
        os.system("ncdump 100hz.nc > 100hz.dump")
	os.system("diff 100hz.dump dump.control")

	f = open("100hz.dump","r")
	c = open("dump.control","r")
	for line in f:
	    cline = c.readline()
	    result = re.match(r".*DateConvertedFromASCII.*",line)
	    if result is None:
		self.assertEqual(cline,line)

    def test_global_attributes(self):
	# read in global atts from NASA Ames file and ensure they all are written to netCDF
	# file
	a = open("MRLA3_RF05_20080728_010636_100.ames.control","r")
	for line in a:
	    # Lines that start with a letter are all content we want to move to NetCDF atts
	    if re.match(r"^[A-Za-z].*",line) is not None:
		if re.match(r".* = .*",line) is not None:
		    # Found key/value pair. These become NetCDF global atts
		    key,value = line.split(" = ")
		    pattern = value.rstrip()
		elif re.match(r"^Time.*",line) is None: # Skip Time - it is handled differently
		    # AMES format has long_name (units) in a single line. Split off units so
		    # can check that long_name was written to netCDF file.
		    if re.match(r".*\(.*",line) is not None:
		        pattern,rest = line.rstrip().split(" (")
		    else:
		        pattern=line
		    
		#self.assertIsNotNone(subprocess.check_output("grep ".pattern." 100hz.dump"))
		command = ["grep",pattern,"100hz.dump"]
		self.assertIsNotNone(subprocess.check_output(command))


    #def tearDown(self):
	#os.system("rm 100hz.dump")
	#os.system("rm 100hz.nc")

if __name__ == '__main__':
    unittest.main()
