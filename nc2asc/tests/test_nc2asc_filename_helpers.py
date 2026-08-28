#! /usr/bin/env python3
"""Unit tests for the filename helpers in write_data.

``dataDate``, ``icarttFilename``, and ``defaultOutputFile`` are the single
source of the data date, of the strict ICARTT filename, and of the name used
when the user leaves -o off the command line. They are exercised here directly,
with a stand-in for the program object, so the rules stay pinned down without
running a full conversion.
"""

import os
import sys
import unittest

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import nc2asc_testutil as util

wd = util.load_write_data()

TIMESTAMPS = ("2021-05-29 15:30:00", "2021-05-29 15:30:01", "2021-05-29 15:30:02")


class FakeInstance:
    """Minimal stand-in for the nc2asc GUI/command-line object.

    ``timestamps=None`` leaves ``dtime_sep`` unset, the state of the program
    before an input file has been read.
    """

    def __init__(self, timestamps=TIMESTAMPS, **attrs):
        if timestamps is not None:
            self.dtime_sep = pd.Series(list(timestamps)).str.split(" ", expand=True)
        self.__dict__.update(attrs)

    def _log_exception(self, e):
        pass


class TestDataDate(unittest.TestCase):
    def test_date_from_timestamps(self):
        self.assertEqual(wd.dataDate(FakeInstance()), "2021, 05, 29")

    def test_date_is_stored_on_the_instance(self):
        instance = FakeInstance()
        wd.dataDate(instance)
        self.assertEqual(instance.data_date, "2021, 05, 29")

    def test_keeps_previous_date_when_timestamps_missing(self):
        instance = FakeInstance(timestamps=None, data_date="2021, 05, 29")
        self.assertEqual(wd.dataDate(instance), "2021, 05, 29")

    def test_raises_when_no_date_available(self):
        with self.assertRaises(Exception):
            wd.dataDate(FakeInstance(timestamps=None))


class TestIcarttFilename(unittest.TestCase):
    def instance(self, **attrs):
        attrs.setdefault("project_name", "ASPIRE-TEST")
        attrs.setdefault("platform", "C130")
        return FakeInstance(**attrs)

    def test_strict_icartt_name(self):
        self.assertEqual(
            wd.icarttFilename(self.instance(version="R0")),
            "ASPIRE-TEST-CORE_C130_20210529_R0.ict",
        )

    def test_name_is_stored_on_the_instance(self):
        instance = self.instance(version="R0")
        wd.icarttFilename(instance)
        self.assertEqual(instance.icartt_filename, "ASPIRE-TEST-CORE_C130_20210529_R0.ict")

    def test_filename_date_has_no_separators(self):
        instance = self.instance(version="R0")
        wd.icarttFilename(instance)
        self.assertEqual(instance.icartt_filename_date, "20210529")

    def test_version_defaults_to_field_data(self):
        # No version set at all: field data (RA), matching the program default.
        self.assertEqual(
            wd.icarttFilename(self.instance()),
            "ASPIRE-TEST-CORE_C130_20210529_RA.ict",
        )

    def test_no_directory_component(self):
        # The ICARTT convention names the file only; the path is decided elsewhere.
        name = wd.icarttFilename(self.instance(version="RA"))
        self.assertEqual(os.path.basename(name), name)


class TestDefaultOutputFile(unittest.TestCase):
    def instance(self, **attrs):
        attrs.setdefault("project_name", "ASPIRE-TEST")
        attrs.setdefault("platform", "C130")
        attrs.setdefault("version", "R0")
        attrs.setdefault("input_file", "/scr/raf_data/ASPIRE-TEST/ASPIRE-TESTrf01.nc")
        return FakeInstance(**attrs)

    def test_icartt_uses_strict_icartt_name(self):
        self.assertEqual(
            wd.defaultOutputFile(self.instance(header="ICARTT")),
            "ASPIRE-TEST-CORE_C130_20210529_R0.ict",
        )

    def test_plain_uses_input_filename(self):
        self.assertEqual(
            wd.defaultOutputFile(self.instance(header="Plain")), "ASPIRE-TESTrf01.asc"
        )

    def test_ames_uses_input_filename(self):
        self.assertEqual(
            wd.defaultOutputFile(self.instance(header="AMES")), "ASPIRE-TESTrf01.asc"
        )

    def test_icartt_falls_back_to_input_filename_without_a_date(self):
        instance = self.instance(header="ICARTT", timestamps=None)
        self.assertEqual(wd.defaultOutputFile(instance), "ASPIRE-TESTrf01.asc")

    def test_icartt_can_be_overridden(self):
        # Mixed rate output is a plain csv whatever header was requested.
        self.assertEqual(
            wd.defaultOutputFile(self.instance(header="ICARTT"), icartt=False),
            "ASPIRE-TESTrf01.asc",
        )

    def test_falls_back_when_there_is_no_input_file(self):
        instance = self.instance(header="Plain", input_file=False)
        self.assertEqual(wd.defaultOutputFile(instance), "nc2asc_output.asc")

    def test_name_is_relative_to_the_working_directory(self):
        # Output belongs in the CWD, not alongside input data that may be
        # on a read-only directory such as /scr/raf_data.
        for header in ("ICARTT", "Plain"):
            name = wd.defaultOutputFile(self.instance(header=header))
            self.assertFalse(os.path.isabs(name))
            self.assertEqual(os.path.basename(name), name)


if __name__ == "__main__":
    unittest.main()
