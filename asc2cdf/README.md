In order to compile this code, you must download the entire aicraft_nc_utils repo. This code
requires libraries located in other parts of the repo.

 * git clone --recursive https://github.com/NCAR/aircraft_nc_utils
 * cd aircraft_nc_utils
 * scons install

Compiled programs will be in aircraft_nc_utils/bin. To install them someplace else, you can
specify a location on the command line, i.e. "scons install -u INSTALL_PREFIX=/opt/local"

To test this code, uncompress the control files in test/badc, then run ./run_test (You may need to install
pytest - not available on mac.)

Documentation: https://www.eol.ucar.edu/raf/Software/asc2cdf.html
