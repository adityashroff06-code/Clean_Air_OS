# Methodology and interpretation

## Scope

The maintained analysis characterizes **the committed station samples**. It does
not reconstruct a continuous Delhi monitoring network. Source stations, periods,
and sampling density differ, and one station is in Faridabad.

## Processing rules

1. Select archive members ending in `_Open_AQ.csv`, case-insensitively. Exclude the
   fire-detection and derived ITO daily files to avoid incompatible schemas and
   duplicated station coverage.
2. Select PM2.5 parameter rows. Case, spaces, dots, underscores, and hyphens are
   normalized (`pm25`, `PM2.5`, and `pm_2_5` resolve to the same parameter).
3. Accept only finite, non-negative numeric values in explicit `µg/m³`, `μg/m³`,
   or `ug/m3` units after whitespace normalization. Zero is retained. Unsupported
   units are rejected, not converted; there is no undocumented high-value clipping.
4. Require an ISO 8601 `datetimeLocal` with UTC offset or `Z`. Parse the instant and
   convert to `Asia/Kolkata` before extracting the local day. Missing, malformed, or
   offset-free timestamps are rejected rather than assumed to be UTC.
5. Require a non-empty station ID and name. Remove repeats of the same station and
   timestamp with identical validated values. Conflicting values at that key fail
   the analysis, because the bundled schema has no reliable sensor identity to
   resolve them.
6. Compute each station's arithmetic daily mean and retain its observation count.
   Then average the available station-day means equally for each date. This prevents
   a station with more rows from automatically dominating the network summary.
7. Reindex the network summary from the first to last observed local date. Missing
   PM2.5 values remain blank; station and observation counts are zero on empty days.
8. Compute available-day yearly summaries and the percentage of **all calendar days
   in that year** that have observations. Entirely unobserved years remain visible.
   A first or last partial year still uses the full 365/366-day denominator.

The station table's available-day mean gives each observed day equal weight. A
station with a few samples on one day and many on another therefore differs from
the raw-row mean used in parts of the historical notebook.

## Quality accounting

`summary.json` records the selected files, all ignored archive members, per-file
input and PM2.5 counts, rejection reasons, duplicate count, and retained observations.
Rejection reasons may overlap; add `rejected_rows`, not the reason counts, to obtain
the total rejected rows. The input SHA-256 distinguishes data versions.

The code does not impose a minimum number of samples per station-day, a minimum
number of stations per network-day, or instrument quality flags. Observation
counts are exposed so consumers can evaluate coverage. Those missing criteria are
material limitations and must be designed before policy or operational use.

## Limits on conclusions

- An available-day yearly mean is not a defensible complete annual mean when days
  are missing systematically. No missing days are filled with a yearly average.
- Stations observed in different seasons cannot be ranked as spatial inequalities
  without a common, sufficiently covered comparison period.
- Equal station weighting does not estimate population exposure. The changing
  station composition also limits comparisons across years.
- PM2.5 concentration is not an AQI calculation. This workflow does not classify
  days by health categories or evaluate legal standards.
- The workflow does not compute fire or weather correlations. Those require source
  provenance, matching geography, comparable time aggregation, and missingness review.
- A governance proposal is a proposed intervention, not evidence of deployment or
  effectiveness.

The chart uses points for observed station-days and draws no line across the long
gaps. Reference-standard lines are omitted because the sample statistics do not
establish a compatible averaging window or compliance completeness.

## Next evidence needed

Acquire complete, versioned station exports with retrieval queries and permissions;
confirm instrument and calibration metadata; define hourly/daily completeness
thresholds; select a stable geography and comparison period; then validate any
external weather/fire joins. Publish those decisions with new tests and regenerated
figures before making stronger claims.
