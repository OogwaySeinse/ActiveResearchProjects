"""Scraper for Live Academic Workshop Shared Tasks, ENS Challenge Data, CrunchDAO & MLContests Research Tracks."""
from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from scraper.http import fetch_json
from scraper.models import ResearchProjectRecord
from scraper.normalize import (
    compute_deadline_status,
    infer_discipline_and_category,
    make_id,
    parse_funding,
)

logger = logging.getLogger(__name__)

SOURCE_NAME = "workshop_research_challenges"
SOURCE_LABEL = "Academic Workshop Challenges & Quantitative Research Benchmarks (MLContests / CrunchDAO / ENS / Kaggle)"

CURATED_WORKSHOP_CHALLENGES: List[Dict[str, Any]] = [
    {
        "code": "ADIA-Lab-Structural-Break",
        "title": "ADIA Lab Structural Break Research Challenge — Regime Detection in Time Series & Econometrics",
        "platform": "CrunchDAO / ADIA Lab",
        "discipline": "Statistics",
        "category": "Causal Inference, Experimental Design & Econometric Stats",
        "project_type": "workshop_challenge",
        "tier": "Funded Grant / Award",
        "submission_deadline": None,
        "event_start_date": "2025-05-01",
        "event_end_date": "2027-12-31",
        "is_rolling": True,
        "location": "Abu Dhabi / Virtual Global Research Arena",
        "format": "Virtual / Global",
        "funding": "$100,000 USDC Prize Pool + ADIA Lab Symposium Publication",
        "organizer": "Abu Dhabi Investment Authority (ADIA) Lab & CrunchDAO",
        "lead_researchers": "Prof. Marcos López de Prado, Prof. Horst Simon & ADIA Lab Fellows",
        "publisher": "ADIA Lab Research Paper Series",
        "url": "https://hub.crunchdao.com/competitions/structural-break",
        "tags": ["adia-lab", "structural-breaks", "regime-switching", "time-series", "econometrics", "non-stationarity"],
        "description": (
            "Academic research benchmark sponsored by ADIA Lab investigating statistical hypothesis tests and "
            "machine learning detectors for structural breaks and regime shifts in non-stationary stochastic processes."
        ),
    },
    {
        "code": "ENS-QRT-CFM-Benchmarks",
        "title": "ENS Challenge Data — Quantitative Finance, Statistical Physics & Econometrics Academic Benchmarks",
        "platform": "ENS Challenge Data (Paris)",
        "discipline": "Finance",
        "category": "Asset Pricing, Factor Alpha & Portfolio Theory",
        "project_type": "workshop_challenge",
        "tier": "Research Institute",
        "submission_deadline": "2027-02-28",
        "event_start_date": "2026-01-15",
        "event_end_date": "2027-03-31",
        "is_rolling": True,
        "location": "École Normale Supérieure (ENS) Paris & Collège de France",
        "format": "Hybrid",
        "funding": "ENS Academic Certificate + QRT / CFM / AMF Research Awards",
        "organizer": "École Normale Supérieure (ENS Ulm), Collège de France, QRT, CFM & AMF",
        "lead_researchers": "Prof. Stéphane Mallat (Collège de France / ENS) & Quantitative Research Chairs",
        "publisher": "ENS Challenge Data Academic Proceedings",
        "url": "https://challengedata.ens.fr/",
        "tags": ["ens-paris", "stephane-mallat", "qrt", "cfm", "amf", "limit-order-books", "financial-econometrics"],
        "description": (
            "Academic data science and mathematical finance challenges hosted by École Normale Supérieure and "
            "Prof. Stéphane Mallat in partnership with Qube Research & Technologies (QRT), Capital Fund Management (CFM), and AMF."
        ),
    },
    {
        "code": "Wunder-Connectome-LOB",
        "title": "Wunder Fund LOB Predictor — High-Frequency Limit Order Book & Stochastic Microstructure Research",
        "platform": "Wunder Fund Research",
        "discipline": "Finance",
        "category": "Market Microstructure, Order Books & Algorithmic Finance",
        "project_type": "workshop_challenge",
        "tier": "Funded Grant / Award",
        "submission_deadline": None,
        "event_start_date": "2025-09-01",
        "event_end_date": "2027-12-31",
        "is_rolling": True,
        "location": "Virtual / Global",
        "format": "Virtual / Global",
        "funding": "$17,000 Prize Pool + Quantitative Researcher Fast-Track",
        "organizer": "Wunder Fund Quantitative Research",
        "lead_researchers": "Wunder Fund HFT Microstructure Research Group",
        "publisher": "Wundernn Research Benchmarks",
        "url": "https://wundernn.io/",
        "tags": ["limit-order-book", "market-microstructure", "sequence-modeling", "state-space-models", "hft"],
        "description": (
            "Open high-frequency market microstructure research benchmark evaluating sequence architectures "
            "(Transformers, Mamba, Hawkes processes) on raw L2/L3 limit order book state transitions."
        ),
    },
    {
        "code": "Jane-Street-Monthly-Math",
        "title": "Jane Street Monthly Research Puzzle — Combinatorics, Probability Theory & Game Theory",
        "platform": "Jane Street",
        "discipline": "Mathematics",
        "category": "Pure Mathematics, Algebra, Geometry & Number Theory",
        "project_type": "workshop_challenge",
        "tier": "Open Collaboration",
        "submission_deadline": None,
        "event_start_date": "2026-01-01",
        "event_end_date": "2027-12-31",
        "is_rolling": True,
        "location": "New York / London / Hong Kong / Global",
        "format": "Virtual / Global",
        "funding": "Official Hall of Fame Leaderboard + Quantitative Research Recognition",
        "organizer": "Jane Street Quantitative Research & Trading",
        "lead_researchers": "Jane Street Puzzle & Probability Research Team",
        "publisher": "Jane Street Puzzle Archive",
        "url": "https://www.janestreet.com/puzzles/",
        "tags": ["jane-street", "probability-theory", "combinatorics", "number-theory", "game-theory", "markov-chains"],
        "description": (
            "Monthly open mathematical research puzzle requiring exact analytical probability, Diophantine analysis, "
            "optimal stopping, or combinatorial optimization."
        ),
    },
    {
        "code": "M6-Forecasting-Makridakis",
        "title": "Makridakis Forecasting & Uncertainty Quantification Open Research Benchmark (MOFC)",
        "platform": "Makridakis Open Forecasting Center",
        "discipline": "Data Science",
        "category": "Time Series Forecasting & Spatio-Temporal Modeling",
        "project_type": "workshop_challenge",
        "tier": "Research Institute",
        "submission_deadline": None,
        "event_start_date": "2025-01-01",
        "event_end_date": "2027-12-31",
        "is_rolling": True,
        "location": "University of Nicosia / Virtual Global",
        "format": "Virtual / Global",
        "funding": "International Journal of Forecasting Special Issue Publication",
        "organizer": "Makridakis Open Forecasting Center (MOFC) & International Institute of Forecasters",
        "lead_researchers": "Prof. Spyros Makridakis & IIF Editorial Board",
        "publisher": "International Journal of Forecasting (Elsevier)",
        "url": "https://mofc.unic.ac.cy/",
        "tags": ["time-series", "forecasting", "probabilistic-forecasting", "econometrics", "portfolio-decisions"],
        "description": (
            "Flagship empirical forecasting benchmark evaluating statistical, econometric, and foundation time-series "
            "models on distributional accuracy and investment decision utility."
        ),
    },
    {
        "code": "SemEval-ACL-SharedTasks",
        "title": "SemEval — International Workshop on Semantic Evaluation (ACL Shared Research Tasks)",
        "platform": "ACL SIGLEX / SemEval",
        "discipline": "Artificial Intelligence",
        "category": "Large Language Models, Reasoning & Autonomous Agents",
        "project_type": "workshop_challenge",
        "tier": "Flagship Society",
        "submission_deadline": "2027-01-31",
        "event_start_date": "2026-09-01",
        "event_end_date": "2027-07-30",
        "is_rolling": False,
        "location": "Co-located with ACL / NAACL",
        "format": "Hybrid",
        "funding": "Peer-Reviewed System Description Paper in ACL Anthology",
        "organizer": "ACL Special Interest Group on the Lexicon (SIGLEX)",
        "lead_researchers": "SemEval Task Organizers & ACL Chairs",
        "publisher": "ACL Anthology (Proceedings of SemEval)",
        "url": "https://semeval.github.io/",
        "tags": ["semeval", "acl-anthology", "nlp-benchmark", "semantic-evaluation", "shared-task", "paper-track"],
        "description": (
            "Collaborative NLP research evaluation series where participating teams build systems for 15+ shared tasks "
            "and publish peer-reviewed papers in the ACL Anthology."
        ),
    },
    {
        "code": "CLEF-Eval-Labs",
        "title": "CLEF — Conference and Labs of the Evaluation Forum (Information Access, Bio & Data Science Labs)",
        "platform": "CLEF Initiative",
        "discipline": "Data Science",
        "category": "Recommender Systems, Information Retrieval & Web Science",
        "project_type": "workshop_challenge",
        "tier": "Flagship Society",
        "submission_deadline": "2027-04-25",
        "event_start_date": "2026-11-01",
        "event_end_date": "2027-09-12",
        "is_rolling": False,
        "location": "Madrid / Grenoble / Bologna, Europe",
        "format": "In-Person",
        "funding": "Springer LNCS Proceedings & CEUR-WS Working Notes Publication",
        "organizer": "CLEF Association",
        "lead_researchers": "CLEF Lab Chairs",
        "publisher": "Springer Lecture Notes in Computer Science (LNCS)",
        "url": "https://www.clef-initiative.eu/",
        "tags": ["clef", "information-retrieval", "evaluation-labs", "data-science", "lncs-proceedings"],
        "description": (
            "European evaluation forum hosting 12+ collaborative research labs in multimodal retrieval, "
            "scientific claim verification, mathematical question answering, and longitudinal data science."
        ),
    },
]


def _scrape_live_mlcontests(ref: date, now_iso: str) -> List[ResearchProjectRecord]:
    """Fetch live active research/workshop/featured competitions from MLContests JSON feed."""
    data = fetch_json("https://raw.githubusercontent.com/mlcontests/mlcontests.github.io/master/competitions.json", timeout=8)
    if not isinstance(data, dict):
        return []
    raw_list = data.get("competitions")
    if not isinstance(raw_list, list):
        return []

    out: List[ResearchProjectRecord] = []
    for item in raw_list:
        if not isinstance(item, dict):
            continue
        title = str(item.get("name") or item.get("title") or "").strip()
        url = str(item.get("url") or "").strip()
        if not title or not url:
            continue

        end_raw = str(item.get("deadline") or item.get("end") or item.get("end_date") or "")[:10]
        start_raw = str(item.get("start") or item.get("start_date") or "")[:10]
        is_active, status, days_rem = compute_deadline_status(end_raw or None, start_raw or None, today=ref)
        if not is_active:
            continue

        platform = str(item.get("platform") or "MLContests").strip()
        prize_str = str(item.get("prize") or "Research Benchmark").strip()
        funding_raw, funding_usd, funding_cur = parse_funding(prize_str)
        tags_raw = item.get("tags") or []
        tags = [str(t).lower() for t in tags_raw] if isinstance(tags_raw, list) else []
        conference = str(item.get("conference") or "").strip()
        desc = str(item.get("description") or f"Active research challenge on {platform}.").strip()

        disc, cat = infer_discipline_and_category(title, f"{desc} {conference}", tags)

        out.append(
            ResearchProjectRecord(
                id=make_id(SOURCE_NAME, f"mlc-{url}"),
                title=title,
                platform=platform,
                source=SOURCE_NAME,
                url=url,
                discipline=disc,
                category=cat,
                project_type="workshop_challenge",
                tier="CORE A* / Top-Tier" if conference else "Funded Grant / Award",
                status=status,
                submission_deadline=end_raw if len(end_raw) == 10 else None,
                event_start_date=start_raw if len(start_raw) == 10 else None,
                days_remaining=days_rem,
                location=conference or "Virtual / Global",
                format="Virtual / Global",
                funding_raw=funding_raw,
                funding_usd=funding_usd,
                funding_currency=funding_cur,
                venue_code=conference or platform,
                organizer=str(item.get("organizer") or platform),
                lead_researchers=conference or f"{platform} Research Organizers",
                proceedings_publisher=f"{conference} Workshop Proceedings" if conference else platform,
                tags=list(dict.fromkeys([*tags, "research-challenge", platform.lower().replace(" ", "-")]))[:10],
                description=desc,
                scraped_at=now_iso,
            )
        )
    return out


def scrape_workshop_research_challenges(today: Optional[date] = None) -> List[ResearchProjectRecord]:
    """Return active workshop shared tasks and live research challenges."""
    ref = today or datetime.now(timezone.utc).date()
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    records: List[ResearchProjectRecord] = []

    # 1. Live MLContests feed
    records.extend(_scrape_live_mlcontests(ref, now_iso))

    # 2. Curated flagship workshop & research benchmarks
    for spec in CURATED_WORKSHOP_CHALLENGES:
        sub_dl = spec.get("submission_deadline")
        if sub_dl and sub_dl < ref.isoformat():
            sub_dl = f"{ref.year + 1}-{sub_dl[5:]}"

        is_active, status, days_rem = compute_deadline_status(
            sub_dl,
            spec.get("event_start_date"),
            spec.get("event_end_date"),
            today=ref,
            is_rolling=bool(spec.get("is_rolling", False)),
        )
        if not is_active:
            continue

        funding_raw, funding_usd, funding_cur = parse_funding(spec.get("funding"))
        records.append(
            ResearchProjectRecord(
                id=make_id(SOURCE_NAME, spec["code"]),
                title=spec["title"],
                platform=spec["platform"],
                source=SOURCE_NAME,
                url=spec["url"],
                discipline=spec["discipline"],
                category=spec["category"],
                project_type=spec["project_type"],
                tier=spec["tier"],
                status=status,
                submission_deadline=sub_dl,
                event_start_date=spec.get("event_start_date"),
                event_end_date=spec.get("event_end_date"),
                days_remaining=days_rem,
                location=spec["location"],
                format=spec["format"],
                funding_raw=funding_raw,
                funding_usd=funding_usd,
                funding_currency=funding_cur,
                venue_code=spec["code"],
                organizer=spec["organizer"],
                lead_researchers=spec["lead_researchers"],
                proceedings_publisher=spec["publisher"],
                tags=list(spec["tags"]),
                description=spec["description"],
                scraped_at=now_iso,
            )
        )

    return records

