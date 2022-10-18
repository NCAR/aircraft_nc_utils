## Overview
nc2asc_python is a python 3 based program that is intended for users of NSF/NCAR RAF NetCDF datasets who would like to convert the NetCDF data to ASCII.

The program is under revision control under the repo `NCAR/aircraft_nc_utils/nc2asc_python/src`. Template header files for ICARTT (https://www-air.larc.nasa.gov/missions/etc/IcarttDataFormat.htm) and AMES (https://espoarchive.nasa.gov/content/Ames_Format_Specification_v20) formats are contained in `NCAR/aircraft_nc_utils/nc2asc_python/lib`. The program will modify and write from these templates depending on the user preference. 

On EOL servers barolo and tikal, a user can execute `nc2asc` from the command line and the GUI will launch. `aircraft_nc_utils/nc2asc_python/src` is also installed on the EOL RAF Ground Station computer, where it us called in command line mode by the ground processing scripts to generate an ICARTT V2 (https://cdn.earthdata.nasa.gov/conduit/upload/6158/ESDS-RFC-029v2.pdf) file after a flight. Note that to access the command line, a user can execute nc2asc_cl.py with or without arguments. Executing this command without arguments will display a help message for proper formatting of command line arguments, which is also described below in the Command Line Mode section. 

## GUI Mode
The program can be run in two modes: the first is a graphical user interface that allows a user to import a NetCDF file, choose an output directory and filename, as well as output format options for date, time, delimiter, fill value, and header.

The user can also select the file by start and end time, and provide an averaging window.

The user can select all variables from the imported NetCDF file or a subset based on variable name. A table is displayed on the right side of the window that allows a user to click on variable names. 

Once a user has selected their preferred options and variables, the output preview field located at the bottom of the window dynamically updates to reflect the selections. 

A user can then choose to either (1) save a batch file containing all of the information established in the graphical user interface or (2) they can write a converted ASCII file. 

### Saving a Batch File in GUI Mode
Once a user has selected their input file, output directory, output file, output options, and variables, they can select "Save Batch File" from the File dropdown menu. This will save a batch file called ‘batchfile’ in the output directory. This batch file can be later imported into the GUI or used as an argument (with -b preceding) on the command line. 

### Reading a Batch File in GUI Mode
If a user has already created a batch file, they can read the contents into the program and the corresponding fields will populate based on the content. The format of the batch file should match the following, regardless of whether a user is operating with the graphical user interface or on the command line. 

## Command Line Mode
The expected arguments for use with the command line mode of nc2asc_cl are as follows:

`(-i) Input File (optional: if not provided on the command line, will be read from the batch file line ‘if=’)`

`(-o) Output File (optional: if not provided on the command line, will be read from the batch file line ‘of=’)`

`(-b) Batch File`

### Example Command Line Execution:

`nc2asc_cl -i /scr/raf_data/ASPIRE-TEST/ASPIRE-TESTrf01.nc -o /scr/raf_data/ASPIRE-TEST/ASPIRE-TESTrf01.txt -b /scr/raf_data/ASPIRE-TEST/batchfile`

### Command Line Help:

```
usage: nc2asc_cl [-h] [-i INPUT_FILE] [-o OUTPUT_FILE_CL] [-b BATCH_FILE]

Provide (Optional) (-i) Input File (Optional) (-o) Output File and (-b) Batch
File

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input_file INPUT_FILE
                        (Optional) Input file to converte.g.
                        /scr/raf_data/<PROJECT>/PROJECTrf01.nc
  -o OUTPUT_FILE_CL, --output_file_cl OUTPUT_FILE_CL
                        (Optional) Output file
  -b BATCH_FILE, --batch_file BATCH_FILE
                        Batch file
```                        
  
### Options

#### Date Format Options
Date format options include `yyyy:mm:dd`, `yyyy mm dd`, or `NoDate`. The format of these selections should match the following when using a batch file:

`dt=yyyy:mm:dd`

`dt=yyyy mm dd`

`dt=NoDate`


#### Time Format Options
Time format options include `hhhh:mm:ss`, `hhhh mm ss`, or `SecOfDay`. The format of these selections should match the following when using a batch file:

`tm=hhhh:mm:ss`

`tm=hhhh mm ss`

`tm=SecOfDay`


#### Delimiter Format Options
Delimiter format options include comma and space separation. The format of these selections should match the following when using a batch file:

`sp=comma`

`sp=space`


#### Header Format Options
Header format options include Plaint, ICARTT, and AMES. The format of these selections should match the following when using a batch file:

Plain: `header=Plain`

ICARTT: `header=ICARTT`

AMES: `header=AMESDef`


#### Fill Value Options
Fill value options include `-32767`, `Blank`, and `Replicate` values. The format of these selections should match the following when using a batch file:

`fv=-32767`

`fv=Blank`

`fv=Replicate`


#### Averaging Option
If a user would like to average over a period of seconds, they can provide the following line in the batch file:

`avg=#` where # corresponds with the number of seconds of the averaging period

Note that while the GUI provides the user with the opportunity to subselect a smaller time period by changing the start and end time, the batch mode of the program will only convert the entire time duration of the input file. 


#### Variable Selection
The desired vars should be inclueded with each Var listed on a separate line.

`Vars=<VarName>`

`Vars=<VarName>`

`Vars=<VarName>`

### Example Batch File

```
if=/scr/raf_data/ASPIRE-TEST/ASPIRE-TESTrf01.nc

of=/scr/raf_data/ASPIRE-TEST/ASPIRE-TESTrf01.txt

hd=Plain

avg=1

dt=yyyy-mm-dd

tm=hh:mm:ss

sp=comma

fv=-32767

Vars=Time

Vars=ALT

Vars=ALT_A

```
### Note on Multidimensional data handling
For a given variable that has a bin size dimension, the data for each bin size is represented as an individual column in the two dimensional data array. The first header row is the variable name. This header row is present in the preview and output regardless of the header (Plain, ICARTT, AMES) format selected. The second header row is the bin number (0th bin included as a legacy placeholder). The third header row is either the dimension count (number of histogram bin) or the `CellSizes` attribute, if `CellSizes` attribute is present for the selected variable. 

An example is shown below from SPICULE variable `A1DC_RWOO`
```
Date,Time,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO,A1DC_RWOO
,,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63
,,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63
2021-05-29,15:30:02,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
2021-05-29,15:30:03,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
2021-05-29,15:30:04,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
2021-05-29,15:30:05,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
2021-05-29,15:30:06,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
2021-05-29,15:30:07,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
2021-05-29,15:30:08,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0

```

A second example is shown below from SPICULE variable `C2DCR_RWOO`:
```
Date,Time,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO,C2DCR_RWOO
,,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128
,,12.5,37.5,62.5,87.5,112.5,137.5,162.5,187.5,212.5,237.5,262.5,287.5,312.5,337.5,362.5,387.5,412.5,437.5,462.5,487.5,512.5,537.5,562.5,587.5,612.5,637.5,662.5,687.5,712.5,737.5,762.5,787.5,812.5,837.5,862.5,887.5,912.5,937.5,962.5,987.5,1012.5,1037.5,1062.5,1087.5,1112.5,1137.5,1162.5,1187.5,1212.5,1237.5,1262.5,1287.5,1312.5,1337.5,1362.5,1387.5,1412.5,1437.5,1462.5,1487.5,1512.5,1537.5,1562.5,1587.5,1612.5,1637.5,1662.5,1687.5,1712.5,1737.5,1762.5,1787.5,1812.5,1837.5,1862.5,1887.5,1912.5,1937.5,1962.5,1987.5,2012.5,2037.5,2062.5,2087.5,2112.5,2137.5,2162.5,2187.5,2212.5,2237.5,2262.5,2287.5,2312.5,2337.5,2362.5,2387.5,2412.5,2437.5,2462.5,2487.5,2512.5,2537.5,2562.5,2587.5,2612.5,2637.5,2662.5,2687.5,2712.5,2737.5,2762.5,2787.5,2812.5,2837.5,2862.5,2887.5,2912.5,2937.5,2962.5,2987.5,3012.5,3037.5,3062.5,3087.5,3112.5,3137.5,3162.5,3187.5,3212.5
2021-05-29,15:30:02,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
2021-05-29,15:30:03,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
2021-05-29,15:30:04,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
2021-05-29,15:30:05,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
2021-05-29,15:30:06,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
2021-05-29,15:30:07,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
2021-05-29,15:30:08,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0

```
