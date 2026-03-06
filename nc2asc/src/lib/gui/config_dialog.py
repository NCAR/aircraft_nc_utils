"""
Configuration Editor Dialog for nc2asc GUI.

Provides dialogs for editing header metadata, normal comments,
and managing configuration files.

Copyright University Corporation for Atmospheric Research (2021-2025)
"""

from pathlib import Path
from typing import Optional
import json

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QLineEdit, QTextEdit, QLabel, QPushButton,
    QDialogButtonBox, QFileDialog, QMessageBox, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
)
from PyQt5.QtCore import Qt

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from ..config_manager import (
    HeaderConfig, NormalComments, MergedConfiguration, PlatformMapping
)


class ConfigEditorDialog(QDialog):
    """
    Dialog for editing configuration including header metadata and comments.

    Features:
    - Tab-based interface for different config sections
    - Header metadata (PI name, organization, etc.)
    - Normal comments (16 ICARTT fields)
    - Platform mapping editor
    - Load/save YAML or JSON configs
    """

    def __init__(self, config: Optional[MergedConfiguration] = None,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Editor")
        self.setMinimumSize(600, 500)

        self._config = config or MergedConfiguration.default()
        self._setup_ui()
        self._load_config_to_ui()

    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Header tab
        self.header_tab = self._create_header_tab()
        self.tabs.addTab(self.header_tab, "Header")

        # Normal Comments tab
        self.comments_tab = self._create_comments_tab()
        self.tabs.addTab(self.comments_tab, "Normal Comments")

        # Platform Mapping tab
        self.platform_tab = self._create_platform_tab()
        self.tabs.addTab(self.platform_tab, "Platform Mapping")

        # Load/Save buttons
        file_layout = QHBoxLayout()
        self.load_btn = QPushButton("Load Config...")
        self.load_btn.clicked.connect(self._load_config_file)
        self.save_btn = QPushButton("Save Config...")
        self.save_btn.clicked.connect(self._save_config_file)
        file_layout.addWidget(self.load_btn)
        file_layout.addWidget(self.save_btn)
        file_layout.addStretch()
        layout.addLayout(file_layout)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _create_header_tab(self) -> QWidget:
        """Create the header metadata editing tab."""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # PI Name
        self.pi_name_edit = QLineEdit()
        layout.addRow("PI Name:", self.pi_name_edit)

        # PI Organization
        self.pi_org_edit = QLineEdit()
        layout.addRow("PI Organization:", self.pi_org_edit)

        # Data source description
        self.datasource_edit = QLineEdit()
        layout.addRow("Data Source:", self.datasource_edit)

        # Data interval
        self.interval_edit = QLineEdit()
        self.interval_edit.setMaximumWidth(100)
        layout.addRow("Data Interval (s):", self.interval_edit)

        # Missing value
        self.missing_edit = QLineEdit()
        self.missing_edit.setMaximumWidth(100)
        layout.addRow("Missing Value:", self.missing_edit)

        return widget

    def _create_comments_tab(self) -> QWidget:
        """Create the normal comments editing tab."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # All 16 ICARTT normal comment fields
        self.comment_edits = {}

        fields = [
            ('pi_contact_info', 'PI Contact Info'),
            ('platform', 'Platform'),
            ('location', 'Location'),
            ('associated_data', 'Associated Data'),
            ('instrument_info', 'Instrument Info'),
            ('data_info', 'Data Info'),
            ('uncertainty', 'Uncertainty'),
            ('ulod_flag', 'ULOD Flag'),
            ('ulod_value', 'ULOD Value'),
            ('llod_flag', 'LLOD Flag'),
            ('llod_value', 'LLOD Value'),
            ('dm_contact_info', 'DM Contact Info'),
            ('project_info', 'Project Info'),
            ('stipulations_on_use', 'Stipulations on Use'),
            ('other_comments', 'Other Comments'),
            ('revision', 'Revision'),
        ]

        for field_name, label in fields:
            edit = QLineEdit()
            self.comment_edits[field_name] = edit
            layout.addRow(f"{label}:", edit)

        # Revision comments (special handling)
        revision_group = QGroupBox("Revision Comments")
        revision_layout = QFormLayout(revision_group)

        self.revision_comment_edits = {}
        for rev in ['RA', 'RB', 'RC', 'R0', 'R1']:
            edit = QLineEdit()
            self.revision_comment_edits[rev] = edit
            revision_layout.addRow(f"{rev}:", edit)

        layout.addRow(revision_group)

        scroll.setWidget(widget)
        return scroll

    def _create_platform_tab(self) -> QWidget:
        """Create the platform mapping editing tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Description
        desc = QLabel(
            "Map aircraft tail numbers to platform names used in output filenames."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Table for mappings
        self.platform_table = QTableWidget()
        self.platform_table.setColumnCount(2)
        self.platform_table.setHorizontalHeaderLabels(["Tail Number", "Platform"])
        self.platform_table.horizontalHeader().setStretchLastSection(True)
        self.platform_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        layout.addWidget(self.platform_table)

        # Add/Remove buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Mapping")
        add_btn.clicked.connect(self._add_platform_mapping)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self._remove_platform_mapping)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return widget

    def _load_config_to_ui(self):
        """Load configuration values into UI widgets."""
        # Header
        header = self._config.header
        self.pi_name_edit.setText(header.pi_name)
        self.pi_org_edit.setText(header.pi_organization)
        self.datasource_edit.setText(header.datasource_desc)
        self.interval_edit.setText(str(header.data_interval))
        self.missing_edit.setText(str(header.missing_value))

        # Normal comments
        comments = self._config.normal_comments
        comment_values = {
            'pi_contact_info': comments.pi_contact_info,
            'platform': comments.platform,
            'location': comments.location,
            'associated_data': comments.associated_data,
            'instrument_info': comments.instrument_info,
            'data_info': comments.data_info,
            'uncertainty': comments.uncertainty,
            'ulod_flag': comments.ulod_flag,
            'ulod_value': comments.ulod_value,
            'llod_flag': comments.llod_flag,
            'llod_value': comments.llod_value,
            'dm_contact_info': comments.dm_contact_info,
            'project_info': comments.project_info,
            'stipulations_on_use': comments.stipulations_on_use,
            'other_comments': comments.other_comments,
            'revision': comments.revision,
        }

        for field_name, value in comment_values.items():
            if field_name in self.comment_edits:
                self.comment_edits[field_name].setText(value)

        # Revision comments
        for rev, comment in comments.revision_comments.items():
            if rev in self.revision_comment_edits:
                self.revision_comment_edits[rev].setText(comment)

        # Platform mapping
        self.platform_table.setRowCount(0)
        for tail, platform in self._config.platform_mapping.tail_to_platform.items():
            row = self.platform_table.rowCount()
            self.platform_table.insertRow(row)
            self.platform_table.setItem(row, 0, QTableWidgetItem(tail))
            self.platform_table.setItem(row, 1, QTableWidgetItem(platform))

    def _get_config_from_ui(self) -> MergedConfiguration:
        """Build configuration from UI values."""
        # Header
        try:
            data_interval = float(self.interval_edit.text())
        except ValueError:
            data_interval = 1.0

        try:
            missing_value = float(self.missing_edit.text())
        except ValueError:
            missing_value = -99999.0

        header = HeaderConfig(
            pi_name=self.pi_name_edit.text(),
            pi_organization=self.pi_org_edit.text(),
            datasource_desc=self.datasource_edit.text(),
            data_interval=data_interval,
            missing_value=missing_value
        )

        # Normal comments
        revision_comments = {}
        for rev, edit in self.revision_comment_edits.items():
            revision_comments[rev] = edit.text()

        comments = NormalComments(
            pi_contact_info=self.comment_edits['pi_contact_info'].text(),
            platform=self.comment_edits['platform'].text(),
            location=self.comment_edits['location'].text(),
            associated_data=self.comment_edits['associated_data'].text(),
            instrument_info=self.comment_edits['instrument_info'].text(),
            data_info=self.comment_edits['data_info'].text(),
            uncertainty=self.comment_edits['uncertainty'].text(),
            ulod_flag=self.comment_edits['ulod_flag'].text(),
            ulod_value=self.comment_edits['ulod_value'].text(),
            llod_flag=self.comment_edits['llod_flag'].text(),
            llod_value=self.comment_edits['llod_value'].text(),
            dm_contact_info=self.comment_edits['dm_contact_info'].text(),
            project_info=self.comment_edits['project_info'].text(),
            stipulations_on_use=self.comment_edits['stipulations_on_use'].text(),
            other_comments=self.comment_edits['other_comments'].text(),
            revision=self.comment_edits['revision'].text(),
            revision_comments=revision_comments
        )

        # Platform mapping
        platform_map = {}
        for row in range(self.platform_table.rowCount()):
            tail_item = self.platform_table.item(row, 0)
            platform_item = self.platform_table.item(row, 1)
            if tail_item and platform_item:
                tail = tail_item.text().strip()
                platform = platform_item.text().strip()
                if tail and platform:
                    platform_map[tail] = platform

        platform_mapping = PlatformMapping(tail_to_platform=platform_map)

        return MergedConfiguration(
            header=header,
            normal_comments=comments,
            special_comments=self._config.special_comments,
            options=self._config.options,
            platform_mapping=platform_mapping
        )

    def _add_platform_mapping(self):
        """Add a new platform mapping row."""
        row = self.platform_table.rowCount()
        self.platform_table.insertRow(row)
        self.platform_table.setItem(row, 0, QTableWidgetItem(""))
        self.platform_table.setItem(row, 1, QTableWidgetItem(""))
        self.platform_table.editItem(self.platform_table.item(row, 0))

    def _remove_platform_mapping(self):
        """Remove selected platform mapping row."""
        row = self.platform_table.currentRow()
        if row >= 0:
            self.platform_table.removeRow(row)

    def _load_config_file(self):
        """Load configuration from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Configuration",
            "",
            "Config Files (*.yaml *.yml *.json);;YAML Files (*.yaml *.yml);;JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            return

        try:
            path = Path(file_path)
            with open(path, 'r') as f:
                if path.suffix in ('.yaml', '.yml'):
                    if not YAML_AVAILABLE:
                        QMessageBox.warning(
                            self,
                            "YAML Not Available",
                            "PyYAML is required to load YAML files. Install with: pip install pyyaml"
                        )
                        return
                    data = yaml.safe_load(f) or {}
                else:
                    data = json.load(f)

            # Parse loaded data into config
            self._apply_loaded_data(data)
            self._load_config_to_ui()
            QMessageBox.information(self, "Success", f"Configuration loaded from {path.name}")

        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load configuration:\n{str(e)}")

    def _apply_loaded_data(self, data: dict):
        """Apply loaded data to the config."""
        # Header
        if 'header' in data:
            h = data['header']
            self._config.header.pi_name = h.get('pi_name', self._config.header.pi_name)
            self._config.header.pi_organization = h.get('pi_organization', self._config.header.pi_organization)
            self._config.header.datasource_desc = h.get('datasource_desc', self._config.header.datasource_desc)
            self._config.header.data_interval = h.get('data_interval', self._config.header.data_interval)
            self._config.header.missing_value = h.get('missing_value', self._config.header.missing_value)

        # Normal comments
        if 'normal_comments' in data:
            nc = data['normal_comments']
            for field in ['pi_contact_info', 'platform', 'location', 'associated_data',
                         'instrument_info', 'data_info', 'uncertainty', 'ulod_flag',
                         'ulod_value', 'llod_flag', 'llod_value', 'dm_contact_info',
                         'project_info', 'stipulations_on_use', 'other_comments', 'revision']:
                if field in nc:
                    setattr(self._config.normal_comments, field, nc[field])
            if 'revision_comments' in nc:
                self._config.normal_comments.revision_comments.update(nc['revision_comments'])

        # Platform mapping
        if 'platform_mapping' in data:
            self._config.platform_mapping.tail_to_platform = data['platform_mapping']

    def _save_config_file(self):
        """Save configuration to file."""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Configuration",
            "",
            "YAML Files (*.yaml);;JSON Files (*.json)"
        )

        if not file_path:
            return

        try:
            config = self._get_config_from_ui()
            path = Path(file_path)

            # Build data dict
            data = {
                'header': {
                    'pi_name': config.header.pi_name,
                    'pi_organization': config.header.pi_organization,
                    'datasource_desc': config.header.datasource_desc,
                    'data_interval': config.header.data_interval,
                    'missing_value': config.header.missing_value,
                },
                'normal_comments': {
                    'pi_contact_info': config.normal_comments.pi_contact_info,
                    'platform': config.normal_comments.platform,
                    'location': config.normal_comments.location,
                    'associated_data': config.normal_comments.associated_data,
                    'instrument_info': config.normal_comments.instrument_info,
                    'data_info': config.normal_comments.data_info,
                    'uncertainty': config.normal_comments.uncertainty,
                    'ulod_flag': config.normal_comments.ulod_flag,
                    'ulod_value': config.normal_comments.ulod_value,
                    'llod_flag': config.normal_comments.llod_flag,
                    'llod_value': config.normal_comments.llod_value,
                    'dm_contact_info': config.normal_comments.dm_contact_info,
                    'project_info': config.normal_comments.project_info,
                    'stipulations_on_use': config.normal_comments.stipulations_on_use,
                    'other_comments': config.normal_comments.other_comments,
                    'revision': config.normal_comments.revision,
                    'revision_comments': config.normal_comments.revision_comments,
                },
                'platform_mapping': config.platform_mapping.tail_to_platform,
            }

            with open(path, 'w') as f:
                if path.suffix in ('.yaml', '.yml') or 'yaml' in selected_filter.lower():
                    if not YAML_AVAILABLE:
                        QMessageBox.warning(
                            self,
                            "YAML Not Available",
                            "PyYAML is required to save YAML files. Saving as JSON instead."
                        )
                        path = path.with_suffix('.json')
                        json.dump(data, f, indent=2)
                    else:
                        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
                else:
                    json.dump(data, f, indent=2)

            QMessageBox.information(self, "Success", f"Configuration saved to {path.name}")

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save configuration:\n{str(e)}")

    def get_config(self) -> MergedConfiguration:
        """
        Get the edited configuration.

        Returns:
            MergedConfiguration with edited values
        """
        return self._get_config_from_ui()

    @staticmethod
    def edit_config(config: MergedConfiguration,
                   parent: Optional[QWidget] = None) -> Optional[MergedConfiguration]:
        """
        Static method to show dialog and get edited config.

        Args:
            config: Configuration to edit
            parent: Parent widget

        Returns:
            Edited configuration if accepted, None if cancelled
        """
        dialog = ConfigEditorDialog(config, parent)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_config()
        return None
