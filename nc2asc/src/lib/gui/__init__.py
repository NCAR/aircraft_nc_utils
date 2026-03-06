"""
GUI Module for nc2asc NetCDF to ASCII Converter.

This package provides a PyQt5 graphical user interface for the nc2asc converter,
supporting multi-dimensional data and various output formats including ICARTT FFI 2110.

Components:
- NC2ASCGUI: Main application window
- VariableTableWidget: Variable selection table with multi-dim highlighting
- OutputOptionsPanel: Output format and conversion options
- PreviewPanel: Live preview of output content
- ConfigEditorDialog: Header and comment configuration editor

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

from .main_window import NC2ASCGUI
from .variable_table import VariableTableWidget
from .options_panel import OutputOptionsPanel
from .preview_panel import PreviewPanel
from .config_dialog import ConfigEditorDialog

__all__ = [
    'NC2ASCGUI',
    'VariableTableWidget',
    'OutputOptionsPanel',
    'PreviewPanel',
    'ConfigEditorDialog',
]
