# Setup and operation

## Requirements

- Python 3.11–3.13 and pip. Python 3.11 is the minimum because the input manifest
  uses the standard-library streaming file hash API.
- A checkout including the committed 19 MB ZIP archive. No extraction is needed.
- Enough disk space for a Python environment and generated reports.

Follow the environment commands in the [README](../README.md). The runtime uses
pandas, NumPy, Matplotlib, and timezone data. `requirements.txt` specifies compatible
version ranges rather than a fully locked environment. To record an exact research
environment, save `python -m pip freeze > outputs/environment.txt` after running.

On Windows, if activation is restricted, use the environment interpreter directly:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m clean_air_os
```

No system policy change is necessary. On systems where Python is named `python3`,
use `python3` to create the environment, then `python` after activation.

## Configuration

```sh
python -m clean_air_os --help
python -m clean_air_os --archive path/to/export.zip --output outputs/custom
python -m clean_air_os --no-charts --output outputs/tables
```

| Option | Default | Behavior |
| --- | --- | --- |
| `--archive` | `Raw_data_files-20260118T205457Z-3-001.zip` | ZIP path, resolved from the working directory |
| `--output` | `outputs` | Creates directories and writes named reports |
| `--no-charts` | Disabled | Skips PNG generation; still writes all tables and JSON |

Run commands from the repository root. Re-running overwrites generated reports of
the same names. It does not remove other files in the output directory; use separate
directories for separate input versions. `summary.json` lists outputs written by the
current run, so a PNG left from an earlier chart-enabled run is not a new result.

Custom archives must follow the [input contract](DATA.md#input-contract). There is
no automatic data download, API credential, `.env` setting, server, or database.
Archive members are read as streams and are never extracted to filesystem paths.

## Notebook

```sh
python -m pip install -r requirements-dev.txt
python -m ipykernel install --user --name clean-air-os --display-name "Clean Air OS"
python -m jupyter lab Clean_Air_OS.ipynb
```

Select the **Clean Air OS** kernel, then restart the kernel and run all cells. The
notebook calls the maintained package; the same cleaning and aggregation rules apply
to both entry points. Generated files are written to `outputs/notebook/`.

For an automated execution check from the repository root:

```sh
python scripts/check_notebook.py
```

The historical notebook under `notebooks/` is intentionally outside this execution
check. It contains old exploratory cells and external-service dependencies.

## Troubleshooting

| Symptom | Resolution |
| --- | --- |
| `No module named clean_air_os` | Change to the repository root and use the environment's Python |
| `No module named pandas` | Install requirements using the same interpreter running the analysis |
| Archive not found | Restore the committed ZIP or provide its path with `--archive` |
| No station exports | Member filenames must end in `_Open_AQ.csv`, ignoring case |
| Missing required columns | Inspect the export against the documented long-form schema; wide daily files are unsupported |
| No valid PM2.5 observations | Inspect parameter names, numeric values, units, offset-bearing timestamps, and station identity |
| Conflicting station/timestamp values | Resolve overlapping exports or separate sensors before combining; the pipeline refuses to silently average them |
| Sparse or blank years in output | This is expected for the supplied samples; blank dates and years are preserved rather than filled |
| Notebook cannot import package | Launch Jupyter from the checkout and select the installed environment's kernel |

Read rejection counts in `summary.json`. Unsupported units are rejected rather than
converted implicitly. A successful run reports computable summaries; it does not
certify adequate scientific coverage.
