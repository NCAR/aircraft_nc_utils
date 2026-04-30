"""
Main Window for nc2asc GUI.

The main application window that integrates all GUI components
for NetCDF to ASCII conversion.

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

import os
import sys
from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QGroupBox, QLabel, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QStatusBar, QMenuBar, QMenu, QAction,
    QProgressDialog, QApplication
)
from PyQt5.QtCore import Qt, QSettings

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .variable_table import VariableTableWidget
from .options_panel import OutputOptionsPanel
from .preview_panel import PreviewPanel, VariableDetailPanel
from .config_dialog import ConfigEditorDialog

from ..config_manager import (
    ConfigManager, ConversionOptions, MergedConfiguration, OutputFormat
)
from ..dimension_handler import categorize_variables


def _get_netcdf_converter():
    """Load NetCDFConverter from nc2asc_multidim script (no .py extension)."""
    import importlib.machinery
    import importlib.util
    src_dir = Path(__file__).parent.parent.parent
    module_path = src_dir / "nc2asc_multidim"
    loader = importlib.machinery.SourceFileLoader("nc2asc_multidim", str(module_path))
    spec = importlib.util.spec_from_loader("nc2asc_multidim", loader)
    nc2asc_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nc2asc_module)
    return nc2asc_module.NetCDFConverter


class NC2ASCGUI(QMainWindow):
    """
    Main application window for nc2asc converter.

    Provides a complete GUI for:
    - Loading NetCDF files
    - Selecting variables (with multi-dimensional highlighting)
    - Configuring output format and options
    - Previewing output
    - Converting to various ASCII formats

    Layout:
    - Left panel: Input/output paths and variable table
    - Right panel: Output options
    - Bottom panel: Preview and variable details
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("nc2asc - NetCDF to ASCII Converter")
        self.setMinimumSize(1200, 850)

        # State
        self._converter = None
        self._config = self._load_default_config()
        self._netcdf_path: Optional[Path] = None
        self._output_dir: Optional[Path] = None
        self._settings = QSettings("NCAR-EOL", "nc2asc")

        self._setup_ui()
        self._setup_menu()
        self._connect_signals()
        self._load_settings()

    def _load_default_config(self) -> MergedConfiguration:
        """Load the default configuration file."""
        config_dir = Path(__file__).parent.parent.parent.parent / "config"
        default_config = config_dir / "example_config.yaml"

        if default_config.exists():
            try:
                config_manager = ConfigManager(config_path=default_config)
                return config_manager.load()
            except Exception as e:
                print(f"Warning: Could not load default config: {e}")

        return MergedConfiguration.default()

    def _setup_ui(self):
        """Set up the main window UI."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Main splitter (horizontal: left/right panels)
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter, 1)

        # Left panel (input/output + variable table)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)

        # Input file group
        input_group = QGroupBox("Input")
        input_layout = QHBoxLayout(input_group)
        self.input_path_edit = QLineEdit()
        self.input_path_edit.setReadOnly(True)
        self.input_path_edit.setPlaceholderText("Select a NetCDF file...")
        self.input_browse_btn = QPushButton("Browse...")
        self.input_browse_btn.clicked.connect(self._browse_input)
        input_layout.addWidget(self.input_path_edit, 1)
        input_layout.addWidget(self.input_browse_btn)
        left_layout.addWidget(input_group)

        # Output directory group
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)

        dir_layout = QHBoxLayout()
        dir_label = QLabel("Directory:")
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Same as input file")
        self.output_dir_browse_btn = QPushButton("Browse...")
        self.output_dir_browse_btn.clicked.connect(self._browse_output_dir)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.output_dir_edit, 1)
        dir_layout.addWidget(self.output_dir_browse_btn)
        output_layout.addLayout(dir_layout)

        name_layout = QHBoxLayout()
        name_label = QLabel("Filename:")
        self.output_name_edit = QLineEdit()
        self.output_name_edit.setPlaceholderText("Auto-generated from metadata")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.output_name_edit, 1)
        output_layout.addLayout(name_layout)

        left_layout.addWidget(output_group)

        # Variable table
        var_group = QGroupBox("Variables")
        var_layout = QVBoxLayout(var_group)
        self.variable_table = VariableTableWidget()
        var_layout.addWidget(self.variable_table)
        left_layout.addWidget(var_group, 1)

        main_splitter.addWidget(left_panel)

        # Right panel (options)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)

        options_group = QGroupBox("Conversion Options")
        options_layout = QVBoxLayout(options_group)
        self.options_panel = OutputOptionsPanel()
        options_layout.addWidget(self.options_panel)
        options_layout.addStretch()
        right_layout.addWidget(options_group, 1)

        # Config button
        self.config_btn = QPushButton("Edit Header Config...")
        self.config_btn.clicked.connect(self._edit_config)
        right_layout.addWidget(self.config_btn)

        # Convert button
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.setEnabled(False)
        self.convert_btn.setMinimumHeight(40)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0055aa;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.convert_btn.clicked.connect(self._convert)
        right_layout.addWidget(self.convert_btn)

        right_panel.setMinimumWidth(350)
        main_splitter.addWidget(right_panel)

        # Set splitter sizes (55% left, 45% right)
        main_splitter.setSizes([600, 500])

        # Bottom panel (preview + variable details)
        bottom_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(bottom_splitter)

        # Preview panel
        preview_group = QGroupBox("Output Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.preview_panel = PreviewPanel()
        preview_layout.addWidget(self.preview_panel)
        bottom_splitter.addWidget(preview_group)

        # Variable detail panel
        self.detail_panel = VariableDetailPanel()
        bottom_splitter.addWidget(self.detail_panel)

        bottom_splitter.setSizes([700, 300])

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _setup_menu(self):
        """Set up the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open NetCDF...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._browse_input)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        load_config_action = QAction("Load &Config...", self)
        load_config_action.setShortcut("Ctrl+Shift+O")
        load_config_action.triggered.connect(self._load_config)
        file_menu.addAction(load_config_action)

        save_config_action = QAction("&Save Config...", self)
        save_config_action.setShortcut("Ctrl+Shift+S")
        save_config_action.triggered.connect(self._save_config)
        file_menu.addAction(save_config_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        select_all_action = QAction("Select &All Variables", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.variable_table.select_all)
        edit_menu.addAction(select_all_action)

        clear_all_action = QAction("&Clear Selection", self)
        clear_all_action.triggered.connect(self.variable_table.clear_all)
        edit_menu.addAction(clear_all_action)

        invert_action = QAction("&Invert Selection", self)
        invert_action.triggered.connect(self.variable_table.invert_selection)
        edit_menu.addAction(invert_action)

        edit_menu.addSeparator()

        config_action = QAction("Edit Header &Config...", self)
        config_action.triggered.connect(self._edit_config)
        edit_menu.addAction(config_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _connect_signals(self):
        """Connect widget signals."""
        self.variable_table.selection_changed.connect(self._update_preview)
        self.variable_table.variable_selected.connect(self._show_variable_details)
        self.options_panel.options_changed.connect(self._update_preview)
        self.preview_panel.refresh_btn.clicked.connect(self._update_preview)

    def _load_settings(self):
        """Load saved settings."""
        geometry = self._settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        last_dir = self._settings.value("last_input_dir")
        if last_dir and Path(last_dir).exists():
            self._output_dir = Path(last_dir)

    def _save_settings(self):
        """Save settings before closing."""
        self._settings.setValue("geometry", self.saveGeometry())
        if self._netcdf_path:
            self._settings.setValue("last_input_dir", str(self._netcdf_path.parent))

    def closeEvent(self, event):
        """Handle window close."""
        self._save_settings()
        super().closeEvent(event)

    def _browse_input(self):
        """Browse for input NetCDF file."""
        if self._netcdf_path:
            start_dir = str(self._netcdf_path.parent)
        else:
            start_dir = os.environ.get('DATA_DIR', '')
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open NetCDF File",
            start_dir,
            "NetCDF Files (*.nc *.nc4 *.cdf);;All Files (*)"
        )

        if file_path:
            self.load_netcdf_file(file_path)

    def _browse_output_dir(self):
        """Browse for output directory."""
        start_dir = str(self._output_dir) if self._output_dir else ""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            start_dir
        )

        if dir_path:
            self._output_dir = Path(dir_path)
            self.output_dir_edit.setText(dir_path)

    def load_netcdf_file(self, file_path: str):
        """
        Load a NetCDF file.

        Args:
            file_path: Path to the NetCDF file
        """
        path = Path(file_path)
        if not path.exists():
            QMessageBox.critical(self, "Error", f"File not found: {file_path}")
            return

        self.status_bar.showMessage(f"Loading {path.name}...")
        QApplication.processEvents()

        try:
            # Import converter here to avoid circular imports
            NetCDFConverter = _get_netcdf_converter()

            self._converter = NetCDFConverter(str(path), self._config)
            if not self._converter.load_netcdf():
                QMessageBox.critical(self, "Error", "Failed to load NetCDF file")
                self.status_bar.showMessage("Load failed")
                return

            self._netcdf_path = path
            self.input_path_edit.setText(str(path))

            # Set default output directory
            if not self._output_dir:
                self._output_dir = path.parent

            # Update output filename
            self.output_name_edit.setText(self._converter.generate_output_filename())

            # Populate variable table
            self.variable_table.populate_from_dataset(self._converter.ds)

            # Set time range from file
            if self._converter.metadata.start_time and self._converter.metadata.end_time:
                self.options_panel.set_file_time_range(
                    self._converter.metadata.start_time,
                    self._converter.metadata.end_time
                )

            # Enable convert button
            self.convert_btn.setEnabled(True)

            # Update preview
            self._update_preview()

            # Update status
            var_cats = categorize_variables(self._converter.ds)
            n_1d = len(var_cats['1d'])
            n_2d = len(var_cats['2d'])
            n_3d = len(var_cats['3d'])
            self.status_bar.showMessage(
                f"Loaded {path.name}: {n_1d} 1D, {n_2d} 2D, {n_3d} 3D variables"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
            self.status_bar.showMessage("Load failed")
            import traceback
            traceback.print_exc()

    def _update_preview(self):
        """Update the output preview."""
        if self._converter is None:
            return

        try:
            # Update config with current options
            options = self.options_panel.get_conversion_options()
            options.variables = self.variable_table.get_selected_variables()

            self._config = MergedConfiguration(
                header=self._config.header,
                normal_comments=self._config.normal_comments,
                special_comments=self._config.special_comments,
                options=options,
                platform_mapping=self._config.platform_mapping
            )
            self._converter.config = self._config
            self._converter.options = options

            # Update output filename based on format
            self.output_name_edit.setText(self._converter.generate_output_filename())

            # Update preview panel
            self.preview_panel.update_preview(self._converter, self._config)

        except Exception as e:
            self.preview_panel.preview_text.setPlainText(f"Preview error: {str(e)}")
            import traceback
            traceback.print_exc()

    def _show_variable_details(self, var_name: str):
        """Show details for a selected variable."""
        if self._converter:
            self.detail_panel.show_variable(self._converter, var_name)

    def _edit_config(self):
        """Open the configuration editor dialog."""
        edited = ConfigEditorDialog.edit_config(self._config, self)
        if edited:
            self._config = edited
            self._update_preview()
            self.status_bar.showMessage("Configuration updated")

    def _load_config(self):
        """Load configuration from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Configuration",
            "",
            "Config Files (*.yaml *.yml *.json);;All Files (*)"
        )

        if not file_path:
            return

        try:
            config_manager = ConfigManager(config_path=Path(file_path))
            self._config = config_manager.load()
            self.options_panel.set_from_config(self._config)
            self._update_preview()
            self.status_bar.showMessage(f"Configuration loaded from {Path(file_path).name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load config:\n{str(e)}")

    def _save_config(self):
        """Save configuration to file."""
        # Update config with current UI state
        options = self.options_panel.get_conversion_options()
        options.variables = self.variable_table.get_selected_variables()
        self._config = MergedConfiguration(
            header=self._config.header,
            normal_comments=self._config.normal_comments,
            special_comments=self._config.special_comments,
            options=options,
            platform_mapping=self._config.platform_mapping
        )

        # Open editor to save
        dialog = ConfigEditorDialog(self._config, self)
        dialog._save_config_file()

    def _convert(self):
        """Perform the conversion."""
        if self._converter is None:
            QMessageBox.warning(self, "Warning", "No NetCDF file loaded")
            return

        selected_vars = self.variable_table.get_selected_variables()
        if not selected_vars:
            QMessageBox.warning(self, "Warning", "No variables selected")
            return

        # Determine output path
        output_dir = self._output_dir or self._netcdf_path.parent
        output_name = self.output_name_edit.text() or self._converter.generate_output_filename()
        output_path = output_dir / output_name

        # Confirm overwrite if file exists
        if output_path.exists():
            result = QMessageBox.question(
                self,
                "Confirm Overwrite",
                f"File {output_name} already exists.\nOverwrite?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if result != QMessageBox.Yes:
                return

        # Show progress
        progress = QProgressDialog("Converting...", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        QApplication.processEvents()

        try:
            # Update config with final options
            options = self.options_panel.get_conversion_options()
            options.variables = selected_vars

            self._config = MergedConfiguration(
                header=self._config.header,
                normal_comments=self._config.normal_comments,
                special_comments=self._config.special_comments,
                options=options,
                platform_mapping=self._config.platform_mapping
            )

            # Create fresh converter with updated config
            NetCDFConverter = _get_netcdf_converter()
            converter = NetCDFConverter(str(self._netcdf_path), self._config)

            # Convert
            result_path = converter.convert(str(output_path))

            progress.close()

            QMessageBox.information(
                self,
                "Success",
                f"File converted successfully:\n{result_path}"
            )
            self.status_bar.showMessage(f"Saved: {output_path.name}")

        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "Error", f"Conversion failed:\n{str(e)}")
            self.status_bar.showMessage("Conversion failed")
            import traceback
            traceback.print_exc()

    def _show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About nc2asc",
            """<h2>nc2asc - NetCDF to ASCII Converter</h2>
            <p>Version 2.0 (Multi-dimensional support)</p>
            <p>Converts NetCDF files to various ASCII formats:</p>
            <ul>
                <li>Plain ASCII (CSV or space-delimited)</li>
                <li>ICARTT FFI 1001 (1D time-series)</li>
                <li>ICARTT FFI 2110 (multi-dimensional)</li>
                <li>NASA AMES 1001</li>
            </ul>
            <p>Copyright University Corporation for Atmospheric Research (2021-2025)</p>
            <p>NCAR Earth Observing Laboratory</p>
            """
        )
