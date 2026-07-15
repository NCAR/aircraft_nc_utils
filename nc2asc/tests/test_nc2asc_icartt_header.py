#! /usr/bin/env python3
"""Tests for ICARTT header generation (write_data.ICARTTHeader via processData).

Driven the way ICARTT files are really produced on the command line: a batch
file with an ICARTT header and NoDate/SecOfDay time formatting. Asserts the
substituted header content, the ICARTT line-count invariant, the strict .ict
filename, and that the data section has a single Time_Start (seconds) column
with no stray Date column.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import nc2asc_testutil as util


class TestICARTTHeader(unittest.TestCase):
    N_DATA_ROWS = 5  # one row per Time sample in the synthetic file

    def setUp(self):
        self.module = util.load_nc2asc()
        self.tmp = tempfile.TemporaryDirectory()
        tmp = self.tmp.name
        self.input_file = os.path.join(tmp, "sample.nc")
        self.output_file = os.path.join(tmp, "out.ict")
        self.batch_file = os.path.join(tmp, "batchfile")
        util.write_sample_netcdf(self.input_file)
        # ICARTT batches use NoDate/SecOfDay (as in the real project batch files).
        util.write_batch_file(
            self.batch_file, self.input_file, self.output_file,
            header="ICARTT", variables=["Time", "ATX"],
            date="NoDate", time="SecOfDay",
        )

        # ICARTTHeader writes scratch files (header*.tmp) into the CWD, so run
        # the conversion from inside the temp dir and restore afterwards.
        self.prev_cwd = os.getcwd()
        os.chdir(tmp)

        self.cl = self.module.nc2asc_CL()
        self.cl.processData(util.make_cl_args(batch_file=self.batch_file))

        # ICARTT overrides the output name to a strict .ict filename.
        self.ict_path = os.path.join(tmp, self.cl.icartt_filename)
        with open(self.ict_path) as fh:
            self.lines = fh.read().splitlines()
        # ICARTT line 1 gives the number of header lines; data follows.
        self.n_header = int(self.lines[0].split(",")[0])
        self.header_lines = self.lines[: self.n_header]
        self.data_lines = self.lines[self.n_header:]
        self.column_header = self.lines[self.n_header - 1]

    def tearDown(self):
        os.chdir(self.prev_cwd)
        self.tmp.cleanup()

    # --- filename / file creation ---------------------------------------
    def test_ict_filename_format(self):
        self.assertEqual(
            self.cl.icartt_filename, "ASPIRE-TEST-CORE_C130_20210529_RA.ict"
        )

    def test_ict_file_created(self):
        self.assertTrue(os.path.exists(self.ict_path))

    # --- ICARTT format invariants ---------------------------------------
    def test_first_line_file_format_index(self):
        self.assertEqual(self.lines[0].split(",")[1].strip(), "1001")

    def test_header_line_count_is_correct(self):
        # header count + data rows must equal the total file length
        self.assertEqual(self.n_header + self.N_DATA_ROWS, len(self.lines))

    def test_scale_and_fill_rows_match_variable_count(self):
        scale = next(ln for ln in self.header_lines
                     if ln and all(f == "1.0" for f in ln.split(",")))
        fill = next(ln for ln in self.header_lines
                    if ln and all(f == "-99999.0" for f in ln.split(",")))
        self.assertEqual(len(scale.split(",")), len(fill.split(",")))
        # one dependent variable (ATX); Time is the independent Time_Start column
        self.assertEqual(len(scale.split(",")), 1)

    # --- substituted content --------------------------------------------
    def test_project_name_substituted(self):
        self.assertIn("ASPIRE-TEST", self.header_lines)

    def test_platform_in_instrument_line(self):
        self.assertIn("RAF instruments on C130", self.header_lines)

    def test_platform_line(self):
        self.assertIn("PLATFORM: NSF/NCAR C130 N130AR", self.header_lines)

    def test_data_date_line(self):
        self.assertTrue(any(ln.startswith("2021, 05, 29") for ln in self.header_lines))

    def test_revision_and_version(self):
        self.assertIn("REVISION: RA", self.header_lines)

    def test_independent_variable_described(self):
        self.assertTrue(
            any(ln.startswith("Time_Start, seconds") for ln in self.header_lines)
        )

    def test_variable_metadata_row(self):
        self.assertIn("ATX,deg_C,ambient temperature", self.header_lines)

    # --- data section ---------------------------------------------------
    def test_column_header_is_time_start_and_vars(self):
        cols = self.column_header.split(",")
        self.assertEqual(cols[0], "Time_Start")
        self.assertIn("ATX", cols)

    def test_no_date_column(self):
        # command-line ICARTT output must not gain a Date column
        self.assertNotIn("Date", self.column_header.split(","))

    def test_single_time_start_column(self):
        self.assertEqual(self.column_header.split(",").count("Time_Start"), 1)

    def test_data_rows_present(self):
        self.assertEqual(len(self.data_lines), self.N_DATA_ROWS)
        for row in self.data_lines:
            self.assertEqual(len(row.split(",")), 2)


if __name__ == "__main__":
    unittest.main()
