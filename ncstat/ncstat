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

# Add flags to parser for more customized output
parser = argparse.ArgumentParser()
parser.add_argument("-c", help="Print statistics in separated columns", action='store_true')
parser.add_argument("-v", "--vars", nargs="+", help="Print subset of file variables. VARS should be space separated.")
parser.add_argument("-f", "--file", nargs=1, help="Input netCDF file", required=True)
args, unknown = parser.parse_known_args()

ncFileName = args.file[0]
ncFile = Dataset(ncFileName, 'a') # for netCDF4 module

def multiply(numbers):
    total = 1
    for x in numbers:
	total *=x
    return total

def stats(var):
	# Remove missing values from statistics calculations
	ncFile.variables[var] = np.ma.masked_equal(ncFile.variables[var],-32767)
	nmissing = np.ma.count_masked(ncFile.variables[var])
        min = np.min(ncFile.variables[var])
	max = np.max(ncFile.variables[var])
	variance = np.var(ncFile.variables[var])
	stddev = math.sqrt(variance)
	mean = np.mean(ncFile.variables[var])

	stats = [var.encode('UTF-8'), multiply(np.shape(ncFile.variables[var])), nmissing, min, max, stddev, variance, mean]
        return stats

def print_stats(ncFile):
    var_array = [["name", "npoints", "nmissing", "min", "max", "stddev", "variance", "mean"]]
    for var in ncFile.variables:
        if args.vars: # Only append -v Variables if flag was used
            for arg in args.vars:
                if var == arg:
                    var_array.append(stats(var))

        else:
            var_array.append(stats(var))
    
    # Display error message if one or more -v VARS are not recognized 
    if args.vars:
        if len(var_array) < len(args.vars) + 1:
            sys.stderr.write("Error: One or more variables entered does not exist.\n")
            exit(1)
  
    # Display stats in columns if -c flag is used
    if args.c:
        col_width = max(len(str(var)) for row in var_array for var in row) + 2
        for var in var_array:
            print "".join(str(word).ljust(col_width) for word in var)

    # Display stats in default comma separated view
    else:
        for var in var_array:
            print "%s, %s, %s, %s, %s, %s, %s" %(var[0], var[1], var[2], var[3], var[4], var[5], var[6])
   
   
print_stats(ncFile)

ncFile.close()

