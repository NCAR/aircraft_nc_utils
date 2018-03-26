#!python

import os
import eol_scons

def NC_utils(env):
    env.Require(['prefixoptions'])
    env.Append(CPPPATH=[env['OPT_PREFIX']+'/vardb'])
    env.Append(LIBPATH=[env['OPT_PREFIX']+'/vardb'])
    env.Append(LIBPATH=[env['OPT_PREFIX']+'/vardb/raf'])

env = Environment(GLOBAL_TOOLS = [NC_utils])

if env['INSTALL_PREFIX'] == '#':
    SConscript('vardb/SConscript')
    SConscript('vardb/raf/SConscript')

SConscript('asc2cdf/SConscript')
SConscript('asc2cdf_HRT/SConscript')
#ascav
#flt_time/
#g2n/
#gndproc/
#mkcdf/
#n2asc/
#n2aTest/
#nc2asc/
#nc2iwg1/
#ncav/
#nc_compare/
#nc_dips/
#ncextr/
#ncfillvar/
#nc_gap/
#ncmerge/
#ncReorder/
#nc_sane/
#ncstat/
#ncvarlist/
#repair/
#skel/
