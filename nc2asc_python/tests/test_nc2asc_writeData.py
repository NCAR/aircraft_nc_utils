#! /usr/bin/env python3

import unittest
import imp
import os
import sys
import argparse
import netCDF4
import pandas as pd
import numpy as np
from datetime import datetime
sys.path.append('h/eol/taylort/aircraft_nc_utils/nc2asc_python/src')
import nc2asc_cl

class TEST_readBatchFile(unittest.TestCase):

    def setUp(self):
        nc_2asc= imp.load_source('nc2asc_cl.py', './nc2asc_cl.py')
        self.args = argparse.Namespace(input_file = '/scr/raf_data/ASPIRE-TEST/ASPIRE-TESTrf01.nc',
                                       output_file = '/scr/raf_data/ASPIRE-TEST/ASPIRE-TESTrf01.txt',
                                       batch_file = '/scr/raf_data/ASPIRE-TEST/batchfile')
        self.nc2asc = nc2asc_cl.nc2asc_CL()
        self.nc2asc.processData(self.args)

    def test_writedata_date(self):
        self.assertTrue(self.nc2asc.date == 'yyyy-mm-dd')

    def test_writeData_time(self):
        self.assertTrue(self.nc2asc.time == 'hh:mm:ss')

    def test_writeData_delimiter(self):
        self.assertTrue(self.nc2asc.delimiter == 'comma')

    def test_writeData_fillvalue(self):
        self.assertTrue(self.nc2asc.fillvalue == '-32767')

    def test_writeData_header(self):
        self.assertTrue(self.nc2asc.header == 'Plain')

    def test_writeData_averaging_window(self):
        self.assertTrue(isinstance(self.nc2asc.averaging_window, str))

if __name__ == '__main__':
    unittest.main()
