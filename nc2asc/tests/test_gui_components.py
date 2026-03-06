"""
Tests for nc2asc GUI components.

These tests verify the GUI widgets work correctly in isolation.
Requires PyQt5 and pytest-qt for execution.

Usage:
    pytest tests/test_gui_components.py -v

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Skip all tests if PyQt5 not available
pytest.importorskip("PyQt5")

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from lib.config_manager import (
    MergedConfiguration, ConversionOptions, OutputFormat,
    HeaderConfig, NormalComments, PlatformMapping
)


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for all tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def default_config():
    """Create default configuration for testing."""
    return MergedConfiguration.default()


class TestVariableTableWidget:
    """Tests for VariableTableWidget."""

    def test_create_widget(self, qapp):
        """Test widget can be created."""
        from lib.gui.variable_table import VariableTableWidget
        widget = VariableTableWidget()
        assert widget is not None
        assert widget.table.columnCount() == 5

    def test_select_all(self, qapp):
        """Test select all functionality."""
        from lib.gui.variable_table import VariableTableWidget
        widget = VariableTableWidget()
        # With no data, select_all should not error
        widget.select_all()
        assert widget.get_selected_variables() == []

    def test_clear_all(self, qapp):
        """Test clear all functionality."""
        from lib.gui.variable_table import VariableTableWidget
        widget = VariableTableWidget()
        widget.clear_all()
        assert widget.get_selected_variables() == []


class TestOutputOptionsPanel:
    """Tests for OutputOptionsPanel."""

    def test_create_panel(self, qapp):
        """Test panel can be created."""
        from lib.gui.options_panel import OutputOptionsPanel
        panel = OutputOptionsPanel()
        assert panel is not None

    def test_get_conversion_options(self, qapp):
        """Test getting conversion options."""
        from lib.gui.options_panel import OutputOptionsPanel
        panel = OutputOptionsPanel()
        options = panel.get_conversion_options()
        assert isinstance(options, ConversionOptions)
        # Plain ASCII is first in the combo box, so it's the default
        assert options.output_format == OutputFormat.PLAIN

    def test_set_output_format(self, qapp):
        """Test setting output format."""
        from lib.gui.options_panel import OutputOptionsPanel
        panel = OutputOptionsPanel()

        panel.set_output_format(OutputFormat.ICARTT_2110)
        assert panel.get_output_format() == OutputFormat.ICARTT_2110

        panel.set_output_format(OutputFormat.PLAIN)
        assert panel.get_output_format() == OutputFormat.PLAIN

    def test_set_from_config(self, qapp, default_config):
        """Test setting panel from configuration."""
        from lib.gui.options_panel import OutputOptionsPanel
        panel = OutputOptionsPanel()
        panel.set_from_config(default_config)
        # Should not error
        options = panel.get_conversion_options()
        assert options is not None


class TestPreviewPanel:
    """Tests for PreviewPanel."""

    def test_create_panel(self, qapp):
        """Test panel can be created."""
        from lib.gui.preview_panel import PreviewPanel
        panel = PreviewPanel()
        assert panel is not None

    def test_clear(self, qapp):
        """Test clearing preview."""
        from lib.gui.preview_panel import PreviewPanel
        panel = PreviewPanel()
        panel.clear()
        assert panel.preview_text.toPlainText() == ""

    def test_set_preview_text(self, qapp):
        """Test setting preview text."""
        from lib.gui.preview_panel import PreviewPanel
        panel = PreviewPanel()
        panel.set_preview_text("Test content", header_lines=2)
        assert "Test content" in panel.preview_text.toPlainText()


class TestConfigEditorDialog:
    """Tests for ConfigEditorDialog."""

    def test_create_dialog(self, qapp, default_config):
        """Test dialog can be created."""
        from lib.gui.config_dialog import ConfigEditorDialog
        dialog = ConfigEditorDialog(default_config)
        assert dialog is not None

    def test_get_config(self, qapp, default_config):
        """Test getting configuration from dialog."""
        from lib.gui.config_dialog import ConfigEditorDialog
        dialog = ConfigEditorDialog(default_config)
        config = dialog.get_config()
        assert isinstance(config, MergedConfiguration)


class TestMainWindow:
    """Tests for NC2ASCGUI main window."""

    def test_create_window(self, qapp):
        """Test main window can be created."""
        from lib.gui.main_window import NC2ASCGUI
        window = NC2ASCGUI()
        assert window is not None
        assert window.windowTitle() == "nc2asc - NetCDF to ASCII Converter"

    def test_window_has_menu(self, qapp):
        """Test main window has menu bar."""
        from lib.gui.main_window import NC2ASCGUI
        window = NC2ASCGUI()
        menubar = window.menuBar()
        assert menubar is not None

    def test_convert_button_disabled_initially(self, qapp):
        """Test convert button is disabled without data."""
        from lib.gui.main_window import NC2ASCGUI
        window = NC2ASCGUI()
        assert not window.convert_btn.isEnabled()
