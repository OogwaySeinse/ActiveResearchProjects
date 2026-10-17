"""Data models for Active Research Projects, Academic Conferences, Workshops, and Grants."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, List, Optional


@dataclass
class ResearchProjectRecord:
    """Unified record representing an active or upcoming research project, conference CFP,
    institute program, open problem collaboration, workshop shared task, or research grant.
    """

    id: str
    title: str
    platform: str  # Host society, research institute, or platform
    source: str  # Scraper module name
    url: str

    # Core 6-field discipline & specialized sub-category
    discipline: str  # Mathematics | Finance | Statistics | Data Science | Artificial Intelligence | Economy
    category: str

    # Project classification
    project_type: str = "conference"  # conference | research_project | workshop_challenge | grant_fellowship | thematic_program
    tier: str = "CORE A* / Top-Tier"  # CORE A* / Top-Tier | Flagship Society | Research Institute | Funded Grant / Award | Open Collaboration
    status: str = "active"  # active | ending_soon | upcoming | rolling

    # Dates & Timeline (ISO YYYY-MM-DD)
    abstract_deadline: Optional[str] = None
    submission_deadline: Optional[str] = None
    notification_date: Optional[str] = None
    event_start_date: Optional[str] = None
    event_end_date: Optional[str] = None
    days_remaining: Optional[int] = None

    # Location & Format
    location: str = "Global / Hybrid"
    format: str = "In-Person"  # In-Person | Hybrid | Virtual / Global

    # Funding, Grants, Awards & Prizes
    funding_raw: str = "Publication / Peer-Reviewed"
    funding_usd: float = 0.0
    funding_currency: str = "USD"

    # Academic Metadata
    venue_code: str = ""
    organizer: str = ""
    lead_researchers: str = ""
    proceedings_publisher: str = ""
    paper_url: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    description: str = ""
    participants_count: Optional[int] = None

    # History & Telemetry
    sources: List[str] = field(default_factory=list)
    first_seen_at: Optional[str] = None
    is_new: bool = False
    scraped_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # Build multi-discipline list starting with primary discipline
        discs: List[str] = [self.discipline] if self.discipline else ["Artificial Intelligence"]
        hay = f"{self.title} {self.category} {self.description} {' '.join(self.tags)}".lower()
        secondary_rules = [
            ("Mathematics", ("math", "lean 4", "stochastic", "pde", "siam", "theorem", "algebra", "geometry")),
            ("Finance", ("finance", "financial", "asset pricing", "portfolio", "microstructure", "icaif", "bachelier", "quant")),
            ("Statistics", ("statistic", "bayesian", "causal", "econometric", "biostat", "ims", "jsm", "probability")),
            ("Data Science", ("data mining", "data science", "kdd", "vldb", "sigmod", "wsdm", "forecasting", "time series")),
            ("Artificial Intelligence", ("artificial intelligence", "machine learning", "deep learning", "neurips", "icml", "iclr", "llm", "neural")),
            ("Economy", ("econom", "macro", "monetary", "nber", "cepr", "assa", "market design")),
        ]
        for disc_name, kws in secondary_rules:
            if disc_name not in discs and any(kw in hay for kw in kws):
                discs.append(disc_name)
            if len(discs) >= 3:
                break

        kind_map = {
            "conference": "conference",
            "research_project": "research_project",
            "workshop_challenge": "workshop_challenge",
            "grant_fellowship": "grant_fellowship",
            "thematic_program": "symposium_seminar",
        }
        mapped_kind = kind_map.get(self.project_type, "conference")

        event_dates_str: Optional[str] = None
        if self.event_start_date and self.event_end_date and self.event_start_date != self.event_end_date:
            event_dates_str = f"{self.event_start_date} to {self.event_end_date}"
        elif self.event_start_date:
            event_dates_str = self.event_start_date

        tier_lower = (self.tier or "").lower()
        normalized_tier = (
            "flagship"
            if any(k in tier_lower for k in ("flagship", "core a*", "top-tier", "award", "grant"))
            else "standard"
        )
        normalized_status = "active" if self.status == "ending_soon" else self.status

        # Provide unified fields for the React dashboard + sibling index consumers
        d["disciplines"] = discs
        d["kind"] = mapped_kind
        d["deadline"] = self.submission_deadline or self.event_start_date
        d["start_date"] = self.event_start_date
        d["end_date"] = self.submission_deadline or self.event_start_date
        d["event_dates"] = event_dates_str
        d["prize_pool_usd"] = self.funding_usd if self.funding_usd > 0 else None
        d["prize_pool_raw"] = self.funding_raw
        d["currency"] = self.funding_currency
        d["tier_flag"] = normalized_tier
        d["status_normalized"] = normalized_status
        d["name"] = self.title
        d["prize"] = self.funding_raw
        d["prize_raw"] = self.funding_raw
        d["prize_usd"] = self.funding_usd
        d["competition_type"] = self.project_type
        d["co_authors"] = self.lead_researchers
        d["journal_venue"] = self.venue_code or self.proceedings_publisher
        d["is_research"] = True
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ResearchProjectRecord":
        known = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        filtered = {k: v for k, v in d.items() if k in known}
        return cls(**filtered)


@dataclass
class SourceStatus:
    name: str
    label: str
    status: str  # ok | cached | degraded | error
    count: int
    duration_ms: int
    error: Optional[str] = None
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

