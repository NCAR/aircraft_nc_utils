"""
Output Formatters for nc2asc NetCDF to ASCII Converter.

This package provides pluggable output format drivers:
- PlainWriter: Simple delimiter-separated ASCII
- ICARTT1001Writer: ICARTT FFI 1001 format (1D time-series)
- ICARTT2110Writer: ICARTT FFI 2110 format (multi-dimensional)
- AMESWriter: NASA Ames 1001 format

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

from .base import OutputFormatter
from .factory import FormatterFactory, OutputFormat
from .plain import PlainWriter
from .icartt_1001 import ICARTT1001Writer
from .icartt_2110 import ICARTT2110Writer
from .ames import AMESWriter

__all__ = [
    'OutputFormatter',
    'FormatterFactory',
    'OutputFormat',
    'PlainWriter',
    'ICARTT1001Writer',
    'ICARTT2110Writer',
    'AMESWriter',
]
