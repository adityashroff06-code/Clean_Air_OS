"""Offline PM2.5 analysis with explicit quality and coverage accounting."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd

from . import __version__

ARCHIVE_NAME = "Raw_data_files-20260118T205457Z-3-001.zip"
REQUIRED_COLUMNS = {
    "location_id", "location_name", "parameter", "value", "unit", "datetimeLocal"
}


def clean_frame(frame: pd.DataFrame, source: str) -> tuple[pd.DataFrame, dict]:
    """Validate a long-form OpenAQ export and retain usable PM2.5 observations.

    Timestamps must include a UTC offset. Convert to Asia/Kolkata before
    assigning dates; treating local midnight as UTC changes the day.
    """
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"{source}: missing required columns: {', '.join(sorted(missing))}")
    parameter = frame["parameter"].astype("string").str.lower().str.replace(
        r"[\s._-]", "", regex=True
    )
    selected = frame.loc[parameter.eq("pm25").fillna(False)].copy()
    values = pd.to_numeric(selected["value"], errors="coerce")
    units = (selected["unit"].astype("string").str.strip().str.lower()
             .str.replace("μ", "u").str.replace("µ", "u")
             .str.replace("³", "3").str.replace(" ", ""))
    raw_time = selected["datetimeLocal"].astype("string").str.strip()
    has_offset = raw_time.str.contains(r"(?:Z|[+-]\d{2}:?\d{2})$", na=False)
    timestamps = pd.to_datetime(raw_time.where(has_offset), format="ISO8601", errors="coerce", utc=True)
    station = selected["location_id"].astype("string").str.strip()
    name = selected["location_name"].astype("string").str.strip()
    valid_value = values.notna() & np.isfinite(values) & values.ge(0)
    valid_unit = units.eq("ug/m3").fillna(False)
    valid_time = timestamps.notna()
    valid_station = station.notna() & station.ne("") & name.notna() & name.ne("")
    valid = valid_value & valid_unit & valid_time & valid_station
    cleaned = pd.DataFrame({
        "station_id": station,
        "station_name": name,
        "timestamp": timestamps.dt.tz_convert("Asia/Kolkata"),
        "pm25_ug_m3": values,
        "source_file": source,
    }).loc[valid].reset_index(drop=True)
    report = {
        "source_file": source,
        "input_rows": len(frame),
        "pm25_rows": len(selected),
        "valid_rows_before_deduplication": len(cleaned),
        "rejected_rows": int((~valid).sum()),
        # A rejected row may have more than one reason.
        "invalid_value_rows": int((~valid_value).sum()),
        "unsupported_unit_rows": int((~valid_unit).sum()),
        "invalid_timestamp_rows": int((~valid_time).sum()),
        "invalid_station_rows": int((~valid_station).sum()),
    }
    return cleaned, report


def load_observations(archive: Path) -> tuple[pd.DataFrame, dict]:
    """Read only station exports directly from ZIP; never extract its paths."""
    frames, reports = [], []
    with ZipFile(archive) as bundle:
        members = sorted(name for name in bundle.namelist()
                         if name.lower().endswith("_open_aq.csv"))
        if not members:
            raise ValueError("Archive contains no *_Open_AQ.csv station exports.")
        for member in members:
            with bundle.open(member) as stream:
                frame = pd.read_csv(stream, dtype={"location_id": "string"})
            cleaned, report = clean_frame(frame, member)
            frames.append(cleaned)
            reports.append(report)
        ignored = sorted(set(bundle.namelist()) - set(members))
    observations = pd.concat(frames, ignore_index=True)
    if observations.empty:
        raise ValueError("No valid PM2.5 observations remain after quality checks.")
    keys = ["station_id", "timestamp"]
    conflicts = observations.groupby(keys)["pm25_ug_m3"].nunique().gt(1)
    if conflicts.any():
        raise ValueError(
            f"Found {int(conflicts.sum())} station/timestamp groups with conflicting "
            "PM2.5 values. Resolve sensor identity or source conflicts before aggregation."
        )
    duplicates = int(observations.duplicated(keys).sum())
    observations = observations.drop_duplicates(keys).sort_values(keys).reset_index(drop=True)
    observations["date"] = observations["timestamp"].dt.tz_localize(None).dt.normalize()
    quality = {
        "files": reports, "ignored_members": ignored,
        "duplicate_observations_removed": duplicates,
        "retained_observations": len(observations),
        "rejected_rows": sum(r["rejected_rows"] for r in reports),
    }
    return observations, quality


def summarize(observations: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Average within station-days, then equally across available stations.

    This sample-network summary does not estimate population exposure or
    a complete Delhi annual mean. Missing days remain missing.
    """
    station_daily = observations.groupby(["station_id", "date"], as_index=False).agg(
        station_name=("station_name", "first"),
        pm25_ug_m3=("pm25_ug_m3", "mean"),
        observations=("pm25_ug_m3", "size"),
    )
    daily = station_daily.groupby("date").agg(
        sampled_network_pm25_ug_m3=("pm25_ug_m3", "mean"),
        reporting_stations=("station_id", "nunique"),
        observations=("observations", "sum"),
    )
    date_range = pd.date_range(daily.index.min(), daily.index.max(), freq="D", name="date")
    daily = daily.reindex(date_range)
    daily[["reporting_stations", "observations"]] = (
        daily[["reporting_stations", "observations"]].fillna(0).astype(int)
    )
    yearly = daily.groupby(daily.index.year).agg(
        available_day_mean_pm25_ug_m3=("sampled_network_pm25_ug_m3", "mean"),
        days_with_data=("sampled_network_pm25_ug_m3", "count"),
        observations=("observations", "sum"),
    )
    yearly.index.name = "year"
    yearly["calendar_days"] = [366 if pd.Timestamp(f"{y}-01-01").is_leap_year else 365
                               for y in yearly.index]
    yearly["calendar_coverage_percent"] = 100 * yearly.days_with_data / yearly.calendar_days
    stations = station_daily.groupby("station_id").agg(
        station_name=("station_name", "first"),
        first_observed_day=("date", "min"),
        last_observed_day=("date", "max"),
        observed_days=("date", "nunique"),
        observations=("observations", "sum"),
        available_day_mean_pm25_ug_m3=("pm25_ug_m3", "mean"),
    )
    return {"station_daily": station_daily, "sampled_network_daily": daily.reset_index(),
            "yearly_coverage": yearly.reset_index(), "station_coverage": stations.reset_index()}


def plot_coverage(tables: dict[str, pd.DataFrame], destination: Path) -> None:
    """Plot individual sampled station-days without joining gaps across years."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    frame = tables["station_daily"]
    fig, ax = plt.subplots(figsize=(12, 6))
    for name, group in frame.groupby("station_name"):
        ax.scatter(group["date"], group["pm25_ug_m3"], s=13, alpha=0.75, label=name)
    ax.set(title="Bundled station samples: observed daily PM2.5",
           xlabel="Local date (Asia/Kolkata)", ylabel="PM2.5 (µg/m³)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.15)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=8, frameon=False)
    fig.text(0.5, 0.01, "Sparse samples; station coverage varies. No gap filling or citywide estimate.",
             ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(destination, dpi=160, bbox_inches="tight")
    plt.close(fig)


def run_analysis(archive: Path, output_dir: Path, *, charts: bool = True) -> dict:
    """Write deterministic tables and a reproducibility/quality manifest."""
    archive = Path(archive)
    observations, quality = load_observations(archive)
    tables = summarize(observations)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in tables.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False, float_format="%.6f")
    files = [f"{name}.csv" for name in tables] + ["summary.json"]
    if charts:
        plot_coverage(tables, output_dir / "station_samples.png")
        files.append("station_samples.png")
    with archive.open("rb") as stream:
        archive_sha256 = hashlib.file_digest(stream, "sha256").hexdigest()
    summary = {
        "analysis_version": __version__,
        "archive_file": archive.name,
        "archive_sha256": archive_sha256,
        "timezone": "Asia/Kolkata", "unit": "µg/m³",
        "station_count": int(observations.station_id.nunique()),
        "first_observed_day": str(observations.date.min().date()),
        "last_observed_day": str(observations.date.max().date()),
        "days_with_data": int(tables["sampled_network_daily"].reporting_stations.gt(0).sum()),
        "quality": quality,
        "outputs": files,
        "limitations": [
            "Bundled exports have sparse, unequal coverage and include Faridabad.",
            "Available-day summaries are not annual means or citywide exposure estimates.",
            "No missing-value imputation, regulatory completeness test, or causal attribution.",
            "FIRMS and the derived ITO 2025 file are excluded from this workflow.",
        ],
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8"
    )
    return summary
