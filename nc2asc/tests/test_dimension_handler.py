"""
Unit tests for DimensionHandler module.

Tests multi-dimensional variable flattening and high-rate data processing.
"""

import numpy as np
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from lib.dimension_handler import (
    DimensionHandler,
    FlattenedVariable,
    HighRateHandler,
    categorize_variables,
)


class TestFlattenedVariable:
    """Tests for FlattenedVariable dataclass."""

    def test_create_flattened_variable(self):
        """Test creating a FlattenedVariable."""
        values = np.random.rand(100, 10)
        col_names = [f"VAR_{i}" for i in range(10)]

        flat_var = FlattenedVariable(
            base_name="VAR",
            column_names=col_names,
            values=values,
            units="um",
            long_name="Test Variable"
        )

        assert flat_var.n_elements == 10
        assert flat_var.base_name == "VAR"
        assert len(flat_var.column_names) == 10

    def test_get_long_name_for_bin_with_values(self):
        """Test generating long name for bin with values."""
        values = np.random.rand(100, 3)
        bin_values = np.array([0.5, 1.5, 2.5])

        flat_var = FlattenedVariable(
            base_name="SIZE",
            column_names=["SIZE_0", "SIZE_1", "SIZE_2"],
            values=values,
            units="um",
            long_name="Particle Size",
            bin_values=bin_values,
            bin_units="um"
        )

        name = flat_var.get_long_name_for_bin(1)
        assert "1.5" in name
        assert "um" in name

    def test_get_long_name_for_bin_without_values(self):
        """Test generating long name for bin without values."""
        values = np.random.rand(100, 3)

        flat_var = FlattenedVariable(
            base_name="SIZE",
            column_names=["SIZE_0", "SIZE_1", "SIZE_2"],
            values=values,
            units="um",
            long_name="Particle Size"
        )

        name = flat_var.get_long_name_for_bin(1)
        assert "bin 1" in name


class TestHighRateHandler:
    """Tests for HighRateHandler class."""

    def test_first_sample_strategy(self):
        """Test first sample extraction strategy."""
        handler = HighRateHandler(strategy="first")
        data = np.arange(120).reshape(4, 3, 10)  # 4 time, 3 sps, 10 bins

        result = handler.process(data)

        assert result.shape == (4, 10)
        # Should be first SPS sample
        np.testing.assert_array_equal(result[0], data[0, 0, :])

    def test_average_strategy(self):
        """Test averaging strategy."""
        handler = HighRateHandler(strategy="average")
        data = np.ones((4, 3, 10)) * 2.0  # All values are 2

        result = handler.process(data)

        assert result.shape == (4, 10)
        np.testing.assert_array_almost_equal(result, 2.0)

    def test_expand_strategy(self):
        """Test expand strategy."""
        handler = HighRateHandler(strategy="expand")
        data = np.arange(120).reshape(4, 3, 10)

        result = handler.process(data)

        assert result.shape == (12, 10)  # 4 * 3 = 12

    def test_invalid_strategy(self):
        """Test that invalid strategy raises error."""
        with pytest.raises(ValueError):
            HighRateHandler(strategy="invalid")

    def test_invalid_dimensions(self):
        """Test that non-3D data raises error."""
        handler = HighRateHandler(strategy="first")
        data = np.arange(100).reshape(10, 10)  # 2D data

        with pytest.raises(ValueError):
            handler.process(data)

    def test_expand_time(self):
        """Test time expansion for full rate."""
        handler = HighRateHandler(strategy="expand")
        time_data = np.array([0.0, 1.0, 2.0, 3.0])
        sps = 3

        expanded = handler.get_expanded_time(time_data, sps)

        assert len(expanded) == 12
        assert expanded[0] == 0.0
        assert expanded[1] == pytest.approx(0.333, rel=0.01)
        assert expanded[3] == 1.0

    def test_no_expand_time_for_other_strategies(self):
        """Test that time is not expanded for non-expand strategies."""
        handler = HighRateHandler(strategy="first")
        time_data = np.array([0.0, 1.0, 2.0])
        sps = 3

        result = handler.get_expanded_time(time_data, sps)

        np.testing.assert_array_equal(result, time_data)


class TestCategorizeVariables:
    """Tests for categorize_variables function."""

    def test_categorize_mock_dataset(self):
        """Test categorizing a mock dataset structure."""
        # Create a mock dataset-like object
        class MockVar:
            def __init__(self, dims):
                self.dims = dims

        class MockDataset:
            def __init__(self):
                self.variables = {
                    'Time': MockVar(('Time',)),
                    'LATC': MockVar(('Time',)),
                    'AUHSAS': MockVar(('Time', 'bins')),
                    'HIGHRATE': MockVar(('Time', 'sps', 'bins')),
                    'STATIC': MockVar(('x', 'y')),  # Not time-based
                }

            def __getitem__(self, key):
                return self.variables[key]

            def __iter__(self):
                return iter(self.variables)

        ds = MockDataset()
        categories = categorize_variables(ds)

        assert 'LATC' in categories['1d']
        assert 'AUHSAS' in categories['2d']
        assert 'HIGHRATE' in categories['3d']
        assert 'STATIC' in categories['other']
        assert 'Time' not in categories['1d']  # Skipped by default


class TestDimensionHandler:
    """Tests for DimensionHandler class."""

    def test_flatten_variable(self):
        """Test flattening a multi-dimensional variable."""
        # Create mock dataset
        class MockDataset:
            def __init__(self):
                pass

            def __contains__(self, key):
                return key == 'VAR'

            def __getitem__(self, key):
                class MockVar:
                    dims = ('Time', 'bins')
                return MockVar()

            def items(self):
                return []

            @property
            def coords(self):
                return {}

        ds = MockDataset()
        units = {'VAR': 'counts'}
        long_names = {'VAR': 'Test Variable'}
        cell_sizes = {}

        handler = DimensionHandler(ds, units, long_names, cell_sizes)

        data = np.random.rand(100, 10)
        flat = handler.flatten_variable('VAR', data)

        assert flat.base_name == 'VAR'
        assert len(flat.column_names) == 10
        assert flat.column_names[0] == 'VAR_0'
        assert flat.column_names[9] == 'VAR_9'
        assert flat.units == 'counts'

    def test_flatten_with_cell_sizes(self):
        """Test flattening with CellSizes metadata."""
        class MockDataset:
            def __init__(self):
                pass

            def __contains__(self, key):
                return key == 'AUHSAS'

            def __getitem__(self, key):
                class MockVar:
                    dims = ('Time', 'bins')
                return MockVar()

            def items(self):
                return []

            @property
            def coords(self):
                return {}

        ds = MockDataset()
        units = {'AUHSAS': '#/cm3'}
        long_names = {'AUHSAS': 'Size Distribution'}
        cell_sizes = {'AUHSAS': np.array([0.1, 0.2, 0.3])}

        handler = DimensionHandler(ds, units, long_names, cell_sizes)

        data = np.random.rand(100, 3)
        flat = handler.flatten_variable('AUHSAS', data)

        assert flat.bin_values is not None
        assert len(flat.bin_values) == 3
        assert flat.bin_units == 'um'

    def test_build_cell_sizes_comment(self):
        """Test building CellSizes comment line."""
        class MockDataset:
            pass

        ds = MockDataset()
        cell_sizes = {'VAR': np.array([0.1, 0.2, 0.3])}

        handler = DimensionHandler(ds, {}, {}, cell_sizes)

        comment = handler.build_cell_sizes_comment('VAR')

        assert comment is not None
        assert 'CellSizes VAR' in comment
        assert '0.1' in comment

    def test_no_cell_sizes_comment(self):
        """Test that no comment is returned when no CellSizes."""
        class MockDataset:
            pass

        ds = MockDataset()
        handler = DimensionHandler(ds, {}, {}, {})

        comment = handler.build_cell_sizes_comment('VAR')

        assert comment is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
