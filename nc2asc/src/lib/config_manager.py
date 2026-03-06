"""
Configuration Manager for nc2asc NetCDF to ASCII Converter.

Handles configuration from multiple sources with precedence:
CLI args > Batch file > YAML/JSON config > Format defaults > Global defaults

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Type

import json

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class OutputFormat(Enum):
    """Supported output formats."""
    PLAIN = "plain"
    ICARTT_1001 = "icartt"
    ICARTT_2110 = "icartt2110"
    AMES_1001 = "ames"


@dataclass
class HeaderConfig:
    """ICARTT/AMES header metadata configuration."""
    pi_name: str = "Unknown PI"
    pi_organization: str = "Unknown Organization"
    datasource_desc: str = "Instruments on"
    data_interval: float = 1.0
    missing_value: float = -99999.0


@dataclass
class NormalComments:
    """ICARTT required normal comment fields."""
    pi_contact_info: str = "Contact PI"
    platform: str = "NSF/NCAR {platform} {tail_number}"
    location: str = "See navigation data"
    associated_data: str = "Full data in NetCDF file"
    instrument_info: str = "See header"
    data_info: str = "Processed data"
    uncertainty: str = "Contact PI"
    ulod_flag: str = "-77777"
    ulod_value: str = "N/A"
    llod_flag: str = "-88888"
    llod_value: str = "N/A"
    dm_contact_info: str = "NCAR/EOL Archive"
    project_info: str = ""
    stipulations_on_use: str = "Preliminary data"
    other_comments: str = "none"
    revision: str = "RA"
    revision_comments: dict = field(default_factory=lambda: {
        "RA": "Field Data",
        "RB": "Trimmed to flight time",
        "RC": "Post-mission preliminary QC",
        "R0": "Final quality controlled data",
        "R1": "First revision to final data"
    })


@dataclass
class ConversionOptions:
    """Runtime conversion options."""
    output_format: OutputFormat = OutputFormat.ICARTT_1001
    date_format: str = "NoDate"  # 'yyyy-mm-dd', 'yyyy mm dd', 'NoDate'
    time_format: str = "SecOfDay"  # 'hh:mm:ss', 'hh mm ss', 'SecOfDay'
    delimiter: str = "comma"  # 'comma', 'space'
    fill_value: float = -99999.0
    variables: list = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    averaging: Optional[int] = None
    version: str = "RA"
    high_rate_strategy: str = "first"  # 'first', 'average', 'expand'


@dataclass
class PlatformMapping:
    """Aircraft platform mappings."""
    tail_to_platform: dict = field(default_factory=lambda: {
        "N677F": "GV",
        "N130AR": "C130",
        "N2UW": "KingAir"
    })

    def get_platform(self, tail_number: str) -> str:
        """Get platform name from tail number."""
        return self.tail_to_platform.get(tail_number, "Unknown")


@dataclass
class FlightMetadata:
    """Metadata extracted from NetCDF file."""
    project_name: str = ""
    platform: str = ""
    tail_number: str = ""
    flight_date: str = ""
    start_time: str = ""
    end_time: str = ""


@dataclass
class MergedConfiguration:
    """Complete merged configuration from all sources."""
    header: HeaderConfig
    normal_comments: NormalComments
    special_comments: list
    options: ConversionOptions
    platform_mapping: PlatformMapping

    @classmethod
    def default(cls) -> 'MergedConfiguration':
        """Create a default configuration."""
        return cls(
            header=HeaderConfig(),
            normal_comments=NormalComments(),
            special_comments=[],
            options=ConversionOptions(),
            platform_mapping=PlatformMapping()
        )


class ConfigManager:
    """
    Manages configuration from multiple sources with precedence.

    Precedence (highest to lowest):
    1. CLI Arguments
    2. Batch File Settings
    3. YAML/JSON Config File
    4. Format-specific Defaults
    5. Global Defaults
    """

    # Format-specific default values
    FORMAT_DEFAULTS = {
        OutputFormat.PLAIN: {"fill_value": -99999.0, "delimiter": ","},
        OutputFormat.ICARTT_1001: {"fill_value": -99999.0, "delimiter": ", "},
        OutputFormat.ICARTT_2110: {"fill_value": -99999.0, "delimiter": ", "},
        OutputFormat.AMES_1001: {"fill_value": 9999.0, "delimiter": " "},
    }

    # Mapping from string to OutputFormat
    FORMAT_MAP = {
        'plain': OutputFormat.PLAIN,
        'icartt': OutputFormat.ICARTT_1001,
        'icartt1001': OutputFormat.ICARTT_1001,
        'icartt2110': OutputFormat.ICARTT_2110,
        'ames': OutputFormat.AMES_1001,
    }

    def __init__(
        self,
        config_path: Optional[Path] = None,
        batch_settings: Optional[dict] = None,
        cli_args: Optional[dict] = None
    ):
        """
        Initialize ConfigManager.

        Args:
            config_path: Path to YAML or JSON configuration file
            batch_settings: Dictionary of settings from batch file
            cli_args: Dictionary of command-line arguments
        """
        self.config_path = Path(config_path) if config_path else None
        self.batch_settings = batch_settings or {}
        self.cli_args = cli_args or {}

        self._file_config: dict = {}
        self._merged: Optional[MergedConfiguration] = None

    def load(self) -> MergedConfiguration:
        """
        Load and merge configuration from all sources.

        Returns:
            MergedConfiguration with all settings merged by precedence
        """
        # Load file config (YAML or JSON)
        if self.config_path and self.config_path.exists():
            self._file_config = self._load_config_file(self.config_path)

        # Build merged config with precedence
        self._merged = self._merge_configs()
        return self._merged

    def _load_config_file(self, path: Path) -> dict:
        """
        Load YAML or JSON configuration file.

        Args:
            path: Path to configuration file

        Returns:
            Dictionary with configuration values
        """
        with open(path, 'r') as f:
            if path.suffix in ('.yaml', '.yml'):
                if not YAML_AVAILABLE:
                    raise ImportError("PyYAML is required to load YAML config files. "
                                     "Install with: pip install pyyaml")
                return yaml.safe_load(f) or {}
            else:
                return json.load(f)

    def _merge_configs(self) -> MergedConfiguration:
        """
        Merge configs with CLI > Batch > File > Format > Global precedence.

        Returns:
            MergedConfiguration with all settings merged
        """
        # Determine output format first (affects format-specific defaults)
        output_format = self._resolve_output_format()
        format_defaults = self.FORMAT_DEFAULTS.get(output_format, {})

        # Build header config
        header = self._build_header_config(format_defaults)

        # Build normal comments
        normal_comments = self._build_normal_comments()

        # Build options
        options = self._build_options(output_format, format_defaults)

        # Special comments
        special_comments = self._file_config.get('special_comments', [])

        # Platform mapping
        platform_mapping = PlatformMapping(
            tail_to_platform=self._file_config.get(
                'platform_mapping',
                PlatformMapping().tail_to_platform
            )
        )

        return MergedConfiguration(
            header=header,
            normal_comments=normal_comments,
            special_comments=special_comments,
            options=options,
            platform_mapping=platform_mapping
        )

    def _get_value(self, key: str, default: Any = None) -> Any:
        """
        Get value with precedence: CLI > Batch > File > Default.

        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if not found

        Returns:
            Configuration value from highest precedence source
        """
        # Check CLI args first
        if key in self.cli_args and self.cli_args[key] is not None:
            return self.cli_args[key]

        # Check batch settings
        if key in self.batch_settings and self.batch_settings[key] is not None:
            return self.batch_settings[key]

        # Check file config (supports dot notation)
        parts = key.split('.')
        value = self._file_config
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default

        return value if value != self._file_config else default

    def _resolve_output_format(self) -> OutputFormat:
        """
        Resolve output format from sources.

        Returns:
            OutputFormat enum value
        """
        format_str = self._get_value('defaults.output_format') or \
                     self._get_value('output_format') or \
                     self._get_value('format')
        if format_str and isinstance(format_str, str):
            return self.FORMAT_MAP.get(format_str.lower(), OutputFormat.ICARTT_1001)
        return OutputFormat.ICARTT_1001

    def _build_header_config(self, format_defaults: dict) -> HeaderConfig:
        """Build HeaderConfig from merged sources."""
        file_header = self._file_config.get('header', {})

        return HeaderConfig(
            pi_name=self._get_value('header.pi_name') or file_header.get('pi_name', HeaderConfig.pi_name),
            pi_organization=self._get_value('header.pi_organization') or
                           file_header.get('pi_organization', HeaderConfig.pi_organization),
            datasource_desc=self._get_value('header.datasource_desc') or
                           file_header.get('datasource_desc', HeaderConfig.datasource_desc),
            data_interval=float(self._get_value('header.data_interval') or
                               file_header.get('data_interval', HeaderConfig.data_interval)),
            missing_value=float(self._get_value('fill_value') or
                               file_header.get('missing_value', format_defaults.get('fill_value', -99999.0)))
        )

    def _build_normal_comments(self) -> NormalComments:
        """Build NormalComments from merged sources."""
        file_comments = self._file_config.get('normal_comments', {})
        defaults = NormalComments()

        return NormalComments(
            pi_contact_info=file_comments.get('pi_contact_info', defaults.pi_contact_info),
            platform=file_comments.get('platform', defaults.platform),
            location=file_comments.get('location', defaults.location),
            associated_data=file_comments.get('associated_data', defaults.associated_data),
            instrument_info=file_comments.get('instrument_info', defaults.instrument_info),
            data_info=file_comments.get('data_info', defaults.data_info),
            uncertainty=file_comments.get('uncertainty', defaults.uncertainty),
            ulod_flag=file_comments.get('ulod_flag', defaults.ulod_flag),
            ulod_value=file_comments.get('ulod_value', defaults.ulod_value),
            llod_flag=file_comments.get('llod_flag', defaults.llod_flag),
            llod_value=file_comments.get('llod_value', defaults.llod_value),
            dm_contact_info=file_comments.get('dm_contact_info', defaults.dm_contact_info),
            project_info=file_comments.get('project_info', defaults.project_info),
            stipulations_on_use=file_comments.get('stipulations_on_use', defaults.stipulations_on_use),
            other_comments=file_comments.get('other_comments', defaults.other_comments),
            revision=self._get_value('version') or file_comments.get('revision', defaults.revision),
            revision_comments=file_comments.get('revision_comments', defaults.revision_comments)
        )

    def _build_options(self, output_format: OutputFormat, format_defaults: dict) -> ConversionOptions:
        """Build ConversionOptions from merged sources."""
        file_defaults = self._file_config.get('defaults', {})

        # Get delimiter with format-specific default
        delimiter = self._get_value('delimiter')
        if delimiter is None:
            delimiter = file_defaults.get('delimiter', 'comma')

        # Get fill value with format-specific default
        fill_value = self._get_value('fill_value')
        if fill_value is None:
            fill_value = file_defaults.get('fill_value', format_defaults.get('fill_value', -99999.0))

        return ConversionOptions(
            output_format=output_format,
            date_format=self._get_value('date_format') or file_defaults.get('date_format', 'NoDate'),
            time_format=self._get_value('time_format') or file_defaults.get('time_format', 'SecOfDay'),
            delimiter=delimiter,
            fill_value=float(fill_value),
            variables=self._get_value('variables') or [],
            start_time=self._get_value('start_time'),
            end_time=self._get_value('end_time'),
            averaging=self._get_value('averaging'),
            version=self._get_value('version') or file_defaults.get('version', 'RA'),
            high_rate_strategy=self._get_value('high_rate_strategy') or
                              file_defaults.get('high_rate_strategy', 'first')
        )

    def get_config(self) -> MergedConfiguration:
        """
        Get the merged configuration.

        Returns:
            MergedConfiguration (calls load() if not already loaded)
        """
        if self._merged is None:
            return self.load()
        return self._merged

    def update_from_cli(self, args: dict) -> None:
        """
        Update CLI args and reload configuration.

        Args:
            args: Dictionary of CLI arguments
        """
        self.cli_args.update(args)
        self._merged = None  # Force reload on next access

    def update_from_batch(self, settings: dict) -> None:
        """
        Update batch settings and reload configuration.

        Args:
            settings: Dictionary of batch file settings
        """
        self.batch_settings.update(settings)
        self._merged = None  # Force reload on next access


def parse_batch_file(batch_path: str) -> dict:
    """
    Parse a batch file and return settings as a dictionary.

    Batch file format:
        hd=ICARTT          # Header format: Plain, ICARTT, ICARTT2110, AMES
        dt=NoDate          # Date format: yyyy-mm-dd, yyyy mm dd, NoDate
        tm=SecOfDay        # Time format: hh:mm:ss, hh mm ss, SecOfDay
        sp=comma           # Delimiter: comma, space
        fv=-99999          # Fill value
        version=RA         # Version string
        avg=10             # Averaging window (optional)
        ti=50000,70000     # Time interval start,end (optional)
        if=/path/to/input.nc   # Input file (optional, overridden by -i)
        of=/path/to/output.ict # Output file (optional, overridden by -o)
        Vars=LATC          # Variables to include (one per line)
        Vars=LONC
        REM This is a comment

    Args:
        batch_path: Path to the batch file

    Returns:
        Dictionary with parsed settings
    """
    settings = {
        'header': None,
        'date_format': None,
        'time_format': None,
        'delimiter': None,
        'fill_value': None,
        'version': None,
        'averaging': None,
        'start_time': None,
        'end_time': None,
        'input_file': None,
        'output_file': None,
        'variables': [],
    }

    # Mapping from batch file values to internal values
    header_map = {
        'Plain': 'plain',
        'ICARTT': 'icartt',
        'ICARTT2110': 'icartt2110',
        'icartt2110': 'icartt2110',
        'AMES': 'ames',
    }

    date_map = {
        'yyyy-mm-dd': 'yyyy-mm-dd',
        'yyyy mm dd': 'yyyy mm dd',
        'NoDate': 'NoDate',
    }

    time_map = {
        'hh:mm:ss': 'hh:mm:ss',
        'hh mm ss': 'hh mm ss',
        'SecOfDay': 'SecOfDay',
    }

    with open(batch_path, 'r') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('REM') or line.startswith('#'):
                continue

            # Parse key=value pairs
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip().lower()
                value = value.strip()

                if key == 'hd':
                    settings['header'] = header_map.get(value, value.lower())
                elif key == 'dt':
                    settings['date_format'] = date_map.get(value, value)
                elif key == 'tm':
                    settings['time_format'] = time_map.get(value, value)
                elif key == 'sp':
                    settings['delimiter'] = value.lower()
                elif key == 'fv':
                    try:
                        settings['fill_value'] = float(value)
                    except ValueError:
                        pass
                elif key == 'version':
                    settings['version'] = value
                elif key == 'avg':
                    try:
                        settings['averaging'] = int(value)
                    except ValueError:
                        pass
                elif key == 'ti':
                    # Time interval: start,end or X,X for full file
                    parts = value.split(',')
                    if len(parts) == 2:
                        start, end = parts
                        if start.strip() != 'X':
                            try:
                                settings['start_time'] = float(start.strip())
                            except ValueError:
                                pass
                        if end.strip() != 'X':
                            try:
                                settings['end_time'] = float(end.strip())
                            except ValueError:
                                pass
                elif key == 'if':
                    settings['input_file'] = value
                elif key == 'of':
                    settings['output_file'] = value
                elif key == 'vars':
                    # Handle variable - skip 'Time' as it's implicit
                    if value and value != 'Time':
                        settings['variables'].append(value)

    return settings
