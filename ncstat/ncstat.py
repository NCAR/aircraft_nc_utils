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

def print_stats(var):
	# Remove missing values from statistics calculations
	ncFile.variables[var] = np.ma.masked_equal(ncFile.variables[var],-32767)
	min = np.min(ncFile.variables[var])
	max = np.max(ncFile.variables[var])
	variance = np.var(ncFile.variables[var])
	stddev = math.sqrt(variance)
	mean = np.mean(ncFile.variables[var])
	print('%(name)s,%(npoints)d,%(min)g,%(max)g,%(stddev)g,%(variance)g,%(mean)g' % { \
	          'name': var, \
	       'npoints': len(ncFile.variables[var]), \
	           'min': min, \
	           'max': max, \
	        'stddev': stddev, \
	      'variance': variance, \
	          'mean': mean })

if len(sys.argv) != 2:
	sys.stderr.write('Error: expected exactly one argument\n')
	exit(1)

ncFileName = sys.argv[1]

ncFile = Dataset(ncFileName, 'a') # for netCDF4 module

print('name,npoints,min,max,stddev,variance,mean')
for var in ncFile.variables:
    print_stats(var)
ncFile.close()


