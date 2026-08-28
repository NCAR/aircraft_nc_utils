#! /usr/bin/env python3
"""Tests for reading/parsing a batch file (nc2asc process_batch_file)."""

import contextlib
import io
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


class TestBatchFileRevisions(unittest.TestCase):
    """version=, the cumulative rev= history, and # comments."""

    HISTORY = [
        "R2: Corrected ATX calibration",
        "R1: Trimmed to flight time",
        "R0: Final Data",
    ]

    def setUp(self):
        self.module = util.load_nc2asc()
        self.tmp = tempfile.TemporaryDirectory()
        self.batch_file = os.path.join(self.tmp.name, "batchfile")

    def tearDown(self):
        self.tmp.cleanup()

    def read(self, version=None, revisions=None, comments=False):
        util.write_batch_file(
            self.batch_file, "in.nc", "out.ict", header="ICARTT",
            version=version, revisions=revisions, comments=comments,
        )
        cl = self.module.nc2asc_CL()
        self.module.gui.process_batch_file(cl, self.batch_file)
        return cl

    def test_revisions_kept_in_order(self):
        self.assertEqual(self.read(version="R2", revisions=self.HISTORY).revisions,
                         self.HISTORY)

    def test_no_revisions_is_an_empty_history(self):
        self.assertEqual(self.read(version="R0").revisions, [])

    def test_version_read_from_the_batch_file(self):
        self.assertEqual(self.read(version="R2", revisions=self.HISTORY).version, "R2")

    def test_version_defaults_to_the_most_recent_revision(self):
        self.assertEqual(self.read(revisions=self.HISTORY).version, "R2")

    def test_version_is_not_corrected_to_match_the_history(self):
        # Mismatches are warned about, not silently changed.
        self.assertEqual(self.read(version="R1", revisions=self.HISTORY).version, "R1")

    def test_comments_are_ignored(self):
        # The fixture comments out an hd=AMES line, which must not take effect.
        cl = self.read(version="R0", comments=True)
        self.assertEqual(cl.header, "ICARTT")

    def read_quietly(self, **kwargs):
        """Read a batch file, returning the run and what it printed."""
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            cl = self.read(**kwargs)
        return cl, output.getvalue()

    def test_a_complete_history_is_not_warned_about(self):
        cl, output = self.read_quietly(version="R2", revisions=self.HISTORY)
        self.assertNotIn("WARNING", output)

    def test_skipped_revision_warns(self):
        cl, output = self.read_quietly(
            version="R2", revisions=["R2: Corrected ATX calibration", "R0: Final Data"]
        )
        self.assertIn("skips a revision", output)

    def test_repeated_revision_warns(self):
        cl, output = self.read_quietly(
            version="R1", revisions=["R1: fixed", "R1: fixed again", "R0: Final Data"]
        )
        self.assertIn("listed more than once", output)

    def test_revision_without_a_description_warns(self):
        cl, output = self.read_quietly(
            version="R1", revisions=["R1 no description", "R0: Final Data"]
        )
        self.assertIn("no description", output)

    def test_version_not_matching_the_history_warns(self):
        cl, output = self.read_quietly(version="R1", revisions=self.HISTORY)
        self.assertIn("is not the most recent revision listed", output)

    def test_field_revisions_before_final_ones_are_in_order(self):
        # A final release still lists the field revisions that preceded it.
        cl, output = self.read_quietly(
            version="R0",
            revisions=["R0: Final Data", "RB: Field Data", "RA: Field Data"],
        )
        self.assertNotIn("WARNING", output)

    def test_revisions_reset_between_batch_files(self):
        # Reading a second batch file replaces the history, never appends to it.
        cl = self.read(version="R2", revisions=self.HISTORY)
        util.write_batch_file(
            self.batch_file, "in.nc", "out.ict", header="ICARTT", version="RA",
            revisions=["RA: Field Data"],
        )
        self.module.gui.process_batch_file(cl, self.batch_file)
        self.assertEqual(cl.revisions, ["RA: Field Data"])


if __name__ == "__main__":
    unittest.main()
