"""
Preview Panel for nc2asc GUI.

Provides a live preview of the conversion output including header and data rows.

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

from typing import Optional, TYPE_CHECKING
import io

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
    QSpinBox, QPushButton, QGroupBox
)
from PyQt5.QtGui import QFont, QTextOption
from PyQt5.QtCore import Qt

if TYPE_CHECKING:
    from ..config_manager import MergedConfiguration


class PreviewPanel(QWidget):
    """
    Panel widget for previewing conversion output.

    Shows the header and first N data lines that would be written
    to the output file with current settings.

    Features:
    - Monospace font for proper alignment
    - Configurable number of preview lines
    - Refresh button for manual updates
    - Scrollable text area
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()
        self._preview_lines = 5

    def _setup_ui(self):
        """Set up the panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header with controls
        header_layout = QHBoxLayout()
        header_label = QLabel("Output Preview")
        header_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(header_label)

        # Number of data lines to show
        lines_label = QLabel("Data lines:")
        self.lines_spin = QSpinBox()
        self.lines_spin.setRange(1, 50)
        self.lines_spin.setValue(5)
        self.lines_spin.valueChanged.connect(self._on_lines_changed)
        header_layout.addWidget(lines_label)
        header_layout.addWidget(self.lines_spin)

        header_layout.addStretch()

        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setEnabled(False)
        header_layout.addWidget(self.refresh_btn)

        layout.addLayout(header_layout)

        # Preview text area
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Courier New", 10))
        self.preview_text.setWordWrapMode(QTextOption.NoWrap)
        self.preview_text.setMinimumHeight(150)
        self.preview_text.setPlaceholderText(
            "Load a NetCDF file and select variables to see output preview..."
        )
        layout.addWidget(self.preview_text)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.status_label)

    def _on_lines_changed(self, value: int):
        """Handle change in number of preview lines."""
        self._preview_lines = value

    def clear(self):
        """Clear the preview."""
        self.preview_text.clear()
        self.status_label.setText("")
        self.refresh_btn.setEnabled(False)

    def set_preview_text(self, text: str, header_lines: int = 0):
        """
        Set the preview text directly.

        Args:
            text: The text content to display
            header_lines: Number of header lines (for status display)
        """
        self.preview_text.setPlainText(text)
        if header_lines > 0:
            total_lines = text.count('\n') + 1
            data_lines = total_lines - header_lines
            self.status_label.setText(
                f"Showing {header_lines} header lines + {data_lines} data lines"
            )
        self.refresh_btn.setEnabled(True)

    def update_preview(self, converter, config: 'MergedConfiguration', num_lines: Optional[int] = None):
        """
        Update preview from a converter instance.

        Args:
            converter: NetCDFConverter instance with loaded data
            config: MergedConfiguration with current settings
            num_lines: Number of data lines to show (default: use spin box value)
        """
        if num_lines is None:
            num_lines = self.lines_spin.value()

        try:
            preview_text, header_count = self._generate_preview(converter, config, num_lines)
            self.set_preview_text(preview_text, header_count)
        except Exception as e:
            self.preview_text.setPlainText(f"Error generating preview:\n{str(e)}")
            self.status_label.setText("Preview error")

    def _generate_preview(self, converter, config: 'MergedConfiguration', num_lines: int) -> tuple:
        """
        Generate preview text from converter.

        Args:
            converter: NetCDFConverter instance
            config: Current configuration
            num_lines: Number of data lines to include

        Returns:
            Tuple of (preview_text, header_line_count)
        """
        from ..formatters import FormatterFactory, OutputFormat as FmtOutputFormat

        # Create formatter
        formatter = FormatterFactory.create(
            FmtOutputFormat(config.options.output_format.value),
            converter,
            config
        )

        # Build header
        header_lines = formatter.build_header()
        header_text = '\n'.join(header_lines)
        header_count = len(header_lines)

        # Build sample data lines
        data_text = self._build_data_preview(formatter, converter, config, num_lines)

        preview = header_text + '\n' + data_text
        return preview, header_count

    def _build_data_preview(self, formatter, converter, config: 'MergedConfiguration',
                            num_lines: int) -> str:
        """
        Build preview of data rows.

        Args:
            formatter: OutputFormatter instance
            converter: NetCDFConverter instance
            config: Current configuration
            num_lines: Number of lines to generate

        Returns:
            String with data rows
        """
        import pandas as pd
        import numpy as np

        # Get all time data first (we'll filter later)
        time_data = converter.time_data if converter.time_data is not None else []

        # Build data dict with all data
        data = {'Time_Start': time_data}

        # Add raw date/time for filtering
        if converter.date_series is not None:
            data['_raw_date'] = converter.date_series.values
        if converter.time_series is not None:
            data['_raw_time'] = converter.time_series.values

        # Add 1D variables
        selected_vars = config.options.variables or []
        for var_name in selected_vars:
            if var_name in converter.data_1d:
                data[var_name] = converter.data_1d[var_name]
            elif var_name in converter.data_multidim:
                # For multi-dim, show first bin only in preview
                var_data = converter.data_multidim[var_name]
                if var_data.ndim >= 2:
                    data[f"{var_name}_0"] = var_data[:, 0]

        if not data or len(data) <= 1:
            return "(No data to preview - select variables)"

        # Create DataFrame
        df = pd.DataFrame(data)

        # Apply time filtering
        if config.options.start_time is not None:
            df = df[df['Time_Start'] >= config.options.start_time]
        if config.options.end_time is not None:
            df = df[df['Time_Start'] <= config.options.end_time]

        # Limit to num_lines after filtering
        df = df.head(num_lines).reset_index(drop=True)

        # Process date/time columns
        prepend_cols = {}

        if config.options.time_format != "SecOfDay" and '_raw_time' in df.columns:
            time_col = df['_raw_time'].copy()
            if config.options.time_format == 'hh mm ss':
                time_col = time_col.str.replace(':', ' ')
            prepend_cols['Time'] = time_col.values
            df = df.drop(columns=['_raw_time'])
        elif '_raw_time' in df.columns:
            df = df.drop(columns=['_raw_time'])

        if config.options.date_format != "NoDate" and '_raw_date' in df.columns:
            date_col = df['_raw_date'].copy()
            if config.options.date_format == 'yyyy mm dd':
                date_col = date_col.str.replace('-', ' ')
            prepend_cols['Date'] = date_col.values
            df = df.drop(columns=['_raw_date'])
        elif '_raw_date' in df.columns:
            df = df.drop(columns=['_raw_date'])

        # Prepend date/time columns using concat to avoid fragmentation
        if prepend_cols:
            prepend_df = pd.DataFrame(prepend_cols, index=df.index)
            df = pd.concat([prepend_df, df], axis=1)

        # Apply fill values
        fill_val = config.options.fill_value
        for col in df.columns:
            if df[col].dtype in [np.float64, np.float32]:
                df[col] = df[col].where(np.isfinite(df[col]), fill_val)
        df = df.fillna(fill_val)

        # Format rows
        rows = []
        for _, row in df.iterrows():
            formatted = formatter.format_data_row(row)
            rows.append(formatted)

        return '\n'.join(rows)

    def show_variable_details(self, converter, var_name: str):
        """
        Show details about a specific variable.

        Args:
            converter: NetCDFConverter instance
            var_name: Name of the variable to show details for
        """
        if converter is None or converter.ds is None:
            return

        if var_name not in converter.ds:
            return

        var = converter.ds[var_name]
        details = []
        details.append(f"Variable: {var_name}")
        details.append(f"Shape: {var.shape}")
        details.append(f"Dimensions: {var.dims}")
        details.append(f"dtype: {var.dtype}")

        # Attributes
        if var.attrs:
            details.append("\nAttributes:")
            for key, value in var.attrs.items():
                if key == 'CellSizes':
                    # Truncate long cell sizes
                    if hasattr(value, '__len__') and len(value) > 5:
                        value = f"[{value[0]:.4g}, {value[1]:.4g}, ..., {value[-1]:.4g}] ({len(value)} values)"
                details.append(f"  {key}: {value}")

        # Sample data
        details.append("\nSample values (first 5):")
        if var.dims == ('Time',):
            sample = var.values[:5]
            details.append(f"  {sample}")
        elif len(var.dims) == 2 and 'Time' in var.dims:
            details.append(f"  First time step: {var.values[0, :5]}...")
        elif len(var.dims) == 3 and 'Time' in var.dims:
            details.append(f"  First time/sample: {var.values[0, 0, :5]}...")

        self.preview_text.setPlainText('\n'.join(details))
        self.status_label.setText(f"Showing details for {var_name}")


class VariableDetailPanel(QWidget):
    """
    Separate panel for showing variable details.

    Used when a variable is selected in the table to show its metadata
    and sample values.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Group box
        group = QGroupBox("Variable Details")
        group_layout = QVBoxLayout(group)

        # Detail text
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setFont(QFont("Courier New", 9))
        self.detail_text.setMaximumHeight(100)
        self.detail_text.setPlaceholderText("Click a variable to see details...")
        group_layout.addWidget(self.detail_text)

        layout.addWidget(group)

    def show_variable(self, converter, var_name: str):
        """
        Show details about a variable.

        Args:
            converter: NetCDFConverter instance
            var_name: Name of the variable
        """
        if converter is None or converter.ds is None:
            self.detail_text.setPlainText("No data loaded")
            return

        if var_name not in converter.ds:
            self.detail_text.setPlainText(f"Variable {var_name} not found")
            return

        var = converter.ds[var_name]
        lines = []
        lines.append(f"Shape: {var.shape} | Dims: {var.dims}")

        units = var.attrs.get('units', 'N/A')
        long_name = var.attrs.get('long_name', 'N/A')
        lines.append(f"Units: {units}")
        lines.append(f"Description: {long_name}")

        if 'CellSizes' in var.attrs:
            sizes = var.attrs['CellSizes']
            n_bins = len(sizes) if hasattr(sizes, '__len__') else 1
            lines.append(f"Cell Sizes: {n_bins} bins defined")

        self.detail_text.setPlainText('\n'.join(lines))

    def clear(self):
        """Clear the detail display."""
        self.detail_text.clear()
