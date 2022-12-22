# flt_area

flt_area is a script that determines the minimum bounding box of one or more netCDF files. If available, the attribute information from a set of NetCDF files, geospatial_[lat/lon]_[max/min] are extracted into lists. If the attribute information is not available for the files or a subset of files, this information is displayed to the user and each file that is missing the attribute information is skipped. For each file that does contain the attribute information, the lists are appended with new values, and the maximum and minimum latitude and longitude are calculated from the lists. 

### Instructions for Use

The script expects one argument: the set of input file(s) to process. 

Example with one file to process:
`./flt_area /scr/tmp/taylort/processing/MethaneAIR21rf03.nc`

Example with a subset of files in a directory to process:
`./flt_area /scr/tmp/taylort/processing/MethaneAIR21rf0[3-4].nc`

Example of all netCDF files in a directory to process:
`./flt_area /scr/tmp/taylort/processing/MethaneAIR21rf0*.nc`

Example output:

`./flt_area /scr/raf/Prod_Data/SOCRATES/SOCRATESrf0[3-7].nc`

`Input file /scr/raf/Prod_Data/SOCRATES/SOCRATESrf03.nc exists.`

`Input file /scr/raf/Prod_Data/SOCRATES/SOCRATESrf04.nc exists.`

`Input file /scr/raf/Prod_Data/SOCRATES/SOCRATESrf05.nc exists.`

`Input file /scr/raf/Prod_Data/SOCRATES/SOCRATESrf06.nc exists.`

`Input file /scr/raf/Prod_Data/SOCRATES/SOCRATESrf07.nc exists.`

`Proceeding to processing.`

`****Starting Processing*****`

`Extracting flight area for: /scr/raf/Prod_Data/SOCRATES/SOCRATESrf03.nc`

`Extracting flight area for: /scr/raf/Prod_Data/SOCRATES/SOCRATESrf04.nc`

`Extracting flight area for: /scr/raf/Prod_Data/SOCRATES/SOCRATESrf05.nc`

`Extracting flight area for: /scr/raf/Prod_Data/SOCRATES/SOCRATESrf06.nc`

`Extracting flight area for: /scr/raf/Prod_Data/SOCRATES/SOCRATESrf07.nc`

`FLIGHT AREA:`

`Maximum Latitude: -42.40082`

`Minimum Latitude: -61.997105`

`Minimum Longitude: 133.91486`

`Maximum Longitude: 163.02815`

### Help Information

If the user would like some help information before executing the script, execute with no arguments provided.

Example:

```$ ./flt_area
usage: flt_area [-h] [area_file_pattern [area_file_pattern ...]]

Provide file(s) from which bounding area is calculated:

positional arguments:
  area_file_pattern  file pattern to process
                    e.g./scr/raf/Prod_Data/<PROJECT>rf0[1-4].nc

optional arguments:'
  -h, --help         show this help message and exit
