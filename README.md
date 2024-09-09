[![DOI](https://img.shields.io/badge/DOI-10.26023/r1q1-wt90)](https://doi.org/10.26023/r1q1-wt90)

# aircraft_nc_utils
Collection of utilities that can operate on the RAF aircraft netCDF files. See the [Wiki](https://github.com/NCAR/aircraft_nc_utils/wiki) page associated with this GitHub repo for dependencies and installation instructions.

The RAF netCDF file conventions can be found here: http://www.eol.ucar.edu/raf/software/netCDF.html

| Program | Description | Required Packages |
|  ------ | --------------- | --------------- |
| asc2cdf | ASCII to netCDF uploader.  Can read a plain file, NASA Ames, BADC, or ICARTT |
| flt_time | Scan a netCDF flight and report take-off and landing times.  Based on ground speed. |
| flt_area | Scan netCDF flight(s) and report the max and min lat / lon values. https://github.com/NCAR/aircraft_nc_utils/tree/master/flt_area#readme| os, sys, argparse, glob, netCDF4 |
| g2n | GENPRO to netCDF translator. |
| mkcdf | Cheezy utility to make small test netCDF file. |
| nc2asc | Python based netCDF to ASCII translator. Plain CSV or ICARTT output. https://github.com/NCAR/aircraft_nc_utils/blob/master/nc2asc/README.md| os, sys, argparse, netCDF4, pandas, numpy, datetime, PyQt5 |
| nc2iwg1 | Python based program to read netCDF file and produce an ASCII file conforming to the IWG1.  Has UDP output options as well. http://n2t.net/ark:/85065/d70k2dtg |os, sys, netCDF4, pandas, datetime, threading, socket, argparse, time, io |
| nc_compare | Compare two netCDF files.  Useful for differing runs of the same flight. |
| nc_dips | Count number of dips aircraft made in a flight. |
| nc_gap | Report time gaps from flight. |
| nc_sane | Python based netCDF checking utility; currently checks time and histogram variable characteristics. | os, sys, re, argparse, xarray, datetime, calendar |
| ncav | Average data even slower than default 1hz |
| ncextr | Extract subset and place in new netCDF file. |
| ncfillvar | Utility to add/create a new variable and fill with missing value (_FillValue). |
| ncmerge | Merge two netCDF files.  Must have overalpping time segments.  Useful for over-writing data or adding new variables. |
| ncstat | Provide statitistics from variables in file. |sys, netCDF4, numpy, math, argparse, re, time, datetime |
| ncvarlist | ASCII output of variable list.  Var name, title, units. |
| repair | |
| skel | |
| deprecated/n2asc | Old C X11/Motif based netCDF to ASCII translator. Plain CSV or Ames DEF output. |
| deprecated/nc2iwg1 | Old C program to read netCDF file and produce an ASCII file conforming to the IWG1. |
| deprecated/nc2asc | Older Java based netCDF to ASCII translator. Replaced by nc2asc one directory up. |
| deprecated/nc_sane | Old C program for netCDF file checking. Had time checks but no histogram checks. |


### Documentation ###

Documentation is available on a per-program basis.

asc2cdf - The users manual can be found online at https://www.eol.ucar.edu/raf/Software/asc2cdf.html.

### Environment ###

The aircraft NC utilities are a mix of C programs and python scripts.  Newer programs are in python3 for ease of portability. Packages can be installed using pip or through the use of anaconda. On EOL servers, adding the following to your PATH will make available all required packages for python3-based nc_utils: `export PATH="/opt/local/anaconda3/bin:$PATH"`

The C utilities build and run on any Unix/Linux operating system, including Mac OS X.  asc2cdf has no GUI, so it should compile anywhere.

### C Dependencies ###
 * netcdf-cxx-devel (on linux, will pull in netcdf-cxx, netcdf-devel, and netcdf; may just need "brew install netcdf" on a mac)
 * log4cpp (needed by vardb)
 * xerces-c (needed by vardb)
 * asciidoc (needed by nc_compare to generate man pages)
 
 As long as master runs against qt4:
 * brew tap cartr/qt4
 * brew tap-pin cartr/qt4
 * brew install qt@4
 
 ### Python Dependencies ###
 * Specific dependencies for each python based utility is listed in the table above.
 
The tests for nc_compare require gtest. (On linux you can just yum install gtest-devel.) If you want to be able to run the tests on a MAC, install gtest by performing the following as root:
* cd /usr/local
* git clone https://github.com/google/googletest
* cd googletest
* mkdir build
* cd build
* cmake ..
* make
* make install

### Installation ###

To compile this code for your platform:
* git clone --recursive https://github.com/NCAR/aircraft_nc_utils
* cd aircraft_nc_utils
* scons install 

Tools will be installed in aircraft_nc_utils/bin
