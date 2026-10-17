"""Registry of all research and conference scraper sources."""
from __future__ import annotations

from typing import Callable, Dict, List, Tuple

from scraper.models import ResearchProjectRecord
from scraper.sources.ai_ds_conferences import (
    SOURCE_LABEL as AI_DS_LABEL,
    SOURCE_NAME as AI_DS_NAME,
    scrape_ai_ds_conferences,
)
from scraper.sources.finance_econ_conferences import (
    SOURCE_LABEL as FIN_ECON_LABEL,
    SOURCE_NAME as FIN_ECON_NAME,
    scrape_finance_econ_conferences,
)
from scraper.sources.math_stats_conferences import (
    SOURCE_LABEL as MATH_STATS_LABEL,
    SOURCE_NAME as MATH_STATS_NAME,
    scrape_math_stats_conferences,
)
from scraper.sources.open_research_projects import (
    SOURCE_LABEL as OPEN_PROJ_LABEL,
    SOURCE_NAME as OPEN_PROJ_NAME,
    scrape_open_research_projects,
)
from scraper.sources.research_grants_fellowships import (
    SOURCE_LABEL as GRANTS_LABEL,
    SOURCE_NAME as GRANTS_NAME,
    scrape_research_grants_fellowships,
)
from scraper.sources.workshop_research_challenges import (
    SOURCE_LABEL as WORKSHOPS_LABEL,
    SOURCE_NAME as WORKSHOPS_NAME,
    scrape_workshop_research_challenges,
)

ScraperFn = Callable[[], List[ResearchProjectRecord]]

ALL_SCRAPERS: Dict[str, Tuple[str, ScraperFn]] = {
    AI_DS_NAME: (AI_DS_LABEL, scrape_ai_ds_conferences),
    MATH_STATS_NAME: (MATH_STATS_LABEL, scrape_math_stats_conferences),
    FIN_ECON_NAME: (FIN_ECON_LABEL, scrape_finance_econ_conferences),
    OPEN_PROJ_NAME: (OPEN_PROJ_LABEL, scrape_open_research_projects),
    GRANTS_NAME: (GRANTS_LABEL, scrape_research_grants_fellowships),
    WORKSHOPS_NAME: (WORKSHOPS_LABEL, scrape_workshop_research_challenges),
}

