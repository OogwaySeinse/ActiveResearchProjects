"""Main scraper orchestration pipeline: fetch -> deduplicate -> history -> write JSON & CSV outputs."""
from __future__ import annotations

import csv
import json
import logging
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from scraper.dedupe import deduplicate_records
from scraper.fx import load_fx_rates
from scraper.history import annotate_with_history
from scraper.models import ResearchProjectRecord, SourceStatus
from scraper.normalize import compute_deadline_status
from scraper.sources import ALL_SCRAPERS

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
DASHBOARD_PUBLIC_DATA = ROOT_DIR / "apps" / "dashboard" / "public" / "data"

CSV_COLUMNS = [
    "id",
    "title",
    "venue_code",
    "discipline",
    "category",
    "project_type",
    "tier",
    "status",
    "platform",
    "abstract_deadline",
    "submission_deadline",
    "notification_date",
    "event_start_date",
    "event_end_date",
    "days_remaining",
    "location",
    "format",
    "funding_raw",
    "funding_usd",
    "funding_currency",
    "organizer",
    "lead_researchers",
    "proceedings_publisher",
    "paper_url",
    "url",
    "tags",
    "description",
    "first_seen_at",
    "is_new",
    "scraped_at",
]


def _save_records_cache(source_name: str, records: List[ResearchProjectRecord]) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path = CACHE_DIR / f"{source_name}.records.json"
        path.write_text(
            json.dumps([r.to_dict() for r in records], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as exc:
        logger.debug("Failed to write cache for %s: %s", source_name, exc)


def _load_records_cache(source_name: str) -> List[ResearchProjectRecord]:
    path = CACHE_DIR / f"{source_name}.records.json"
    if not path.exists():
        return []
    try:
        raw_list = json.loads(path.read_text(encoding="utf-8"))
        restored: List[ResearchProjectRecord] = []
        for item in raw_list:
            if not isinstance(item, dict):
                continue
            active, status, days_rem = compute_deadline_status(
                item.get("submission_deadline"),
                item.get("event_start_date"),
                item.get("event_end_date"),
                is_rolling=item.get("status") == "rolling",
            )
            if not active:
                continue
            item["status"] = status
            item["days_remaining"] = days_rem
            restored.append(ResearchProjectRecord.from_dict(item))
        return restored
    except Exception as exc:
        logger.debug("Failed to load cache for %s: %s", source_name, exc)
        return []


def run_pipeline(selected_sources: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    """Run all (or selected) research & conference scrapers, deduplicate, and write JSON + CSV outputs."""
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    _, fx_source = load_fx_rates()
    sources_to_run = list(selected_sources) if selected_sources else list(ALL_SCRAPERS.keys())

    all_records: List[ResearchProjectRecord] = []
    statuses: List[SourceStatus] = []

    for name in sources_to_run:
        entry = ALL_SCRAPERS.get(name)
        if not entry:
            logger.warning("Unknown scraper source '%s' skipped", name)
            continue
        label, scraper_fn = entry

        t0 = time.perf_counter()
        try:
            records = scraper_fn()
            dt_ms = int((time.perf_counter() - t0) * 1000)
            if records:
                _save_records_cache(name, records)
                all_records.extend(records)
                statuses.append(
                    SourceStatus(
                        name=name,
                        label=label,
                        status="ok",
                        count=len(records),
                        duration_ms=dt_ms,
                        updated_at=now_iso,
                    )
                )
            else:
                cached = _load_records_cache(name)
                if cached:
                    all_records.extend(cached)
                    statuses.append(
                        SourceStatus(
                            name=name,
                            label=label,
                            status="cached",
                            count=len(cached),
                            duration_ms=dt_ms,
                            error="Live scrape returned 0 records; used cached snapshot",
                            updated_at=now_iso,
                        )
                    )
                else:
                    statuses.append(
                        SourceStatus(
                            name=name,
                            label=label,
                            status="degraded",
                            count=0,
                            duration_ms=dt_ms,
                            error="0 records returned",
                            updated_at=now_iso,
                        )
                    )
        except Exception as exc:
            dt_ms = int((time.perf_counter() - t0) * 1000)
            logger.exception("Scraper '%s' raised an error", name)
            cached = _load_records_cache(name)
            if cached:
                all_records.extend(cached)
                statuses.append(
                    SourceStatus(
                        name=name,
                        label=label,
                        status="cached",
                        count=len(cached),
                        duration_ms=dt_ms,
                        error=str(exc),
                        updated_at=now_iso,
                    )
                )
            else:
                statuses.append(
                    SourceStatus(
                        name=name,
                        label=label,
                        status="error",
                        count=0,
                        duration_ms=dt_ms,
                        error=str(exc),
                        updated_at=now_iso,
                    )
                )

    raw_count = len(all_records)
    deduped = deduplicate_records(all_records)
    history_meta = annotate_with_history(deduped)

    # Sort: urgent CFP deadlines first, then active CFPs by days_remaining, then upcoming conferences, then rolling projects
    status_rank = {"ending_soon": 0, "active": 1, "upcoming": 2, "rolling": 3}
    deduped.sort(
        key=lambda r: (
            status_rank.get(r.status, 4),
            r.days_remaining if r.days_remaining is not None else 999999,
            -r.funding_usd,
            r.title.lower(),
        )
    )

    total_funding_usd = round(sum(r.funding_usd for r in deduped), 2)
    ending_soon_count = sum(1 for r in deduped if r.status == "ending_soon")
    by_discipline: Dict[str, int] = {}
    by_type: Dict[str, int] = {}
    by_platform: Dict[str, int] = {}

    for r in deduped:
        by_discipline[r.discipline] = by_discipline.get(r.discipline, 0) + 1
        by_type[r.project_type] = by_type.get(r.project_type, 0) + 1
        by_platform[r.platform] = by_platform.get(r.platform, 0) + 1

    serialized_records = [r.to_dict() for r in deduped]

    metadata: Dict[str, Any] = {
        "generated_at": now_iso,
        "run_date": history_meta["run_date"],
        "total_active": len(deduped),
        "raw_records": raw_count,
        "duplicates_merged": max(0, raw_count - len(deduped)),
        "new_today": history_meta["new_projects"],
        "ending_soon_count": ending_soon_count,
        "total_funding_usd": total_funding_usd,
        "total_prize_usd": total_funding_usd,
        "disciplines_count": len(by_discipline),
        "platforms_count": len(by_platform),
        "by_discipline": by_discipline,
        "by_type": by_type,
        "by_platform": by_platform,
        "fx_source": fx_source,
        "history": history_meta,
        "sources": [s.to_dict() for s in statuses],
    }

    sources_dict: Dict[str, Any] = {
        s.name: {
            "count": s.count,
            "status": "ok" if s.status in ("ok", "cached") else "error",
            "error": s.error,
        }
        for s in statuses
    }

    payload: Dict[str, Any] = {
        "generated_at": now_iso,
        "total_count": len(deduped),
        "active_count": len(deduped),
        "sources": sources_dict,
        "metadata": metadata,
        "meta": metadata,
        "projects": serialized_records,
        "competitions": serialized_records,
    }

    write_outputs(payload, deduped)
    return payload


def write_outputs(payload: Dict[str, Any], records: List[ResearchProjectRecord]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    projects_json = DATA_DIR / "projects.json"
    competitions_json = DATA_DIR / "competitions.json"
    projects_csv = DATA_DIR / "projects.csv"
    competitions_csv = DATA_DIR / "competitions.csv"

    encoded = json.dumps(payload, ensure_ascii=False, indent=2)
    projects_json.write_text(encoded, encoding="utf-8")
    competitions_json.write_text(encoded, encoding="utf-8")

    for csv_target in (projects_csv, competitions_csv):
        with csv_target.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for rec in records:
                row = rec.to_dict()
                row["tags"] = "; ".join(rec.tags or [])
                writer.writerow({col: row.get(col, "") for col in CSV_COLUMNS})

    if DASHBOARD_PUBLIC_DATA.parent.exists():
        DASHBOARD_PUBLIC_DATA.mkdir(parents=True, exist_ok=True)
        for name in ("projects.json", "competitions.json", "projects.csv", "competitions.csv"):
            shutil.copyfile(DATA_DIR / name, DASHBOARD_PUBLIC_DATA / name)

    logger.info(
        "Wrote %d active research projects & conferences to %s",
        len(records),
        projects_json,
    )

