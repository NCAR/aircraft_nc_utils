#!/usr/bin/env python

# Copyright (c) 2016, University Corporation for Atmospheric Research
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Author: Nicholas DeCicco. <decicco@ucar>
#                           <nsd.cicco@gmail.com>

import sys
import numpy as np
from netCDF4 import Dataset
import math
import argparse


def stats(var):
	# Remove missing values from statistics calculations
	ncFile.variables[var] = np.ma.masked_equal(ncFile.variables[var],-32767)
	min = np.min(ncFile.variables[var])
	max = np.max(ncFile.variables[var])
	variance = np.var(ncFile.variables[var])
	stddev = math.sqrt(variance)
	mean = np.mean(ncFile.variables[var])

        stats = [var.encode('UTF-8'), len(ncFile.variables[var]), min, max, stddev, variance, mean]
        return stats

# Print statistic values in clearly separated columns 
def print_cols(ncFile):
    var_array = [["name", "npoints", "min", "max", "stddev", "variance", "mean"]]
    for var in ncFile.variables:
        if args.vars:
            for arg in args.vars:
                if var == arg:
                    var_array.append(stats(var))
        else:
            var_array.append(stats(var))
  
    col_width = max(len(str(var)) for row in var_array for var in row) + 2

    for var in var_array:
        print "".join(str(word).ljust(col_width) for word in var)    

# Print Staticstic values comma separated 
def print_default(ncFile):
    print('name,npoints,min,max,stddev,variance,mean')
    for var in ncFile.variables:
        if args.vars:
            for arg in args.vars:
                if var == arg:
                    stat = stats(var)
                    print "%s, %s, %s, %s, %s, %s, %s" %(stat[0], stat[1], stat[2], stat[3], stat[4], stat[5], stat[6])
        else:
            stat = stats(var)
            print "%s, %s, %s, %s, %s, %s, %s" %(stat[0], stat[1], stat[2], stat[3], stat[4], stat[5], stat[6])

#if len(sys.argv) != 2:
 #   sys.stderr.write('Error: expected exactly one argument\n')
 #   exit(1)

ncFileName = sys.argv[1]
ncFile = Dataset(ncFileName, 'a') # for netCDF4 module

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--cols", help="Print stats in columns", action='store_true')
parser.add_argument("-v", "--vars", nargs="+", help="Print subset of file variables")
args, unknown = parser.parse_known_args()

if args.cols:
    print_cols(ncFile)
else:
    print_default(ncFile)


ncFile.close()

# Test
