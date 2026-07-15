"""Shared test helpers for the nc2asc test suite.

Importing this module installs lightweight PyQt5 stubs so that ``nc2asc`` (a
GUI program) can be imported and exercised headlessly. It also provides helpers
to load the program as a module and to build small synthetic RAF-style netCDF
and batch-file fixtures, so the tests run anywhere without requiring the real
project data on /scr/raf_data.
"""

import argparse
import importlib.util
import pathlib
import sys
import types
from importlib.machinery import SourceFileLoader

import numpy as np
import xarray as xr

ROOT = pathlib.Path(__file__).resolve().parents[1]
LIB_DIR = ROOT / "src" / "lib" / "nc2asc"
BIN_FILE = ROOT / "src" / "bin" / "nc2asc"


def _install_pyqt5_stubs():
    """Register minimal PyQt5 stub modules so nc2asc imports without a display."""
    for name in ("PyQt5", "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets"):
        sys.modules.setdefault(name, types.ModuleType(name))
    qtc = sys.modules["PyQt5.QtCore"]
    qtg = sys.modules["PyQt5.QtGui"]
    qtw = sys.modules["PyQt5.QtWidgets"]

    qtc.QUrl = object
    qtc.QStringListModel = object
    qtc.Qt = types.SimpleNamespace(white=0, White=0)

    qtg.QDesktopServices = types.SimpleNamespace(openUrl=lambda *a, **k: True)
    qtg.QColor = object

    for widget in (
        "QTextBrowser", "QGroupBox", "QGridLayout", "QWidget", "QHBoxLayout",
        "QFrame", "QScrollBar", "QToolBar", "QFileDialog", "QTableWidgetItem",
        "QVBoxLayout", "QMenu", "QMenuBar", "QMainWindow", "QAction", "qApp",
        "QApplication",
    ):
        setattr(qtw, widget, object)
    # writeData/saveBatchFile reference these class-level members, so a bare
    # object() stub is not enough.
    qtw.QMessageBox = types.SimpleNamespace(
        No=65536, Yes=16384,
        question=lambda *a, **k: 65536,
        warning=lambda *a, **k: None,
    )


def load_nc2asc():
    """Load and return the nc2asc program as an importable module."""
    _install_pyqt5_stubs()
    if str(LIB_DIR) not in sys.path:
        sys.path.insert(0, str(LIB_DIR))
    loader = SourceFileLoader("nc2asc_mod", str(BIN_FILE))
    spec = importlib.util.spec_from_loader("nc2asc_mod", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def write_sample_netcdf(path, n=5):
    """Write a small synthetic RAF-style netCDF file to ``path``.

    Contains a decodable ``Time`` coordinate and one 1-Hz variable, plus the
    ``project``/``platform`` global attributes nc2asc expects.
    """
    ds = xr.Dataset(
        {
            "ATX": (
                "Time",
                np.arange(n, dtype="float32"),
                {"units": "deg_C", "long_name": "ambient temperature"},
            ),
        },
        coords={
            "Time": (
                "Time",
                np.arange(n),
                {
                    "units": "seconds since 2021-05-29 15:30:00 +0000",
                    "long_name": "time of measurement",
                },
            )
        },
        attrs={"project": "ASPIRE-TEST", "platform": "N130AR"},
    )
    ds.to_netcdf(str(path))
    return str(path)


def write_batch_file(path, input_file, output_file, header="Plain",
                     variables=None, date="yyyy-mm-dd", time="hh:mm:ss"):
    """Write a batch file pointing at the given input/output files.

    ``header`` selects the output format (``Plain``/``ICARTT``/``AMES``).
    ``variables`` is an optional list of variable names to emit as ``Vars=``
    lines; when omitted nc2asc takes its convert-all code path. ``date``/``time``
    set the ``dt=``/``tm=`` directives (ICARTT batches use ``NoDate``/``SecOfDay``).
    """
    with open(path, "w") as fh:
        fh.write(f"if={input_file}\n")
        fh.write(f"of={output_file}\n\n")
        fh.write(f"hd={header}\n")
        fh.write(f"dt={date}\n")
        fh.write(f"tm={time}\n")
        fh.write("sp=comma\n")
        fh.write("fv=-32767\n")
        fh.write("ti=X,X\n")
        for var in variables or []:
            fh.write(f"Vars={var}\n")
    return str(path)


def make_cl_args(input_file=None, output_file=None, batch_file=None):
    """Build an argparse.Namespace matching what nc2asc_CL.processData reads."""
    return argparse.Namespace(
        i=input_file, o=output_file, b=batch_file, mixed_rate=False, v=None
    )
