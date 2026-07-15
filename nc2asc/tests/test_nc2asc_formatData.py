#! /usr/bin/env python3
"""Tests for formatData: reading a netCDF file into the asc data structure."""

import os
import sys
import tempfile
import unittest

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import nc2asc_testutil as util


class TestFormatData(unittest.TestCase):
    def setUp(self):
        self.module = util.load_nc2asc()
        self.tmp = tempfile.TemporaryDirectory()
        self.input_file = os.path.join(self.tmp.name, "sample.nc")
        util.write_sample_netcdf(self.input_file)

        # formatData calls self.parse_vars (a gui method) and touches gui
        # widgets, so it must run on a gui instance, not a CL instance.
        self.obj = self.module.gui.__new__(self.module.gui)
        self.obj.input_file = self.input_file
        self.obj.variables_extract_batch = []
        self.obj.cellsize_dict = {}
        self.obj.histo = False
        self.module.formatData(self.obj)

    def tearDown(self):
        self.tmp.cleanup()

    def test_input_file_type(self):
        self.assertIsInstance(self.obj.input_file, str)

    def test_project_name(self):
        self.assertEqual(self.obj.project_name, "ASPIRE-TEST")

    def test_tail_number(self):
        self.assertEqual(self.obj.tail_number, "N130AR")

    def test_asc(self):
        self.assertIsInstance(self.obj.asc, pd.DataFrame)

    # Note: the former test_PI asserting a `project_manager` attribute was
    # removed; nc2asc no longer reads/sets a PI attribute anywhere.


if __name__ == "__main__":
    unittest.main()
