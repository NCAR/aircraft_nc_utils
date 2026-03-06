"""
Dimension Handler for nc2asc NetCDF to ASCII Converter.

Handles multi-dimensional variable processing including:
- Flattening 2D variables into columns
- Preserving bin metadata (CellSizes, coordinates)
- Processing 3D high-rate (SPS) data

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Tuple

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    import xarray as xr


@dataclass
class FlattenedVariable:
    """
    Represents a flattened multi-dimensional variable.

    Attributes:
        base_name: Original variable name
        column_names: List of flattened column names (e.g., ['VAR_0', 'VAR_1', ...])
        values: 2D numpy array with shape (time, n_elements)
        units: Variable units
        long_name: Variable description
        bin_values: Optional array of bin center/edge values
        bin_units: Optional units for bin values
    """
    base_name: str
    column_names: list
    values: np.ndarray
    units: str
    long_name: str
    bin_values: Optional[np.ndarray] = None
    bin_units: Optional[str] = None

    @property
    def n_elements(self) -> int:
        """Number of elements in the flattened dimension."""
        return len(self.column_names)

    def get_long_name_for_bin(self, bin_idx: int) -> str:
        """
        Generate descriptive long name for a specific bin.

        Args:
            bin_idx: Index of the bin

        Returns:
            Descriptive string for the bin column
        """
        if self.bin_values is not None and bin_idx < len(self.bin_values):
            bin_val = self.bin_values[bin_idx]
            units_str = f" {self.bin_units}" if self.bin_units else ""
            return f"{self.long_name} at {bin_val:.4g}{units_str}"
        else:
            return f"{self.long_name} bin {bin_idx}"


class DimensionHandler:
    """
    Handles multi-dimensional variable processing.

    This class provides methods to:
    - Flatten 2D variables into separate columns
    - Extract and preserve bin metadata
    - Find associated dimension variables
    """

    def __init__(self, dataset: 'xr.Dataset', units: dict, long_names: dict, cell_sizes: dict):
        """
        Initialize DimensionHandler.

        Args:
            dataset: xarray Dataset containing the variables
            units: Dictionary mapping variable names to units
            long_names: Dictionary mapping variable names to descriptions
            cell_sizes: Dictionary mapping variable names to CellSizes arrays
        """
        self.ds = dataset
        self.units = units
        self.long_names = long_names
        self.cell_sizes = cell_sizes

    def flatten_variable(self, var_name: str, data: np.ndarray) -> FlattenedVariable:
        """
        Flatten a multi-dimensional variable to columns.

        Args:
            var_name: Name of the variable
            data: 2D numpy array with shape (time, n_elements)

        Returns:
            FlattenedVariable with column names and metadata
        """
        n_elements = data.shape[1]

        # Generate column names
        column_names = [f"{var_name}_{i}" for i in range(n_elements)]

        # Get bin values if available
        bin_values, bin_units = self._get_bin_metadata(var_name, n_elements)

        return FlattenedVariable(
            base_name=var_name,
            column_names=column_names,
            values=data,
            units=self.units.get(var_name, 'unitless'),
            long_name=self.long_names.get(var_name, var_name),
            bin_values=bin_values,
            bin_units=bin_units
        )

    def _get_bin_metadata(self, var_name: str, n_elements: int) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """
        Get bin center/edge values and units for a multi-dimensional variable.

        Searches in order:
        1. CellSizes attribute (particle instruments)
        2. Coordinate variable
        3. Variable with matching dimension shape

        Args:
            var_name: Name of the variable
            n_elements: Number of elements in the variable's non-time dimension

        Returns:
            Tuple of (bin_values array, bin_units string) or (None, None)
        """
        # Check CellSizes attribute first
        if var_name in self.cell_sizes:
            cell_sizes = np.array(self.cell_sizes[var_name]).flatten()
            # Convert cell sizes to bin centers (cumulative sum of midpoints)
            bin_edges = np.concatenate([[0], np.cumsum(cell_sizes)])
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            return bin_centers, 'um'  # Assume micrometers for particle data

        # Check for coordinate variable
        if var_name in self.ds:
            var = self.ds[var_name]
            for dim in var.dims:
                if dim == 'Time':
                    continue

                # Check if dimension itself is a coordinate
                if dim in self.ds.coords:
                    coord = self.ds.coords[dim]
                    if len(coord) == n_elements:
                        return coord.values, coord.attrs.get('units', 'index')

                # Search for variables with matching dimension
                for coord_name, coord_var in self.ds.items():
                    if coord_var.dims == (dim,) and len(coord_var) == n_elements:
                        return coord_var.values, coord_var.attrs.get('units', 'index')

        return None, None

    def find_dimension_variable(self, var_name: str) -> Optional[str]:
        """
        Find the dimension variable associated with a multi-dimensional variable.

        This is used for FFI 2110 format to identify bin center/edge values.

        Args:
            var_name: Name of the multi-dimensional variable

        Returns:
            Name of the dimension variable, or None if not found
        """
        if var_name not in self.ds:
            return None

        var = self.ds[var_name]

        for dim in var.dims:
            if dim == 'Time':
                continue

            # Check if dimension itself is a coordinate
            if dim in self.ds.coords:
                return dim

            # Check for CellSizes attribute
            if 'CellSizes' in var.attrs:
                return f"{var_name}_CellSizes"

            # Search for variables with matching dimension
            for coord_name, coord_var in self.ds.items():
                if coord_var.dims == (dim,):
                    return coord_name

        return None

    def get_dimension_values(self, dim_var_name: Optional[str], var_name: str,
                            n_elements: int) -> np.ndarray:
        """
        Get the values for a dimension variable.

        Args:
            dim_var_name: Name of the dimension variable (or None)
            var_name: Name of the data variable (for CellSizes fallback)
            n_elements: Number of elements expected

        Returns:
            Array of dimension values (bin centers, indices, etc.)
        """
        # Try to get from dimension variable
        if dim_var_name and dim_var_name in self.ds:
            values = self.ds[dim_var_name].values
            if len(values) == n_elements:
                return values

        # Try CellSizes
        if var_name in self.cell_sizes:
            cell_sizes = np.array(self.cell_sizes[var_name]).flatten()
            bin_edges = np.concatenate([[0], np.cumsum(cell_sizes)])
            return (bin_edges[:-1] + bin_edges[1:]) / 2

        # Fall back to indices
        return np.arange(n_elements)

    def to_dataframe(self, flattened: FlattenedVariable, time_length: int) -> pd.DataFrame:
        """
        Convert flattened variable to DataFrame columns.

        Args:
            flattened: FlattenedVariable to convert
            time_length: Length of the time dimension to truncate to

        Returns:
            DataFrame with flattened columns
        """
        df = pd.DataFrame(
            flattened.values[:time_length],
            columns=flattened.column_names
        )
        return df

    def build_cell_sizes_comment(self, var_name: str) -> Optional[str]:
        """
        Build a comment line containing CellSizes information.

        Args:
            var_name: Variable name

        Returns:
            Formatted comment string or None
        """
        if var_name in self.cell_sizes:
            sizes = self.cell_sizes[var_name]
            sizes_str = ', '.join(f"{s:.6g}" for s in np.array(sizes).flatten())
            return f"CellSizes {var_name}: {sizes_str}"
        return None


class HighRateHandler:
    """
    Handles 3D high-rate (SPS) data.

    High-rate data typically has dimensions (Time, SPS, Bins) where SPS
    is the samples-per-second dimension for data collected faster than 1 Hz.
    """

    # Available processing strategies
    FIRST_SAMPLE = "first"      # Take first SPS sample only
    AVERAGE = "average"          # Average across SPS dimension
    EXPAND = "expand"            # Expand to full sample rate

    VALID_STRATEGIES = [FIRST_SAMPLE, AVERAGE, EXPAND]

    def __init__(self, strategy: str = "first"):
        """
        Initialize HighRateHandler.

        Args:
            strategy: Processing strategy - 'first', 'average', or 'expand'
        """
        if strategy not in self.VALID_STRATEGIES:
            raise ValueError(f"Invalid strategy: {strategy}. "
                           f"Must be one of: {self.VALID_STRATEGIES}")
        self.strategy = strategy

    def process(self, data: np.ndarray, sps_dim: int = 1) -> np.ndarray:
        """
        Process 3D high-rate data according to the configured strategy.

        Args:
            data: 3D numpy array with shape (Time, SPS, Bins)
            sps_dim: Index of the SPS dimension (default: 1)

        Returns:
            Processed 2D array with shape (Time, Bins) or (Time*SPS, Bins)
        """
        if data.ndim != 3:
            raise ValueError(f"Expected 3D array, got {data.ndim}D")

        if self.strategy == self.FIRST_SAMPLE:
            # Take only the first SPS sample
            if sps_dim == 1:
                return data[:, 0, :]
            else:
                return np.take(data, 0, axis=sps_dim)

        elif self.strategy == self.AVERAGE:
            # Average across SPS dimension, ignoring NaN
            return np.nanmean(data, axis=sps_dim)

        elif self.strategy == self.EXPAND:
            # Flatten time and SPS dimensions to full rate
            n_time, n_sps, n_bins = data.shape
            return data.reshape(n_time * n_sps, n_bins)

        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

    def get_expanded_time(self, time_data: np.ndarray, sps: int) -> np.ndarray:
        """
        Expand time array to match expanded high-rate data.

        Args:
            time_data: Original time array (1 Hz)
            sps: Samples per second

        Returns:
            Expanded time array with fractional seconds
        """
        if self.strategy != self.EXPAND:
            return time_data

        expanded = []
        for t in time_data:
            for s in range(sps):
                expanded.append(t + s / sps)
        return np.array(expanded)


def categorize_variables(dataset: 'xr.Dataset', skip_vars: Optional[list] = None) -> dict:
    """
    Categorize all variables in a dataset by dimensionality.

    Args:
        dataset: xarray Dataset to analyze
        skip_vars: Variable names to skip (default: ['Time'])

    Returns:
        Dictionary with keys '1d', '2d', '3d' and lists of variable names
    """
    if skip_vars is None:
        skip_vars = ['Time']

    categories = {
        '1d': [],
        '2d': [],
        '3d': [],
        'other': []
    }

    for var_name in dataset.variables:
        if var_name in skip_vars:
            continue

        var = dataset[var_name]
        dims = var.dims

        if dims == ('Time',):
            categories['1d'].append(var_name)
        elif len(dims) == 2 and 'Time' in dims:
            categories['2d'].append(var_name)
        elif len(dims) == 3 and 'Time' in dims:
            categories['3d'].append(var_name)
        else:
            categories['other'].append(var_name)

    return categories
