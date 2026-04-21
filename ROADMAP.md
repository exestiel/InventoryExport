# Roadmap

Possible extensions for Inventory Export. Nothing here is committed work—use it to prioritize and track ideas.

**Baseline today:** `inventory_export.py` reads a multi-line CSV, finds `NN-YYYYY-ZZZZZ` cells, and assumes five columns follow each UPC; GS1 helpers live in `scripts/gs1.py`. Optional paths: `extract_inventory` → `add_upca`; `validate_upca_check` for check digits. Windows: `start.bat` / `run_export.bat`. Tests: unit coverage for `gs1` in `tests/test_gs1.py`.

## Phase 1 — Near-term / high leverage

- **Configurable column layout** — Describe offsets or header names in YAML/JSON so different POS exports do not require code edits.
- **Dry-run and stats** — Flags such as `--dry-run`, optional `--limit`, row counts, and a duplicate-UPC summary before writing files.
- **README** — Keep troubleshooting in sync; link to this roadmap for long-term ideas.

## Phase 2 — Robustness

- **Logging** — Replace ad hoc `print` with `logging`, plus `--verbose` / `--quiet` for scripts and automation.
- **Stronger validation** — Beyond GS1 check digits: empty descriptions, suspicious prices, or unexpected UPC formats.
- **Large files** — Optional progress reporting while streaming CSV (rows processed or throughput).

## Phase 3 — Developer experience

- **Packaging** — `pyproject.toml`, pinned Python, and a console entry point so `pip install` exposes a single command.
- **Importable package** — Layout that supports `python -m ...` without relying on `scripts/` on `sys.path`.
- **CI** — GitHub Actions (or similar) running `pytest` on each push/PR.
- **Integration test** — Tiny anonymized CSV fixture plus one test that exercises `inventory_export` row matching end-to-end.

## Phase 4 — Distribution and UX

- **Non-developer installs** — Document or automate a pinned Python; optional PyInstaller (or similar) for a double-click binary.
- **Combined launcher / subcommands** — One CLI with subcommands (`export`, `validate`, …) or a small menu-driven `.bat` for common tasks.
- **Deduplication** — Optional “one row per UPC” with explicit rules (first wins, merge fields)—needs agreed business rules first.

## Not planned / out of scope

- Replacing a POS or inventory system, real-time sync, or cloud-hosted processing. This project stays a **local CSV transform and validation** tool unless goals change.
