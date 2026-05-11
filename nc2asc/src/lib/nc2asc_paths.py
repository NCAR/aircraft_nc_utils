"""
Path constants for nc2asc — resolves correctly from source and after scons install.

Source:    src/lib/nc2asc_paths.py              -> LIB_DIR = src/lib/
Installed: $PREFIX/lib/nc2asc/nc2asc_paths.py  -> LIB_DIR = $PREFIX/lib/nc2asc/

Import anywhere with:  from nc2asc_paths import LIB_DIR, NC2ASC_BIN, EXAMPLE_CONFIG
"""

from pathlib import Path

# Always the directory containing the lib modules (gui/, formatters/, etc.)
LIB_DIR = Path(__file__).parent

# nc2asc binary:
#   Source:    src/nc2asc
#   Installed: $PREFIX/bin/nc2asc   (two levels above lib/nc2asc/, then into bin/)
_installed_bin = LIB_DIR.parent.parent / 'bin' / 'nc2asc'
_source_bin    = LIB_DIR.parent / 'nc2asc'
NC2ASC_BIN = _installed_bin if _installed_bin.exists() else _source_bin

# example_config.yaml:
#   Installed: next to lib modules at $PREFIX/lib/nc2asc/example_config.yaml
#   Source:    nc2asc/config/example_config.yaml (two levels above lib/)
EXAMPLE_CONFIG = LIB_DIR / 'example_config.yaml'
if not EXAMPLE_CONFIG.exists():
    EXAMPLE_CONFIG = LIB_DIR.parent.parent / 'config' / 'example_config.yaml'
