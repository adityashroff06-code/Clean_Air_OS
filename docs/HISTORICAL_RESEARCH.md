# Historical research and governance proposal

The project started as a Colab analysis and a presentation proposing a data and
governance approach to Delhi air quality. Two artifacts preserve that work:

- [Original presentation](../Clean_AIR_OS_FULL_DECK.pptx): preserved byte-for-byte.
- [Original exploratory notebook](../notebooks/legacy_analysis.ipynb): original
  source cells retained with an archive notice; stored outputs and execution state
  removed to avoid presenting stale charts and debugging sessions as new results.

The original version is also recoverable from Git commit
`0cee45d02633bc8d72f99d6b080d928961317a71`.

## Why there is a maintained workflow

The original notebook combines multiple sessions, hard-coded personal Google Drive
paths, repeated imports, exploratory failures, external downloads, and reused
variable names. It cannot reliably run from a fresh local checkout. The replacement
[primary notebook](../Clean_Air_OS.ipynb) uses the same offline package as the CLI.

## Interpretation corrections

| Historical approach | Maintained approach / reason |
| --- | --- |
| Labelled sampled station averages as a 2020–2025 citywide trend | Reports sampled-network summaries with sparse coverage and a Faridabad station explicitly identified |
| Mixed arbitrary CSVs and a misspelled fire-file exclusion | Selects only the documented long-form station exports |
| Averaged raw rows across stations | First averages station-days, then weights available stations equally |
| Converted UTC timestamps to timezone-naive values before daily grouping | Converts instants to Asia/Kolkata before assigning a local day |
| Filled missing PM2.5 days using a yearly mean in exploratory ITO work | Preserves missing values and exposes full-calendar coverage |
| Compared summary charts with reference lines of unclear averaging compatibility | Omits regulatory/health comparators from the maintained sample analysis |
| Joined a broad GFED region with Delhi yearly summaries | Does not report causal or source-attribution findings from unmatched regional data |
| Weather cells failed from a missing dependency and subsequent undefined variable | Keeps unvalidated online extensions outside the runnable baseline |

The new results are deliberately not expected to reproduce all historical charts:
the old figures used inconsistent inputs and aggregation rules. The deck has not
been rewritten, fact-checked in full, or regenerated, so treat its numerical and
policy claims as historical research requiring review.

## Before extending the proposal

Validate the underlying data coverage and geographic scope first. For each proposed
intervention, distinguish the hypothesis, responsible institutions, implementation
requirements, evaluation method, cost assumptions, and evidence of effectiveness.
An implementation roadmap and an empirical evaluation would be separate future
work; neither is implied by the current notebook or presentation.
