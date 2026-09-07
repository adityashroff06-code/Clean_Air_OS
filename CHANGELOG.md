# Changelog

## Unreleased — reproducible research baseline

- Added an offline command-line analysis for the bundled OpenAQ station exports.
- Added explicit input validation, local-day handling, negative/non-finite reading
  rejection, unit checks, duplicate/conflict handling, and input provenance.
- Added equal-station daily summaries, full-calendar coverage accounting, and
  charts that preserve gaps in the sampled data.
- Replaced the primary notebook with a maintained workflow sharing the same code.
  Preserved the original exploratory notebook separately with outputs cleared.
- Documented setup, configuration, schemas, provenance gaps, architecture, scientific
  limitations, contribution workflow, and security practices.
- Added regression tests, bundled-data validation, and notebook execution in CI.

Historical deck results have not been recalculated or endorsed by this update.
