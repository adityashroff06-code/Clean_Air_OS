# Data inventory and provenance

## Bundled snapshot

Input: `Raw_data_files-20260118T205457Z-3-001.zip` (19,099,320 bytes).

SHA-256:
`c380796788f4dad8060198534d608f7a57a7ec3c231ef478fe31e63bea2d915d`

The archive is preserved unchanged. Its filename is not treated as a verified
retrieval date. The maintained analysis reads nine long-form station exports
directly from the archive; extraction is unnecessary.

| Export filename | Station | Retained PM2.5 rows | Observed local days | First–last observed day |
| --- | --- | ---: | ---: | --- |
| `Bawana_Open_AQ.csv` | Bawana, Delhi (8472) | 1,000 | 12 | 2025-02-19 – 2025-03-02 |
| `Chandnichowk_Open_AQ.csv` | Chandni Chowk, Delhi (11603) | 1,000 | 51 | 2020-11-13 – 2021-01-05 |
| `ITO_OPEN_AQ.csv` | ITO, New Delhi (5613) | 1,992 | 26 | 2020-01-01 – 2025-03-02 |
| `Jahangirpuri_Open_AQ.csv` | Jahangirpuri, Delhi (8235) | 1,000 | 18 | 2020-01-01 – 2020-01-18 |
| `KarniSingh_Open_AQ.csv` | Dr. Karni Singh Shooting Range, Delhi (6934) | 1,000 | 23 | 2020-01-01 – 2020-01-24 |
| `Pratapganj_open_AQ.csv` | Patparganj, Delhi (6960) | 1,000 | 14 | 2020-01-01 – 2020-01-14 |
| `Pusa_Open_AQ.csv` | Pusa, Delhi (6356) | 1,000 | 13 | 2025-02-19 – 2025-03-03 |
| `RKPuram_Open_AQ.csv` | R K Puram, Delhi (17) | 1,000 | 12 | 2025-02-19 – 2025-03-03 |
| `Sector11_Open_AQ.csv` | Sector 11, **Faridabad** (10908) | 1,000 | 13 | 2025-02-19 – 2025-03-03 |

These counts are derived from the committed snapshot using the maintained cleaning
rules. A first–last range does **not** imply continuous coverage. The nine exports
contain 12,000 total pollutant rows, of which 10,000 are PM2.5. Eight negative ITO
readings are rejected, leaving 9,992 observations on 88 distinct local dates. No
duplicate station/timestamp observations were found in this snapshot.

| Year | Dates with any retained observations | Calendar-year coverage |
| --- | ---: | ---: |
| 2020 | 71 | 19.40% |
| 2021 | 4 | 1.10% |
| 2022 | 0 | 0% |
| 2023 | 0 | 0% |
| 2024 | 0 | 0% |
| 2025 | 13 | 3.56% |

Most station exports have exactly 1,000 PM2.5 rows. This suggests a possible
export/query cap, but the original retrieval queries are absent, so the cause is
unverified. Treat the files as samples, not complete historical records.

## Other archived files

| File | Contents / status | Default workflow |
| --- | --- | --- |
| `FIIRMS.csv` | Fire-detection table: location, acquisition date/time, confidence, satellite, instrument, brightness, and fire radiative power fields | Excluded; no validated spatial/time join |
| `ITO_2025_daily_all_pollutants.csv` | Derived daily wide table, including `pm25` and `pm25_filled` | Excluded; overlaps ITO and contains legacy imputation |

The extra `I` in `FIIRMS.csv` is the committed filename. The original notebook's
filename filter used `FIRMS`, which did not reliably exclude this member.

## Input contract

Custom archives must contain at least one `*_Open_AQ.csv` member, case-insensitively,
with a header and these columns:

| Field | Required interpretation |
| --- | --- |
| `location_id` | Non-empty, stable station identifier; read as text |
| `location_name` | Non-empty station label |
| `parameter` | Pollutant identifier; only normalized PM2.5 rows are selected |
| `value` | Numeric finite concentration, zero or greater |
| `unit` | Explicit micrograms per cubic meter, using supported spelling variants |
| `datetimeLocal` | ISO 8601 timestamp with `Z` or explicit UTC offset |

Extra columns are retained in the raw archive but not needed for aggregation.
Bundled exports also contain `datetimeUtc`, `timezone`, coordinates, provider/owner,
and several sparsely populated metadata fields. The pipeline derives local dates
from the offset-bearing timestamp and fixed analysis timezone `Asia/Kolkata`.

This is intentionally a narrow input contract. Wide daily files, other timezones
as the intended study region, multiple sensor identities per station/time, other
pollutants, and implicit unit conversion require a reviewed adapter.

## Provenance and reuse

The station export filenames and columns identify OpenAQ-style data. Their rows
name CPCB as provider and owner names including DPCC, CPCB, IITM, and HSPCB. These
are preserved source labels, not a newly verified chain of custody. The legacy
notebook references the OpenAQ public archive, a GFED 5.1 dry-matter table, and
Meteostat; their complete retrieval queries and versions are not recorded here.

The exact retrieval dates, query limits, original upstream licenses, and permission
to redistribute all bundled data have not been established by this repository.
Before reuse or a new data release, verify and record those terms with each source.
Do not apply a repository-wide license to third-party data by assumption.

For new snapshots, record the source URL/query, retrieval time, source version,
geographic filter, units, sampling frequency, station/sensor identity, completeness
rules, license, attribution, and SHA-256. Keep the prior snapshot and explain any
change in results.
