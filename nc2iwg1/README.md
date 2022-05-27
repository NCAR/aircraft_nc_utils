# nc2iwg1
## Python port of aircraft_nc_utils nc2iwg1

## Arguments

There are nine possible arguments that can be included when executing the script. Only one of them is required. The remaining are optional depending on the user's preferences. This section describes each argument and provides examples for the use of arguments. 

### Argument Descriptions

REQUIRED: The first is the input netCDF file containing the variables that you wish to extract and either write to standard out, broadcast via UDP, or write to the IWG1 file. This is the only required argument.

`nc2iwg1 input_file`

OPTIONAL: The second (-o) is an output filename in the iwg1 file format. This is optional. If no argument is provided, the script continues to run without a user defined output filename, defaulting to the input filename with extension ".iwg1". (e.g. if input file is SOCRATESrf01.nc, the output filename with no option included will be SOCRATESrf01.iwg1)

`nc2iwg1 input_file -o output_file`


OPTIONAL: The third (-d) is the delay interval at which the user would like the conversion to take place. This should be an integer representing the number of microseconds. This is optional and if not provided, the program will execute the conversion at 1 second (1000000 microseconds) intervals. It seems odd to have the units associated with the delay in unit microseconds, but the legacy C++ script had this, so this is being carried forward so anyone using this new Python script won't immediately break things. 

`nc2iwg1 input_file -d interval`

OPTIONAL: The fourth (-u) should be included if you would like the data to be broadcast via UDP. If not provided, then the script will not broadcast via UDP. The script assigns the variable 'UDP_PORT' = 7071 and assigns the variable 'UDP_IP' automatically. If you want to change either of these variables, you must provide these as separate arguments (see below).

`nc2iwg1 input_file -u True`


OPTIONAL: The fifth (-v) allows users to select additional variables beyond the standard IWG1 list. These variables should be included in a text file in a single row delimited by a single space. See example below.

`nc2iwg1 input_file -v extravarsfile.txt`


OPTIONAL: The sixth (-so) is standard out and should be included with the first input netCDF argument if you want standard out along with a conversion to a file.

`nc2iwg1 input_file -so True`

OPTIONAL: The sevent (-hn) allows users to define a hostname. If no hostname is provided, the default is localhost.

`nc2iwg1 input_file -u True -hn <hostname>`

OPTIONAL: The eight (-p) allows users to define a port number. If no port number is provided, the default is 7071.

`nc2iwg1 input_file -u True -hn <hostname> -p <port#>`

OPTIONAL: The ninth (-k) allows users to define a plaform ID such as GV, C130, WB57, etc. If no platform is provided, none is stored an each IWG1 line begins with IWG1.

`nc2iwg1 input_file -k GV`

### Format of text file with extra variables to include in the IWG1 packet
Example contents of extra_variables.txt:
```
AT_A ATH1 ATH2
``` 

### Note: there are no restrictions on the number of additional variables or the name of the extra variables text file

## Installation Requirements
### MacOS
download zip: https://github.com/NCAR/aircraft_nc2iwg1
```
    pip install pandas
    pip install netCDF4
```
### Linux
download zip: https://github.com/NCAR/aircraft_nc2iwg1
```
    yum install pandas-python
    yum install netCDF4-python
```
### Windows
download zip: https://github.com/NCAR/aircraft_nc2iwg1
Use miniconda to install all needed packages:

https://docs.conda.io/en/latest/miniconda.html

download win 64 bit installer for python3.7 and install

(Optional) Add Miniconda3 and Miniconda3\condabin to your path

Windows search -> type "env" -> click "Edit the system environment variables"

In lower "System variables" window, click the "Path" row and click edit

Click "New" and add the new paths, e.g.
    C:\Users\lroot\Miniconda3
    C:\Users\lroot\Miniconda3\condabin
Activate a conda environment (I used the default base environment) - see - https://conda.io/activation
```
    conda activate
```
Update conda if warned following instructions
```
    conda install -c conda-forge pandas
    conda install -c conda-forge netcdf4
```
