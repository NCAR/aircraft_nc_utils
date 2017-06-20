#!/usr/bin/python

import sys
from optparse import OptionParser

class ASCII_average(object):
    def __init__(self,rate,fileType,input_file):
	self.rate = rate
	self.fileType = fileType
	self.input_file = input_file

    def average(self):
	print "Rate: " + str(self.rate)

_usage = """%prog [options]"""

def main(args):
    parser = OptionParser(usage=_usage)
    parser.add_option("--fileType", type="string", default=None,
	    help="Enter file type: a - NASA_AMES, c - BADC_CSV, "
	    "i - ICARTT, l - NASA_LANGLEY")
    parser.add_option("--rate", type="int", default=1, 
	    help="Enter output rate in seconds")
    parser.add_option("--input_file",type="string",default=None,
	    help="Enter the file to be averaged")
    (options, args) = parser.parse_args(args)

    averager = ASCII_average(options.rate,options.fileType,options.input_file)
    averager.average()

if __name__ == "__main__":
    main(sys.argv)
