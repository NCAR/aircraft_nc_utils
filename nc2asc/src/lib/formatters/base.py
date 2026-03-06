"""
Base OutputFormatter Abstract Base Class.

Defines the interface for all output format drivers.

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

import pandas as pd

if TYPE_CHECKING:
    from ..config_manager import MergedConfiguration, FlightMetadata


class OutputFormatter(ABC):
    """
    Abstract base class for output format drivers.

    All output formatters must implement:
    - write(): Write data to output file
    - build_header(): Build format-specific header lines
    - format_data_row(): Format a single data row

    Properties to define:
    - file_extension: Expected file extension
    - delimiter: Field delimiter character
    - default_fill_value: Default missing value code
    """

    def __init__(self, converter: 'NetCDFConverter', config: 'MergedConfiguration'):
        """
        Initialize OutputFormatter.

        Args:
            converter: NetCDFConverter instance with loaded data
            config: MergedConfiguration with settings
        """
        self.converter = converter
        self.config = config
        self._validate_config()

    @abstractmethod
    def write(self, output_path: Path) -> None:
        """
        Write data to output file.

        Args:
            output_path: Path to output file
        """
        pass

    @abstractmethod
    def build_header(self) -> List[str]:
        """
        Build format-specific header lines.

        Returns:
            List of header line strings
        """
        pass

    def format_data_row(self, row: pd.Series) -> str:
        """
        Format a single data row.

        Args:
            row: Pandas Series with row data

        Returns:
            Formatted string for the row
        """
        values = []
        for val in row:
            if pd.isna(val):
                values.append(str(int(self.config.options.fill_value)))
            elif isinstance(val, float):
                # Check if it's a fill value
                if val == self.config.options.fill_value:
                    values.append(str(int(val)))
                else:
                    values.append(f"{val:.6g}")
            else:
                values.append(str(val))
        return self.delimiter.join(values)

    def validate_output(self, output_path: Path) -> bool:
        """
        Validate written output conforms to format specification.

        Args:
            output_path: Path to output file

        Returns:
            True if valid, False otherwise
        """
        if not output_path.exists():
            return False
        return self._validate_header_line_count(output_path)

    def _validate_config(self) -> None:
        """
        Validate configuration has required fields for this format.

        Override in subclasses for format-specific validation.
        """
        pass

    def _validate_header_line_count(self, output_path: Path) -> bool:
        """
        Verify NLHEAD matches actual header line count.

        Args:
            output_path: Path to output file

        Returns:
            True if NLHEAD is correct
        """
        with open(output_path, 'r') as f:
            first_line = f.readline().strip()

        # Parse NLHEAD from first line
        try:
            parts = first_line.replace(',', ' ').split()
            declared_nlhead = int(parts[0])
        except (ValueError, IndexError):
            return False

        # Count actual header lines
        with open(output_path, 'r') as f:
            lines = f.readlines()

        # For ICARTT/AMES, header ends at NLHEAD line (inclusive)
        # Validate declared count matches
        return declared_nlhead <= len(lines)

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Return expected file extension for this format."""
        pass

    @property
    @abstractmethod
    def delimiter(self) -> str:
        """Return field delimiter for this format."""
        pass

    @property
    @abstractmethod
    def default_fill_value(self) -> float:
        """Return default missing value code for this format."""
        pass

    def _get_units(self, col_name: str) -> str:
        """
        Get units for a column, handling flattened multi-dim variables.

        Args:
            col_name: Column name (may be flattened like VAR_0)

        Returns:
            Units string
        """
        if col_name in self.converter.units:
            return self.converter.units[col_name]
        # Try base name for flattened columns (e.g., AUHSAS_RO_0 -> AUHSAS_RO)
        if '_' in col_name:
            parts = col_name.rsplit('_', 1)
            if len(parts) == 2 and parts[1].isdigit():
                base_name = parts[0]
                return self.converter.units.get(base_name, 'unitless')
        return 'unitless'

    def _get_long_name(self, col_name: str) -> str:
        """
        Get long name for a column, handling flattened multi-dim variables.

        Args:
            col_name: Column name (may be flattened like VAR_0)

        Returns:
            Long name string
        """
        if col_name in self.converter.long_names:
            return self.converter.long_names[col_name]
        # Try base name for flattened columns
        if '_' in col_name:
            parts = col_name.rsplit('_', 1)
            if len(parts) == 2 and parts[1].isdigit():
                base_name = parts[0]
                return self.converter.long_names.get(base_name, col_name)
        return col_name
