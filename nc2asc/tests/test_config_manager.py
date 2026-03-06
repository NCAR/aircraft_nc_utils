"""
Unit tests for ConfigManager module.

Tests configuration merging, precedence, and YAML/JSON loading.
"""

import json
import tempfile
from pathlib import Path
import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from lib.config_manager import (
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


class TestConfigManager:
    """Tests for ConfigManager class."""

    def test_default_configuration(self):
        """Test that default configuration is created correctly."""
        config = MergedConfiguration.default()

        assert config.header.pi_name == "Unknown PI"
        assert config.options.output_format == OutputFormat.ICARTT_1001
        assert config.options.fill_value == -99999.0
        assert config.options.version == "RA"

    def test_load_json_config(self, tmp_path):
        """Test loading JSON configuration file."""
        config_data = {
            "header": {
                "pi_name": "Test PI",
                "pi_organization": "Test Org"
            },
            "normal_comments": {
                "pi_contact_info": "test@example.com"
            }
        }

        config_file = tmp_path / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        manager = ConfigManager(config_path=config_file)
        config = manager.load()

        assert config.header.pi_name == "Test PI"
        assert config.header.pi_organization == "Test Org"
        assert config.normal_comments.pi_contact_info == "test@example.com"

    def test_cli_precedence_over_file(self, tmp_path):
        """Test that CLI args take precedence over file config."""
        config_data = {
            "defaults": {
                "fill_value": -99999.0,
                "version": "RA"
            }
        }

        config_file = tmp_path / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        cli_args = {
            "fill_value": -88888.0,
            "version": "RB"
        }

        manager = ConfigManager(
            config_path=config_file,
            cli_args=cli_args
        )
        config = manager.load()

        assert config.options.fill_value == -88888.0
        assert config.options.version == "RB"

    def test_batch_settings_precedence(self, tmp_path):
        """Test that batch settings override file but not CLI."""
        config_data = {
            "defaults": {
                "fill_value": -99999.0,
                "delimiter": "comma"
            }
        }

        config_file = tmp_path / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        batch_settings = {
            "fill_value": -77777.0,
            "delimiter": "space"
        }

        cli_args = {
            "fill_value": -66666.0
        }

        manager = ConfigManager(
            config_path=config_file,
            batch_settings=batch_settings,
            cli_args=cli_args
        )
        config = manager.load()

        # CLI should win for fill_value
        assert config.options.fill_value == -66666.0
        # Batch should win for delimiter (no CLI override)
        assert config.options.delimiter == "space"

    def test_format_specific_defaults(self):
        """Test that format-specific defaults are applied."""
        # AMES format should have fill_value 9999
        cli_args = {"output_format": "ames"}

        manager = ConfigManager(cli_args=cli_args)
        config = manager.load()

        assert config.options.output_format == OutputFormat.AMES_1001

    def test_platform_mapping(self, tmp_path):
        """Test platform mapping from config."""
        config_data = {
            "platform_mapping": {
                "N123AB": "TestPlane"
            }
        }

        config_file = tmp_path / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        manager = ConfigManager(config_path=config_file)
        config = manager.load()

        assert config.platform_mapping.get_platform("N123AB") == "TestPlane"
        assert config.platform_mapping.get_platform("UNKNOWN") == "Unknown"


class TestParseBatchFile:
    """Tests for batch file parsing."""

    def test_parse_basic_batch(self, tmp_path):
        """Test parsing a basic batch file."""
        batch_content = """
hd=ICARTT
dt=NoDate
tm=SecOfDay
sp=comma
fv=-99999
version=RA
Vars=LATC
Vars=LONC
"""
        batch_file = tmp_path / "test.bat"
        batch_file.write_text(batch_content)

        settings = parse_batch_file(str(batch_file))

        assert settings['header'] == 'icartt'
        assert settings['date_format'] == 'NoDate'
        assert settings['time_format'] == 'SecOfDay'
        assert settings['delimiter'] == 'comma'
        assert settings['fill_value'] == -99999.0
        assert settings['version'] == 'RA'
        assert settings['variables'] == ['LATC', 'LONC']

    def test_parse_time_interval(self, tmp_path):
        """Test parsing time interval from batch file."""
        batch_content = """
ti=50000,70000
"""
        batch_file = tmp_path / "test.bat"
        batch_file.write_text(batch_content)

        settings = parse_batch_file(str(batch_file))

        assert settings['start_time'] == 50000.0
        assert settings['end_time'] == 70000.0

    def test_parse_averaging(self, tmp_path):
        """Test parsing averaging from batch file."""
        batch_content = """
avg=10
"""
        batch_file = tmp_path / "test.bat"
        batch_file.write_text(batch_content)

        settings = parse_batch_file(str(batch_file))

        assert settings['averaging'] == 10

    def test_skip_comments(self, tmp_path):
        """Test that comments are skipped."""
        batch_content = """
REM This is a comment
# This is also a comment
hd=ICARTT
"""
        batch_file = tmp_path / "test.bat"
        batch_file.write_text(batch_content)

        settings = parse_batch_file(str(batch_file))

        assert settings['header'] == 'icartt'

    def test_skip_time_variable(self, tmp_path):
        """Test that Time variable is skipped."""
        batch_content = """
Vars=Time
Vars=LATC
"""
        batch_file = tmp_path / "test.bat"
        batch_file.write_text(batch_content)

        settings = parse_batch_file(str(batch_file))

        assert 'Time' not in settings['variables']
        assert 'LATC' in settings['variables']


class TestDataclasses:
    """Tests for configuration dataclasses."""

    def test_header_config_defaults(self):
        """Test HeaderConfig default values."""
        header = HeaderConfig()

        assert header.pi_name == "Unknown PI"
        assert header.data_interval == 1.0
        assert header.missing_value == -99999.0

    def test_normal_comments_defaults(self):
        """Test NormalComments default values."""
        comments = NormalComments()

        assert comments.ulod_flag == "-77777"
        assert comments.llod_flag == "-88888"
        assert "RA" in comments.revision_comments

    def test_conversion_options_defaults(self):
        """Test ConversionOptions default values."""
        options = ConversionOptions()

        assert options.output_format == OutputFormat.ICARTT_1001
        assert options.date_format == "NoDate"
        assert options.time_format == "SecOfDay"
        assert options.high_rate_strategy == "first"

    def test_flight_metadata(self):
        """Test FlightMetadata dataclass."""
        metadata = FlightMetadata(
            project_name="TEST",
            platform="GV",
            tail_number="N677F",
            flight_date="2025, 07, 22"
        )

        assert metadata.project_name == "TEST"
        assert metadata.platform == "GV"


class TestOutputFormatEnum:
    """Tests for OutputFormat enum."""

    def test_format_values(self):
        """Test that format enum values are correct."""
        assert OutputFormat.PLAIN.value == "plain"
        assert OutputFormat.ICARTT_1001.value == "icartt"
        assert OutputFormat.ICARTT_2110.value == "icartt2110"
        assert OutputFormat.AMES_1001.value == "ames"

    def test_format_map(self):
        """Test ConfigManager format mapping."""
        assert ConfigManager.FORMAT_MAP['plain'] == OutputFormat.PLAIN
        assert ConfigManager.FORMAT_MAP['icartt'] == OutputFormat.ICARTT_1001
        assert ConfigManager.FORMAT_MAP['icartt1001'] == OutputFormat.ICARTT_1001
        assert ConfigManager.FORMAT_MAP['icartt2110'] == OutputFormat.ICARTT_2110
        assert ConfigManager.FORMAT_MAP['ames'] == OutputFormat.AMES_1001


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
