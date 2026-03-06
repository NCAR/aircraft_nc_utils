"""
NASA Ames 1001 Output Formatter.

NASA Ames format for airborne data exchange.

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd

from .base import OutputFormatter
from .factory import FormatterFactory, OutputFormat


@FormatterFactory.register(OutputFormat.AMES_1001)
class AMESWriter(OutputFormatter):
    """
    Formatter for NASA Ames 1001 format.

    Implements the NASA Ames DEF standard for time-series data.
    """

    @property
    def file_extension(self) -> str:
        return ".ames"

    @property
    def delimiter(self) -> str:
        return " "  # NASA Ames uses space delimiter

    @property
    def default_fill_value(self) -> float:
        return 9999.0  # NASA Ames typically uses 9999

    def build_header(self, df: pd.DataFrame = None) -> List[str]:
        """
        Build NASA Ames 1001 header.

        Args:
            df: DataFrame with data columns

        Returns:
            List of header line strings
        """
        if df is None:
            df = self._build_data_frame()

        lines = []

        metadata = self.converter.metadata
        num_vars = len(df.columns) - 1  # Exclude UTs
        today = datetime.today().strftime('%Y %m %d').replace(' 0', ' ')

        # Convert date format for AMES (space-delimited, no leading zeros)
        if metadata.flight_date:
            date_parts = metadata.flight_date.replace(',', '').split()
            flight_date_ames = ' '.join(date_parts)
        else:
            flight_date_ames = today

        # Line 1: NLHEAD FFI (space-delimited for AMES)
        lines.append("NLHEAD_PLACEHOLDER 1001")

        # Line 2: Originator name
        lines.append(self.config.header.pi_name)

        # Line 3: Organization
        lines.append(self.config.header.pi_organization)

        # Line 4: Source/instrument
        lines.append(f"Flight data from: {metadata.platform}")

        # Line 5: Mission name
        lines.append(metadata.project_name)

        # Line 6: Volume numbers (space-delimited)
        lines.append("1 1")

        # Line 7: Data date, Revision date (space-delimited)
        lines.append(f"{flight_date_ames} {today}")

        # Line 8: Data interval
        lines.append("1.0")

        # Line 9: Independent variable description
        lines.append("UTs seconds UTC_seconds_from_midnight")

        # Line 10: Number of primary variables
        lines.append(str(num_vars))

        # Line 11: Scale factors (space-delimited)
        lines.append(" ".join(["1.0"] * num_vars))

        # Line 12: Missing value markers (space-delimited)
        fill = str(int(self.default_fill_value))
        lines.append(" ".join([fill] * num_vars))

        # Lines 13+: Variable descriptions
        for col in df.columns[1:]:  # Skip UTs
            units = self._get_units(col)
            long_name = self._get_long_name(col).replace(' ', '_')
            lines.append(f"{col} {units} {long_name}")

        # Special comments (NSCOML)
        lines.append("0")

        # Normal comments (NNCOML) - minimal for AMES
        normal_comments = [
            f"Data from {metadata.project_name} project",
            f"Platform: {metadata.platform} ({metadata.tail_number})",
        ]
        lines.append(str(len(normal_comments)))
        lines.extend(normal_comments)

        # Column headers
        lines.append(" ".join(df.columns))

        # Update NLHEAD
        nlhead = len(lines)
        lines[0] = f"{nlhead} 1001"

        return lines

    def _build_data_frame(self) -> pd.DataFrame:
        """
        Build the output DataFrame.

        Returns:
            DataFrame ready for output
        """
        df = self.converter._build_dataframe_1d()

        # Rename Time_Start to UTs for AMES
        df = df.rename(columns={'Time_Start': 'UTs'})

        # Flatten multidim data using pd.concat to avoid fragmentation
        _, data_multi = self.converter._filter_variables()
        if data_multi:
            multi_cols = {}
            for var_name, values in data_multi.items():
                for i in range(values.shape[1]):
                    col_name = f"{var_name}_{i}"
                    multi_cols[col_name] = values[:len(df), i]
            df = pd.concat([df, pd.DataFrame(multi_cols)], axis=1)

        # Apply fill values (use AMES default)
        for col in df.columns:
            if df[col].dtype in ['float64', 'float32']:
                df[col] = df[col].where(
                    pd.notna(df[col]) & (df[col] != self.config.options.fill_value),
                    self.default_fill_value
                )

        return df

    def write(self, output_path: Path) -> None:
        """
        Write NASA Ames 1001 output.

        Args:
            output_path: Path to output file
        """
        output_path = Path(output_path)

        # Build data frame
        df = self._build_data_frame()

        # Build header
        header_lines = self.build_header(df)

        # Write output
        with open(output_path, 'w') as f:
            for line in header_lines:
                f.write(line + '\n')

        # Write data (space-delimited, no header row)
        df.to_csv(
            output_path, mode='a', index=False, header=False,
            sep=' ', na_rep=str(int(self.default_fill_value))
        )
