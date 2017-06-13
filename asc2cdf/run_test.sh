#!/usr/bin/csh
#
# This is a wrapper script to drill down to the sample file for each format and test asc2cdf on it.
# Individual tests reside in the sample file dirs.

# 100hz file in NASA Ames format
cd test/100hz
py.test test_100hz.py
cd ../..

# 10hz file in NASA Ames format
cd test/ames
py.test test_ames.py
cd ../..
