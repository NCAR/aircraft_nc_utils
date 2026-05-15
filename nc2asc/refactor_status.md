# nc2asc Refactor Status

Branch: `feature/nc2asc-multidim`

## Completed

### Issue #11 — Multidimensional/histogram functionality

- `src/lib/dimension_handler.py` — flattens 2D vars into columns, extracts bin metadata, handles 3D high-rate (SPS) data
- `src/lib/formatters/icartt_2110.py` — ICARTT 2110 format writer
- `src/nc2asc` — unified CLI entry point (~230 lines, CLI wiring only)
- Unit tests written and passing

### Issue #6 — ICARTT Configuration File

- `src/lib/config_manager.py` — priority hierarchy: CLI > batch > config file > format defaults > global defaults
- `config/example_config.yaml` — all 16 required ICARTT normal comment keywords with dynamic platform/tail number placeholders
- Unit tests written and passing

### Issue #13 — HRT/SRT (partial)

- `HighRateHandler` in `dimension_handler.py` supports `first_sample`, `average`, and `expand` strategies
- Unit tests pass for all three strategies

### Issue #12 — nc2asc capability gaps (partial)

- Batchfile reading via `parse_batch_file` is implemented
- CLI arguments take precedence over batch file settings

### GUI rewrite

- New modular components: `main_window`, `options_panel`, `preview_panel`, `variable_table`, `config_dialog`
- `src/nc2asc_gui` entry point added
- Ctrl+C (SIGINT) support via `QTimer` + `signal.signal` so the GUI exits cleanly on keyboard interrupt
- Unit tests written and passing

### Formatter refactoring

- New class hierarchy: `base -> factory -> plain / ames / icartt_1001 / icartt_2110`
- All 70 unit tests pass

### Path management

- `src/lib/nc2asc_paths.py` — single source of truth for `LIB_DIR`, `NC2ASC_BIN`, `EXAMPLE_CONFIG`; resolves correctly from both source tree and SCons-installed layouts
- All lib files import path constants from `nc2asc_paths`; no individual file does its own path detection
- `nc2asc_paths.py` added to `SConscript` install list

### Converter refactor

- `NetCDFConverter` moved from entry script to `src/lib/converter.py`; GUI imports it directly without importlib hackery
- Dead code removed: `process_nc.py`, `read_batch.py`, `write_data.py`

### Filename compliance enforcement

- ICARTT (1001 and 2110) and NASA Ames output filenames are always overwritten to spec-compliant names, even when the user passes `-o`; directory component is preserved
- NASA Ames convention: `CCyyyyMMdd_Rn.PLATFORM` — default two-letter code `RF` (Research Aviation Facility), overridable via `--ames-file-code`

## Not Yet Done

| Item | Issue | Note |
| --- | --- | --- |
| GUI batchfile save | #12 | `read_batch.py` was removed (dead code); batchfile save from GUI needs to be re-implemented if desired |
| Cumulative revision versioning in config | — | Was a TODO in deleted `write_data.py`; not yet implemented elsewhere |
| "Variable not found" user warning | #12 | Not implemented |
| Multi-rate data (vars at different sample rates) | #13 | Not implemented |

## Needs End-to-End Testing

Unit tests pass but no integration tests exist against real NetCDF files.

1. **1D variable conversion** — `nc2asc` on a standard NC file to ICARTT 1001; verify header and data columns
2. **2D histogram conversion** — file with a 2D variable (e.g., `A2DCR_RPC[]`) to ICARTT 2110; verify bin metadata and header match spec
3. **HRT data** — each strategy (`first_sample`, `average`, `expand`) against real high-rate NC data
4. **Config file loading** — `--config` flag overrides defaults correctly
5. **Batchfile round-trip** — load a batch file, confirm parsing; GUI save is not implemented (#12)
6. **GUI workflow** — open `nc2asc_gui`, load NC file, select vars, preview, convert, inspect output

## Known Issues

- Preview on GUI is wrong for multidim variables
