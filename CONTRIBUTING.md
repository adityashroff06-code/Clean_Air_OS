# Contributing

Start with the [setup guide](docs/SETUP.md) and [methodology](docs/METHODOLOGY.md).
For a proposed method change, describe the data issue and expected effect on the
reported results before changing the calculation.

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m clean_air_os --output outputs/review
python scripts/check_notebook.py
```

For each change:

- Keep cleaning and aggregation in `clean_air_os/analysis.py` so notebook and CLI
  behavior agree. Add a small synthetic regression case for a meaningful data bug.
- Document changes to schemas, units, geography, timezone handling, station
  weighting, or completeness rules. Explain why the new rule is justified.
- Report the input hash, validation commands, and actual results. Inspect the chart
  and coverage tables; a command exiting successfully is not scientific validation.
- Keep generated reports, environment folders, credentials, and notebook outputs
  out of commits. Use synthetic fixtures rather than adding large downloads.
- Do not silently replace the bundled data or historical deck. New data needs its
  retrieval date, source query, version, rights, and attribution recorded.

Submit a focused pull request explaining the problem, changed behavior, validation,
and remaining limitations. CI covers the maintained workflow only; it does not
verify historical policy claims or upstream data rights. The maintainer must choose
an explicit repository license before contributors assume broad reuse rights.
