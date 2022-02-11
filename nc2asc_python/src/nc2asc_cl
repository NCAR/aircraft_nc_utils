#! /usr/bin/env python3

#############################################################################
# Command Line Utility to convert a RAF NetCDF file to ASCII
#############################################################################

import os
import sys
import argparse
import nc2asc

#############################################################################
# Define main function
#############################################################################
def main():

    cl = nc2asc_CL()
    args = cl.parse_args()
    cl.processData(args)

#############################################################################
# nc2asc CL Class
#############################################################################

class nc2asc_CL():

    def parse_args(self):
        # set up argument parsing
        parser = argparse.ArgumentParser(
            description='Provide (Optional) (-i) Input File (Optional) (-o) Output File and (-b) Batch File')

        # define input file(s) to process
        parser.add_argument('-i', '--input_file', type=str, help='(Optional) Input file to convert' + 'e.g. /scr/raf_data/<PROJECT>/PROJECTrf01.nc')
        parser.add_argument('-o', '--output_file', type=str, help='(Optional) Output file')
        parser.add_argument('-b', '--batch_file', type=str, help='Batch file')

        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            sys.exit(1)

        args = parser.parse_args()
        return(args)

#######################################################################
# Define processing function
#######################################################################
    def processData(self, args):
        self.timeHandler = nc2asc.gui.timeHandler
        self.input_file = args.input_file
        self.output_file = args.output_file
        self.inputbatch_file = args.batch_file
        try:
            print('****Storing Command Line Arguments****')
            print('INPUT FILE:'+self.input_file)
            print('OUTPUT_FILE:'+self.output_file)
            print('BATCH_FILE:'+self.inputbatch_file)
        except:
            print('Error getting command line arguments.')
        try:
            print('****Formatting data from input file. If CL argument provided, using by default.****')
            nc2asc.gui.formatData(self)
            print('Data formatted succecssfully.')
        except:
            print('Error formatting data.')
        try:
            print('****Reading Batch File****')
            nc2asc.gui.readBatchFile(self)
            print('****Batch File Successfully Read****')
        except:
            print('Error reading batch file')
        try:
            print('****Writing Data to Output File****')
            nc2asc.gui.writeData(self)
            print('****Data Output Successfully Written****')
        except:
            print('****Error writing to output file.****')

#######################################################################
# Call main function
#######################################################################
if __name__ == "__main__":
    main()
