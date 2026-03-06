"""
Output Options Panel for nc2asc GUI.

Provides UI controls for configuring output format and conversion options.

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

from typing import Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QGridLayout,
    QComboBox, QRadioButton, QButtonGroup, QLineEdit, QLabel,
    QSpinBox, QDoubleSpinBox, QTimeEdit, QCheckBox
)
from PyQt5.QtCore import pyqtSignal, QTime

from ..config_manager import ConversionOptions, OutputFormat, MergedConfiguration


class OutputOptionsPanel(QWidget):
    """
    Panel widget for configuring output format and conversion options.

    Contains controls for:
    - Output format selection (Plain, ICARTT 1001, ICARTT 2110, AMES)
    - Date/time format options
    - Delimiter selection
    - Fill value and version string
    - High-rate data handling strategy
    - Time filtering and averaging

    Signals:
        options_changed: Emitted when any option is modified
    """

    options_changed = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Set up the panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        self.setMinimumWidth(320)

        # Output Format Group
        format_group = QGroupBox("Output Format")
        format_layout = QFormLayout(format_group)
        format_layout.setSpacing(10)
        format_layout.setContentsMargins(10, 15, 10, 10)

        self.format_combo = QComboBox()
        self.format_combo.addItem("Plain ASCII", "plain")
        self.format_combo.addItem("ICARTT FFI 1001", "icartt")
        self.format_combo.addItem("ICARTT FFI 2110", "icartt2110")
        self.format_combo.addItem("NASA AMES 1001", "ames")
        self.format_combo.setMinimumHeight(25)
        format_layout.addRow("Format:", self.format_combo)

        layout.addWidget(format_group)

        # Date/Time & Filtering Group (combined with two columns)
        datetime_group = QGroupBox("Date/Time Format & Filtering")
        datetime_grid = QGridLayout(datetime_group)
        datetime_grid.setSpacing(10)
        datetime_grid.setContentsMargins(10, 15, 10, 10)

        # Left column: Date/Time Format
        datetime_grid.addWidget(QLabel("Date:"), 0, 0)
        self.date_combo = QComboBox()
        self.date_combo.addItem("No Date", "NoDate")
        self.date_combo.addItem("yyyy-mm-dd", "yyyy-mm-dd")
        self.date_combo.addItem("yyyy mm dd", "yyyy mm dd")
        self.date_combo.setMinimumHeight(25)
        datetime_grid.addWidget(self.date_combo, 0, 1)

        datetime_grid.addWidget(QLabel("Time:"), 1, 0)
        self.time_combo = QComboBox()
        self.time_combo.addItem("Seconds of Day", "SecOfDay")
        self.time_combo.addItem("hh:mm:ss", "hh:mm:ss")
        self.time_combo.addItem("hh mm ss", "hh mm ss")
        self.time_combo.setMinimumHeight(25)
        datetime_grid.addWidget(self.time_combo, 1, 1)

        datetime_grid.addWidget(QLabel("Averaging:"), 2, 0)
        self.averaging_spin = QSpinBox()
        self.averaging_spin.setRange(0, 3600)
        self.averaging_spin.setValue(0)
        self.averaging_spin.setSuffix(" sec")
        self.averaging_spin.setSpecialValueText("None")
        self.averaging_spin.setMinimumHeight(25)
        datetime_grid.addWidget(self.averaging_spin, 2, 1)

        # Right column: Time Filtering
        self.start_time_check = QCheckBox("Start:")
        self.start_time_check.setChecked(False)
        datetime_grid.addWidget(self.start_time_check, 0, 2)
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm:ss")
        self.start_time_edit.setMinimumHeight(25)
        self.start_time_edit.setEnabled(False)
        datetime_grid.addWidget(self.start_time_edit, 0, 3)
        self.start_time_check.toggled.connect(self.start_time_edit.setEnabled)

        self.end_time_check = QCheckBox("End:")
        self.end_time_check.setChecked(False)
        datetime_grid.addWidget(self.end_time_check, 1, 2)
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("HH:mm:ss")
        self.end_time_edit.setMinimumHeight(25)
        self.end_time_edit.setEnabled(False)
        datetime_grid.addWidget(self.end_time_edit, 1, 3)
        self.end_time_check.toggled.connect(self.end_time_edit.setEnabled)

        # Keep button groups for compatibility but don't display them
        self.date_group = QButtonGroup(self)
        self.time_group = QButtonGroup(self)

        layout.addWidget(datetime_group)

        # Delimiter Group
        delimiter_group = QGroupBox("Delimiter")
        delimiter_layout = QHBoxLayout(delimiter_group)
        delimiter_layout.setContentsMargins(10, 15, 10, 10)
        self.delimiter_group = QButtonGroup(self)
        self.delimiter_comma = QRadioButton("Comma")
        self.delimiter_comma.setChecked(True)
        self.delimiter_space = QRadioButton("Space")
        self.delimiter_group.addButton(self.delimiter_comma, 0)
        self.delimiter_group.addButton(self.delimiter_space, 1)
        delimiter_layout.addWidget(self.delimiter_comma)
        delimiter_layout.addWidget(self.delimiter_space)
        delimiter_layout.addStretch()
        layout.addWidget(delimiter_group)

        # Data Options Group
        data_group = QGroupBox("Data Options")
        data_layout = QFormLayout(data_group)
        data_layout.setSpacing(10)
        data_layout.setContentsMargins(10, 15, 10, 10)

        # Fill value
        self.fill_value_edit = QLineEdit("-99999.0")
        self.fill_value_edit.setMinimumHeight(25)
        data_layout.addRow("Fill Value:", self.fill_value_edit)

        # Version
        self.version_edit = QLineEdit("RA")
        self.version_edit.setMinimumHeight(25)
        data_layout.addRow("Version:", self.version_edit)

        # High-rate strategy
        self.high_rate_combo = QComboBox()
        self.high_rate_combo.addItem("First sample", "first")
        self.high_rate_combo.addItem("Average", "average")
        self.high_rate_combo.addItem("Expand", "expand")
        self.high_rate_combo.setMinimumHeight(25)
        data_layout.addRow("High-Rate:", self.high_rate_combo)

        layout.addWidget(data_group)

        # Add stretch to push everything to the top
        layout.addStretch()

    def _connect_signals(self):
        """Connect widget signals to options_changed."""
        self.format_combo.currentIndexChanged.connect(self._emit_options_changed)
        self.date_combo.currentIndexChanged.connect(self._emit_options_changed)
        self.time_combo.currentIndexChanged.connect(self._emit_options_changed)
        self.delimiter_group.buttonClicked.connect(self._emit_options_changed)
        self.fill_value_edit.textChanged.connect(self._emit_options_changed)
        self.version_edit.textChanged.connect(self._emit_options_changed)
        self.high_rate_combo.currentIndexChanged.connect(self._emit_options_changed)
        self.start_time_check.toggled.connect(self._emit_options_changed)
        self.end_time_check.toggled.connect(self._emit_options_changed)
        self.start_time_edit.timeChanged.connect(self._emit_options_changed)
        self.end_time_edit.timeChanged.connect(self._emit_options_changed)
        self.averaging_spin.valueChanged.connect(self._emit_options_changed)

    def _emit_options_changed(self):
        """Emit options_changed signal."""
        self.options_changed.emit()

    def get_conversion_options(self) -> ConversionOptions:
        """
        Get current options as a ConversionOptions object.

        Returns:
            ConversionOptions with current UI settings
        """
        # Output format
        format_str = self.format_combo.currentData()
        format_map = {
            'plain': OutputFormat.PLAIN,
            'icartt': OutputFormat.ICARTT_1001,
            'icartt2110': OutputFormat.ICARTT_2110,
            'ames': OutputFormat.AMES_1001,
        }
        output_format = format_map.get(format_str, OutputFormat.ICARTT_1001)

        # Date format
        date_format = self.date_combo.currentData() or 'NoDate'

        # Time format
        time_format = self.time_combo.currentData() or 'SecOfDay'

        # Delimiter
        delimiter = 'comma' if self.delimiter_comma.isChecked() else 'space'

        # Fill value
        try:
            fill_value = float(self.fill_value_edit.text())
        except ValueError:
            fill_value = -99999.0

        # Version
        version = self.version_edit.text() or 'RA'

        # High-rate strategy
        high_rate_strategy = self.high_rate_combo.currentData() or 'first'

        # Time filtering - convert QTime to seconds of day
        start_time = None
        end_time = None
        if self.start_time_check.isChecked():
            t = self.start_time_edit.time()
            start_time = t.hour() * 3600 + t.minute() * 60 + t.second()
        if self.end_time_check.isChecked():
            t = self.end_time_edit.time()
            end_time = t.hour() * 3600 + t.minute() * 60 + t.second()

        # Averaging
        averaging = self.averaging_spin.value()
        if averaging == 0:
            averaging = None

        return ConversionOptions(
            output_format=output_format,
            date_format=date_format,
            time_format=time_format,
            delimiter=delimiter,
            fill_value=fill_value,
            version=version,
            high_rate_strategy=high_rate_strategy,
            start_time=start_time,
            end_time=end_time,
            averaging=averaging,
            variables=[]  # Variables are set separately from the table
        )

    def set_from_config(self, config: MergedConfiguration):
        """
        Set UI values from a configuration.

        Args:
            config: MergedConfiguration to load settings from
        """
        options = config.options

        # Block signals during update
        self.blockSignals(True)

        # Output format
        format_map = {
            OutputFormat.PLAIN: 0,
            OutputFormat.ICARTT_1001: 1,
            OutputFormat.ICARTT_2110: 2,
            OutputFormat.AMES_1001: 3,
        }
        self.format_combo.setCurrentIndex(format_map.get(options.output_format, 1))

        # Date format
        date_index = self.date_combo.findData(options.date_format)
        if date_index >= 0:
            self.date_combo.setCurrentIndex(date_index)

        # Time format
        time_index = self.time_combo.findData(options.time_format)
        if time_index >= 0:
            self.time_combo.setCurrentIndex(time_index)

        # Delimiter
        if options.delimiter == 'space':
            self.delimiter_space.setChecked(True)
        else:
            self.delimiter_comma.setChecked(True)

        # Fill value
        self.fill_value_edit.setText(str(options.fill_value))

        # Version
        self.version_edit.setText(options.version)

        # High-rate strategy
        strategy_map = {'first': 0, 'average': 1, 'expand': 2}
        self.high_rate_combo.setCurrentIndex(strategy_map.get(options.high_rate_strategy, 0))

        # Time filtering - convert seconds of day to QTime
        if options.start_time is not None:
            self.start_time_check.setChecked(True)
            secs = int(options.start_time)
            self.start_time_edit.setTime(QTime(secs // 3600, (secs % 3600) // 60, secs % 60))
        else:
            self.start_time_check.setChecked(False)

        if options.end_time is not None:
            self.end_time_check.setChecked(True)
            secs = int(options.end_time)
            self.end_time_edit.setTime(QTime(secs // 3600, (secs % 3600) // 60, secs % 60))
        else:
            self.end_time_check.setChecked(False)

        # Averaging
        self.averaging_spin.setValue(options.averaging or 0)

        self.blockSignals(False)

    def get_output_format(self) -> OutputFormat:
        """Get the currently selected output format."""
        format_str = self.format_combo.currentData()
        format_map = {
            'plain': OutputFormat.PLAIN,
            'icartt': OutputFormat.ICARTT_1001,
            'icartt2110': OutputFormat.ICARTT_2110,
            'ames': OutputFormat.AMES_1001,
        }
        return format_map.get(format_str, OutputFormat.ICARTT_1001)

    def set_output_format(self, fmt: OutputFormat):
        """Set the output format."""
        format_map = {
            OutputFormat.PLAIN: 0,
            OutputFormat.ICARTT_1001: 1,
            OutputFormat.ICARTT_2110: 2,
            OutputFormat.AMES_1001: 3,
        }
        self.format_combo.setCurrentIndex(format_map.get(fmt, 1))

    def set_file_time_range(self, start_time_str: str, end_time_str: str):
        """
        Set the time edit widgets from file start/end time strings.

        Args:
            start_time_str: Start time in format like "2025-07-22 12:34:56"
            end_time_str: End time in format like "2025-07-22 23:45:00"
        """
        try:
            # Extract time portion (after space) and parse
            if ' ' in start_time_str:
                time_part = start_time_str.split(' ')[1]
                # Handle fractional seconds
                if '.' in time_part:
                    time_part = time_part.split('.')[0]
                parts = time_part.split(':')
                if len(parts) >= 3:
                    self.start_time_edit.setTime(QTime(int(parts[0]), int(parts[1]), int(parts[2])))
        except (ValueError, IndexError):
            pass

        try:
            if ' ' in end_time_str:
                time_part = end_time_str.split(' ')[1]
                if '.' in time_part:
                    time_part = time_part.split('.')[0]
                parts = time_part.split(':')
                if len(parts) >= 3:
                    self.end_time_edit.setTime(QTime(int(parts[0]), int(parts[1]), int(parts[2])))
        except (ValueError, IndexError):
            pass
