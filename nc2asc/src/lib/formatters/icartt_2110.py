"""
ICARTT FFI 2110 Output Formatter.

ICARTT v2.0 format for multi-dimensional data (e.g., size distributions).

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd

from .base import OutputFormatter
from .factory import FormatterFactory, OutputFormat
from .icartt_1001 import ICARTT1001Writer


@FormatterFactory.register(OutputFormat.ICARTT_2110)
class ICARTT2110Writer(OutputFormatter):
    """
    Formatter for ICARTT FFI 2110 format (multi-dimensional data).

    Preserves 2D data structure for size distributions and similar
    multi-dimensional variables.
    """

    @property
    def file_extension(self) -> str:
        return ".ict"

    @property
    def delimiter(self) -> str:
        return ", "

    @property
    def default_fill_value(self) -> float:
        return -99999.0

    def _find_dimension_variable(self, var_name: str) -> Optional[str]:
        """
        Find the dimension variable associated with a multi-dim variable.

        Searches in order:
        1. Coordinate attribute on the dimension
        2. CellSizes attribute
        3. Variables with matching dimension shape

        Args:
            var_name: Name of the multi-dimensional variable

        Returns:
            Name of dimension variable or None
        """
        if var_name not in self.converter.ds:
            return None

        var = self.converter.ds[var_name]

        for dim in var.dims:
            if dim == 'Time':
                continue

            # Check if dimension itself is a coordinate
            if dim in self.converter.ds.coords:
                return dim

            # Check for CellSizes attribute
            if 'CellSizes' in var.attrs:
                return f"{var_name}_CellSizes"

            # Search for variables with matching dimension
            for coord_name, coord_var in self.converter.ds.items():
                if coord_var.dims == (dim,):
                    return coord_name

        return None

    def _get_dimension_values(self, dim_var_name: Optional[str],
                             var_name: str, n_elements: int) -> np.ndarray:
        """
        Get the values for a dimension variable.

        Args:
            dim_var_name: Name of dimension variable
            var_name: Name of data variable (for CellSizes fallback)
            n_elements: Expected number of elements

        Returns:
            Array of dimension values
        """
        # Try dimension variable
        if dim_var_name and dim_var_name in self.converter.ds:
            values = self.converter.ds[dim_var_name].values
            if len(values) == n_elements:
                return values

        # Try CellSizes
        if var_name in self.converter.cell_sizes:
            cell_sizes = np.array(self.converter.cell_sizes[var_name]).flatten()
            bin_edges = np.concatenate([[0], np.cumsum(cell_sizes)])
            return (bin_edges[:-1] + bin_edges[1:]) / 2

        # Fall back to indices
        return np.arange(n_elements)

    def _get_primary_multidim_var(self) -> Optional[str]:
        """
        Get the primary multi-dimensional variable for FFI 2110 output.

        Returns:
            Variable name or None
        """
        _, data_multi = self.converter._filter_variables()
        if not data_multi:
            return None
        return list(data_multi.keys())[0]

    def build_header(self) -> List[str]:
        """
        Build ICARTT FFI 2110 header.

        Returns:
            List of header line strings
        """
        lines = []

        # Get primary variable info
        primary_var = self._get_primary_multidim_var()
        if not primary_var:
            raise ValueError("No multi-dimensional variables found for FFI 2110")

        _, data_multi = self.converter._filter_variables()
        primary_data = data_multi[primary_var]
        n_bins = primary_data.shape[1]

        dim_var_name = self._find_dimension_variable(primary_var)

        # Get config values
        header_cfg = self.config.header
        metadata = self.converter.metadata
        fill_value = int(self.config.options.fill_value)
        today = datetime.today().strftime('%Y, %m, %d')

        # Line 1: NLHEAD, FFI (placeholder)
        lines.append("NLHEAD_PLACEHOLDER, 2110")

        # Lines 2-5: Common header info
        lines.append(header_cfg.pi_name)
        lines.append(header_cfg.pi_organization)
        lines.append(f"{header_cfg.datasource_desc} {metadata.platform}")
        lines.append(metadata.project_name)

        # Line 6: Volume numbers
        lines.append("1, 1")

        # Line 7: Data date, Revision date
        lines.append(f"{metadata.flight_date}, {today}")

        # Line 8: Data interval
        lines.append(str(header_cfg.data_interval))

        # Line 9: Independent variable
        lines.append("Time_Start, seconds, UTC seconds from midnight on flight date")

        # Line 10: Number of dependent variables
        lines.append("1")  # One 2D dependent variable

        # Line 11: Scale factor for independent bound variable
        lines.append("1.0")

        # Line 12: Independent bound variable description
        dim_units = self._get_units(dim_var_name) if dim_var_name else 'index'
        dim_name = dim_var_name if dim_var_name else 'BinIndex'
        lines.append(f"{dim_name}[], {dim_units}, Bin dimension values")

        # Line 13: Primary independent variable description
        lines.append("Time_Start, seconds, UTC seconds from midnight on flight date")

        # Line 14: Number of elements in bounded dimension
        lines.append(str(n_bins))

        # Lines 15-16: Scale and fill for bounded data
        lines.append("1.0")
        lines.append(str(fill_value))

        # Line 17: Dependent variable description with [] suffix
        var_units = self._get_units(primary_var)
        var_long = self._get_long_name(primary_var).replace(',', ';')
        lines.append(f"{primary_var}[], {var_units}, {var_long}")

        # Auxiliary variables (1D variables)
        data_1d, _ = self.converter._filter_variables()
        aux_vars = list(data_1d.keys())
        lines.append(str(len(aux_vars)))

        if aux_vars:
            lines.append(", ".join(["1.0"] * len(aux_vars)))  # Scale factors
            lines.append(", ".join([str(fill_value)] * len(aux_vars)))  # Fill values
            for var in aux_vars:
                units = self._get_units(var)
                long_name = self._get_long_name(var).replace(',', ';')
                lines.append(f"{var}, {units}, {long_name}")

        # Special comments
        special_comments = self.config.special_comments or []

        # Add CellSizes info if present
        if primary_var in self.converter.cell_sizes:
            sizes = self.converter.cell_sizes[primary_var]
            sizes_str = ', '.join(f"{s:.6g}" for s in np.array(sizes).flatten())
            special_comments.append(f"CellSizes {primary_var}: {sizes_str}")

        lines.append(str(len(special_comments)))
        lines.extend(special_comments)

        # Normal comments (reuse ICARTT1001 builder)
        normal_lines = self._build_normal_comments()
        lines.append(str(len(normal_lines)))
        lines.extend(normal_lines)

        # Column headers
        lines.append(f"Time_Start, NumBins, {dim_name}[], {primary_var}[]")

        # Update NLHEAD
        nlhead = len(lines)
        lines[0] = f"{nlhead}, 2110"

        return lines

    def _build_normal_comments(self) -> List[str]:
        """Build normal comment lines (reuse from ICARTT1001)."""
        # Create temporary ICARTT1001Writer to reuse logic
        temp_writer = ICARTT1001Writer(self.converter, self.config)
        return temp_writer._build_normal_comments()

    def _generate_data_rows(self, data: np.ndarray, dim_values: np.ndarray) -> List[str]:
        """
        Generate FFI 2110 data rows.

        Args:
            data: 2D data array (time, bins)
            dim_values: Array of dimension values

        Returns:
            List of formatted data row strings
        """
        rows = []
        fill = int(self.config.options.fill_value)
        num_bins = len(dim_values)

        for i, time_val in enumerate(self.converter.time_data[:len(data)]):
            # Main data line: UTC, NumBins
            rows.append(f"{time_val:.0f}, {num_bins}")

            # Bin data lines: dim_value, data_value
            for j in range(num_bins):
                dim_val = dim_values[j]
                data_val = data[i, j]
                if np.isnan(data_val) or np.isinf(data_val):
                    data_val = fill
                rows.append(f"   {dim_val:.6g}, {data_val:.0f}")

        return rows

    def write(self, output_path: Path) -> None:
        """
        Write ICARTT FFI 2110 output.

        Args:
            output_path: Path to output file
        """
        output_path = Path(output_path)

        # Get multi-dim data
        _, data_multi = self.converter._filter_variables()

        if not data_multi:
            print("Warning: No multi-dimensional data found, falling back to FFI 1001")
            ICARTT1001Writer(self.converter, self.config).write(output_path)
            return

        # Use first multidim variable as primary
        primary_var = list(data_multi.keys())[0]
        primary_data = data_multi[primary_var]

        # Get dimension variable and values
        dim_var_name = self._find_dimension_variable(primary_var)
        dim_values = self._get_dimension_values(
            dim_var_name, primary_var, primary_data.shape[1]
        )

        # Build header
        header_lines = self.build_header()

        # Generate data rows
        data_rows = self._generate_data_rows(primary_data, dim_values)

        # Write output
        with open(output_path, 'w') as f:
            for line in header_lines:
                f.write(line + '\n')
            for row in data_rows:
                f.write(row + '\n')
