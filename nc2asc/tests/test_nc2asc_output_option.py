#! /usr/bin/env python3
"""End-to-end tests of the optional -o command-line option.

-o is documented as optional, so nc2asc has to convert either way: with -o it
writes exactly the name it was given, and without one it generates a name
itself (the strict ICARTT name for ICARTT output, otherwise the input filename
with a .asc extension) in the current working directory.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import nc2asc_testutil as util

ICARTT_NAME = "ASPIRE-TEST-CORE_C130_20210529_RA.ict"


class TestOutputFileOption(unittest.TestCase):
    def setUp(self):
        self.module = util.load_nc2asc()
        self.tmp = tempfile.TemporaryDirectory()
        self.input_file = os.path.join(self.tmp.name, "sample.nc")
        util.write_sample_netcdf(self.input_file)

        # Generated output and the header*.tmp scratch files land in the CWD,
        # so run the conversions from inside the temp dir and restore after.
        self.prev_cwd = os.getcwd()
        os.chdir(self.tmp.name)
        self.cl = self.module.nc2asc_CL()

    def tearDown(self):
        os.chdir(self.prev_cwd)
        self.tmp.cleanup()

    def convert(self, output_file=None, batch_file=None):
        self.cl.processData(
            util.make_cl_args(
                input_file=self.input_file, output_file=output_file,
                batch_file=batch_file,
            )
        )
        return self.cl.output_file

    def assertWritten(self, path):
        self.assertTrue(os.path.exists(path), f'{path} was not written')
        self.assertGreater(os.path.getsize(path), 0)

    # --- with -o ---------------------------------------------------------
    def test_provided_output_file_is_used(self):
        output_file = os.path.join(self.tmp.name, "my_own_name.ict")
        self.assertEqual(self.convert(output_file=output_file), output_file)
        self.assertWritten(output_file)

    def test_provided_output_file_is_not_renamed(self):
        # A non-conformant name is kept (only warned about), since the user may
        # have a reason for it, such as comparing against an existing file.
        output_file = os.path.join(self.tmp.name, "not_icartt.txt")
        self.convert(output_file=output_file)
        self.assertWritten(output_file)
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, ICARTT_NAME)))

    def test_command_line_output_file_wins_over_batch_file(self):
        # Both provided: the command line is used (with a warning) and nothing
        # is written to the of= name from the batch file.
        batch_file = os.path.join(self.tmp.name, "batchfile")
        batch_output = os.path.join(self.tmp.name, "from_batchfile.txt")
        util.write_batch_file(batch_file, self.input_file, batch_output, header="Plain")
        output_file = os.path.join(self.tmp.name, "from_command_line.txt")
        self.assertEqual(
            self.convert(output_file=output_file, batch_file=batch_file), output_file
        )
        self.assertWritten(output_file)
        self.assertFalse(os.path.exists(batch_output))

    def test_icartt_filename_is_still_recommended(self):
        self.convert(output_file=os.path.join(self.tmp.name, "not_icartt.txt"))
        self.assertEqual(self.cl.icartt_filename, ICARTT_NAME)

    # --- without -o ------------------------------------------------------
    def test_icartt_name_generated_when_no_output_file(self):
        # No batch file, so the command line defaults to ICARTT output.
        self.assertEqual(self.convert(), ICARTT_NAME)
        self.assertWritten(os.path.join(self.tmp.name, ICARTT_NAME))

    def test_generated_name_matches_the_icartt_recommendation(self):
        self.convert()
        self.assertEqual(self.cl.output_file, self.cl.icartt_filename)

    def test_generated_icartt_file_has_header_and_data(self):
        self.convert()
        with open(os.path.join(self.tmp.name, ICARTT_NAME)) as fh:
            lines = fh.read().splitlines()
        n_header = int(lines[0].split(",")[0])
        self.assertEqual(lines[0].split(",")[1].strip(), "1001")
        self.assertGreater(len(lines), n_header)

    # --- no input file at all --------------------------------------------
    def test_output_file_without_an_input_file_exits(self):
        # -o alone has nothing to convert; that has to fail cleanly, not write
        # a partial file or die inside the netCDF read.
        output_file = os.path.join(self.tmp.name, "out.ict")
        with self.assertRaises(SystemExit):
            self.cl.processData(util.make_cl_args(output_file=output_file))
        self.assertFalse(os.path.exists(output_file))

    def test_plain_name_generated_from_input_file(self):
        # A batch file with no of= line is the batch equivalent of no -o.
        batch_file = os.path.join(self.tmp.name, "batchfile")
        util.write_batch_file(batch_file, self.input_file, None, header="Plain")
        self.assertEqual(self.convert(batch_file=batch_file), "sample.asc")
        self.assertWritten(os.path.join(self.tmp.name, "sample.asc"))


if __name__ == "__main__":
    unittest.main()
