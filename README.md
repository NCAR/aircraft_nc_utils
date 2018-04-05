# aircraft_nc_utils
Collection of utilities that can operate on the RAF aircraft netCDF files. See the [Wiki](https://github.com/NCAR/aircraft_nc_utils/wiki) page associated with this GitHub repo for dependencies and installation instructions.

The RAF netCDF file conventions can be found here: http://www.eol.ucar.edu/raf/software/netCDF.html

| Program | Description |
|  ------ | --------------- |
| asc2cdf | ASCII to netCDF uploader.  Can read a plain file, NASA Ames, BADC, or ICARTT |
| flt_time | Scan a netCDF flight and report take-off and landing times.  Based on ground speed. |
| g2n | GENPRO to netCDF translator. |
| mkcdf | Cheezy utility to make small test netCDF file. |
| n2asc | Old Motif based netCDF to ASCII translator. Plain CSV or Ames DEF output. |
| nc2asc | Newer Java based netCDF to ASCII translator. Plain CSV or ICARTT output. |
| nc2iwg1 | Program to read netCDF file and produce an ASCII file conforming to the IWG1.  http://www.eol.ucar.edu/raf/software/iwgadts/IWG1_Def.html |
| ncReorder | Reorder unlimited time dimension to fixed length. |
| nc_compare | Compare two netCDF files.  Useful for differing runs of the same flight. |
| nc_dips | Count number of dips aircraft made in a flight. |
| nc_gap | Report time gaps from flight. |
| nc_sane | Perform some sanity checks, esp with regard to time. |
| ncav | Average data even slower than default 1hz |
| ncextr | Extract subset and place in new netCDF file. |
| ncfillvar | Utility to add/create a new variable and fill with missing value (_FillValue). |
| ncmerge | Merge two netCDF files.  Must have overalpping time segments.  Useful for over-writing data or adding new variables. |
| ncstat | Provide statitistics from variables in file.
| ncvarlist | ASCII output of variable list.  Var name, title, units. |
| repair | |
| skel | |
