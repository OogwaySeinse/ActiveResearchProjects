"""First-seen tracking and daily snapshot history for Active Research & Conference Projects."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from scraper.models import ResearchProjectRecord

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
HISTORY_DIR = ROOT_DIR / "data" / "history"
FIRST_SEEN_PATH = HISTORY_DIR / "first_seen.json"
SNAPSHOTS_DIR = HISTORY_DIR / "snapshots"


def annotate_with_history(
    records: List[ResearchProjectRecord],
    history_dir: Path = HISTORY_DIR,
) -> Dict[str, Any]:
    """Track first_seen dates, mark newly discovered items, and write daily snapshots."""
    today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    first_seen_file = history_dir / "first_seen.json"
    snapshots_dir = history_dir / "snapshots"

    history_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    first_seen: Dict[str, str] = {}
    if first_seen_file.exists():
        try:
            loaded = json.loads(first_seen_file.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                first_seen = {str(k): str(v) for k, v in loaded.items()}
        except Exception as exc:
            logger.debug("Could not read first_seen.json: %s", exc)

    is_bootstrap = len(first_seen) == 0
    new_count = 0

    for rec in records:
        seen_date = first_seen.get(rec.id)
        if not seen_date:
            first_seen[rec.id] = today_iso
            rec.first_seen_at = today_iso
            # On initial bootstrap, only flag recently announced items as new so not every item is badged NEW
            rec.is_new = False if is_bootstrap else True
            if rec.is_new:
                new_count += 1
        else:
            rec.first_seen_at = seen_date
            rec.is_new = seen_date == today_iso
            if rec.is_new:
                new_count += 1

    try:
        first_seen_file.write_text(
            json.dumps(first_seen, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        snapshot_path = snapshots_dir / f"{today_iso}.json"
        snapshot_path.write_text(
            json.dumps(
                {
                    "date": today_iso,
                    "total_active": len(records),
                    "new_count": new_count,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    except Exception as exc:
        logger.debug("Failed to persist history snapshot: %s", exc)

    return {
        "run_date": today_iso,
        "new_projects": new_count,
        "tracked_total": len(first_seen),
    }

