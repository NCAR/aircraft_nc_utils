# Example nc2asc batch file, set up for ICARTT output.
#
# One batch file per project. The input and output files are usually given on
# the command line, one flight at a time, and the command line wins over any
# if=/of= line here:
#
#     nc2asc -i /scr/raf_data/<PROJECT>/<PROJECT>rf01.nc -b nc2asc.bat
#
# Lines starting with # are comments. Blank lines are ignored. Anything nc2asc
# does not recognize is ignored too, so keep notes here as needed.

if=/scr/raf_data/ASPIRE-TEST/ASPIRE-TESTrf01.nc
of=/scr/raf_data/ASPIRE-TEST/ASPIRE-TEST-CORE_C130_20210529_RA.ict

hd=ICARTT
dt=NoDate
tm=SecOfDay
sp=comma
fv=-32767
ti=X,X

# --------------------------------------------------------------------------
# ICARTT revisions
# --------------------------------------------------------------------------
# version= is the revision this conversion produces. It sets the REVISION line
# in the header and the _R?? part of the ICARTT filename.
#
#   RA, RB, RC ...  field data, not for publication use
#   R0, R1, R2 ...  final data, for publication use
#
# ICARTT requires the full revision history in every file, most recent first,
# so add a rev= line each time you release a new revision - do not replace the
# old ones. Say what changed, briefly:
#
#     version=R2
#     rev=R2: Corrected ATX calibration
#     rev=R1: Trimmed to flight time
#     rev=R0: Final Data
#
# nc2asc warns if version= is not the most recent rev= line, if a revision is
# listed twice or out of order, or if the history skips a revision. Leave
# version= out entirely and the most recent rev= line is used.
#
# With no rev= lines at all, the header gets a single generated line for the
# current revision ("R0: Final Data" or "RA: Field Data").

version=RA
rev=RA: Field Data

# --------------------------------------------------------------------------
# Variables to convert. Leave all Vars= lines out to convert everything.
# --------------------------------------------------------------------------
Vars=Time
Vars=ATX
Vars=PSXC
