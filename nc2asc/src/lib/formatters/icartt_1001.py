"""
ICARTT FFI 1001 Output Formatter.

ICARTT v2.0 format for 1D time-series data with full header compliance.

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

from datetime import datetime
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from .base import OutputFormatter
from .factory import FormatterFactory, OutputFormat


@FormatterFactory.register(OutputFormat.ICARTT_1001)
class ICARTT1001Writer(OutputFormatter):
    """
    Formatter for ICARTT FFI 1001 format (1D time-series data).

    Implements the ICARTT v2.0 standard with all required header fields
    and normal comment keywords.
    """

    # All 16 required normal comment keywords
    REQUIRED_NORMAL_COMMENTS = [
        ('pi_contact_info', 'PI_CONTACT_INFO'),
        ('platform', 'PLATFORM'),
        ('location', 'LOCATION'),
        ('associated_data', 'ASSOCIATED_DATA'),
        ('instrument_info', 'INSTRUMENT_INFO'),
        ('data_info', 'DATA_INFO'),
        ('uncertainty', 'UNCERTAINTY'),
        ('ulod_flag', 'ULOD_FLAG'),
        ('ulod_value', 'ULOD_VALUE'),
        ('llod_flag', 'LLOD_FLAG'),
        ('llod_value', 'LLOD_VALUE'),
        ('dm_contact_info', 'DM_CONTACT_INFO'),
        ('project_info', 'PROJECT_INFO'),
        ('stipulations_on_use', 'STIPULATIONS_ON_USE'),
        ('other_comments', 'OTHER_COMMENTS'),
        ('revision', 'REVISION'),
    ]

    @property
    def file_extension(self) -> str:
        return ".ict"

    @property
    def delimiter(self) -> str:
        return ", "  # ICARTT uses comma-space

    @property
    def default_fill_value(self) -> float:
        return -99999.0

    def build_header(self, df: pd.DataFrame = None) -> List[str]:
        """
        Build complete ICARTT FFI 1001 header.

        Args:
            df: DataFrame with data columns (for variable info)

        Returns:
            List of header line strings
        """
        if df is None:
            df = self._build_data_frame()

        lines = []

        # Get config values
        header_cfg = self.config.header
        metadata = self.converter.metadata

        num_vars = len(df.columns) - 1  # Exclude Time_Start
        fill_value = int(self.config.options.fill_value)
        today = datetime.today().strftime('%Y, %m, %d')

        # Build variable descriptions
        var_descriptions = []
        for col in df.columns[1:]:  # Skip Time_Start
            units = self._get_units(col)
            long_name = self._get_long_name(col)
            # Clean long_name of commas (ICARTT uses comma as delimiter)
            long_name = long_name.replace(',', ';')
            var_descriptions.append(f"{col}, {units}, {long_name}")

        # Line 1: NLHEAD, FFI (placeholder - will be updated)
        lines.append("NLHEAD_PLACEHOLDER, 1001")

        # Line 2: PI name
        lines.append(header_cfg.pi_name)

        # Line 3: Organization
        lines.append(header_cfg.pi_organization)

        # Line 4: Data source + platform
        lines.append(f"{header_cfg.datasource_desc} {metadata.platform}")

        # Line 5: Project name
        lines.append(metadata.project_name)

        # Line 6: Volume numbers
        lines.append("1, 1")

        # Line 7: Data date, Revision date
        lines.append(f"{metadata.flight_date}, {today}")

        # Line 8: Data interval
        lines.append(str(header_cfg.data_interval))

        # Line 9: Independent variable description
        lines.append("Time_Start, seconds, UTC seconds from midnight on flight date")

        # Line 10: Number of dependent variables
        lines.append(str(num_vars))

        # Line 11: Scale factors
        lines.append(", ".join(["1.0"] * num_vars))

        # Line 12: Fill values
        lines.append(", ".join([str(fill_value)] * num_vars))

        # Lines 13-N: Variable descriptions (one per line)
        lines.extend(var_descriptions)

        # Special comments
        special_comments = self.config.special_comments or []

        # Add CellSizes to special comments only for selected multi-dim variables
        _, filtered_multi = self.converter._filter_variables()
        for var_name, sizes in self.converter.cell_sizes.items():
            if var_name in filtered_multi:
                sizes_str = ', '.join(f"{s:.6g}" for s in np.array(sizes).flatten())
                special_comments.append(f"CellSizes {var_name}: {sizes_str}")

        lines.append(str(len(special_comments)))
        lines.extend(special_comments)

        # Normal comments
        normal_comment_lines = self._build_normal_comments()
        lines.append(str(len(normal_comment_lines)))
        lines.extend(normal_comment_lines)

        # Column headers (last header line)
        lines.append(", ".join(df.columns))

        # Update NLHEAD
        nlhead = len(lines)
        lines[0] = f"{nlhead}, 1001"

        return lines

    def _build_normal_comments(self) -> List[str]:
        """
        Build required normal comment lines.

        Returns:
            List of formatted comment lines
        """
        lines = []
        nc = self.config.normal_comments
        metadata = self.converter.metadata

        for key, label in self.REQUIRED_NORMAL_COMMENTS:
            # Get value from config
            value = getattr(nc, key, '') or ''

            # Handle dynamic substitutions
            if key == 'platform':
                # Format platform string with metadata
                try:
                    value = value.format(
                        platform=metadata.platform,
                        tail_number=metadata.tail_number
                    )
                except (KeyError, ValueError):
                    value = f"NSF/NCAR {metadata.platform} {metadata.tail_number}"

            elif key == 'project_info':
                # Include project name if not already set
                if not value:
                    year = metadata.flight_date.split(',')[0].strip() if metadata.flight_date else ''
                    value = f"{metadata.project_name} {year}".strip()

            elif key == 'revision':
                # Include revision code and description
                version = self.config.options.version
                rev_comments = nc.revision_comments or {}
                rev_desc = rev_comments.get(version, '')
                value = f"{version}: {rev_desc}" if rev_desc else version

            lines.append(f"{label}: {value}")

        return lines

    def _build_data_frame(self) -> pd.DataFrame:
        """
        Build the output DataFrame with flattened multi-dim data.

        Returns:
            DataFrame ready for output
        """
        df = self.converter._build_dataframe_1d()

        # Flatten multidim data into columns for FFI 1001
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
        return df

    def write(self, output_path: Path) -> None:
        """
        Write ICARTT FFI 1001 output.

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

        # Write data
        df.to_csv(output_path, mode='a', index=False, header=False)
