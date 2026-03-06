"""
Plain ASCII Output Formatter.

Simple delimiter-separated ASCII output.

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from .base import OutputFormatter
from .factory import FormatterFactory, OutputFormat


@FormatterFactory.register(OutputFormat.PLAIN)
class PlainWriter(OutputFormatter):
    """
    Formatter for plain ASCII output.

    Outputs simple CSV or space-delimited files with optional
    CellSizes header comments for histogram data.
    """

    @property
    def file_extension(self) -> str:
        return ".txt"

    @property
    def delimiter(self) -> str:
        if self.config.options.delimiter == 'comma':
            return ','
        return ' '

    @property
    def default_fill_value(self) -> float:
        return -99999.0

    def build_header(self) -> List[str]:
        """
        Build plain ASCII header.

        Returns:
            List of header lines (CellSizes comments + column headers)
        """
        lines = []

        # Add CellSizes comments only for selected multi-dim variables
        _, filtered_multi = self.converter._filter_variables()
        for var_name, sizes in self.converter.cell_sizes.items():
            if var_name in filtered_multi:
                sizes_str = ', '.join(f"{s:.6g}" for s in np.array(sizes).flatten())
                lines.append(f"# CellSizes {var_name}: {sizes_str}")

        # Add column header line with variable names
        df = self.converter._build_dataframe_1d()
        df = self.converter._process_datetime_columns(df)

        # Add flattened multi-dim column names
        col_names = list(df.columns)
        for var_name in filtered_multi:
            values = filtered_multi[var_name]
            for i in range(values.shape[1]):
                col_names.append(f"{var_name}_{i}")

        lines.append(self.delimiter.join(col_names))

        return lines

    def write(self, output_path: Path) -> None:
        """
        Write plain ASCII output.

        Args:
            output_path: Path to output file
        """
        output_path = Path(output_path)

        # Build DataFrame from 1D variables
        df = self.converter._build_dataframe_1d()
        df = self.converter._process_datetime_columns(df)

        # Handle multi-dimensional data by flattening
        # Build all columns at once using pd.concat to avoid fragmentation
        _, data_multi = self.converter._filter_variables()
        if data_multi:
            multi_cols = {}
            for var_name, values in data_multi.items():
                for i in range(values.shape[1]):
                    col_name = f"{var_name}_{i}"
                    multi_cols[col_name] = values[:len(df), i]
            df = pd.concat([df, pd.DataFrame(multi_cols)], axis=1)

        df = self.converter._apply_fill_values(df)

        # Build header
        header_lines = self.build_header()

        # Write output
        with open(output_path, 'w') as f:
            # Write header lines (CellSizes comments + column names)
            for line in header_lines:
                f.write(line + '\n')

        # Write data (without header since we already wrote column names)
        na_rep = str(int(self.config.options.fill_value))
        df.to_csv(output_path, mode='a', index=False, header=False, sep=self.delimiter, na_rep=na_rep)
