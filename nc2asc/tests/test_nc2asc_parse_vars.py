import importlib.util
import pathlib
import sys
import types
import unittest
from importlib.machinery import SourceFileLoader

import numpy as np
import xarray as xr


class _DummyQtModule(types.ModuleType):
    pass


# Provide a lightweight stub for PyQt5 so the module can be imported in tests.
pyqt5_stub = _DummyQtModule("PyQt5")
qtcore_stub = _DummyQtModule("PyQt5.QtCore")
qtgui_stub = _DummyQtModule("PyQt5.QtGui")
qtwidgets_stub = _DummyQtModule("PyQt5.QtWidgets")
qtcore_stub.QUrl = object
qtcore_stub.QStringListModel = object
qtcore_stub.Qt = types.SimpleNamespace(white=0, White=0)
qtgui_stub.QDesktopServices = types.SimpleNamespace(openUrl=lambda *args, **kwargs: True)
qtgui_stub.QMessageBox = types.SimpleNamespace(warning=lambda *args, **kwargs: None)
qtwidgets_stub.QTextBrowser = object
qtwidgets_stub.QGroupBox = object
qtwidgets_stub.QGridLayout = object
qtwidgets_stub.QWidget = object
qtwidgets_stub.QHBoxLayout = object
qtwidgets_stub.QFrame = object
qtwidgets_stub.QScrollBar = object
qtwidgets_stub.QToolBar = object
qtwidgets_stub.QMessageBox = object
qtwidgets_stub.QFileDialog = object
qtwidgets_stub.QTableWidgetItem = object
qtwidgets_stub.QVBoxLayout = object
qtwidgets_stub.QMenu = object
qtwidgets_stub.QMenuBar = object
qtwidgets_stub.QMainWindow = object
qtwidgets_stub.QAction = object
qtwidgets_stub.qApp = object
qtwidgets_stub.QApplication = object

sys.modules.setdefault("PyQt5", pyqt5_stub)
sys.modules.setdefault("PyQt5.QtCore", qtcore_stub)
sys.modules.setdefault("PyQt5.QtGui", qtgui_stub)
sys.modules.setdefault("PyQt5.QtWidgets", qtwidgets_stub)


class TestParseVars(unittest.TestCase):
    def setUp(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root / "src" / "lib"))
        loader = SourceFileLoader("nc2asc_mod", str(root / "src" / "nc2asc"))
        spec = importlib.util.spec_from_loader("nc2asc_mod", loader)
        self.module = importlib.util.module_from_spec(spec)
        loader.exec_module(self.module)

    def _new_gui(self):
        obj = self.module.gui.__new__(self.module.gui)
        obj.asc = {}
        obj.units = {}
        obj.long_name = {}
        obj.variables = {}
        obj.cellsize_dict = {}
        obj.histo = False
        return obj

    def test_parse_vars_skips_sps1_coordinate_variable(self):
        # A netCDF coordinate variable sps1(sps1) contains the substring "sps1"
        # but is not histogram data. It must be skipped, not abort the run.
        obj = self._new_gui()

        ds = xr.Dataset(
            {
                "sps1": (
                    ("sps1",),
                    np.array([0.0], dtype="float32"),
                    {"units": "s", "long_name": "subsecond offset"},
                ),
            }
        )

        obj.parse_vars(ds)

        self.assertNotIn("sps1", obj.asc)
        self.assertFalse(obj.histo)

    def test_parse_vars_skips_non_histogram_with_sps1_dim(self):
        # A 2-D variable using the sps1 dimension is not a histogram and is skipped.
        obj = self._new_gui()

        ds = xr.Dataset(
            {
                "bad_hist": (("Time", "sps1"), np.array([[1, 2], [3, 4]])),
            },
            coords={"Time": ("Time", [0, 1], {"long_name": "time", "units": "s"})},
        )

        obj.parse_vars(ds)

        self.assertNotIn("bad_hist", obj.asc)

    def test_parse_vars_parses_real_histogram(self):
        # A genuine 3-D histogram (Time, sps1, nbins) is parsed into self.asc.
        obj = self._new_gui()

        data = np.arange(2 * 1 * 3).reshape(2, 1, 3)
        ds = xr.Dataset(
            {
                "CCDP": (
                    ("Time", "sps1", "nbins"),
                    data,
                    {"units": "count", "long_name": "concentration"},
                ),
            },
            coords={"Time": ("Time", [0, 1], {"long_name": "time", "units": "s"})},
        )

        obj.parse_vars(ds)

        self.assertIn("CCDP", obj.asc)
        self.assertTrue(obj.histo)


if __name__ == "__main__":
    unittest.main()
