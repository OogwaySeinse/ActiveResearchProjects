"""Scraper for Active & Upcoming Finance and Economy Conferences, NBER/CEPR Calls & Central Bank Symposia."""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from scraper.models import ResearchProjectRecord
from scraper.normalize import compute_deadline_status, make_id, parse_funding
from scraper.sources.ai_ds_conferences import _rolling_dates

SOURCE_NAME = "finance_econ_conferences"
SOURCE_LABEL = "Finance & Economics Conferences (AFA / WFA / EFA / NBER / Econometric Society / CEPR)"

FINANCE_ECON_EVENTS: List[Dict[str, Any]] = [
    # ---------------- FINANCE CONFERENCES & CALLS FOR PAPERS ----------------
    {
        "code": "AFA",
        "title_tpl": "AFA {year} — American Finance Association Annual Meeting",
        "platform": "American Finance Association (AFA)",
        "discipline": "Finance",
        "category": "Asset Pricing, Factor Alpha & Portfolio Theory",
        "project_type": "conference",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 3,
        "sub_day": 15,
        "start_month": 1,
        "start_day": 3,
        "duration": 3,
        "location": "Philadelphia / San Francisco / Boston, USA",
        "format": "In-Person",
        "funding": "Brattle Group & Dimensional Fund Advisors Prizes ($25,000) + PhD Travel Grants",
        "organizer": "American Finance Association (ASSA Joint Meeting)",
        "chairs": "AFA Program Chair & Journal of Finance Editors",
        "publisher": "The Journal of Finance (Wiley)",
        "url": "https://afajof.org/annual-meeting/",
        "tags": ["afa", "asset-pricing", "corporate-finance", "market-microstructure", "journal-of-finance"],
        "description": (
            "Premier global academic conference in financial economics, asset pricing, corporate finance, "
            "market microstructure, and household finance held jointly with ASSA."
        ),
    },
    {
        "code": "WFA",
        "title_tpl": "WFA {year} — Western Finance Association Annual Conference",
        "platform": "Western Finance Association (WFA)",
        "discipline": "Finance",
        "category": "Asset Pricing, Factor Alpha & Portfolio Theory",
        "project_type": "conference",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 11,
        "sub_day": 15,
        "start_month": 6,
        "start_day": 21,
        "duration": 4,
        "location": "Snowbird / Huntington Beach / Seattle",
        "format": "In-Person",
        "funding": "$10,000 Cubist Systematic & Two Sigma Best Paper Awards",
        "organizer": "Western Finance Association",
        "chairs": "WFA Program Committee",
        "publisher": "Review of Financial Studies (RFS) / JFQA",
        "url": "https://westernfinance.org/",
        "tags": ["wfa", "asset-pricing", "quantitative-finance", "derivatives", "empirical-finance"],
        "description": (
            "Highly selective finance conference featuring empirical and theoretical asset pricing, "
            "quantitative investment strategies, derivatives, and financial intermediation."
        ),
    },
    {
        "code": "EFA",
        "title_tpl": "EFA {year} — European Finance Association Annual Meeting",
        "platform": "European Finance Association (EFA)",
        "discipline": "Finance",
        "category": "Asset Pricing, Factor Alpha & Portfolio Theory",
        "project_type": "conference",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 2,
        "sub_day": 1,
        "start_month": 8,
        "start_day": 19,
        "duration": 4,
        "location": "Paris / Bratislava / Zurich / Amsterdam",
        "format": "In-Person",
        "funding": "€10,000 EFA Best Paper & Doctoral Tutorial Stipends",
        "organizer": "European Finance Association",
        "chairs": "EFA Program Chair & Review of Finance Board",
        "publisher": "Review of Finance (Oxford University Press)",
        "url": "https://european-finance.org/",
        "tags": ["efa", "european-finance", "asset-pricing", "sustainable-finance", "market-microstructure"],
        "description": (
            "Leading European conference in financial economics, quantitative asset management, "
            "sustainable finance, banking regulation, and doctoral finance research."
        ),
    },
    {
        "code": "SFS-Cavalcade",
        "title_tpl": "SFS Cavalcade {year} — Society for Financial Studies North America",
        "platform": "Society for Financial Studies (SFS)",
        "discipline": "Finance",
        "category": "Asset Pricing, Factor Alpha & Portfolio Theory",
        "project_type": "conference",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 12,
        "sub_day": 10,
        "start_month": 5,
        "start_day": 18,
        "duration": 4,
        "location": "New Haven / Atlanta / Austin, USA",
        "format": "In-Person",
        "funding": "$5,000 SFS Best Paper Awards in Asset Pricing & Corporate Finance",
        "organizer": "Society for Financial Studies (RFS / RCFS / RAPS)",
        "chairs": "SFS Cavalcade Program Chairs",
        "publisher": "Review of Financial Studies / Review of Asset Pricing Studies",
        "url": "https://sfs.org/sfs-cavalcade-north-america/",
        "tags": ["sfs-cavalcade", "rfs", "asset-pricing", "market-microstructure", "financial-econometrics"],
        "description": (
            "Top-tier academic conference hosted by the Society for Financial Studies (publishers of RFS, RAPS, RCFS) "
            "on asset pricing, market microstructure, and financial econometrics."
        ),
    },
    {
        "code": "Bachelier",
        "title_tpl": "Bachelier {year} — Bachelier Finance Society World Congress on Mathematical Finance",
        "platform": "Bachelier Finance Society",
        "discipline": "Finance",
        "category": "Derivatives, Quantitative Risk & Mathematical Finance",
        "project_type": "conference",
        "tier": "Flagship Society",
        "sub_month": 12,
        "sub_day": 15,
        "start_month": 7,
        "start_day": 6,
        "duration": 5,
        "location": "Rio de Janeiro / Bologna / New York",
        "format": "In-Person",
        "funding": "Bruti-Liberati Prize + Early Career Travel Support",
        "organizer": "Bachelier Finance Society",
        "chairs": "Bachelier Scientific Committee",
        "publisher": "Finance and Stochastics / Mathematical Finance",
        "url": "https://www.bachelierfinance.org/",
        "tags": ["bachelier", "mathematical-finance", "stochastic-volatility", "rough-volatility", "optimal-execution", "derivatives"],
        "description": (
            "World congress of the Bachelier Finance Society covering stochastic calculus in finance, "
            "rough volatility, martingale optimal transport, mean-field games, and optimal execution."
        ),
    },
    {
        "code": "SIAM-FM",
        "title_tpl": "SIAM FM{year_short} — Conference on Financial Mathematics and Engineering",
        "platform": "SIAM Activity Group on Financial Math",
        "discipline": "Finance",
        "category": "Derivatives, Quantitative Risk & Mathematical Finance",
        "project_type": "conference",
        "tier": "Flagship Society",
        "sub_month": 11,
        "sub_day": 20,
        "start_month": 6,
        "start_day": 8,
        "duration": 4,
        "location": "Miami / Philadelphia / Chicago, USA",
        "format": "In-Person",
        "funding": "SIAM SIAG/FME Early Career & Student Paper Prizes ($3,000)",
        "organizer": "Society for Industrial and Applied Mathematics (SIAG/FME)",
        "chairs": "SIAM Financial Mathematics Organizing Committee",
        "publisher": "SIAM Journal on Financial Mathematics (SIFIN)",
        "url": "https://www.siam.org/conferences-events/",
        "tags": ["siam-fm", "financial-mathematics", "limit-order-books", "deep-hedging", "systematic-trading", "sifin"],
        "description": (
            "Brings together mathematical finance theorists and quantitative hedge fund/bank researchers on "
            "deep hedging, limit order book dynamics, systemic risk, and reinforcement learning in finance."
        ),
    },
    {
        "code": "ACM-ICAIF",
        "title_tpl": "ACM ICAIF {year} — International Conference on AI in Finance",
        "platform": "ACM SIGAI / ICAIF",
        "discipline": "Finance",
        "category": "FinTech, Decentralized Finance & Financial AI",
        "project_type": "conference",
        "tier": "Flagship Society",
        "sub_month": 7,
        "sub_day": 22,
        "start_month": 11,
        "start_day": 14,
        "duration": 4,
        "location": "Singapore / New York / London",
        "format": "Hybrid",
        "funding": "ACM DL + Best Paper & FinLLM Workshop Challenges ($15,000)",
        "organizer": "Association for Computing Machinery (ACM)",
        "chairs": "ACM ICAIF Program & Workshop Chairs",
        "publisher": "ACM Digital Library",
        "url": "https://ai-finance.org/",
        "tags": ["icaif", "ai-in-finance", "financial-llms", "limit-order-book", "algorithmic-trading", "synthetic-data"],
        "description": (
            "Premier peer-reviewed academic conference dedicated to AI and Machine Learning in Finance, "
            "including market simulators, financial LLMs, alpha generation, and regulatory technology."
        ),
    },
    {
        "code": "Market-Microstructure",
        "title_tpl": "Stern / ILB {year} — Market Microstructure & High-Frequency Finance Conference",
        "platform": "Institut Louis Bachelier / NYU Stern",
        "discipline": "Finance",
        "category": "Market Microstructure, Order Books & Algorithmic Finance",
        "project_type": "conference",
        "tier": "Flagship Society",
        "sub_month": 2,
        "sub_day": 20,
        "start_month": 5,
        "start_day": 28,
        "duration": 3,
        "location": "Paris / New York",
        "format": "In-Person",
        "funding": "€5,000 Best Paper on Liquidity & Order Book Design",
        "organizer": "Institut Louis Bachelier & NYU Stern Volatility and Risk Institute",
        "chairs": "Microstructure Scientific Committee",
        "publisher": "Journal of Financial Markets / Market Microstructure and Liquidity",
        "url": "https://www.institutlouisbachelier.org/en/",
        "tags": ["market-microstructure", "order-book", "high-frequency-trading", "hawkes-processes", "decentralized-exchanges"],
        "description": (
            "Specialized academic symposium on limit order book modeling, Hawkes point processes, "
            "latency arbitrage, automated market makers (AMMs), and cross-venue price discovery."
        ),
    },
    # ---------------- ECONOMY & ECONOMETRICS CONFERENCES ----------------
    {
        "code": "ASSA-AEA",
        "title_tpl": "ASSA / AEA {year} — Allied Social Science Associations & American Economic Association Meeting",
        "platform": "American Economic Association (AEA)",
        "discipline": "Economy",
        "category": "Labor, Development, Public & Climate Economics",
        "project_type": "conference",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 4,
        "sub_day": 15,
        "start_month": 1,
        "start_day": 3,
        "duration": 3,
        "location": "Philadelphia / San Francisco / Atlanta, USA",
        "format": "In-Person",
        "funding": "AEA Papers and Proceedings Publication",
        "organizer": "American Economic Association & 64 Allied Economics Societies",
        "chairs": "AEA President-Elect & Program Committee",
        "publisher": "AEA Papers and Proceedings / American Economic Review",
        "url": "https://www.aeaweb.org/conference/",
        "tags": ["aea", "assa", "macroeconomics", "microeconomics", "econometrics", "monetary-policy", "trade"],
        "description": (
            "Flagship annual congress of the economics profession featuring AEA, Econometric Society, "
            "AFA, and 60+ allied societies across macroeconomics, econometrics, trade, and industrial organization."
        ),
    },
    {
        "code": "ES-World-Regional",
        "title_tpl": "Econometric Society {year} — North American, European & Asian Meetings (ESEM / NASMES)",
        "platform": "The Econometric Society",
        "discipline": "Economy",
        "category": "Econometrics, Panel Data & Structural Estimation",
        "project_type": "conference",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 2,
        "sub_day": 15,
        "start_month": 8,
        "start_day": 24,
        "duration": 5,
        "location": "Rotterdam / Seoul / Davis / Toronto",
        "format": "In-Person",
        "funding": "Frisch Medal Track & Developing Economy Scholar Travel Grants ($2,500)",
        "organizer": "The Econometric Society",
        "chairs": "Econometric Society Program Committee",
        "publisher": "Econometrica / Quantitative Economics / Theoretical Economics",
        "url": "https://www.econometricsociety.org/meetings",
        "tags": ["econometric-society", "econometrica", "structural-estimation", "panel-data", "economic-theory", "identification"],
        "description": (
            "Premier meetings of the Econometric Society advancing economic theory, structural econometrics, "
            "nonparametric identification, dynamic stochastic general equilibrium, and causal panel methods."
        ),
    },
    {
        "code": "NBER-SI",
        "title_tpl": "NBER Summer Institute {year} — National Bureau of Economic Research Calls for Papers",
        "platform": "NBER",
        "discipline": "Economy",
        "category": "Macroeconomics, Monetary Policy & Central Banking",
        "project_type": "conference",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 3,
        "sub_day": 25,
        "start_month": 7,
        "start_day": 7,
        "duration": 19,
        "location": "Cambridge, Massachusetts, USA",
        "format": "Hybrid",
        "funding": "NBER Working Paper Distribution + Travel Reimbursement",
        "organizer": "National Bureau of Economic Research (NBER)",
        "chairs": "NBER Program Directors (EFG, AP, CF, ME, LS, ITI)",
        "publisher": "NBER Working Paper Series / NBER Macroeconomics Annual",
        "url": "https://www.nber.org/conferences/summer-institute",
        "tags": ["nber", "summer-institute", "macroeconomics", "asset-pricing", "monetary-economics", "ai-economics"],
        "description": (
            "Three-week flagship NBER Summer Institute in Cambridge spanning 50+ specialized workshops in "
            "Economic Fluctuations & Growth, Asset Pricing, Monetary Economics, and Economics of Digitization & AI."
        ),
    },
    {
        "code": "ACM-EC",
        "title_tpl": "ACM EC {year} — Conference on Economics and Computation",
        "platform": "ACM SIGecom",
        "discipline": "Economy",
        "category": "Microeconomic Theory, Market Design & Game Theory",
        "project_type": "conference",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 2,
        "sub_day": 5,
        "start_month": 7,
        "start_day": 7,
        "duration": 5,
        "location": "Stanford / New Haven / London",
        "format": "In-Person",
        "funding": "ACM DL + Best Paper & Student Travel Grants ($2,000)",
        "organizer": "ACM Special Interest Group on Economics and Computation (SIGecom)",
        "chairs": "ACM EC Program Chairs",
        "publisher": "ACM Digital Library / Operations Research / Games and Economic Behavior",
        "url": "https://sigecom.org/conferences/",
        "tags": ["acm-ec", "market-design", "game-theory", "mechanism-design", "auctions", "algorithmic-economics"],
        "description": (
            "Premier conference at the interface of microeconomic theory and computer science, covering "
            "mechanism design, spectrum and ad auctions, matching markets, social choice, and contract theory."
        ),
    },
    {
        "code": "SED",
        "title_tpl": "SED {year} — Society for Economic Dynamics Annual Meeting",
        "platform": "Society for Economic Dynamics (SED)",
        "discipline": "Economy",
        "category": "Macroeconomics, Monetary Policy & Central Banking",
        "project_type": "conference",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 1,
        "sub_day": 15,
        "start_month": 6,
        "start_day": 25,
        "duration": 4,
        "location": "Copenhagen / Barcelona / Buenos Aires / Madison",
        "format": "In-Person",
        "funding": "Review of Economic Dynamics Special Track",
        "organizer": "Society for Economic Dynamics",
        "chairs": "SED Program Committee",
        "publisher": "Review of Economic Dynamics (RED)",
        "url": "https://economicdynamics.org/",
        "tags": ["sed", "macroeconomics", "heterogeneous-agents", "hank", "business-cycles", "fiscal-policy"],
        "description": (
            "Leading dynamic macroeconomics conference focusing on Heterogeneous Agent New Keynesian (HANK) models, "
            "firm dynamics, quantitative trade, sovereign debt, and computational economics."
        ),
    },
    {
        "code": "CEPR-ESSIM",
        "title_tpl": "CEPR {year} — European Summer Symposium in International Macroeconomics & Financial Markets",
        "platform": "CEPR (Centre for Economic Policy Research)",
        "discipline": "Economy",
        "category": "Macroeconomics, Monetary Policy & Central Banking",
        "project_type": "conference",
        "tier": "Flagship Society",
        "sub_month": 2,
        "sub_day": 28,
        "start_month": 7,
        "start_day": 12,
        "duration": 10,
        "location": "Gerzensee (Switzerland) / Paris / Frankfurt",
        "format": "In-Person",
        "funding": "CEPR Discussion Paper Series + Central Bank Travel Support",
        "organizer": "Centre for Economic Policy Research (CEPR) & Study Center Gerzensee",
        "chairs": "CEPR International Macroeconomics & Finance RPN Directors",
        "publisher": "CEPR Discussion Papers / Economic Policy",
        "url": "https://cepr.org/events",
        "tags": ["cepr", "international-macroeconomics", "exchange-rates", "central-banking", "financial-stability"],
        "description": (
            "Flagship European macro-finance research symposium hosted by CEPR and Study Center Gerzensee "
            "on international capital flows, monetary policy transmission, and sovereign risk."
        ),
    },
    {
        "code": "ECB-Forum",
        "title_tpl": "ECB {year} — European Central Bank Forum on Central Banking & Young Economists Prize",
        "platform": "European Central Bank (ECB)",
        "discipline": "Economy",
        "category": "Macroeconomics, Monetary Policy & Central Banking",
        "project_type": "conference",
        "tier": "Funded Grant / Award",
        "sub_month": 2,
        "sub_day": 18,
        "start_month": 6,
        "start_day": 29,
        "duration": 3,
        "location": "Sintra, Portugal",
        "format": "Hybrid",
        "funding": "€10,000 ECB Young Economists Prize + Full Sintra Invitation",
        "organizer": "European Central Bank (ECB Directorate General Research)",
        "chairs": "ECB Chief Economist & Monetary Policy Research Committee",
        "publisher": "ECB Forum Proceedings & ECB Working Paper Series",
        "url": "https://www.ecb.europa.eu/pub/conferences/html/index.en.html",
        "tags": ["ecb", "sintra", "central-banking", "monetary-policy", "inflation", "young-economists-prize"],
        "description": (
            "Annual ECB Sintra Forum on Central Banking and PhD Young Economists Competition awarding €10,000 "
            "for frontier research on monetary policy, inflation dynamics, and euro-area financial stability."
        ),
    },
]


def scrape_finance_econ_conferences(today: Optional[date] = None) -> List[ResearchProjectRecord]:
    """Return active and upcoming Finance and Economy conferences and calls for papers."""
    ref = today or datetime.now(timezone.utc).date()
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    records: List[ResearchProjectRecord] = []

    for spec in FINANCE_ECON_EVENTS:
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
        year_short = year[-2:]
        title = spec["title_tpl"].format(year=year, year_short=year_short)
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
                paper_url=spec.get("paper_url"),
                tags=list(spec["tags"]),
                description=spec["description"],
                scraped_at=now_iso,
            )
        )

    return records

