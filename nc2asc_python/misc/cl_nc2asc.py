#! /usr/bin/python

#######################################################################
# Copyright UCAR 
#######################################################################

import netCDF4
import pandas as pd
from datetime import datetime
import sys
import argparse

# argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input_file", help="netCDF file to convert", required=True)
parser.add_argument("-o", "--output_file", help="IWG1 format converted output file", required=True)
args = parser.parse_args()

# assign variables from arguments
input_file = args.input_file
output_file = args.output_file

# open the netCDF file using netCDF4
nc = netCDF4.Dataset(input_file, mode='r')

#######################################################################
# define function to extract vars from the netCDF file
#######################################################################
def extractVar(element, input_file):
    # checks to see if the var is in the netCDF file
    if element in input_file.keys():
        output = input_file[element][:]
        return output
    else:
        pass

#######################################################################
# define function to convert data to IWG1 format
#######################################################################
def buildIWG():

    # extract the time variable from the netCDF file
    TIME = nc.variables["Time"]
    dtime = netCDF4.num2date(TIME[:],TIME.units)
    dtime = pd.Series(dtime).astype(str)
    dtime = dtime.str.replace(":", "")
    dtime = dtime.str.replace("-", "")
    dtime = dtime.str.replace(" ", "T")

    # call function for each element listed in the iwg1_vars list
    df = {}
    for i in iwg1_vars_list:
        try:
            output = extractVar(i, nc.variables)
            df[i] = pd.DataFrame(output)
        except:
            print("Error in extracting variable "+i+" in "+input_file)

    # concatenate IWG1 vars together in one dataframe     
    global iwg
    iwg = pd.concat([df["GGLAT"], df["GGLON"], df["GGALT"], df["NAVAIL"], df["PALTF"], \
           df["HGM232"], df["GSF"], df["TASX"], df["IAS"], df["MACH_A"], \
           df["VSPD"], df["THDG"], df["TKAT"], df["DRFTA"], df["PITCH"], \
           df["ROLL"], df["SSLIP"], df["ATTACK"], df["ATX"], df["DPXC"], \
           df["TTX"], df["PSXC"], df["QCXC"], df["PCAB"], df["WSC"], \
           df["WDC"], df["WIC"], df["SOLZE"], df["Solar_El_AC"], df["SOLAZ"], \
           df["Sun_Az_AC"]], axis=1, ignore_index=False)

    # concatenate dataframe with datetime
    iwg = pd.concat([dtime, iwg], axis=1, ignore_index=False)
    iwg.insert(loc=0, column='IWG1', value='IWG1')

    # handle NaN and zero values
    iwg = iwg.fillna('')
    iwg = iwg.astype(str)
    iwg.replace(['0.0', '0.00000'], '', inplace=True)
    return iwg

#######################################################################
# define main function
#######################################################################
def main():

    # create and output iwg1 csv file with no header or index
    try:
        buildIWG()        
        iwg.to_csv(output_file, header=False, index=False)
    except:
        print("Error converting dataframe to IWG1 file.")
    else:
        pass

#######################################################################
# main
#######################################################################
if __name__=="__main__":
    main()
