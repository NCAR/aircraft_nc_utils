"""
Variable Table Widget for nc2asc GUI.

Provides a table view for selecting variables from NetCDF files,
with support for highlighting multi-dimensional variables.

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

from typing import List, Optional, Set

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush, QFont

import xarray as xr


class VariableTableWidget(QWidget):
    """
    Table widget for displaying and selecting NetCDF variables.

    Features:
    - Checkbox selection for each variable
    - Multi-dimensional variables highlighted with different color
    - Search/filter functionality
    - Select All / Clear All / Invert Selection buttons

    Signals:
        selection_changed: Emitted when variable selection changes
        variable_selected: Emitted with variable name when a row is clicked
    """

    selection_changed = pyqtSignal()
    variable_selected = pyqtSignal(str)

    # Column indices
    COL_CHECKBOX = 0
    COL_VARIABLE = 1
    COL_DIMS = 2
    COL_UNITS = 3
    COL_LONG_NAME = 4

    # Colors for highlighting
    COLOR_1D = QColor(255, 255, 255)  # White for 1D variables
    COLOR_2D = QColor(230, 242, 255)  # Light blue for 2D variables
    COLOR_3D = QColor(255, 242, 230)  # Light orange for 3D variables

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()
        self._all_variables: List[dict] = []
        self._filtered_indices: List[int] = []

    def _setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Search/filter bar
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter:")
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Search variables...")
        self.filter_edit.textChanged.connect(self._apply_filter)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_edit)
        layout.addLayout(filter_layout)

        # Variable table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "", "Variable", "Dimensions", "Units", "Long Name"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(
            self.COL_CHECKBOX, QHeaderView.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            self.COL_VARIABLE, QHeaderView.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            self.COL_DIMS, QHeaderView.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            self.COL_UNITS, QHeaderView.ResizeToContents
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.cellClicked.connect(self._on_cell_clicked)
        self.table.cellChanged.connect(self._on_cell_changed)
        self.table.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.table)

        # Selection buttons
        button_layout = QHBoxLayout()
        self.select_1d_btn = QPushButton("Select 1D")
        self.select_1d_btn.clicked.connect(self.select_1d_only)
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all)
        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.clicked.connect(self.clear_all)
        self.invert_btn = QPushButton("Invert Selection")
        self.invert_btn.clicked.connect(self.invert_selection)

        button_layout.addWidget(self.select_1d_btn)
        button_layout.addWidget(self.select_all_btn)
        button_layout.addWidget(self.clear_all_btn)
        button_layout.addWidget(self.invert_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Variable count label
        self.count_label = QLabel("No variables loaded")
        layout.addWidget(self.count_label)

    def populate_from_dataset(self, ds: xr.Dataset):
        """
        Populate the table from an xarray Dataset.

        Args:
            ds: xarray Dataset containing variables to display
        """
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        self._all_variables = []

        for var_name in ds.variables:
            if var_name == 'Time':
                continue

            var = ds[var_name]
            dims = var.dims
            units = var.attrs.get('units', '')
            long_name = var.attrs.get('long_name', '')

            # Determine dimensionality
            if dims == ('Time',):
                dim_type = '1d'
                dims_str = 'Time'
            elif len(dims) == 2 and 'Time' in dims:
                dim_type = '2d'
                other_dim = [d for d in dims if d != 'Time'][0]
                bin_count = var.shape[dims.index(other_dim)]
                dims_str = f"Time x {bin_count}"
            elif len(dims) == 3 and 'Time' in dims:
                dim_type = '3d'
                other_dims = [d for d in dims if d != 'Time']
                sizes = [var.shape[dims.index(d)] for d in other_dims]
                dims_str = f"Time x {sizes[0]} x {sizes[1]}"
            else:
                dim_type = 'other'
                dims_str = ' x '.join(dims)

            self._all_variables.append({
                'name': var_name,
                'dims': dims_str,
                'dim_type': dim_type,
                'units': units,
                'long_name': long_name,
            })

        # Sort variables: 1D first, then 2D, then 3D, alphabetically within each
        self._all_variables.sort(key=lambda v: (
            {'1d': 0, '2d': 1, '3d': 2, 'other': 3}.get(v['dim_type'], 4),
            v['name'].lower()
        ))

        self._filtered_indices = list(range(len(self._all_variables)))
        self._populate_table()
        self.table.blockSignals(False)
        self._update_count_label()

    def _populate_table(self):
        """Populate table rows from filtered variables."""
        self.table.blockSignals(True)
        self.table.setRowCount(len(self._filtered_indices))

        for row, idx in enumerate(self._filtered_indices):
            var = self._all_variables[idx]
            self._add_row(row, var)

        self.table.blockSignals(False)

    def _add_row(self, row: int, var: dict):
        """Add a single row to the table."""
        # Checkbox - default to checked for 1D variables only
        checkbox_item = QTableWidgetItem()
        checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        default_state = Qt.Checked if var['dim_type'] == '1d' else Qt.Unchecked
        checkbox_item.setCheckState(default_state)
        self.table.setItem(row, self.COL_CHECKBOX, checkbox_item)

        # Variable name
        name_item = QTableWidgetItem(var['name'])
        name_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        if var['dim_type'] in ('2d', '3d'):
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)
        self.table.setItem(row, self.COL_VARIABLE, name_item)

        # Dimensions
        dims_item = QTableWidgetItem(var['dims'])
        dims_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.table.setItem(row, self.COL_DIMS, dims_item)

        # Units
        units_item = QTableWidgetItem(var['units'])
        units_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.table.setItem(row, self.COL_UNITS, units_item)

        # Long name
        long_name_item = QTableWidgetItem(var['long_name'])
        long_name_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.table.setItem(row, self.COL_LONG_NAME, long_name_item)

        # Set row background color based on dimensionality
        if var['dim_type'] == '2d':
            bg_color = self.COLOR_2D
        elif var['dim_type'] == '3d':
            bg_color = self.COLOR_3D
        else:
            bg_color = self.COLOR_1D

        # Set colors for all cells in the row (skip checkbox column for foreground)
        text_color = QColor(0, 0, 0)  # Black text for readability
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item:
                item.setBackground(QBrush(bg_color))
                # Don't set foreground on checkbox column - it affects checkbox visibility
                if col != self.COL_CHECKBOX:
                    item.setForeground(QBrush(text_color))

    def _apply_filter(self, text: str):
        """Filter visible variables based on search text."""
        text = text.lower().strip()
        if not text:
            self._filtered_indices = list(range(len(self._all_variables)))
        else:
            self._filtered_indices = [
                i for i, var in enumerate(self._all_variables)
                if text in var['name'].lower() or
                   text in var['long_name'].lower() or
                   text in var['units'].lower()
            ]

        self._populate_table()
        self._update_count_label()

    def _on_cell_clicked(self, row: int, column: int):
        """Handle cell click events."""
        # Emit variable selected signal for non-checkbox columns
        if column != self.COL_CHECKBOX:
            name_item = self.table.item(row, self.COL_VARIABLE)
            if name_item:
                self.variable_selected.emit(name_item.text())

    def _on_cell_changed(self, row: int, column: int):
        """Handle cell change events (checkbox toggling)."""
        if column == self.COL_CHECKBOX:
            self.selection_changed.emit()
            self._update_count_label()

    def _on_item_clicked(self, item):
        """Handle item click events (for checkbox clicks)."""
        if item.column() == self.COL_CHECKBOX:
            # The checkbox state has already been toggled by Qt
            self.selection_changed.emit()
            self._update_count_label()

    def _update_count_label(self):
        """Update the variable count label."""
        total = len(self._all_variables)
        visible = len(self._filtered_indices)
        selected = len(self.get_selected_variables())

        if total == 0:
            self.count_label.setText("No variables loaded")
        elif visible == total:
            self.count_label.setText(f"{selected} of {total} variables selected")
        else:
            self.count_label.setText(
                f"{selected} selected, showing {visible} of {total} variables"
            )

    def get_selected_variables(self) -> List[str]:
        """
        Get list of selected variable names.

        Returns:
            List of variable names that are checked
        """
        selected = []
        for row in range(self.table.rowCount()):
            checkbox = self.table.item(row, self.COL_CHECKBOX)
            name_item = self.table.item(row, self.COL_VARIABLE)
            if checkbox and name_item and checkbox.checkState() == Qt.Checked:
                selected.append(name_item.text())
        return selected

    def set_selected_variables(self, variables: List[str]):
        """
        Set which variables are selected.

        Args:
            variables: List of variable names to select
        """
        var_set = set(variables)
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            checkbox = self.table.item(row, self.COL_CHECKBOX)
            name_item = self.table.item(row, self.COL_VARIABLE)
            if checkbox and name_item:
                state = Qt.Checked if name_item.text() in var_set else Qt.Unchecked
                checkbox.setCheckState(state)
        self.table.blockSignals(False)
        self.selection_changed.emit()
        self._update_count_label()

    def select_all(self):
        """Select all visible variables."""
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            item = self.table.item(row, self.COL_CHECKBOX)
            if item:
                item.setCheckState(Qt.Checked)
        self.table.blockSignals(False)
        self.selection_changed.emit()
        self._update_count_label()

    def select_1d_only(self):
        """Select only 1D variables, deselect all others."""
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            idx = self._filtered_indices[row]
            var = self._all_variables[idx]
            item = self.table.item(row, self.COL_CHECKBOX)
            if item:
                if var['dim_type'] == '1d':
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
        self.table.blockSignals(False)
        self.selection_changed.emit()
        self._update_count_label()

    def clear_all(self):
        """Deselect all visible variables."""
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            item = self.table.item(row, self.COL_CHECKBOX)
            if item:
                item.setCheckState(Qt.Unchecked)
        self.table.blockSignals(False)
        self.selection_changed.emit()
        self._update_count_label()

    def invert_selection(self):
        """Invert selection of all visible variables."""
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            item = self.table.item(row, self.COL_CHECKBOX)
            if item:
                new_state = Qt.Unchecked if item.checkState() == Qt.Checked else Qt.Checked
                item.setCheckState(new_state)
        self.table.blockSignals(False)
        self.selection_changed.emit()
        self._update_count_label()

    def get_variable_info(self, var_name: str) -> Optional[dict]:
        """
        Get information about a specific variable.

        Args:
            var_name: Name of the variable

        Returns:
            Dictionary with variable info or None if not found
        """
        for var in self._all_variables:
            if var['name'] == var_name:
                return var
        return None

    def highlight_multidim_vars(self):
        """Refresh highlighting for multi-dimensional variables."""
        # This is called automatically during populate, but can be called
        # manually if needed to refresh the display
        for row in range(self.table.rowCount()):
            idx = self._filtered_indices[row] if row < len(self._filtered_indices) else row
            if idx < len(self._all_variables):
                var = self._all_variables[idx]
                if var['dim_type'] == '2d':
                    bg_color = self.COLOR_2D
                elif var['dim_type'] == '3d':
                    bg_color = self.COLOR_3D
                else:
                    bg_color = self.COLOR_1D

                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QBrush(bg_color))
