"""Deduplication and field-level enrichment across research and conference scrapers."""
from __future__ import annotations

import re
from typing import Dict, List

from scraper.models import ResearchProjectRecord
from scraper.normalize import canonicalize_url


def _norm_title_key(title: str, venue_code: str = "") -> str:
    base = re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()
    base = re.sub(r"\b(the|annual|international|conference|on|and|of|for|call|papers|cfp)\b", "", base)
    base = re.sub(r"\s+", " ", base).strip()
    if venue_code:
        v = re.sub(r"[^a-z0-9]+", "", venue_code.lower())
        if len(v) >= 4 and len(base) < 12:
            return f"{v}:{base}"
    return base


def _merge_two(primary: ResearchProjectRecord, secondary: ResearchProjectRecord) -> ResearchProjectRecord:
    """Merge metadata from secondary into primary in place."""
    sources = list(dict.fromkeys([*(primary.sources or [primary.source]), *(secondary.sources or [secondary.source])]))
    primary.sources = sources

    if secondary.funding_usd > primary.funding_usd:
        primary.funding_usd = secondary.funding_usd
        primary.funding_raw = secondary.funding_raw
        primary.funding_currency = secondary.funding_currency

    if not primary.abstract_deadline and secondary.abstract_deadline:
        primary.abstract_deadline = secondary.abstract_deadline
    if not primary.submission_deadline and secondary.submission_deadline:
        primary.submission_deadline = secondary.submission_deadline
    if not primary.notification_date and secondary.notification_date:
        primary.notification_date = secondary.notification_date
    if not primary.event_start_date and secondary.event_start_date:
        primary.event_start_date = secondary.event_start_date
    if not primary.event_end_date and secondary.event_end_date:
        primary.event_end_date = secondary.event_end_date
    if not primary.paper_url and secondary.paper_url:
        primary.paper_url = secondary.paper_url
    if not primary.lead_researchers and secondary.lead_researchers:
        primary.lead_researchers = secondary.lead_researchers
    if not primary.proceedings_publisher and secondary.proceedings_publisher:
        primary.proceedings_publisher = secondary.proceedings_publisher
    if len(secondary.description or "") > len(primary.description or ""):
        primary.description = secondary.description

    merged_tags = list(dict.fromkeys([*(primary.tags or []), *(secondary.tags or [])]))
    primary.tags = merged_tags[:14]
    return primary


def deduplicate_records(records: List[ResearchProjectRecord]) -> List[ResearchProjectRecord]:
    """Deduplicate research projects and conferences by canonical URL and normalized title key."""
    by_url: Dict[str, ResearchProjectRecord] = {}
    by_title: Dict[str, ResearchProjectRecord] = {}
    unique: List[ResearchProjectRecord] = []

    for rec in records:
        if not rec.sources:
            rec.sources = [rec.source]

        url_key = canonicalize_url(rec.url)
        title_key = _norm_title_key(rec.title, rec.venue_code)

        existing = None
        if url_key and url_key in by_url and len(url_key) > 22:
            existing = by_url[url_key]
        elif title_key and title_key in by_title and len(title_key) >= 8:
            existing = by_title[title_key]

        if existing is not None:
            _merge_two(existing, rec)
        else:
            unique.append(rec)
            if url_key and len(url_key) > 22:
                by_url[url_key] = rec
            if title_key and len(title_key) >= 8:
                by_title[title_key] = rec

    return unique

