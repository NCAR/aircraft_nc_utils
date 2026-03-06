"""
Formatter Factory for nc2asc.

Provides a factory pattern for creating output formatters.

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

from enum import Enum
from typing import TYPE_CHECKING, Dict, Type

if TYPE_CHECKING:
    from .base import OutputFormatter
    from ..config_manager import MergedConfiguration


class OutputFormat(Enum):
    """Supported output formats."""
    PLAIN = "plain"
    ICARTT_1001 = "icartt"
    ICARTT_2110 = "icartt2110"
    AMES_1001 = "ames"


class FormatterFactory:
    """
    Factory for creating output formatters.

    Uses a registry pattern where formatter classes register themselves
    using the @FormatterFactory.register decorator.
    """

    _registry: Dict[OutputFormat, Type['OutputFormatter']] = {}

    @classmethod
    def register(cls, format_type: OutputFormat):
        """
        Decorator to register formatter classes.

        Usage:
            @FormatterFactory.register(OutputFormat.PLAIN)
            class PlainWriter(OutputFormatter):
                ...

        Args:
            format_type: OutputFormat enum value

        Returns:
            Decorator function
        """
        def decorator(formatter_class: Type['OutputFormatter']):
            cls._registry[format_type] = formatter_class
            return formatter_class
        return decorator

    @classmethod
    def create(
        cls,
        format_type: OutputFormat,
        converter: 'NetCDFConverter',
        config: 'MergedConfiguration'
    ) -> 'OutputFormatter':
        """
        Create formatter instance for specified format.

        Args:
            format_type: OutputFormat enum value
            converter: NetCDFConverter with loaded data
            config: MergedConfiguration with settings

        Returns:
            OutputFormatter instance

        Raises:
            ValueError: If format_type is not registered
        """
        if format_type not in cls._registry:
            available = ', '.join(fmt.value for fmt in cls._registry.keys())
            raise ValueError(f"Unknown format: {format_type}. "
                           f"Available formats: {available}")
        return cls._registry[format_type](converter, config)

    @classmethod
    def available_formats(cls) -> list:
        """
        List all registered format types.

        Returns:
            List of format value strings
        """
        return [fmt.value for fmt in cls._registry.keys()]

    @classmethod
    def get_format_enum(cls, format_str: str) -> OutputFormat:
        """
        Convert format string to OutputFormat enum.

        Args:
            format_str: Format string (e.g., 'icartt', 'plain')

        Returns:
            OutputFormat enum value

        Raises:
            ValueError: If format string is not recognized
        """
        format_map = {
            'plain': OutputFormat.PLAIN,
            'icartt': OutputFormat.ICARTT_1001,
            'icartt1001': OutputFormat.ICARTT_1001,
            'icartt2110': OutputFormat.ICARTT_2110,
            'ames': OutputFormat.AMES_1001,
        }
        format_lower = format_str.lower()
        if format_lower not in format_map:
            raise ValueError(f"Unknown format: {format_str}. "
                           f"Available: {list(format_map.keys())}")
        return format_map[format_lower]
