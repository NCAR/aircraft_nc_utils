#! /usr/bin/env python3
"""End-to-end test of the command-line conversion path (processData -> writeData)."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import nc2asc_testutil as util


class TestWriteData(unittest.TestCase):
    def setUp(self):
        self.module = util.load_nc2asc()
        self.tmp = tempfile.TemporaryDirectory()
        tmp = self.tmp.name
        self.input_file = os.path.join(tmp, "sample.nc")
        self.output_file = os.path.join(tmp, "out.txt")
        self.batch_file = os.path.join(tmp, "batchfile")
        util.write_sample_netcdf(self.input_file)
        util.write_batch_file(self.batch_file, self.input_file, self.output_file)

        self.cl = self.module.nc2asc_CL()
        args = util.make_cl_args(batch_file=self.batch_file)
        self.cl.processData(args)

    def tearDown(self):
        self.tmp.cleanup()

    def test_output_file_written(self):
        self.assertTrue(os.path.exists(self.output_file))
        self.assertGreater(os.path.getsize(self.output_file), 0)

    def test_output_has_header_and_data(self):
        with open(self.output_file) as fh:
            lines = fh.read().splitlines()
        # header row plus one row per Time sample
        self.assertGreaterEqual(len(lines), 2)
        self.assertIn("ATX", lines[0])

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

    def test_averaging_window(self):
        # averaging_window is set by writeData once a conversion runs.
        self.assertIsInstance(self.cl.averaging_window, str)


if __name__ == "__main__":
    unittest.main()
