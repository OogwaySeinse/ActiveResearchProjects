"""Unit tests for deduplication and sourcescrapers across the 6 disciplines."""
from __future__ import annotations

from datetime import date

from scraper.dedupe import deduplicate_records
from scraper.models import ResearchProjectRecord
from scraper.normalize import DISCIPLINES
from scraper.sources.ai_ds_conferences import scrape_ai_ds_conferences
from scraper.sources.finance_econ_conferences import scrape_finance_econ_conferences
from scraper.sources.math_stats_conferences import scrape_math_stats_conferences
from scraper.sources.open_research_projects import scrape_open_research_projects
from scraper.sources.research_grants_fellowships import scrape_research_grants_fellowships


def test_deduplicate_merges_records_with_same_url() -> None:
    r1 = ResearchProjectRecord(
        id="a1",
        title="NeurIPS 2027 — Conference on Neural Information Processing Systems",
        platform="NeurIPS",
        source="src_a",
        url="https://neurips.cc/",
        discipline="Artificial Intelligence",
        category="Deep Learning, Foundation Models & Representation Learning",
        funding_raw="Peer-Reviewed",
        funding_usd=0.0,
        tags=["neurips"],
    )
    r2 = ResearchProjectRecord(
        id="a2",
        title="NeurIPS 2027 — Conference on Neural Information Processing Systems",
        platform="NeurIPS",
        source="src_b",
        url="https://www.neurips.cc",
        discipline="Artificial Intelligence",
        category="Deep Learning, Foundation Models & Representation Learning",
        funding_raw="Travel Award $2,500",
        funding_usd=2500.0,
        paper_url="https://neurips.cc/cfp",
        tags=["foundation-models"],
    )
    deduped = deduplicate_records([r1, r2])
    assert len(deduped) == 1
    merged = deduped[0]
    assert merged.funding_usd == 2500.0
    assert merged.paper_url == "https://neurips.cc/cfp"
    assert "neurips" in merged.tags and "foundation-models" in merged.tags
    assert set(merged.sources) == {"src_a", "src_b"}


def test_all_core_scrapers_cover_all_six_disciplines() -> None:
    ref = date(2026, 10, 17)
    records = []
    records.extend(scrape_ai_ds_conferences(today=ref))
    records.extend(scrape_math_stats_conferences(today=ref))
    records.extend(scrape_finance_econ_conferences(today=ref))
    records.extend(scrape_open_research_projects(today=ref))
    records.extend(scrape_research_grants_fellowships(today=ref))

    assert len(records) >= 50
    present_disciplines = {r.discipline for r in records}
    assert present_disciplines == set(DISCIPLINES)

