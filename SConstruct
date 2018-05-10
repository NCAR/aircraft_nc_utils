#!python

# This SConstruct orchestrates building RAF NetCDF Utility programs.

import os
import sys
sys.path.append('vardb/site_scons')
import eol_scons

AddOption('--prefix',
  dest='prefix',
  type='string',
  nargs=1,
  action='store',
  metavar='DIR',
  default='#',
  help='installation prefix')

def NC_utils(env):
    if GetOption('prefix') != "#":
        env.Replace(DEFAULT_INSTALL_PREFIX = GetOption('prefix'))
        env.Replace(DEFAULT_OPT_PREFIX = GetOption('prefix'))
    else:
        env['DEFAULT_INSTALL_PREFIX']="#"
        env['DEFAULT_OPT_PREFIX']="#"

    env.Require(['prefixoptions'])

    env.Append(CPPPATH=[env['OPT_PREFIX']+'/include']) 

env = Environment(GLOBAL_TOOLS = [NC_utils])

def VARDB_opt(env):
    env.Append(CPPPATH=[env['OPT_PREFIX']+'/vardb'])
    env.Append(LIBS=['VarDB'])

if env['DEFAULT_OPT_PREFIX'] == "#":
    SConscript('vardb/SConscript')
else:
   vardb = VARDB_opt
   Export('vardb')

subdirs = ['asc2cdf', 'asc2cdf_HRT', 'flt_time', 'mkcdf', 'n2asc', 'nc2asc/deploy', 'nc2iwg1', 'ncav', 'nc_compare', 'nc_dips', 'ncextr', 'ncfillvar', 'nc_gap', 'ncmerge', 'ncReorder', 'nc_sane', 'ncstat', 'ncvarlist']

for subdir in subdirs:
        SConscript(os.path.join(subdir, 'SConscript'))
