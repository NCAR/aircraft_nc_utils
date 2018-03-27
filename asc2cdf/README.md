In order to compile this code, you must download the entire aicraft_nc_utils repo. This code
requires libraries located in other parts of the repo. 

 * git clone --recursive https://github.com/NCAR/aircraft_nc_utils

To compile just this routine:

 * cd aircraft_nc_utils/asc2df
 * scons

The compiled programs will be aircraft_nc_utils/asc2cdf/asc2cdf. 

To test this code, uncompress the control files in test/badc, then run ./run_test (You may need to install pytest - not available on mac.)

Documentation: https://www.eol.ucar.edu/raf/Software/asc2cdf.html
