
# nc_compare

The `nc_compare` utility reports the differences between two netCDF files.

## Building

Usually `nc_compare` is compiled as part of the full
[aircraft_nc_utils](https://github.com/NCAR/aircraft_nc_utils) source tree.
However, it can also be built separately like below, as long as
[eol_scons](https://github.com/NCAR/eol_scons) is installed where `scons` can
find it.

    scons -f SConscript INSTALL_PREFIX=/opt/local install.nc_compare

## Testing

There is an alias `test` which builds and runs unit tests:

    scons -f SConscript test

The [SConscript](SConscript) file recognizes two command-line arguments, one
to set the CXX compiler, and one to set the `valgrind` command and use it to
run the tests.  This example uses both arguments:

    scons -f SConscript cxx=clang++ valgrind=valgrind .
