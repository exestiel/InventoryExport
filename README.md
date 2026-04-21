# Inventory Export

Turns a multi-line inventory CSV export into a flat file with UPC-related columns: hyphenated item codes (`NN-YYYYY-ZZZZZ`) are expanded to GS1-style values (EAN-13 / UPC-A style fields) plus description, department, size, UOM, and regular price.

## Requirements

- **Python 3.11+** with `py` or `python` on your PATH ([python.org](https://www.python.org/downloads/) or Microsoft Store).
- **Windows** for the included launchers (`start.bat`, `run_export.bat`), or run the Python scripts from any OS.

## Folder layout

| Path | Purpose |
|------|---------|
| `source/` | Put your raw export here as `inventory.csv` (or pass paths on the command line). |
| `result/` | Output CSV files from the export and validation steps. |
| `scripts/` | Python tools (see below). |

## Workflows

**Primary (recommended):** run **`inventory_export.py`** once. It reads the raw multi-line CSV and writes the final columns (`UPC`, `UPCA`, `UPCA_No_Check_Digit`, `UPC12`, `UPC12_No_Check_Digit`, etc.).

**Optional two-step:** use **`extract_inventory.py`** to produce `source/extracted.csv`, then **`add_upca.py`** to add barcode columns to `result/extracted_with_upca.csv`. Use this when you want to inspect the extracted rows before computing UPCA.

**Validation:** **`validate_upca_check.py`** checks GS1 check digits on the `UPCA` column in a result file and can write bad rows to another CSV.

## Quick start (Windows)

### Interactive (`start.bat`)

1. Copy your inventory export to **`source\inventory.csv`**.
2. Double-click **`start.bat`** (opens a console window).
3. At the first prompt, **Y** means you are ready to continue. **N** only prints the path where the file should go; it does not skip the later check—if the file is missing, the batch file still exits with an error.
4. Choose an output file name (default: `Inventory_Final.csv`).
5. Find the file under **`result\`**. The window stays open until you press a key.

### Silent / automation (`run_export.bat`)

**`run_export.bat`** runs the same export **without prompts**: always **`source\inventory.csv`** → **`result\Inventory_Final.csv`**. It forwards Python’s exit code and does **not** pause—suitable for Task Scheduler or scripts. If you need a custom output name, use **`start.bat`** or the command line.

## Scripts

All scripts resolve default paths relative to the project root (the parent of `scripts/`). **Flags `-i` / `-o` override** the optional positional arguments when provided.

| Script | Role |
|--------|------|
| **`inventory_export.py`** | Main pipeline: raw export → final CSV. |
| **`extract_inventory.py`** | Optional: raw → `source/extracted.csv`. |
| **`add_upca.py`** | Optional: extracted → `result/extracted_with_upca.csv`. |
| **`validate_upca_check.py`** | Validate `UPCA`; second path / `-o` is the **invalid-rows** output file. |

### Command line

From the project root (Windows examples; on macOS/Linux use `python3` and forward slashes):

```bat
py -3 scripts\inventory_export.py
py -3 scripts\inventory_export.py path\to\in.csv path\to\out.csv
py -3 scripts\inventory_export.py -i source\inventory.csv -o result\out.csv
py -3 scripts\inventory_export.py --help
```

Same pattern for `extract_inventory.py` and `add_upca.py`.

Validate:

```bat
py -3 scripts\validate_upca_check.py
py -3 scripts\validate_upca_check.py result\Inventory_Final.csv result\bad_rows.csv
py -3 scripts\validate_upca_check.py -i result\Inventory_Final.csv -o result\bad_rows.csv
```

### Exit codes

Scripts exit with **0** on success and **non-zero** if the input is missing, headers are wrong, or another error is reported—usable from batch files and CI.

## Tests

Install dev dependency and run tests from the project root:

```bat
py -3 -m pip install -r requirements.txt
py -3 -m pytest tests -q
```

Runtime scripts use only the Python standard library; **`requirements.txt`** is for **pytest** (and any future test tooling).

## Troubleshooting

- **Python not found:** Install Python 3.11+ and ensure `py` or `python` is on PATH.
- **Source file not found:** Save the export as **`source\inventory.csv`** (or pass `-i` / a positional path).
- **0 rows written:** The report may not contain cells matching `NN-YYYYY-ZZZZZ`, or columns may not sit in the expected positions after the UPC cell.
- **Garbled text:** Exports are read as UTF-8 (with BOM) or Windows-1252 when possible; extremely unusual encodings may need a manual resave from Excel or Notepad.

## Encoding

Input files are read as UTF-8 (with BOM) or Windows-1252 when possible; output uses UTF-8 with BOM for Excel compatibility.
