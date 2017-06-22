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
import os
import re

class Test_ascav(unittest.TestCase):

    def test_init(self):
	# Test that options are parsed from command line correctly.
	averager = ASCII_average(1,"test.csv")
	assert (averager.rate  == 1)
	assert (averager.fileType  == "")
	assert (averager.input_file  == "test.csv")
	assert (averager.output_file  == "")

    def test_read_write_header(self):
	# Test that derived output file name is as expected
	# Test that parameter short names and units are read 
	# into a hash correctly.
	averager = ASCII_average(1,"test.csv")
	# Be sure test input file exists
	assert(os.path.isfile(averager.input_file))
	averager.set_output_file()
	assert (averager.output_file == "test.csv.1")

	infile = open(averager.input_file,"r")
	outfile = open(averager.output_file,"w")

	averager.read_write_header(infile,outfile)
	assert (averager.short_name['1'] == "Time")
	assert (averager.unit['2'] == '#')
	assert (averager.short_name['5'] == "CHDC")
	assert (averager.unit['6'] == "#/cm3/um")

    def test_read_write_badc(self):
	# Test that header is not changed by reading it in and writing it to 
	# the new output file.
	averager = ASCII_average(1,"test.csv")
	averager.set_output_file()
	assert (averager.output_file == "test.csv.1")
	infile = open(averager.input_file,"r")
	outfile = open(averager.output_file,"r")
	while True:
	    line = infile.readline()
	    oline = outfile.readline()
	    self.assertEqual(line,oline)
	    if (re.match("data",line)): 
		# one more line after "data" line to test
	        line = infile.readline()
	        oline = outfile.readline()
	        self.assertEqual(line,oline)
		break;
	infile.close()
	outfile.close()

    def test_avg_data(self):
	averager = ASCII_average(1,"test.csv")
	averager.unit[str(1)] = 'seconds'
	averager.unit[str(2)] = '#'
	averager.unit[str(3)] = '#/cm3'
	averager.unit[str(4)] = '#'
	for i in range(5,31):
	    averager.unit[str(i)] = '#/cm3/um'
	for i in range(31,57):
	    averager.unit[str(i)] = '#'
	averager.short_name['1'] = 'Time'
	averager.short_name['2'] = 'QC_flag'
	for i in range(3,57):
	    averager.short_name[str(i)] = 'VAR'
	averager.timestamp = 54481
	averager.lines_to_average=["54481.269500,1,0.307692,4,0.023077,0,0,0,0,0,0,0.015385,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0","54481.568600,1,0.461538,6,0.030769,0.030769,0,0,0,0,0,0,0.015385,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0","54481.867300,1,0.230769,3,0,0,0.030769,0,0,0,0,0.015385,0,0.015385,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"]
	out_rec=averager.average()
	out_rec_control = "54481,1.0,0.333333,13,0.0,0.0,0.010256,0.0,0.0,0.0,0.0,0.010257,0.0,0.005128,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,7,1,1,0,0,0,0,2,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,"
	self.assertEqual(out_rec.rstrip(),out_rec_control)





if __name__ == '__main__':
    unittest.main()
