from pathlib import Path
from zipfile import ZipFile

import pandas as pd
import pytest

from clean_air_os.analysis import ARCHIVE_NAME, clean_frame, load_observations, run_analysis, summarize


def observation(**changes):
    row = {"location_id": "1", "location_name": "Example station", "parameter": "pm25",
           "value": 10.0, "unit": "µg/m³", "datetimeLocal": "2020-01-01T00:15:00+05:30"}
    return row | changes


def make_archive(tmp_path, rows, name="Station_Open_AQ.csv"):
    path = tmp_path / "data.zip"
    with ZipFile(path, "w") as archive:
        archive.writestr(name, pd.DataFrame(rows).to_csv(index=False))
    return path


def test_local_day_is_preserved_and_mixed_iso_instants_are_supported():
    rows = [observation(), observation(datetimeLocal="2019-12-31T18:45:00Z"),
            observation(datetimeLocal="2019-12-31T18:45:00.123Z"),
            observation(datetimeLocal="2020-01-01T00:15:00.123456+05:30")]
    cleaned, report = clean_frame(pd.DataFrame(rows), "fixture")
    assert report["rejected_rows"] == 0
    assert cleaned.timestamp.dt.strftime("%Y-%m-%d").tolist() == ["2020-01-01"] * 4
    assert cleaned.timestamp.iloc[0] == cleaned.timestamp.iloc[1]


@pytest.mark.parametrize("changes,reason", [
    ({"value": -1}, "invalid_value_rows"),
    ({"value": "not a reading"}, "invalid_value_rows"),
    ({"value": float("inf")}, "invalid_value_rows"),
    ({"value": None}, "invalid_value_rows"),
    ({"unit": "mg/m3"}, "unsupported_unit_rows"),
    ({"unit": None}, "unsupported_unit_rows"),
    ({"datetimeLocal": "2020-01-01T00:15:00"}, "invalid_timestamp_rows"),
    ({"datetimeLocal": "invalid"}, "invalid_timestamp_rows"),
    ({"location_id": None}, "invalid_station_rows"),
    ({"location_name": " "}, "invalid_station_rows"),
])
def test_rejects_invalid_readings_with_reason(changes, reason):
    cleaned, report = clean_frame(pd.DataFrame([observation(**changes)]), "fixture")
    assert cleaned.empty
    assert report["rejected_rows"] == 1
    assert report[reason] == 1


@pytest.mark.parametrize("parameter,unit", [("PM2.5", "ug/m3"), ("pm_2_5", "μg/m³"),
                                          ("pm-25", " µg/m³ ")])
def test_normalizes_parameter_and_units_and_retains_zero(parameter, unit):
    cleaned, _ = clean_frame(pd.DataFrame([observation(value=0, parameter=parameter, unit=unit)]), "fixture")
    assert cleaned.pm25_ug_m3.tolist() == [0]


def test_non_pm25_rows_are_excluded_without_counting_as_rejected():
    cleaned, report = clean_frame(pd.DataFrame([observation(parameter="co")]), "fixture")
    assert cleaned.empty
    assert report["input_rows"] == 1
    assert report["pm25_rows"] == report["rejected_rows"] == 0


def test_missing_schema_fails_with_source_context():
    with pytest.raises(ValueError, match="fixture: missing required columns"):
        clean_frame(pd.DataFrame({"value": [1]}), "fixture")


def test_duplicate_instants_removed_after_timezone_normalization(tmp_path):
    rows = [observation(), observation(datetimeLocal="2019-12-31T18:45:00Z")]
    cleaned, quality = load_observations(make_archive(tmp_path, rows))
    assert len(cleaned) == 1
    assert quality["duplicate_observations_removed"] == 1


def test_conflicting_values_at_same_station_instant_fail(tmp_path):
    rows = [observation(), observation(value=50)]
    with pytest.raises(ValueError, match="conflicting"):
        load_observations(make_archive(tmp_path, rows))


def test_equal_station_weighting_gaps_and_full_calendar_coverage(tmp_path):
    rows = [observation(value=0), observation(value=10, datetimeLocal="2020-01-01T01:15:00+05:30"),
            observation(value=20, datetimeLocal="2020-01-01T02:15:00+05:30"),
            observation(location_id="2", location_name="Second", value=100),
            observation(value=30, datetimeLocal="2020-01-03T01:15:00+05:30")]
    cleaned, _ = load_observations(make_archive(tmp_path, rows))
    tables = summarize(cleaned)
    daily = tables["sampled_network_daily"]
    # First station mean is 10, second is 100: (10 + 100) / 2, not raw-row mean 32.5.
    assert daily.sampled_network_pm25_ug_m3.iloc[0] == 55
    assert pd.isna(daily.sampled_network_pm25_ug_m3.iloc[1])
    assert daily.reporting_stations.tolist() == [2, 0, 1]
    year = tables["yearly_coverage"].iloc[0]
    assert year.calendar_days == 366
    assert year.days_with_data == 2
    assert year.calendar_coverage_percent == pytest.approx(100 * 2 / 366)


def test_no_matching_exports_and_no_valid_rows_fail(tmp_path):
    with pytest.raises(ValueError, match="no .*station exports"):
        load_observations(make_archive(tmp_path, [observation()], name="derived.csv"))
    with pytest.raises(ValueError, match="No valid PM2.5"):
        load_observations(make_archive(tmp_path, [observation(value=-1)]))


def test_bundled_archive_quality_coverage_and_manifest(tmp_path):
    archive = Path(__file__).resolve().parents[1] / ARCHIVE_NAME
    summary = run_analysis(archive, tmp_path, charts=False)
    assert summary["archive_sha256"] == "c380796788f4dad8060198534d608f7a57a7ec3c231ef478fe31e63bea2d915d"
    assert summary["station_count"] == 9
    assert summary["quality"]["retained_observations"] == 9992
    assert summary["quality"]["rejected_rows"] == 8
    assert summary["days_with_data"] == 88
    assert len(summary["quality"]["ignored_members"]) == 2
    assert all((tmp_path / name).is_file() for name in summary["outputs"])
    years = pd.read_csv(tmp_path / "yearly_coverage.csv").set_index("year")
    assert years.days_with_data.to_dict() == {2020: 71, 2021: 4, 2022: 0, 2023: 0, 2024: 0, 2025: 13}
    assert years.loc[2022:2024, "available_day_mean_pm25_ug_m3"].isna().all()
