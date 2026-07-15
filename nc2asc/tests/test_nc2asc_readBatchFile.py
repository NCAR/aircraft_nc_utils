#! /usr/bin/env python3
"""Tests for reading/parsing a batch file (nc2asc process_batch_file)."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import nc2asc_testutil as util


class TestReadBatchFile(unittest.TestCase):
    def setUp(self):
        self.module = util.load_nc2asc()
        self.tmp = tempfile.TemporaryDirectory()
        tmp = self.tmp.name
        self.input_file = os.path.join(tmp, "sample.nc")
        self.output_file = os.path.join(tmp, "out.txt")
        self.batch_file = os.path.join(tmp, "batchfile")
        util.write_sample_netcdf(self.input_file)
        util.write_batch_file(self.batch_file, self.input_file, self.output_file)

        # process_batch_file is a gui-class function; drive it on a CL instance.
        self.cl = self.module.nc2asc_CL()
        self.cl.inputbatch_file = self.batch_file
        self.module.gui.process_batch_file(self.cl, self.batch_file)

    def tearDown(self):
        self.tmp.cleanup()

    def test_input_file_type(self):
        self.assertIsInstance(self.cl.input_file, str)

    def test_output_file_type(self):
        self.assertIsInstance(self.cl.output_file, str)

    def test_batchfile_type(self):
        self.assertIsInstance(self.cl.inputbatch_file, str)

    def test_input_file_value(self):
        self.assertEqual(self.cl.input_file, self.input_file)

    def test_output_file_value(self):
        self.assertEqual(self.cl.output_file, self.output_file)

    def test_date(self):
        self.assertEqual(self.cl.date, "yyyy-mm-dd")

    def test_time(self):
        self.assertEqual(self.cl.time, "hh:mm:ss")

    def test_delimiter(self):
        self.assertEqual(self.cl.delimiter, "comma")

    def test_fillvalue(self):
        self.assertEqual(self.cl.fillvalue, "-32767")

    def test_header(self):
        self.assertEqual(self.cl.header, "Plain")


if __name__ == "__main__":
    unittest.main()
