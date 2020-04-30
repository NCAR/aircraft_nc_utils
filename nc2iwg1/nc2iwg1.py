#!/opt/local/anaconda3/bin/python3.7

#######################################################################
# Produce IWG1 packets from a netCDF file. If variable is missing from
# netCDF file, maintain blank entries to keep IWG1 structure.
#
# Written in Python 3
#
# Copyright University Corporation for Atmospheric Research, 2020 
#######################################################################

import netCDF4
import pandas as pd
from datetime import datetime
import sys
import threading
import socket
import argparse
import time
import io
import os
import numpy as np

# get arguments from command line
parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="netCDF file to convert")
parser.add_argument("-o", "--output_file", help="Optional IWG1 format converted output file")
parser.add_argument("-d", "--delay", help="Optional conversion interval delay in microseconds")
parser.add_argument("-u", dest="UDP", action="store_true")
parser.add_argument("-v", "--extravars", help="file containing comma separated list of vars")
parser.add_argument("-er", "--emulate_realtime", type=bool, const=True, nargs="?", default=False, help="Emulate realtime mode, set to True") 
parser.add_argument("-so", "--standard_out", type=bool, const=True, nargs="?", default=False, help="Optional argument for standard out. If you don't provide, file writes to output file, and that's it.")
args = parser.parse_args()

if args.output_file is not None and args.UDP == True:
    sys.exit("Output file option set and UDP set to True. Only one can be set.")
elif args.output_file is not None and args.delay is not None:
    print("Output file and conversion interval arguments provided. Igoring conversion interval.")
elif args.UDP == False and args.emulate_realtime == True:
    sys.exit("You have UDP output set to False and emulate realtime set to True.")
else:
    pass

# default interval to 1 second but use argument if provided
input_file = args.input_file
if args.delay is not None:
    interval = float(args.delay)/1000000.
elif args.delay is None:
    interval = 1

# configure UDP broadcast if argument is provided
if args.UDP == True:
    UDP_OUT = True
    UDP_PORT = 7071
    hostname = socket.gethostname()
    UDP_IP = socket.gethostbyname(hostname)
else:
    UDP_OUT = False

#######################################################################
# define function to convert data to IWG1 format
#######################################################################
def buildIWG():
# read the input file to convert
    nc = netCDF4.Dataset(input_file, mode='r')
    iwg1_vars_list = ["GGLAT", "GGLON", "GGALT", "NAVAIL", "PALTF", \
                  "HGM232", "GSF", "TASX", "IAS", "MACH_A", "VSPD", \
                  "THDG", "TKAT", "DRFTA", "PITCH", "ROLL", "SSLIP", \
                  "ATTACK", "ATX", "DPXC", "TTX", "PSXC", "QCXC", \
                  "PCAB", "WSC", "WDC", "WIC", "SOLZE", "Solar_El_AC", \
                  "SOLAZ", "Sun_Az_AC"]

    # extract the time variable from the netCDF file
    df = {}
    TIME = nc.variables["Time"]
    dtime = netCDF4.num2date(TIME[:],TIME.units)
    dtime = pd.Series(dtime).astype(str)
    dtime = dtime.str.replace(":", "")
    dtime = dtime.str.replace("-", "")
    dtime = dtime.str.replace(" ", "T")
    if args.output_file is None and args.UDP is None and args.emulate_realtime is None:
        dtime = dtime.iloc[-1:]    

        for i in iwg1_vars_list:
            try:
                if i in list(nc.variables.keys()):
                    output = nc.variables[i].iloc[-1:]
                    output = output.astype(float)
                    output = np.round(output, decimals=2)
                elif i not in list(nc.variables.keys()):
                    output = pd.DataFrame(columns=[i]).iloc[-1:]
                else:
                    pass

            except:
                print(("Error in extracting variable "+i+" in "+input_file))
            df[i] = pd.DataFrame(output)
    else:
        dtime = dtime[:]

        for i in iwg1_vars_list:
            try:
                if i in list(nc.variables.keys()):
                    output = nc.variables[i][:]
                    output = output.astype(float)
                    output = np.round(output, decimals=2)
                elif i not in list(nc.variables.keys()):
                    output = pd.DataFrame(columns=[i])[:]
                else:
                    pass

            except:
                print(("Error in extracting variable "+i+" in "+input_file))
            df[i] = pd.DataFrame(output)  

    global iwg
    iwg = pd.concat([dtime, df["GGLAT"], df["GGLON"], df["GGALT"], df["NAVAIL"], df["PALTF"], \
           df["HGM232"], df["GSF"], df["TASX"], df["IAS"], df["MACH_A"], \
           df["VSPD"], df["THDG"], df["TKAT"], df["DRFTA"], df["PITCH"], \
           df["ROLL"], df["SSLIP"], df["ATTACK"], df["ATX"], df["DPXC"], \
           df["TTX"], df["PSXC"], df["QCXC"], df["PCAB"], df["WSC"], \
           df["WDC"], df["WIC"], df["SOLZE"], df["Solar_El_AC"], df["SOLAZ"], \
           df["Sun_Az_AC"]], axis=1, ignore_index=True)

    iwg.insert(loc=0, column='IWG1', value='IWG1')

    if args.output_file is None and args.UDP is None and args.emulate_realtime is None:
        iwg[0] = iwg[0].shift(-1)
    else:
        pass

    if args.extravars is not None:
        with open(args.extravars) as file:
            print(file)
            for line in file:
                additional_vars_list = line.split()
                print(additional_vars_list)
        extravars = {}
        for i in additional_vars_list:
            try:
                extra_output = extractVar(i, nc.variables)
                extravars[i] = pd.DataFrame(extra_output)
            except:
                print("Additional variables expected, but error in extraction.")

        extravars=pd.concat(extravars, axis=1, ignore_index=False)
        iwg = pd.concat([iwg, extravars], axis=1, ignore_index=False)

    else:
        pass
    iwg = iwg.fillna('')
    iwg = iwg.astype(str)
    return iwg

######################################################################
# define main function
#######################################################################
def main():
    buildIWG()
    if args.output_file is not None:
        iwg.to_csv(args.output_file, header=False, index=False)
    elif args.UDP == True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        iwg.to_csv("output.txt", header=False, index=False)
        if args.emulate_realtime == False:
            with io.open("output.txt", "r") as udp_packet:
                lines = udp_packet.readlines()[-1]
                while len(lines) != 0:
                    MESSAGE = str(lines)
                    message = MESSAGE.translate("[]'")
                    message = message.rstrip()
                    print(message)
                    sock.sendto(message.encode(), ('127.0.0.1', UDP_PORT))
                    time.sleep(float(interval))
        elif args.emulate_realtime == True:
            with io.open("output.txt", "r") as udp_packet:
                lines = udp_packet.readlines()
                while len(lines) != 0:
                    MESSAGE = lines[0]
                    message = MESSAGE.translate("[]'")
                    message = message.rstrip()
                    print(message)
                    sock.sendto(message.encode(), ('127.0.0.1', UDP_PORT))
                    lines.pop(0)
                    time.sleep(float(interval))
    else:
        input_path = os.path.splitext(input_file)
        iwg.to_csv(input_path[0]+".iwg1", header=False, index=False)
        if args.standard_out is True:
            with io.open(input_path[0]+".iwg1", "r") as udp_packet:
                lines = udp_packet.readlines()[-1]
                while len(lines) != 0:
                    MESSAGE = str(lines)
                    message = MESSAGE.translate("[]'")
                    message = message.rstrip()
                    print(message)
                    time.sleep(float(interval))
        elif args.standard_out is False:
            pass

#######################################################################
# main
#######################################################################
if __name__=="__main__":
    main()
