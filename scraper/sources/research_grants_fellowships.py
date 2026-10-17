"""Scraper for Active Research Grants, Fellowships, Visiting Scholar Calls, and Academic Awards."""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from scraper.models import ResearchProjectRecord
from scraper.normalize import compute_deadline_status, make_id, parse_funding
from scraper.sources.ai_ds_conferences import _rolling_dates

SOURCE_NAME = "research_grants_fellowships"
SOURCE_LABEL = "Research Grants, Fellowships & Academic Awards (NSF / ERC / Simons / Sloan / INQUIRE / Q-Group)"

GRANTS_AND_FELLOWSHIPS: List[Dict[str, Any]] = [
    {
        "code": "NSF-DMS-MathStats",
        "title_tpl": "NSF DMS {year} — Division of Mathematical Sciences & Statistics Research Grants",
        "platform": "National Science Foundation (NSF)",
        "discipline": "Mathematics",
        "category": "Probability, Stochastic Analysis & PDEs",
        "project_type": "grant_fellowship",
        "tier": "Funded Grant / Award",
        "sub_month": 11,
        "sub_day": 15,
        "start_month": 7,
        "start_day": 1,
        "duration": 365,
        "location": "United States Universities & Research Institutes",
        "format": "Virtual / Global",
        "funding": "$300,000 Typical 3-Year NSF DMS Investigator Grant",
        "organizer": "U.S. National Science Foundation — Directorate for Mathematical and Physical Sciences",
        "chairs": "NSF DMS Program Directors (Algebra, Analysis, Probability, Applied Math, Statistics)",
        "publisher": "NSF Award Search & Public Access Repository",
        "url": "https://www.nsf.gov/MPS/DMS/about.jsp",
        "tags": ["nsf-dms", "research-grant", "mathematics", "probability", "pde", "algebra", "topology"],
        "description": (
            "Annual NSF Division of Mathematical Sciences funding cycle supporting investigator-initiated research "
            "across Analysis, Probability, Algebra & Number Theory, Applied Mathematics, and Computational Mathematics."
        ),
    },
    {
        "code": "NSF-DMS-Statistics",
        "title_tpl": "NSF Statistics Program {year} — Statistical Theory, Causal Inference & Data Science Grants",
        "platform": "National Science Foundation (NSF)",
        "discipline": "Statistics",
        "category": "High-Dimensional, Mathematical & Nonparametric Statistics",
        "project_type": "grant_fellowship",
        "tier": "Funded Grant / Award",
        "sub_month": 12,
        "sub_day": 15,
        "start_month": 8,
        "start_day": 1,
        "duration": 365,
        "location": "United States Research Institutions",
        "format": "Virtual / Global",
        "funding": "$280,000 NSF Statistical Methodology & Theory Award",
        "organizer": "National Science Foundation (NSF DMS Statistics Program)",
        "chairs": "NSF Statistics Program Officers",
        "publisher": "NSF Award Abstracts",
        "url": "https://new.nsf.gov/funding/opportunities/statistics",
        "tags": ["nsf", "statistics-grant", "high-dimensional-statistics", "causal-inference", "bayesian", "theory"],
        "description": (
            "Core NSF funding solicitation for statistical theory and methodology, high-dimensional inference, "
            "network and spatial data analysis, causal inference, and uncertainty quantification."
        ),
    },
    {
        "code": "ERC-Starting-Consolidator",
        "title_tpl": "ERC {year} — European Research Council Starting & Consolidator Grants (PE1 Math / PE6 AI / SH1 Econ)",
        "platform": "European Research Council (ERC)",
        "discipline": "Mathematics",
        "category": "Pure Mathematics, Algebra, Geometry & Number Theory",
        "project_type": "grant_fellowship",
        "tier": "Funded Grant / Award",
        "sub_month": 10,
        "sub_day": 24,
        "start_month": 9,
        "start_day": 1,
        "duration": 365,
        "location": "European Union & Horizon Europe Associated Countries",
        "format": "Virtual / Global",
        "funding": "€1,500,000 – €2,000,000 5-Year ERC Frontier Research Grant",
        "organizer": "European Research Council (Horizon Europe)",
        "chairs": "ERC Scientific Council Panels PE1 (Mathematics), PE6 (CS/AI) & SH1 (Economics/Finance)",
        "publisher": "CORDIS EU Research Results",
        "url": "https://erc.europa.eu/apply-grant",
        "tags": ["erc", "horizon-europe", "frontier-research", "pe1-mathematics", "pe6-ai", "sh1-economics"],
        "description": (
            "Flagship European frontier research grants (€1.5M–€2.5M over 5 years) across Panel PE1 (Mathematical "
            "Foundations & Statistics), Panel PE6 (AI & Data Science), and Panel SH1 (Economics, Finance & Management)."
        ),
    },
    {
        "code": "Simons-Fellows-Math",
        "title_tpl": "Simons Fellows in Mathematics {year} — Sabbatical & Targeted Research Grants",
        "platform": "Simons Foundation",
        "discipline": "Mathematics",
        "category": "Pure Mathematics, Algebra, Geometry & Number Theory",
        "project_type": "grant_fellowship",
        "tier": "Funded Grant / Award",
        "sub_month": 9,
        "sub_day": 28,
        "start_month": 7,
        "start_day": 1,
        "duration": 365,
        "location": "United States & Canada",
        "format": "Virtual / Global",
        "funding": "$140,000 Simons Fellowship Sabbatical Salary & Research Support",
        "organizer": "Simons Foundation — Mathematics and Physical Sciences (MPS)",
        "chairs": "Simons Foundation MPS Scientific Advisory Board",
        "publisher": "Simons Foundation MPS Division",
        "url": "https://www.simonsfoundation.org/funding-opportunities/",
        "tags": ["simons-foundation", "mathematics-fellowship", "pure-mathematics", "theoretical-computer-science"],
        "description": (
            "Supports tenured research mathematicians with full-year academic research leaves to focus "
            "exclusively on foundational problems in pure and applied mathematics."
        ),
    },
    {
        "code": "Sloan-Research-Fellowship",
        "title_tpl": "Sloan Research Fellowships {year} — Mathematics, Economics & Computer Science",
        "platform": "Alfred P. Sloan Foundation",
        "discipline": "Economy",
        "category": "Microeconomic Theory, Market Design & Game Theory",
        "project_type": "grant_fellowship",
        "tier": "Funded Grant / Award",
        "sub_month": 9,
        "sub_day": 15,
        "start_month": 2,
        "start_day": 18,
        "duration": 365,
        "location": "United States & Canada Research Universities",
        "format": "Virtual / Global",
        "funding": "$75,000 Flexible 2-Year Early-Career Research Fellowship",
        "organizer": "Alfred P. Sloan Foundation",
        "chairs": "Sloan Selection Committees in Mathematics, Economics, and Computer Science",
        "publisher": "Alfred P. Sloan Foundation Fellows Registry",
        "url": "https://sloan.org/fellowships",
        "tags": ["sloan-fellowship", "early-career", "economics", "mathematics", "computer-science", "ai"],
        "description": (
            "Prestigious early-career research fellowships awarded annually to outstanding tenure-track faculty "
            "in Economics, Mathematics, Statistics, and Artificial Intelligence / Computer Science."
        ),
    },
    {
        "code": "INQUIRE-Europe-Quant",
        "title_tpl": "INQUIRE Europe & UK {year} — Quantitative Investment & Financial Econometrics Research Grants",
        "platform": "INQUIRE Europe",
        "discipline": "Finance",
        "category": "Asset Pricing, Factor Alpha & Portfolio Theory",
        "project_type": "grant_fellowship",
        "tier": "Funded Grant / Award",
        "sub_month": 3,
        "sub_day": 31,
        "start_month": 10,
        "start_day": 12,
        "duration": 180,
        "location": "Europe / Global Academic Institutions",
        "format": "Hybrid",
        "funding": "€15,000 Research Grant + €7,000 Best Paper Prize",
        "organizer": "Institute for Quantitative Investment Research (INQUIRE Europe)",
        "chairs": "INQUIRE Europe Research Committee",
        "publisher": "INQUIRE Europe Seminar & Working Paper Series",
        "url": "https://www.inquire-europe.org/research/",
        "tags": ["inquire-europe", "quantitative-finance", "factor-investing", "portfolio-optimization", "research-grant"],
        "description": (
            "Sponsors academic research projects applying quantitative, statistical, and machine learning methods "
            "to asset pricing, factor investing, derivative pricing, and market microstructure."
        ),
    },
    {
        "code": "Q-Group-Jack-Treynor",
        "title_tpl": "Q-Group {year} — Institute for Quantitative Research in Finance Research Awards",
        "platform": "The Q-Group",
        "discipline": "Finance",
        "category": "Asset Pricing, Factor Alpha & Portfolio Theory",
        "project_type": "grant_fellowship",
        "tier": "Funded Grant / Award",
        "sub_month": 4,
        "sub_day": 15,
        "start_month": 10,
        "start_day": 18,
        "duration": 180,
        "location": "Global Academic Researchers",
        "format": "In-Person",
        "funding": "$20,000 Q-Group Research Grant & Jack Treynor Prize",
        "organizer": "The Institute for Quantitative Research in Finance (Q-Group)",
        "chairs": "Q-Group Academic Research Committee",
        "publisher": "Financial Analysts Journal / Q-Group Symposia",
        "url": "https://www.q-group.org/",
        "tags": ["q-group", "quantitative-finance", "asset-allocation", "risk-management", "treynor-prize"],
        "description": (
            "Competitive academic grant program funding empirical and theoretical research in quantitative "
            "asset management, systematic trading, and financial market structure."
        ),
    },
    {
        "code": "EIF-Louis-Bachelier",
        "title_tpl": "Europlace Institute of Finance (EIF) & Louis Bachelier {year} — Call for Research Projects",
        "platform": "Institut Louis Bachelier / EIF",
        "discipline": "Finance",
        "category": "Derivatives, Quantitative Risk & Mathematical Finance",
        "project_type": "grant_fellowship",
        "tier": "Funded Grant / Award",
        "sub_month": 5,
        "sub_day": 10,
        "start_month": 11,
        "start_day": 5,
        "duration": 180,
        "location": "Paris / Global Academic Teams",
        "format": "Hybrid",
        "funding": "€10,000 per Selected Financial Mathematics & Economics Research Project",
        "organizer": "Europlace Institute of Finance & Institut Louis Bachelier",
        "chairs": "EIF Scientific Council",
        "publisher": "Cahiers Louis Bachelier / Finance & Stochastics",
        "url": "https://www.institutlouisbachelier.org/en/",
        "tags": ["louis-bachelier", "eif", "mathematical-finance", "systemic-risk", "climate-finance", "ai-in-finance"],
        "description": (
            "Annual call for research projects funding 15–20 academic teams working on quantitative finance, "
            "stochastic volatility, systemic risk, AI in finance, and climate macro-finance."
        ),
    },
    {
        "code": "NBER-Economics-of-AI",
        "title_tpl": "NBER {year} — Economics of Artificial Intelligence, Productivity & Macro Research Grants",
        "platform": "NBER",
        "discipline": "Economy",
        "category": "Labor, Development, Public & Climate Economics",
        "project_type": "grant_fellowship",
        "tier": "Funded Grant / Award",
        "sub_month": 4,
        "sub_day": 1,
        "start_month": 9,
        "start_day": 18,
        "duration": 180,
        "location": "Toronto / Cambridge, MA",
        "format": "In-Person",
        "funding": "$40,000 NBER Small Grant & Pre-Doctoral Fellowship",
        "organizer": "National Bureau of Economic Research (NBER)",
        "chairs": "Ajay Agrawal, Joshua Gans, Avi Goldfarb & Catherine Tucker",
        "publisher": "University of Chicago Press / NBER Working Papers",
        "url": "https://www.nber.org/calls-for-papers-and-proposals",
        "tags": ["nber", "economics-of-ai", "productivity", "labor-economics", "market-design", "research-grant"],
        "description": (
            "NBER research calls and grants examining the macroeconomic, labor market, industrial organization, "
            "and econometric impacts of generative AI and automation."
        ),
    },
    {
        "code": "DARPA-AI4Math-expMath",
        "title_tpl": "DARPA expMath & ARIA {year} — Exponentiating Mathematics & Formal AI Reasoning BAA",
        "platform": "DARPA / ARIA Research",
        "discipline": "Artificial Intelligence",
        "category": "Large Language Models, Reasoning & Autonomous Agents",
        "project_type": "grant_fellowship",
        "tier": "Funded Grant / Award",
        "sub_month": 6,
        "sub_day": 30,
        "start_month": 10,
        "start_day": 1,
        "duration": 365,
        "location": "United States / United Kingdom / International Consortia",
        "format": "Virtual / Global",
        "funding": "$1,500,000 Multi-Year Cooperative Research Agreement",
        "organizer": "DARPA Defense Sciences Office & UK ARIA",
        "chairs": "DARPA Mathematical Sciences & AI Program Managers",
        "publisher": "DARPA Technical Reports & Open-Source Formal Libraries",
        "url": "https://www.darpa.mil/work-with-us/opportunities",
        "tags": ["darpa", "expmath", "ai4math", "formal-verification", "lean4", "autoformalization"],
        "description": (
            "Research solicitation funding AI co-authors capable of decomposing frontier mathematical conjectures, "
            "autoformalizing lemmas in Lean 4, and accelerating pure mathematics research."
        ),
    },
]


def scrape_research_grants_fellowships(today: Optional[date] = None) -> List[ResearchProjectRecord]:
    """Return active and upcoming research grants, fellowships, and academic award calls."""
    ref = today or datetime.now(timezone.utc).date()
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    records: List[ResearchProjectRecord] = []

    for spec in GRANTS_AND_FELLOWSHIPS:
        dates = _rolling_dates(
            ref,
            sub_month=spec["sub_month"],
            sub_day=spec["sub_day"],
            start_month=spec["start_month"],
            start_day=spec["start_day"],
            duration_days=spec["duration"],
        )
        is_active, status, days_rem = compute_deadline_status(
            dates["submission_deadline"],
            dates["event_start_date"],
            dates["event_end_date"],
            today=ref,
        )
        if not is_active:
            continue

        year = dates["year"]
        title = spec["title_tpl"].format(year=year)
        funding_raw, funding_usd, funding_cur = parse_funding(spec.get("funding"))

        records.append(
            ResearchProjectRecord(
                id=make_id(SOURCE_NAME, f"{spec['code']}-{year}"),
                title=title,
                platform=spec["platform"],
                source=SOURCE_NAME,
                url=spec["url"],
                discipline=spec["discipline"],
                category=spec["category"],
                project_type=spec["project_type"],
                tier=spec["tier"],
                status=status,
                abstract_deadline=dates["abstract_deadline"],
                submission_deadline=dates["submission_deadline"],
                notification_date=dates["notification_date"],
                event_start_date=dates["event_start_date"],
                event_end_date=dates["event_end_date"],
                days_remaining=days_rem,
                location=spec["location"],
                format=spec["format"],
                funding_raw=funding_raw,
                funding_usd=funding_usd,
                funding_currency=funding_cur,
                venue_code=f"{spec['code']} {year}",
                organizer=spec["organizer"],
                lead_researchers=spec["chairs"],
                proceedings_publisher=spec["publisher"],
                tags=list(spec["tags"]),
                description=spec["description"],
                scraped_at=now_iso,
            )
        )

    return records

