"""Scraper for Active Collaborative Research Projects, Lean 4 Formalizations, and Open Research Benchmarks."""
from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from scraper.http import fetch_json
from scraper.models import ResearchProjectRecord
from scraper.normalize import compute_deadline_status, make_id, parse_funding

logger = logging.getLogger(__name__)

SOURCE_NAME = "open_research_projects"
SOURCE_LABEL = "Live Open Research Projects (Lean 4 Formalization / Polymath / AIMO / QuantEcon / I4R)"

OPEN_RESEARCH_PROJECTS: List[Dict[str, Any]] = [
    {
        "code": "Lean4-FLT",
        "title": "Fermat's Last Theorem (FLT) Formalization Project in Lean 4",
        "platform": "Lean 4 / Imperial College London",
        "discipline": "Mathematics",
        "category": "Formalization, Lean 4 & Automated Theorem Proving",
        "project_type": "research_project",
        "tier": "Open Collaboration",
        "submission_deadline": None,
        "event_start_date": "2024-10-01",
        "event_end_date": "2029-09-30",
        "is_rolling": True,
        "location": "Virtual / Imperial College London (GitHub & Zulip)",
        "format": "Virtual / Global",
        "funding": "£3,500,000 EPSRC Grant + Open Blueprint Micro-Tasks",
        "organizer": "Imperial College London & LeanProver Community",
        "lead_researchers": "Prof. Kevin Buzzard, Richard Taylor & Mathlib Contributors",
        "publisher": "Lean 4 Mathlib / Interactive Blueprint",
        "url": "https://imperialcollegelondon.github.io/FLT/",
        "paper_url": "https://github.com/ImperialCollegeLondon/FLT",
        "github_repo": "ImperialCollegeLondon/FLT",
        "tags": ["lean4", "mathlib", "number-theory", "fermats-last-theorem", "modular-forms", "galois-representations"],
        "description": (
            "EPSRC-backed multi-year open mathematical research collaboration formalizing the proof of "
            "Fermat's Last Theorem in the Lean 4 theorem prover using modular forms and Galois representations."
        ),
    },
    {
        "code": "Lean4-PNT-Plus",
        "title": "PrimeNumberTheoremAnd (PNT+) — Analytic Number Theory Formalization in Lean 4",
        "platform": "Lean 4 / Mathlib Collaboration",
        "discipline": "Mathematics",
        "category": "Formalization, Lean 4 & Automated Theorem Proving",
        "project_type": "research_project",
        "tier": "Open Collaboration",
        "submission_deadline": None,
        "event_start_date": "2024-01-15",
        "event_end_date": "2028-12-31",
        "is_rolling": True,
        "location": "Virtual / Global (Lean Zulip & GitHub)",
        "format": "Virtual / Global",
        "funding": "Open Academic Co-Authorship & Mathlib Integration",
        "organizer": "Rutgers University & UCLA Mathematics",
        "lead_researchers": "Prof. Alex Kontorovich, Prof. Terence Tao & Contributors",
        "publisher": "Lean 4 Blueprint / Mathlib",
        "url": "https://alexkontorovich.github.io/PrimeNumberTheoremAnd/web/",
        "paper_url": "https://github.com/AlexKontorovich/PrimeNumberTheoremAnd",
        "github_repo": "AlexKontorovich/PrimeNumberTheoremAnd",
        "tags": ["lean4", "prime-number-theorem", "analytic-number-theory", "wiener-ikahara", "complex-analysis"],
        "description": (
            "Active collaborative formalization of the Prime Number Theorem with error terms, Wiener-Ikehara "
            "Tauberian theorems, and explicit Chebotarev density bounds in Lean 4."
        ),
    },
    {
        "code": "Lean4-PFR",
        "title": "Polynomial Freiman-Ruzsa (PFR) & Additive Combinatorics Blueprint in Lean 4",
        "platform": "Lean 4 / UCLA & Cambridge",
        "discipline": "Mathematics",
        "category": "Formalization, Lean 4 & Automated Theorem Proving",
        "project_type": "research_project",
        "tier": "Open Collaboration",
        "submission_deadline": None,
        "event_start_date": "2023-11-18",
        "event_end_date": "2028-12-31",
        "is_rolling": True,
        "location": "Virtual / Global",
        "format": "Virtual / Global",
        "funding": "Open Mathematical Research Collaboration",
        "organizer": "UCLA & University of Cambridge",
        "lead_researchers": "Terence Tao, Yaël Dillies, Bhavik Mehta & Contributors",
        "publisher": "Lean 4 Blueprint / Forum of Mathematics, Pi",
        "url": "https://teorth.github.io/pfr/",
        "paper_url": "https://arxiv.org/abs/2311.05762",
        "github_repo": "teorth/pfr",
        "tags": ["lean4", "additive-combinatorics", "entropic-methods", "marton-conjecture", "formalization"],
        "description": (
            "Collaborative formalization of the Polynomial Freiman-Ruzsa (Marton's) Conjecture and subsequent "
            "entropic additive combinatorics extensions in Lean 4."
        ),
    },
    {
        "code": "Lean4-Carleson",
        "title": "Carleson's Theorem & Metric Space Harmonic Analysis Formalization in Lean 4",
        "platform": "Lean 4 / Bonn & Eindhoven",
        "discipline": "Mathematics",
        "category": "Probability, Stochastic Analysis & PDEs",
        "project_type": "research_project",
        "tier": "Open Collaboration",
        "submission_deadline": None,
        "event_start_date": "2024-04-01",
        "event_end_date": "2028-12-31",
        "is_rolling": True,
        "location": "Virtual / University of Bonn",
        "format": "Virtual / Global",
        "funding": "ERC & Open Formalization Collaboration",
        "organizer": "University of Bonn & Lean Community",
        "lead_researchers": "Floris van Doorn, Christoph Thiele & Harmonic Analysis Team",
        "publisher": "Lean 4 Blueprint / arXiv",
        "url": "https://florisvandoorn.com/carleson/",
        "paper_url": "https://github.com/fpvandoorn/carleson",
        "github_repo": "fpvandoorn/carleson",
        "tags": ["lean4", "harmonic-analysis", "carleson-theorem", "fourier-series", "measure-theory"],
        "description": (
            "Open formalization of generalized Carleson theorems on doubling metric measure spaces and "
            "almost-everywhere convergence of Fourier series in Lean 4."
        ),
    },
    {
        "code": "Lean4-Equational",
        "title": "Equational Theories Project — 22 Million Magma Implication Graph in Lean 4",
        "platform": "Lean 4 / Polymath Collaboration",
        "discipline": "Mathematics",
        "category": "Pure Mathematics, Algebra, Geometry & Number Theory",
        "project_type": "research_project",
        "tier": "Open Collaboration",
        "submission_deadline": None,
        "event_start_date": "2024-09-25",
        "event_end_date": "2028-12-31",
        "is_rolling": True,
        "location": "Virtual / Global",
        "format": "Virtual / Global",
        "funding": "Open Polymath Co-Authorship & Automated ATP Exploration",
        "organizer": "Lean Community & Polymath",
        "lead_researchers": "Terence Tao, Pietro Monticone & 100+ Contributors",
        "publisher": "Lean 4 / arXiv Collaborative Monograph",
        "url": "https://teorth.github.io/equational_theories/",
        "paper_url": "https://github.com/teorth/equational_theories",
        "github_repo": "teorth/equational_theories",
        "tags": ["lean4", "universal-algebra", "equational-theories", "automated-theorem-proving", "polymath"],
        "description": (
            "Large-scale collaborative mathematics project combining human proof engineering, SAT/Vampire ATPs, "
            "and Lean 4 to resolve the implication graph of 4,694 equational laws for magmas."
        ),
    },
    {
        "code": "AIMO-Prize",
        "title": "AI Mathematical Olympiad (AIMO) — $10M Open-Source Mathematical Reasoning Initiative",
        "platform": "AIMO Prize / XTX Markets",
        "discipline": "Mathematics",
        "category": "Formalization, Lean 4 & Automated Theorem Proving",
        "project_type": "research_project",
        "tier": "Funded Grant / Award",
        "submission_deadline": "2027-04-15",
        "event_start_date": "2026-01-01",
        "event_end_date": "2027-07-15",
        "is_rolling": False,
        "location": "Global / IMO Host Venue",
        "format": "Virtual / Global",
        "funding": "$10,000,000 Total AIMO Prize Pool ($2.1M Progress Prizes)",
        "organizer": "XTX Markets, Fields Institute & IMO Advisory Board",
        "lead_researchers": "Geoff Smith, Terence Tao, Timothy Gowers & Po-Shen Loh",
        "publisher": "AIMO Open-Weights & Technical Reports",
        "url": "https://aimoprize.com/",
        "paper_url": "https://aimoprize.com/updates",
        "tags": ["aimo", "mathematical-reasoning", "olympiad-math", "llms", "tool-integrated-reasoning", "xtx-markets"],
        "description": (
            "Flagship $10M research initiative driving open-weights AI models capable of solving International "
            "Mathematical Olympiad (IMO) and national olympiad-level problems in algebra, combinatorics, and number theory."
        ),
    },
    {
        "code": "FrontierMath-Epoch",
        "title": "FrontierMath — Research-Level Mathematical Benchmark & Open Problem Evaluation",
        "platform": "Epoch AI",
        "discipline": "Mathematics",
        "category": "Pure Mathematics, Algebra, Geometry & Number Theory",
        "project_type": "research_project",
        "tier": "Research Institute",
        "submission_deadline": None,
        "event_start_date": "2024-11-08",
        "event_end_date": "2028-12-31",
        "is_rolling": True,
        "location": "Virtual / San Francisco, USA",
        "format": "Virtual / Global",
        "funding": "$3,000–$10,000 per Contributed Research Problem",
        "organizer": "Epoch AI",
        "lead_researchers": "Elliot Glazer, Fields Medalists & 60+ Research Mathematicians",
        "publisher": "arXiv / Epoch AI Benchmark Suite",
        "url": "https://epoch.ai/frontiermath",
        "paper_url": "https://arxiv.org/abs/2411.04872",
        "tags": ["frontiermath", "research-mathematics", "algebraic-geometry", "number-theory", "ai-evaluation"],
        "description": (
            "Ongoing benchmark and problem-authoring program commissioning original, unpublished research-grade "
            "mathematics problems across algebraic geometry, analytic number theory, and category theory."
        ),
    },
    {
        "code": "I4R-Replication",
        "title": "Institute for Replication (I4R) — Global Economics, Finance & Political Science Replication Games",
        "platform": "Institute for Replication (I4R)",
        "discipline": "Economy",
        "category": "Econometrics, Panel Data & Structural Estimation",
        "project_type": "research_project",
        "tier": "Open Collaboration",
        "submission_deadline": "2027-03-31",
        "event_start_date": "2026-01-01",
        "event_end_date": "2027-12-31",
        "is_rolling": True,
        "location": "Ottawa / Oslo / Chicago / London / Global",
        "format": "Hybrid",
        "funding": "Co-Authored Meta-Paper in Top Economics Journals + Travel Support",
        "organizer": "Institute for Replication (I4R)",
        "lead_researchers": "Prof. Abel Brodeur & I4R Editorial Board",
        "publisher": "I4R Discussion Paper Series / Nature Human Behaviour / AER",
        "url": "https://i4replication.org/",
        "paper_url": "https://i4replication.org/games.html",
        "tags": ["replication", "econometrics", "aer", "qje", "journal-of-finance", "reproducibility", "causal-inference"],
        "description": (
            "Active collaborative research initiative organizing Replication Games globally where teams of "
            "economists, econometricians, and finance researchers reproduce and stress-test papers in AER, QJE, JPE, Econometrica, and JoF."
        ),
    },
    {
        "code": "QuantEcon-Project",
        "title": "QuantEcon — Open-Source Quantitative Economics, Dynamic Programming & JAX Modeling",
        "platform": "QuantEcon (NumFOCUS / Sloan)",
        "discipline": "Economy",
        "category": "Macroeconomics, Monetary Policy & Central Banking",
        "project_type": "research_project",
        "tier": "Open Collaboration",
        "submission_deadline": None,
        "event_start_date": "2024-01-01",
        "event_end_date": "2028-12-31",
        "is_rolling": True,
        "location": "New York / Canberra / Virtual",
        "format": "Virtual / Global",
        "funding": "Sloan Foundation & NumFOCUS Research Fellowships ($10,000)",
        "organizer": "QuantEcon Inc. (NYU & ANU)",
        "lead_researchers": "Nobel Laureate Thomas J. Sargent & Prof. John Stachurski",
        "publisher": "QuantEcon Lecture Series & Cambridge University Press",
        "url": "https://quantecon.org/",
        "paper_url": "https://github.com/QuantEcon",
        "tags": ["quantecon", "macroeconomics", "dynamic-programming", "jax", "markov-chains", "general-equilibrium"],
        "description": (
            "Open research collaboration led by Nobel Laureate Thomas Sargent and John Stachurski developing "
            "GPU-accelerated JAX/Python computational macroeconomics, dynamic programming, and asset pricing models."
        ),
    },
    {
        "code": "DoubleML-Causal",
        "title": "DoubleML & Causal Inference Open Research Initiative (High-Dimensional Econometrics & Stats)",
        "platform": "DoubleML / Munich & MIT",
        "discipline": "Statistics",
        "category": "Causal Inference, Experimental Design & Econometric Stats",
        "project_type": "research_project",
        "tier": "Open Collaboration",
        "submission_deadline": None,
        "event_start_date": "2024-01-01",
        "event_end_date": "2028-12-31",
        "is_rolling": True,
        "location": "Virtual / Hamburg / Munich / MIT",
        "format": "Virtual / Global",
        "funding": "DFG & Open-Source Statistical Methodology Grants",
        "organizer": "University of Hamburg, LMU Munich & MIT Econometrics",
        "lead_researchers": "Victor Chernozhukov, Martin Spindler, Philipp Bach & Contributors",
        "publisher": "Journal of Statistical Software / Annals of Statistics",
        "url": "https://docs.doubleml.org/",
        "paper_url": "https://arxiv.org/abs/1608.00060",
        "tags": ["double-ml", "causal-inference", "neyman-orthogonality", "semiparametric-statistics", "econometrics"],
        "description": (
            "Active statistical and econometric research project implementing Neyman-orthogonal Double/Debiased "
            "Machine Learning for treatment effects, difference-in-differences, and instrumental variables."
        ),
    },
    {
        "code": "ARC-AGI-Prize",
        "title": "ARC Prize — Abstraction and Reasoning Corpus Open General Intelligence Research Benchmark",
        "platform": "ARC Prize Foundation",
        "discipline": "Artificial Intelligence",
        "category": "Large Language Models, Reasoning & Autonomous Agents",
        "project_type": "research_project",
        "tier": "Funded Grant / Award",
        "submission_deadline": "2026-11-30",
        "event_start_date": "2026-03-01",
        "event_end_date": "2026-12-15",
        "is_rolling": False,
        "location": "Virtual / Global",
        "format": "Virtual / Global",
        "funding": "$1,000,000+ ARC-AGI-2 Grand Prize & Paper Awards",
        "organizer": "ARC Prize Foundation (François Chollet & Mike Knoop)",
        "lead_researchers": "François Chollet, Mike Knoop & ARC Scientific Board",
        "publisher": "ARC Prize Technical Reports & NeurIPS Workshop",
        "url": "https://arcprize.org/",
        "paper_url": "https://arxiv.org/abs/1911.01547",
        "tags": ["arc-agi", "program-synthesis", "abstract-reasoning", "test-time-compute", "neuro-symbolic"],
        "description": (
            "Million-dollar open research benchmark challenging AI researchers to build sample-efficient "
            "program synthesis and abstract reasoning architectures on unseen tasks."
        ),
    },
]


def _enrich_github_stars(repo: str) -> Optional[int]:
    """Optionally query GitHub API for star/watcher count as a proxy for active contributors/watchers."""
    data = fetch_json(f"https://api.github.com/repos/{repo}", timeout=5)
    if isinstance(data, dict) and isinstance(data.get("stargazers_count"), int):
        return int(data["stargazers_count"])
    return None


def scrape_open_research_projects(today: Optional[date] = None) -> List[ResearchProjectRecord]:
    """Return active collaborative research projects and open formalization/benchmark initiatives."""
    ref = today or datetime.now(timezone.utc).date()
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    records: List[ResearchProjectRecord] = []

    for spec in OPEN_RESEARCH_PROJECTS:
        sub_dl = spec.get("submission_deadline")
        # Roll forward fixed annual prize deadlines if past
        if sub_dl and sub_dl < ref.isoformat():
            sub_dl = f"{ref.year + 1}-{sub_dl[5:]}"

        is_active, status, days_rem = compute_deadline_status(
            sub_dl,
            spec.get("event_start_date"),
            spec.get("event_end_date"),
            today=ref,
            is_rolling=bool(spec.get("is_rolling", True)),
        )
        if not is_active:
            continue

        funding_raw, funding_usd, funding_cur = parse_funding(spec.get("funding"))
        participants = None
        if spec.get("github_repo"):
            participants = _enrich_github_stars(spec["github_repo"])

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
                paper_url=spec.get("paper_url"),
                tags=list(spec["tags"]),
                description=spec["description"],
                participants_count=participants,
                scraped_at=now_iso,
            )
        )

    return records

