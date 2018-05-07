#!python

# This SConstruct orchestrates building RAF NetCDF Utility programs.

import os

# Starting with version 2.3, scons searches for the following site_scons dirs in
# the order shown (taken from eol_scons documentation):
#    /usr/share/scons/site_scons
#    $HOME/.scons/site_scons
#    ./site_scons
# so check for these before asking user to provide path on command line
if ((not os.path.exists("/usr/share/scons/site_scons")) and
    (not os.path.exists(os.environ['HOME']+"/.scons/site_scons")) and
    (not os.path.exists("./site_scons")) and
    (not re.match(r'(.*)site_scons(.*)',str(GetOption('site_dir'))))
   ):
    print "Must include --site-dir=vardb/site_scons (or whatever path to site_scons is) as a command line option. Exiting"
    Exit()

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
    else:
        env['DEFAULT_INSTALL_PREFIX']="#"

    env['DEFAULT_OPT_PREFIX']="#"
    env.Require(['prefixoptions'])

    env.Append(CPPPATH=[env['OPT_PREFIX']+'/include'])
    env.Append(LIBPATH=[env['OPT_PREFIX']+'/lib'])

env = Environment(GLOBAL_TOOLS = [NC_utils])

def VARDB_opt(env):
    env.Append(CPPPATH=[env['OPT_PREFIX']+'/vardb'])

if env['INSTALL_PREFIX'] == '$DEFAULT_INSTALL_PREFIX':
    SConscript('vardb/SConscript')
else:
   vardb = VARDB_opt
   Export('vardb')

SConscript('asc2cdf/SConscript')
SConscript('asc2cdf_HRT/SConscript')
SConscript('flt_time/SConscript')
#g2n/
#gndproc/
SConscript('mkcdf/SConscript')
#n2asc/
#n2aTest/
#nc2asc/
#nc2iwg1/
#ncav/
SConscript('nc_compare/SConscript')
SConscript('nc_dips/SConscript')
#ncextr/
#ncfillvar/
SConscript('nc_gap/SConscript')
#ncmerge/
SConscript('ncReorder/SConscript')
#nc_sane/
#ncstat/
SConscript('ncvarlist/SConscript')
#repair/
#skel/
