"""CLI entrypoint for `python -m scraper`."""
from __future__ import annotations

import argparse
import logging
import sys

from scraper.pipeline import run_pipeline
from scraper.sources import ALL_SCRAPERS


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scrape and normalize active & upcoming research projects and academic conferences."
    )
    parser.add_argument(
        "--only",
        nargs="*",
        choices=list(ALL_SCRAPERS.keys()),
        help="Run only the specified scraper sources.",
    )
    parser.add_argument(
        "--min-records",
        type=int,
        default=15,
        help="Minimum number of active records required for a valid run.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    payload = run_pipeline(selected_sources=args.only)
    total = payload["metadata"]["total_active"]
    if total < args.min_records:
        logging.error("Pipeline produced %d records, below --min-records=%d", total, args.min_records)
        return 1

    logging.info(
        "Pipeline succeeded: %d active research projects & conferences across %d disciplines.",
        total,
        payload["metadata"]["disciplines_count"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

