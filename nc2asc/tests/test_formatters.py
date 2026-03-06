"""
Unit tests for Output Formatters.

Tests the FormatterFactory and individual formatter implementations.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from lib.formatters import (
    FormatterFactory,
    OutputFormat,
    OutputFormatter,
    PlainWriter,
    ICARTT1001Writer,
    ICARTT2110Writer,
    AMESWriter,
)
from lib.config_manager import MergedConfiguration


class TestFormatterFactory:
    """Tests for FormatterFactory class."""

    def test_available_formats(self):
        """Test that all formats are registered."""
        formats = FormatterFactory.available_formats()

        assert 'plain' in formats
        assert 'icartt' in formats
        assert 'icartt2110' in formats
        assert 'ames' in formats

    def test_get_format_enum(self):
        """Test string to enum conversion."""
        assert FormatterFactory.get_format_enum('plain') == OutputFormat.PLAIN
        assert FormatterFactory.get_format_enum('icartt') == OutputFormat.ICARTT_1001
        assert FormatterFactory.get_format_enum('icartt1001') == OutputFormat.ICARTT_1001
        assert FormatterFactory.get_format_enum('icartt2110') == OutputFormat.ICARTT_2110
        assert FormatterFactory.get_format_enum('ames') == OutputFormat.AMES_1001

    def test_get_format_enum_invalid(self):
        """Test that invalid format raises error."""
        with pytest.raises(ValueError):
            FormatterFactory.get_format_enum('invalid')

    def test_create_plain_formatter(self):
        """Test creating PlainWriter."""
        converter = MagicMock()
        config = MergedConfiguration.default()

        formatter = FormatterFactory.create(OutputFormat.PLAIN, converter, config)

        assert isinstance(formatter, PlainWriter)

    def test_create_icartt_formatter(self):
        """Test creating ICARTT1001Writer."""
        converter = MagicMock()
        config = MergedConfiguration.default()

        formatter = FormatterFactory.create(OutputFormat.ICARTT_1001, converter, config)

        assert isinstance(formatter, ICARTT1001Writer)

    def test_create_icartt2110_formatter(self):
        """Test creating ICARTT2110Writer."""
        converter = MagicMock()
        config = MergedConfiguration.default()

        formatter = FormatterFactory.create(OutputFormat.ICARTT_2110, converter, config)

        assert isinstance(formatter, ICARTT2110Writer)

    def test_create_ames_formatter(self):
        """Test creating AMESWriter."""
        converter = MagicMock()
        config = MergedConfiguration.default()

        formatter = FormatterFactory.create(OutputFormat.AMES_1001, converter, config)

        assert isinstance(formatter, AMESWriter)


class TestPlainWriter:
    """Tests for PlainWriter class."""

    def test_file_extension(self):
        """Test file extension property."""
        converter = MagicMock()
        config = MergedConfiguration.default()

        formatter = PlainWriter(converter, config)

        assert formatter.file_extension == ".txt"

    def test_default_fill_value(self):
        """Test default fill value."""
        converter = MagicMock()
        config = MergedConfiguration.default()

        formatter = PlainWriter(converter, config)

        assert formatter.default_fill_value == -99999.0

    def test_delimiter_comma(self):
        """Test comma delimiter."""
        converter = MagicMock()
        config = MergedConfiguration.default()
        config.options.delimiter = 'comma'

        formatter = PlainWriter(converter, config)

        assert formatter.delimiter == ','

    def test_delimiter_space(self):
        """Test space delimiter."""
        converter = MagicMock()
        config = MergedConfiguration.default()
        config.options.delimiter = 'space'

        formatter = PlainWriter(converter, config)

        assert formatter.delimiter == ' '


class TestICARTT1001Writer:
    """Tests for ICARTT1001Writer class."""

    def test_file_extension(self):
        """Test file extension property."""
        converter = MagicMock()
        config = MergedConfiguration.default()

        formatter = ICARTT1001Writer(converter, config)

        assert formatter.file_extension == ".ict"

    def test_delimiter(self):
        """Test ICARTT delimiter."""
        converter = MagicMock()
        config = MergedConfiguration.default()

        formatter = ICARTT1001Writer(converter, config)

        assert formatter.delimiter == ", "

    def test_required_normal_comments(self):
        """Test that all 16 required keywords are defined."""
        assert len(ICARTT1001Writer.REQUIRED_NORMAL_COMMENTS) == 16

        keywords = [k[1] for k in ICARTT1001Writer.REQUIRED_NORMAL_COMMENTS]
        assert 'PI_CONTACT_INFO' in keywords
        assert 'PLATFORM' in keywords
        assert 'LOCATION' in keywords
        assert 'UNCERTAINTY' in keywords
        assert 'ULOD_FLAG' in keywords
        assert 'LLOD_FLAG' in keywords
        assert 'REVISION' in keywords


class TestICARTT2110Writer:
    """Tests for ICARTT2110Writer class."""

    def test_file_extension(self):
        """Test file extension property."""
        converter = MagicMock()
        config = MergedConfiguration.default()

        formatter = ICARTT2110Writer(converter, config)

        assert formatter.file_extension == ".ict"


class TestAMESWriter:
    """Tests for AMESWriter class."""

    def test_file_extension(self):
        """Test file extension property."""
        converter = MagicMock()
        config = MergedConfiguration.default()

        formatter = AMESWriter(converter, config)

        assert formatter.file_extension == ".ames"

    def test_delimiter(self):
        """Test AMES delimiter (space)."""
        converter = MagicMock()
        config = MergedConfiguration.default()

        formatter = AMESWriter(converter, config)

        assert formatter.delimiter == " "

    def test_default_fill_value(self):
        """Test AMES default fill value (9999)."""
        converter = MagicMock()
        config = MergedConfiguration.default()

        formatter = AMESWriter(converter, config)

        assert formatter.default_fill_value == 9999.0


class TestOutputFormatterBase:
    """Tests for OutputFormatter base class functionality."""

    def test_get_units_direct(self):
        """Test getting units for direct variable."""
        converter = MagicMock()
        converter.units = {'TEMP': 'C'}
        config = MergedConfiguration.default()

        formatter = PlainWriter(converter, config)

        assert formatter._get_units('TEMP') == 'C'

    def test_get_units_flattened(self):
        """Test getting units for flattened variable."""
        converter = MagicMock()
        converter.units = {'SIZE': 'um'}
        config = MergedConfiguration.default()

        formatter = PlainWriter(converter, config)

        # SIZE_0 should find SIZE's units
        assert formatter._get_units('SIZE_0') == 'um'

    def test_get_units_unknown(self):
        """Test getting units for unknown variable."""
        converter = MagicMock()
        converter.units = {}
        config = MergedConfiguration.default()

        formatter = PlainWriter(converter, config)

        assert formatter._get_units('UNKNOWN') == 'unitless'

    def test_get_long_name_direct(self):
        """Test getting long name for direct variable."""
        converter = MagicMock()
        converter.long_names = {'TEMP': 'Temperature'}
        config = MergedConfiguration.default()

        formatter = PlainWriter(converter, config)

        assert formatter._get_long_name('TEMP') == 'Temperature'

    def test_get_long_name_flattened(self):
        """Test getting long name for flattened variable."""
        converter = MagicMock()
        converter.long_names = {'SIZE': 'Particle Size'}
        config = MergedConfiguration.default()

        formatter = PlainWriter(converter, config)

        # SIZE_5 should find SIZE's long name
        assert formatter._get_long_name('SIZE_5') == 'Particle Size'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
