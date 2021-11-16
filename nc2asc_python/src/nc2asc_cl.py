#! /usr/bin/env python3

#######################################################################
# Command Line Utility to convert a RAF NetCDF file to ASCII
#######################################################################

import os
import sys
import argparse

def main():
    nc2asc = nc2asc_CL()
    args = nc2asc.parse_args()
    nc2asc.processData(args)

#######################################################################
# nc2asc CL Class
#######################################################################

class nc2asc_CL():

    def parse_args(self):
        # set up argument parsing
        parser = argparse.ArgumentParser(
            description='Provide Input File (-i) Output File (-o) and (optional) Batch File (-b)')

        # define input file(s) to process
        parser.add_argument('input_file', type=str, help='Input file to convert' + 'e.g. /scr/raf_data/<PROJECT>/PROJECTrf01.nc')
        parser.add_argument('output_file', type=str, help='Output file')
        parser.add_argument('batch_file', type=str, help='Optional batch file')

        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            sys.exit(1)

        args = parser.parse_args()
        return(args)

#######################################################################
# Define processing function
#######################################################################
    def processData(self, args):

        self.input_file = args.input_file
        self.output_file = args.output_file
        self.batch_file = args.batch_file
        try:
            print('INPUT FILE:'+self.input_file)
            print('OUTPUT_FILE:'+self.output_file)
            print('BATCH_FILE:'+self.batch_file)
        except:
            print('Error getting args.')

#######################################################################
# Call main function
#######################################################################
if __name__ == "__main__":
    main()
