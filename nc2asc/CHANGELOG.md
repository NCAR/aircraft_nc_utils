# Changelog

Changes to nc2asc starting 2026-08-27.
Changes before 2026-08-27 are recorded only in the git history.

## Unreleased

### Added

- Can now set the ICARTT revision history in the batch file:
  - `version=` sets the revision being produced, and a
  `rev=<revision>: <what changed>` line per revision writes the
  cumulative history ICARTT requires into every file, most recent first.
  - Leaving `version=` out uses the most recent `rev=` line.
  Previously the history could only be changed by hacking the installed
  `header2.txt` template, which is shared by every project and replaced on
  reinstall.
- Warnings for a revision history that would misstate the release:`version=`
  that is not the most recent `rev=` line, a revision listed twice or out of
  order, a gap in the numbered history, or a `rev=` line with no description.
  The conversion still runs, and `version=` is used as given, not corrected.
- Can now add comment lines in batch files.
  - Anything starting with `#` is ignored. A commented example batch file is in
  `nc2asc/example_batchfile.bat`.

#### Changed

- Removed hard-coded revision information
  - A final data revision (`R0`, `R1`...) is now described as `Final Data` with
  `STIPULATIONS_ON_USE: Final data for publication use`. Field revisions
  (`RA`, `RB`...) are unchanged: `Field Data`, not for publication use.
- An output filename given with `-o` is used as given and no longer overwritten
  by the generated ICARTT name. A name that does not conform to the ICARTT
  convention is warned about but kept, since there are good reasons to convert
  to a different name, like testing or rerun and diff.
- The command line wins over the batch file for the input and output files, with
  a warning naming both values, rather than prompting for a choice. nc2asc runs
  unattended from project processing scripts, where a prompt would hang the
  conversion.
- The ICARTT revision, its history, and the `version=` line are written back out
  when a batch file is saved from the GUI, which previously dropped them.
- A failed command-line conversion now exits non-zero.
- Added to unit test suite under `nc2asc/tests`
  - Now runs with the standard library `unittest` against synthetic netCDF and
  batch-file fixtures, so it needs neither a display nor the project data on
  `/scr/raf_data`. See the Running the Tests section of `nc2asc/README.md`.

#### Fixed

- An output filename is generated when `-o` is not given, instead of crashing:
  - Generates the strict ICARTT name for ICARTT output, otherwise uses the
    input filename with a `.asc` extension, written to the current directory
    `-o` is documented as optional, and now behaves that way.
- Converting without an input file reported an unrelated netCDF backend error,
  and then failed again inside its own error handler. It now exits gracefully
  with a message that no input file was provided, and how to provide one.
- `nc2asc -i <file>` with ICARTT output (the command line default) crashed with
  `AttributeError: 'dict' object has no attribute 'insert'`, from a variable
  selection step that ran before the variables had been read.

## [1.0] - 2023-01-12 Initial Release
Changes before 2026-08-27 are recorded only in the git history.
