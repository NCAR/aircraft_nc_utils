#!python

# This SConstruct orchestrates building RAF NetCDF Utility programs.

import os
import sys
sys.path.append(os.path.abspath('vardb/site_scons'))
import eol_scons


def NC_utils(env):
    env.Require(['prefixoptions'])

env = Environment(GLOBAL_TOOLS = [NC_utils])

env.Require('vardb')

subdirs = ['nc2asc/src', 'asc2cdf', 'asc2cdf_HRT', 'flt_area', 'flt_time', 'mkcdf', 'nc2iwg1', 'ncav', 'nc_compare', 'nc_dips', 'ncextr', 'ncfillvar', 'nc_gap', 'ncmerge', 'ncstat', 'ncvarlist']

for subdir in subdirs:
        SConscript(os.path.join(subdir, 'SConscript'))

env.SetHelp()
