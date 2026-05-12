"""
NetCDF to ASCII converter core — format-agnostic conversion logic.

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import xarray as xr

from config_manager import FlightMetadata, MergedConfiguration, OutputFormat
from dimension_handler import DimensionHandler, HighRateHandler
from formatters import FormatterFactory, OutputFormat as FmtOutputFormat


class NetCDFConverter:
    """
    Main converter class for NetCDF to ASCII conversion.

    Supports 1D time-series and multi-dimensional data with various output formats.
    """

    PLATFORM_MAP = {"N677F": "GV", "N130AR": "C130", "N2UW": "KingAir"}

    def __init__(self, netcdf_path: str, config: Optional[MergedConfiguration] = None):
        """
        Initialize the converter.

        Args:
            netcdf_path: Path to input NetCDF file
            config: Optional MergedConfiguration (if not provided, uses defaults)
        """
        self.netcdf_path = Path(netcdf_path)
        self.config = config or MergedConfiguration.default()
        self.options = self.config.options
        self.metadata = FlightMetadata()

        self.ds: Optional[xr.Dataset] = None
        self.data_1d: dict = {}
        self.data_multidim: dict = {}
        self.units: dict = {}
        self.long_names: dict = {}
        self.cell_sizes: dict = {}

        self.time_data: Optional[np.ndarray] = None
        self.datetime_data: Optional[pd.Series] = None
        self.date_series: Optional[pd.Series] = None
        self.time_series: Optional[pd.Series] = None

        # Dimension handler (initialized after loading NetCDF)
        self._dim_handler: Optional[DimensionHandler] = None
        self._high_rate_handler: Optional[HighRateHandler] = None

    def load_netcdf(self) -> bool:
        """Load and parse the NetCDF file."""
        try:
            self.ds = xr.open_dataset(self.netcdf_path, decode_times=False)
        except FileNotFoundError:
            print(f"Error: NetCDF file not found: {self.netcdf_path}")
            return False
        except Exception as e:
            print(f"Error opening NetCDF file: {e}")
            return False

        self._extract_metadata()
        self._extract_time_data()
        self._parse_variables()

        # Initialize handlers
        self._dim_handler = DimensionHandler(
            self.ds, self.units, self.long_names, self.cell_sizes
        )
        self._high_rate_handler = HighRateHandler(
            self.config.options.high_rate_strategy
        )

        return True

    def _extract_metadata(self):
        """Extract flight metadata from NetCDF attributes."""
        attrs = self.ds.attrs

        self.metadata.project_name = attrs.get('project', 'Unknown')
        self.metadata.tail_number = attrs.get('Platform', attrs.get('platform', 'Unknown'))

        # Use config platform mapping if available
        if self.config.platform_mapping:
            self.metadata.platform = self.config.platform_mapping.get_platform(
                self.metadata.tail_number
            )
        else:
            self.metadata.platform = self.PLATFORM_MAP.get(
                self.metadata.tail_number, 'Unknown'
            )

        flight_date = attrs.get('FlightDate', attrs.get('TimeInterval', ''))
        if flight_date and '/' in flight_date:
            try:
                self.metadata.flight_date = datetime.strptime(
                    flight_date.split()[0] if ' ' in flight_date else flight_date,
                    "%m/%d/%Y"
                ).strftime('%Y, %m, %d')
            except ValueError:
                self.metadata.flight_date = datetime.today().strftime('%Y, %m, %d')
        else:
            self.metadata.flight_date = datetime.today().strftime('%Y, %m, %d')

    def _extract_time_data(self):
        """Extract and decode time data from NetCDF."""
        self.time_data = self.ds['Time'].values

        try:
            decoded_time = xr.coding.times.decode_cf_datetime(
                self.ds['Time'],
                self.ds['Time'].attrs.get('units', 'seconds since midnight')
            )
            self.datetime_data = pd.Series(decoded_time).astype(str)
            datetime_split = self.datetime_data.str.split(' ', expand=True)
            self.date_series = datetime_split[0]
            self.time_series = datetime_split[1]

            self.metadata.start_time = self.datetime_data.iloc[0]
            self.metadata.end_time = self.datetime_data.iloc[-1]
        except Exception as e:
            print(f"Warning: Could not decode time: {e}")
            self.datetime_data = pd.Series(self.time_data)

    def _parse_variables(self):
        """Parse all variables from NetCDF, categorizing by dimensionality."""
        for var_name in self.ds.variables:
            if var_name == 'Time':
                continue

            var = self.ds[var_name]
            dims = var.dims

            # Extract metadata
            self.units[var_name] = var.attrs.get('units', '')
            self.long_names[var_name] = var.attrs.get('long_name', '').replace(',', '')

            if dims == ('Time',):
                # 1D time-series variable
                self.data_1d[var_name] = var.values
            elif len(dims) == 2 and 'Time' in dims:
                # 2D variable (time x bins)
                self.data_multidim[var_name] = var.values
                if 'CellSizes' in var.attrs:
                    self.cell_sizes[var_name] = var.attrs['CellSizes']
            elif len(dims) == 3 and 'Time' in dims:
                # 3D variable - handle high-rate or squeezable dimensions
                data = var.values
                shape = data.shape

                # Find the Time dimension index
                time_idx = dims.index('Time')

                # Find other dimensions
                other_dims = [(i, dims[i], shape[i]) for i in range(3) if i != time_idx]

                # Check for squeezable dimension (size 1)
                squeezable = [d for d in other_dims if d[2] == 1]

                if squeezable:
                    # Squeeze out the dimension of size 1
                    squeeze_axis = squeezable[0][0]
                    self.data_multidim[var_name] = np.squeeze(data, axis=squeeze_axis)
                elif 'sps' in str(dims).lower():
                    # High-rate histogram data - process according to strategy
                    if self._high_rate_handler:
                        # Determine which axis is the SPS axis (not Time, smaller size typically)
                        sps_candidates = [(i, d, s) for i, d, s in other_dims if 'sps' in d.lower()]
                        if sps_candidates:
                            sps_axis = sps_candidates[0][0]
                        else:
                            # Default to axis 1 if Time is axis 0
                            sps_axis = 1 if time_idx == 0 else (0 if time_idx == 1 else 1)
                        self.data_multidim[var_name] = self._high_rate_handler.process(data, sps_dim=sps_axis)
                    else:
                        # Take first sample of the smaller non-time dimension
                        sizes = [(i, s) for i, d, s in other_dims]
                        sps_axis = min(sizes, key=lambda x: x[1])[0]
                        self.data_multidim[var_name] = np.take(data, 0, axis=sps_axis)
                else:
                    # Unknown 3D structure - try to squeeze or take first slice of smaller dim
                    sizes = [(i, s) for i, d, s in other_dims]
                    smaller_axis = min(sizes, key=lambda x: x[1])[0]
                    self.data_multidim[var_name] = np.take(data, 0, axis=smaller_axis)

                if 'CellSizes' in var.attrs:
                    self.cell_sizes[var_name] = var.attrs['CellSizes']

    def _filter_variables(self) -> tuple:
        """Filter variables based on options.variables list.

        If options.variables is None, return all variables (no filter).
        If options.variables is an empty list, return empty dicts (no variables selected).
        """
        # None means no filter (return all), empty list means no variables selected
        if self.options.variables is None:
            return self.data_1d, self.data_multidim

        filtered_1d = {k: v for k, v in self.data_1d.items()
                       if k in self.options.variables}
        filtered_multi = {k: v for k, v in self.data_multidim.items()
                          if k in self.options.variables}
        return filtered_1d, filtered_multi

    def _apply_time_filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply start/end time filtering if specified."""
        if self.options.start_time is not None or self.options.end_time is not None:
            time_col = df.columns[0]  # Assume first column is time
            if self.options.start_time is not None:
                df = df[df[time_col] >= self.options.start_time]
            if self.options.end_time is not None:
                df = df[df[time_col] <= self.options.end_time]
        return df

    def _apply_averaging(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply time averaging if specified."""
        if self.options.averaging and self.options.averaging > 1:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].rolling(
                self.options.averaging, min_periods=1
            ).mean()
            df = df.iloc[::self.options.averaging]
        return df.reset_index(drop=True)

    def _build_dataframe_1d(self) -> pd.DataFrame:
        """Build DataFrame from 1D variables using xarray for performance."""
        data_1d, _ = self._filter_variables()

        # Build all columns at once using pd.concat to avoid fragmentation
        columns = {'Time_Start': self.time_data}

        # Include raw date/time columns so they get filtered/averaged correctly
        if self.date_series is not None:
            columns['_raw_date'] = self.date_series.values
        if self.time_series is not None:
            columns['_raw_time'] = self.time_series.values

        columns.update(data_1d)
        df = pd.DataFrame(columns)

        df = self._apply_time_filter(df)
        df = self._apply_averaging(df)
        df = self._apply_fill_values(df)
        return df

    def _apply_fill_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Replace NaN and inf values with fill value."""
        fill = self.options.fill_value
        for col in df.columns:
            if df[col].dtype in [np.float64, np.float32]:
                df[col] = df[col].where(np.isfinite(df[col]), fill)
        return df.fillna(fill)

    def _process_datetime_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process date/time columns based on format options.

        Uses _raw_date and _raw_time columns that were included during
        DataFrame construction to ensure correct filtering/averaging.
        """
        prepend_cols = {}

        # Process time column from raw data
        if self.options.time_format != "SecOfDay" and '_raw_time' in df.columns:
            time_col = df['_raw_time'].copy()
            if self.options.time_format == 'hh mm ss':
                time_col = time_col.str.replace(':', ' ')
            prepend_cols['Time'] = time_col.values
            df = df.drop(columns=['_raw_time'])
        elif '_raw_time' in df.columns:
            df = df.drop(columns=['_raw_time'])

        # Process date column from raw data
        if self.options.date_format != "NoDate" and '_raw_date' in df.columns:
            date_col = df['_raw_date'].copy()
            if self.options.date_format == 'yyyy mm dd':
                date_col = date_col.str.replace('-', ' ')
            prepend_cols['Date'] = date_col.values
            df = df.drop(columns=['_raw_date'])
        elif '_raw_date' in df.columns:
            df = df.drop(columns=['_raw_date'])

        # Prepend date/time columns using concat to avoid fragmentation
        if prepend_cols:
            prepend_df = pd.DataFrame(prepend_cols, index=df.index)
            df = pd.concat([prepend_df, df], axis=1)

        return df

    def generate_output_filename(self) -> str:
        """Generate appropriate output filename based on format."""
        date_str = self.metadata.flight_date.replace(", ", "").replace(" ", "")

        if self.options.output_format in [OutputFormat.ICARTT_1001, OutputFormat.ICARTT_2110]:
            ext = ".ict"
            return f"{self.metadata.project_name}-CORE_{self.metadata.platform}_{date_str}_{self.options.version}{ext}"
        elif self.options.output_format == OutputFormat.AMES_1001:
            return f"{self.metadata.project_name}_{self.metadata.platform}_{date_str}.ames"
        else:
            return f"{self.metadata.project_name}_{self.metadata.platform}_{date_str}.txt"

    def convert(self, output_path: Optional[str] = None) -> str:
        """
        Perform the full conversion.

        Args:
            output_path: Optional output file path. If not provided, generates from metadata.

        Returns:
            Path to the output file.
        """
        if not self.load_netcdf():
            raise RuntimeError("Failed to load NetCDF file")

        icartt_formats = {OutputFormat.ICARTT_1001, OutputFormat.ICARTT_2110}
        if self.options.output_format in icartt_formats:
            # ICARTT filenames must follow strict naming conventions regardless of
            # what the user specified; preserve directory if one was given.
            compliant_name = self.generate_output_filename()
            if output_path is not None:
                output_path = str(Path(output_path).parent / compliant_name)
                print(f"ICARTT format requires compliant filename: {compliant_name}")
            else:
                output_path = compliant_name
        elif output_path is None:
            output_path = self.generate_output_filename()

        # Get formatter from factory
        formatter = FormatterFactory.create(
            FmtOutputFormat(self.options.output_format.value),
            self,
            self.config
        )
        formatter.write(Path(output_path))

        print(f"Successfully wrote output to: {output_path}")
        return output_path
