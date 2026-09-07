"""Command-line entry point; run with python -m clean_air_os."""

import argparse
from pathlib import Path
from zipfile import BadZipFile

from .analysis import ARCHIVE_NAME, run_analysis


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze bundled PM2.5 station samples offline.")
    parser.add_argument("--archive", type=Path, default=Path(ARCHIVE_NAME), help="Input ZIP archive")
    parser.add_argument("--output", type=Path, default=Path("outputs"), help="Generated report directory")
    parser.add_argument("--no-charts", action="store_true", help="Write CSV and JSON only")
    args = parser.parse_args()
    try:
        summary = run_analysis(args.archive, args.output, charts=not args.no_charts)
    except (OSError, ValueError, BadZipFile) as error:
        parser.exit(2, f"Analysis failed: {error}\n")
    print(f"Analyzed {summary['quality']['retained_observations']:,} observations "
          f"from {summary['station_count']} sampled stations.")
    print(f"Rejected {summary['quality']['rejected_rows']} rows; "
          f"observed {summary['days_with_data']} distinct local dates.")
    print(f"Reports saved to {args.output.resolve()}")
    print("Coverage is sparse: read yearly_coverage.csv before interpreting averages.")


if __name__ == "__main__":
    main()
