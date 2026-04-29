# nc2asc Refactor Status

Branch: `feature/nc2asc-multidim`

## Completed

**Issue #11 — Multidimensional/histogram functionality**
- `src/lib/dimension_handler.py` — flattens 2D vars into columns, extracts bin metadata, handles 3D high-rate (SPS) data
- `src/lib/formatters/icartt_2110.py` — ICARTT 2110 format writer
- `src/nc2asc_multidim` — unified CLI entry point combining previous scripts
- Unit tests written and passing

**Issue #6 — ICARTT Configuration File**
- `src/lib/config_manager.py` — priority hierarchy: CLI > batch > config file > format defaults > global defaults
- `config/default_config.yaml` — all 16 required ICARTT normal comment keywords with dynamic platform/tail number placeholders
- Unit tests written and passing

**Issue #13 — HRT/SRT (partial)**
- `HighRateHandler` in `dimension_handler.py` supports `first_sample`, `average`, and `expand` strategies
- Unit tests pass for all three strategies

**Issue #12 — nc2asc capability gaps (partial)**
- Batchfile reading via `parse_batch_file` is implemented
- CLI arguments take precedence over batch file settings

**GUI rewrite**
- New modular components: `main_window`, `options_panel`, `preview_panel`, `variable_table`, `config_dialog`
- `src/nc2asc_gui` entry point added
- Unit tests written and passing

**Formatter refactoring**
- New class hierarchy: `base -> factory -> plain / ames / icartt_1001 / icartt_2110`
- All 70 unit tests pass

## Not Yet Done

| Item | Issue | Note |
|---|---|---|
| GUI batchfile save format is broken | #12 | TODO at `src/lib/read_batch.py:252` |
| "Variable not found" user warning | #12 | Not implemented |
| Multi-rate data (vars at different sample rates) | #13 | Not implemented |
| Cumulative revision versioning in config | — | TODO at `src/lib/write_data.py:290` |

## Needs End-to-End Testing

Unit tests pass but no integration tests exist against real NetCDF files.

1. **1D variable conversion** — `nc2asc_multidim` on a standard NC file to ICARTT 1001; verify header and data columns
2. **2D histogram conversion** — file with a 2D variable (e.g., `A2DCR_RPC[]`) to ICARTT 2110; verify bin metadata and header match spec
3. **HRT data** — each strategy (`first_sample`, `average`, `expand`) against real high-rate NC data
4. **Config file loading** — `--config` flag overrides defaults correctly
5. **Batchfile round-trip** — load a batch file, confirm parsing; save from GUI, confirm it re-reads (currently broken, #12)
6. **GUI workflow** — open `nc2asc_gui`, load NC file, select vars, preview, convert, inspect output
