"""
nc2asc Library Modules.

This package provides the core functionality for the nc2asc NetCDF to ASCII converter.

Modules:
- config_manager: Configuration management with multiple source precedence
- dimension_handler: Multi-dimensional variable processing
- formatters: Output format drivers (Plain, ICARTT, AMES)

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

from .config_manager import (
    ConfigManager,
    ConversionOptions,
    FlightMetadata,
    HeaderConfig,
    MergedConfiguration,
    NormalComments,
    OutputFormat,
    PlatformMapping,
    parse_batch_file,
)

from .dimension_handler import (
    DimensionHandler,
    FlattenedVariable,
    HighRateHandler,
    categorize_variables,
)

__all__ = [
    # Config Manager
    'ConfigManager',
    'ConversionOptions',
    'FlightMetadata',
    'HeaderConfig',
    'MergedConfiguration',
    'NormalComments',
    'OutputFormat',
    'PlatformMapping',
    'parse_batch_file',
    # Dimension Handler
    'DimensionHandler',
    'FlattenedVariable',
    'HighRateHandler',
    'categorize_variables',
]
