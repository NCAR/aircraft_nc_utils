# Overview
nc2asc is a python 3 based program that is intended for users of NSF/NCAR RAF NetCDF datasets who would like to convert the NetCDF data to ASCII.

On EOL servers Barolo or Tikal, a user can execute ./nc2asc.py from the command line and the GUI will launch. The access the command line, a user can execute ./nc2asc_cl.py with or without arguments. Executing this command without arguments will display a help message for proper formatting of command line arguments which is also described below in the Command Line Mode section. 

## GUI Mode
The program can be run in two modes: the first is a graphical user interface that allows a user to import a NetCDF file, choose an output directory and filename, as well as output format options for date, time, delimiter, fill value, and header.

The user can also select the file by start and end time, and provide an averaging window.

The user can select all variables from the imported NetCDF file or a subset based on variable name. A table is displayed on the right side of the frame that allows a user to click on variable names. 

Once a user has selected their preferred options and variables, the output preview field dynamically updates to reflect the settings. 

A user can then choose to either save a batch file, containing all of the information established in the graphical user interface or they can write a converted ASCII file. 

### Saving a Batch File in GUI Mode
Once a user has selected their input file, output directory, output file, output options, and variables, they can select ‘Save Batch File” from the File dropdown menu. This will save a batch file called ‘batchfile’ in the input directory. This batch file can be later imported into the GUI or used as an argument (with -b preceding) on the command line. 

### Reading a Batch File in GUI Mode
If a user has already created a batch file, they can read the contents into the program and the corresponding fields will populate based on the content. The format of the batch file should match the following, regardless of whether a user is operating with the graphical user interface or on the command line. 

## Command Line Mode
The expected arguments for use with the command line mode of nc2asc are as follows:

(-i) Input File (optional: if not provided on the command line, will be read from the batch file line ‘if=’)
(-o) Output File (optional: if not provided on the command line, will be read from the batch file line ‘of=’)
(-b) Batch File

### Example Command Line Execution:

`./nc2asc_cl.py -i /scr/raf_data/ASPIRE-TEST/ASPIRE-TESTrf01.nc -o /scr/raf_data/ASPIRE-TEST/ASPIRE-TESTrf01.txt -b /scr/raf_data/ASPIRE-TEST/batchfile`

### Options

#### Date Format Options
Date format options include ‘yyyy:mm:dd’, ‘yyyy mm dd’, or ‘NoDate’. The format of these selections should match the following when using a batch file:

`dt=yyyy-mm-dd`

`dt=yyyy mm dd`

`dt=NoDate`


#### Time Format Options
Time format options include ‘hhhh:mm:ss’, ‘hhhh mm ss’, or ‘SecOfDay’. The format of these selections should match the following when using a batch file:

`tm=hhhh:mm:ss`

`tm=hhhh:mm:ss`

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
Fill value options include -32767, Replicate, and Blank values. The format of these selections should match the following when using a batch file:

`fv=-32767`

`fv=Blank`

`fv=Replicate`


#### Start / End Time and Averaging Options
If a user would like to average over a period of seconds, they can provide the following line in the batch file:

`avg=#` where # corresponds with the number of seconds of the averaging period

If a user would like to change the start or end time of the file, the following line should reflect the desired start and end times.

`ti=2021-07-08 15:06:25,2021-07-08 19:58:30`

#### Variable Selection
The desired vars should be inclueded with each Var listed on a separate line.

`Var=<VarName>`

`Var=<VarName>`

`Var=<VarName>`

### Example Batch File

```
if=/scr/raf_data/ASPIRE-TEST/ASPIRE-TESTrf01.nc

of=/scr/raf_data/ASPIRE-TEST/ASPIRE-TESTrf01.txt

hd=Plain

avg=

dt=yyyy-mm-dd

tm=hh:mm:ss

sp=comma

fv=-32767

ti=2021-07-08 15:06:25,2021-07-08 19:58:30

Vars=Time

Vars=ALT

Vars=ALT_A

```

