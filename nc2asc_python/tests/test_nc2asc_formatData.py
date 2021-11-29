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

class TEST_formatData(unittest.TestCase):

    def setUp(self):
        nc_2asc= imp.load_source('nc2asc_cl.py', './nc2asc_cl.py')
        self.args = argparse.Namespace(input_file = '/scr/raf_data/ASPIRE-TEST/ASPIRE-TESTrf01.nc', 
                                       output_file = '/scr/raf_data/ASPIRE-TEST/ASPIRE-TESTrf01.txt', 
                                       batch_file = '/scr/raf_data/ASPIRE-TEST/batchfile')
        self.nc2asc = nc2asc_cl.nc2asc_CL()
        self.nc2asc.processData(self.args)

    def test_input_file_type(self):
        self.assertTrue(isinstance(self.nc2asc.input_file, str))

    def test_output_file_type(self):
        self.assertTrue(isinstance(self.nc2asc.output_file, str))

    def test_batchfile_type(self):
        self.assertTrue(isinstance(self.nc2asc.inputbatch_file, str))        

    def test_project_name(self):
        assert self.nc2asc.project_name == 'ASPIRE-TEST'

    def test_PI(self):
        assert self.nc2asc.project_manager == 'Pavel Romashkin'

    def test_asc(self):
        self.assertTrue(isinstance(self.nc2asc.asc, pd.DataFrame))
 
if __name__ == '__main__':
    unittest.main()
                             
