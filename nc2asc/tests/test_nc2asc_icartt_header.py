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

        # The batch file names the output, so that is where it is written; the
        # strict ICARTT filename is only recommended (see test_ict_filename_format).
        self.ict_path = self.output_file
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

    def test_batch_file_name_is_not_overwritten(self):
        # A name from the batch file is kept even though it is not the strict
        # ICARTT name, which is only recommended.
        self.assertEqual(self.cl.output_file, self.output_file)
        self.assertFalse(
            os.path.exists(os.path.join(self.tmp.name, self.cl.icartt_filename))
        )

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

    def test_no_leftover_template_text(self):
        # The templates are rewritten in place. Substituting a placeholder for
        # something shorter used to leave the tail of the old content behind as
        # a stray line, since the file was never truncated.
        for line in self.header_lines:
            self.assertFalse(line.endswith('>'), f'leftover template text: {line}')
        fill = self.header_lines.index('-99999.0')
        self.assertEqual(
            self.header_lines[fill + 1], 'ATX,deg_C,ambient temperature'
        )

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


class TestRevisionDescription(unittest.TestCase):
    """ICARTT revisions are RA, RB... while data is preliminary and R0, R1...
    once it is final, and the header describes them accordingly."""

    wd = util.load_write_data()

    def test_numbered_revisions_are_final_data(self):
        for version in ("R0", "R1", "R12"):
            self.assertEqual(self.wd.revisionDescription(version), "Final Data")

    def test_lettered_revisions_are_field_data(self):
        for version in ("RA", "RB"):
            self.assertEqual(self.wd.revisionDescription(version), "Field Data")

    def test_final_data_may_be_published(self):
        self.assertEqual(
            self.wd.revisionStipulation("R0"), "Final data for publication use"
        )

    def test_field_data_may_not_be_published(self):
        self.assertEqual(
            self.wd.revisionStipulation("RA"), "Field data not for publication use"
        )


class ICARTTConversion(unittest.TestCase):
    """Runs an ICARTT conversion per test, with batch file settings to vary.

    No tests of its own; the revision test cases below share it.
    """

    N_DATA_ROWS = 5  # one row per Time sample in the synthetic file

    def setUp(self):
        self.module = util.load_nc2asc()
        self.tmp = tempfile.TemporaryDirectory()
        self.prev_cwd = os.getcwd()
        os.chdir(self.tmp.name)

    def tearDown(self):
        os.chdir(self.prev_cwd)
        self.tmp.cleanup()

    def convert(self, version=None, revisions=None, comments=False):
        """Convert with the given batch file version=/rev= settings, returning
        the run and the header lines of the output file."""
        tmp = self.tmp.name
        input_file = os.path.join(tmp, "sample.nc")
        output_file = os.path.join(tmp, "out.ict")
        batch_file = os.path.join(tmp, "batchfile")
        util.write_sample_netcdf(input_file)
        util.write_batch_file(
            batch_file, input_file, output_file, header="ICARTT",
            variables=["Time", "ATX"], date="NoDate", time="SecOfDay",
            version=version, revisions=revisions, comments=comments,
        )
        cl = self.module.nc2asc_CL()
        cl.processData(util.make_cl_args(batch_file=batch_file))
        with open(output_file) as fh:
            self.lines = fh.read().splitlines()
        return cl, self.lines[: int(self.lines[0].split(",")[0])]

    def revision_index(self, header_lines):
        """Index of the REVISION line, which the history follows."""
        return next(
            i for i, line in enumerate(header_lines)
            if line.startswith("REVISION:")
        )


class TestICARTTRevisionLines(ICARTTConversion):
    """The REVISION/description lines written for a given version= setting."""

    def test_final_data_revision(self):
        cl, header_lines = self.convert(version="R0")
        self.assertIn("REVISION: R0", header_lines)
        self.assertIn("R0: Final Data", header_lines)
        self.assertIn(
            "STIPULATIONS_ON_USE: Final data for publication use", header_lines
        )

    def test_later_field_data_revision(self):
        cl, header_lines = self.convert(version="RB")
        self.assertIn("REVISION: RB", header_lines)
        self.assertIn("RB: Field Data", header_lines)
        self.assertIn(
            "STIPULATIONS_ON_USE: Field data not for publication use", header_lines
        )

    def test_default_revision_is_field_data(self):
        cl, header_lines = self.convert()
        self.assertIn("REVISION: RA", header_lines)
        self.assertIn("RA: Field Data", header_lines)
        self.assertIn(
            "STIPULATIONS_ON_USE: Field data not for publication use", header_lines
        )

    def test_final_data_filename(self):
        cl, _ = self.convert(version="R0")
        self.assertEqual(cl.icartt_filename, "ASPIRE-TEST-CORE_C130_20210529_R0.ict")

    def test_nothing_follows_the_revision(self):
        # The revision block ends the header, above the column names. A final
        # revision writes shorter lines than the field data the template holds,
        # which used to leave a stray line of the old text behind.
        cl, header_lines = self.convert(version="R0")
        self.assertEqual(header_lines[-2:], ["R0: Final Data", "Time_Start,ATX"])


class TestICARTTRevisionHistory(ICARTTConversion):
    """ICARTT wants every revision listed in every file, most recent first.

    The history comes from the rev= lines of the batch file, so that releasing
    a revision means adding a line there rather than editing the installed
    header2.txt template.
    """

    HISTORY = [
        "R2: Corrected ATX calibration",
        "R1: Trimmed to flight time",
        "R0: Final Data",
    ]

    def test_history_written_most_recent_first(self):
        cl, header_lines = self.convert(version="R2", revisions=self.HISTORY)
        start = self.revision_index(header_lines) + 1
        self.assertEqual(header_lines[start:start + len(self.HISTORY)], self.HISTORY)

    def test_history_is_the_end_of_the_normal_comments(self):
        # ICARTT puts the revision block last, just above the column names.
        cl, header_lines = self.convert(version="R2", revisions=self.HISTORY)
        self.assertEqual(header_lines[-4:-1], self.HISTORY)

    def test_normal_comment_count_covers_the_added_lines(self):
        # The normal comment count has to grow with the history, or readers
        # reject the file. The count is the line before the first comment, and
        # the comments run to the end of the header.
        cl, header_lines = self.convert(version="R2", revisions=self.HISTORY)
        first_comment = next(
            i for i, line in enumerate(header_lines)
            if line.startswith("PI_CONTACT_INFO")
        )
        normal_comments = int(header_lines[first_comment - 1])
        self.assertEqual(normal_comments, len(header_lines) - first_comment)
        self.assertEqual(normal_comments, 20)  # 18 in the template, plus 2 revisions

    def test_header_line_count_is_correct(self):
        # The ICARTT line count in line 1 still has to match the file itself.
        cl, header_lines = self.convert(version="R2", revisions=self.HISTORY)
        self.assertEqual(len(header_lines) + self.N_DATA_ROWS, len(self.lines))

    def test_stipulation_follows_the_current_revision(self):
        cl, header_lines = self.convert(version="R2", revisions=self.HISTORY)
        self.assertIn(
            "STIPULATIONS_ON_USE: Final data for publication use", header_lines
        )

    def test_one_long_revision_line(self):
        # The other direction from a short revision: one revision, so no lines
        # are added, but the line written is longer than the template's. The
        # rewrite has to grow the file without disturbing what follows.
        long_revision = (
            "R1: Recomputed ATX from the corrected recovery factor, and trimmed "
            "the file to the flight time reported by WOW_A"
        )
        cl, header_lines = self.convert(version="R1", revisions=[long_revision])
        self.assertEqual(header_lines[-2:], [long_revision, "Time_Start,ATX"])
        first_comment = next(
            i for i, line in enumerate(header_lines)
            if line.startswith("PI_CONTACT_INFO")
        )
        self.assertEqual(int(header_lines[first_comment - 1]), 18)

    def test_version_defaults_to_most_recent_revision(self):
        # With no version= line, the top of the history is the current revision.
        cl, header_lines = self.convert(revisions=self.HISTORY)
        self.assertEqual(cl.version, "R2")
        self.assertIn("REVISION: R2", header_lines)
        self.assertEqual(cl.icartt_filename, "ASPIRE-TEST-CORE_C130_20210529_R2.ict")

    def test_version_wins_over_the_history(self):
        # Mismatched version= is warned about, not silently corrected: the file
        # reports the revision the user asked for, with the history unchanged.
        cl, header_lines = self.convert(version="R1", revisions=self.HISTORY)
        self.assertIn("REVISION: R1", header_lines)
        start = self.revision_index(header_lines) + 1
        self.assertEqual(header_lines[start:start + len(self.HISTORY)], self.HISTORY)

    def test_comments_are_ignored(self):
        cl, header_lines = self.convert(
            version="R2", revisions=self.HISTORY, comments=True
        )
        self.assertEqual(cl.header, "ICARTT")  # not the commented out hd=AMES
        self.assertIn("REVISION: R2", header_lines)
        self.assertFalse([ln for ln in header_lines if ln.startswith("#")])


if __name__ == "__main__":
    unittest.main()
