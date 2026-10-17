"""Scraper for Active & Upcoming Mathematics and Statistics Conferences, Institutes & Thematic Programs."""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from scraper.models import ResearchProjectRecord
from scraper.normalize import compute_deadline_status, make_id, parse_funding
from scraper.sources.ai_ds_conferences import _rolling_dates

SOURCE_NAME = "math_stats_conferences"
SOURCE_LABEL = "Mathematics & Statistics Societies & Research Institutes (AMS / SIAM / IMS / ASA / SLMath / INI)"

MATH_STATS_EVENTS: List[Dict[str, Any]] = [
    # ---------------- MATHEMATICS CONFERENCES & THEMATIC PROGRAMS ----------------
    {
        "code": "JMM",
        "title_tpl": "JMM {year} — Joint Mathematics Meetings (AMS / MAA / SIAM / ASA)",
        "platform": "AMS / Joint Mathematics Meetings",
        "discipline": "Mathematics",
        "category": "Pure Mathematics, Algebra, Geometry & Number Theory",
        "project_type": "conference",
        "tier": "Flagship Society",
        "sub_month": 9,
        "sub_day": 10,
        "start_month": 1,
        "start_day": 6,
        "duration": 4,
        "location": "Washington D.C. / Seattle / Boston, USA",
        "format": "In-Person",
        "funding": "AMS Graduate & Postdoc Travel Grants ($1,500)",
        "organizer": "American Mathematical Society (AMS), MAA, SIAM, AWM & ASA",
        "chairs": "AMS Special Sessions & Invited Address Committee",
        "publisher": "AMS Contemporary Mathematics / Notices of the AMS",
        "url": "https://jointmathematicsmeetings.org/",
        "paper_url": "https://www.ams.org/meetings/national/national",
        "tags": ["jmm", "ams", "pure-mathematics", "applied-mathematics", "algebra", "pde", "number-theory"],
        "description": (
            "The largest annual mathematics gathering in the world, featuring AMS Invited Addresses, "
            "Colloquium Lectures, Special Sessions across pure and applied mathematics, and AI-for-Math symposia."
        ),
    },
    {
        "code": "SIAM-AN",
        "title_tpl": "SIAM AN{year_short} — SIAM Annual Meeting & Applied Mathematics Congress",
        "platform": "SIAM",
        "discipline": "Mathematics",
        "category": "Probability, Stochastic Analysis & PDEs",
        "project_type": "conference",
        "tier": "Flagship Society",
        "sub_month": 1,
        "sub_day": 22,
        "start_month": 7,
        "start_day": 6,
        "duration": 5,
        "location": "Cleveland / Montreal / Pittsburgh",
        "format": "Hybrid",
        "funding": "SIAM Student & Early Career Travel Awards ($2,000)",
        "organizer": "Society for Industrial and Applied Mathematics (SIAM)",
        "chairs": "SIAM Organizing Committee",
        "publisher": "SIAM Review / SIAM Proceedings",
        "url": "https://www.siam.org/conferences-events/",
        "tags": ["siam", "applied-mathematics", "pde", "numerical-analysis", "dynamical-systems", "scientific-computing"],
        "description": (
            "Flagship conference of the Society for Industrial and Applied Mathematics covering PDEs, "
            "numerical linear algebra, inverse problems, stochastic modeling, and scientific machine learning."
        ),
    },
    {
        "code": "SIAM-OP",
        "title_tpl": "SIAM OP{year_short} — Conference on Optimization & Variational Analysis",
        "platform": "SIAM Activity Group on Optimization",
        "discipline": "Mathematics",
        "category": "Optimization, Operations Research & Control",
        "project_type": "conference",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 11,
        "sub_day": 18,
        "start_month": 5,
        "start_day": 26,
        "duration": 4,
        "location": "Edinburgh / Seattle / Toronto",
        "format": "In-Person",
        "funding": "SIAM Optimization Prize + Travel Support ($2,500)",
        "organizer": "Society for Industrial and Applied Mathematics (SIAG/OPT)",
        "chairs": "SIAM SIAG/OPT Program Chairs",
        "publisher": "SIAM Journal on Optimization (SIOPT)",
        "url": "https://www.siam.org/conferences-events/",
        "tags": ["siam-opt", "optimization", "convex-analysis", "integer-programming", "stochastic-optimization", "control"],
        "description": (
            "Premier conference on continuous, discrete, stochastic, and conic optimization, optimal transport, "
            "and algorithmic foundations of large-scale optimization."
        ),
    },
    {
        "code": "STOC",
        "title_tpl": "ACM STOC {year} — Symposium on Theory of Computing (TheoryFest)",
        "platform": "ACM SIGACT",
        "discipline": "Mathematics",
        "category": "Optimization, Operations Research & Control",
        "project_type": "conference",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 11,
        "sub_day": 8,
        "start_month": 6,
        "start_day": 21,
        "duration": 5,
        "location": "Prague / Salt Lake City / Vancouver",
        "format": "In-Person",
        "funding": "ACM DL + Danny Lewin Best Student Paper & Travel Grants ($2,000)",
        "organizer": "ACM Special Interest Group on Algorithms and Computation Theory (SIGACT)",
        "chairs": "STOC Program Committee",
        "publisher": "ACM Digital Library",
        "url": "https://acm-stoc.org/",
        "tags": ["stoc", "discrete-mathematics", "combinatorics", "complexity-theory", "spectral-graph-theory", "algorithms"],
        "description": (
            "Flagship symposium on mathematical foundations of computing, additive combinatorics, "
            "spectral graph theory, high-dimensional geometry, quantum complexity, and optimization."
        ),
    },
    {
        "code": "FOCS",
        "title_tpl": "IEEE FOCS {year} — Symposium on Foundations of Computer Science",
        "platform": "IEEE TCMF",
        "discipline": "Mathematics",
        "category": "Optimization, Operations Research & Control",
        "project_type": "conference",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 4,
        "sub_day": 10,
        "start_month": 11,
        "start_day": 2,
        "duration": 4,
        "location": "Sydney / Chicago / Santa Cruz",
        "format": "In-Person",
        "funding": "IEEE Xplore + Machtey Award & Student Travel Grants ($2,000)",
        "organizer": "IEEE Computer Society Technical Committee on Mathematical Foundations",
        "chairs": "FOCS Program Committee",
        "publisher": "IEEE Xplore",
        "url": "https://focs.computer.org/",
        "tags": ["focs", "mathematical-foundations", "combinatorics", "probability", "convex-geometry", "hardness"],
        "description": (
            "Top-tier symposium on mathematical foundations of algorithms, probabilistic combinatorics, "
            "metric embeddings, algebraic complexity, and theoretical statistics."
        ),
    },
    {
        "code": "SODA",
        "title_tpl": "ACM-SIAM SODA {year} — Symposium on Discrete Algorithms",
        "platform": "SIAM / ACM SIGACT",
        "discipline": "Mathematics",
        "category": "Optimization, Operations Research & Control",
        "project_type": "conference",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 7,
        "sub_day": 12,
        "start_month": 1,
        "start_day": 12,
        "duration": 4,
        "location": "New Orleans / Vancouver / Alexandria",
        "format": "In-Person",
        "funding": "SIAM Proceedings + Travel Fellowships ($1,800)",
        "organizer": "SIAM Activity Group on Discrete Mathematics & ACM SIGACT",
        "chairs": "SODA Program Committee",
        "publisher": "SIAM Digital Library",
        "url": "https://www.siam.org/conferences-events/",
        "tags": ["soda", "discrete-mathematics", "graph-theory", "combinatorial-optimization", "approximation-algorithms"],
        "description": (
            "Joint ACM-SIAM symposium on discrete mathematics, extremal graph theory, matroid theory, "
            "submodular optimization, and randomized algorithms."
        ),
    },
    {
        "code": "SLMath-MSRI",
        "title_tpl": "SLMath (MSRI) {year} — Simons Laufer Mathematical Sciences Institute Thematic Programs",
        "platform": "SLMath (MSRI) Berkeley",
        "discipline": "Mathematics",
        "category": "Pure Mathematics, Algebra, Geometry & Number Theory",
        "project_type": "thematic_program",
        "tier": "Research Institute",
        "sub_month": 10,
        "sub_day": 1,
        "start_month": 1,
        "start_day": 19,
        "duration": 115,
        "location": "Berkeley, California, USA",
        "format": "In-Person",
        "funding": "$45,000 Research Professor / Postdoc Residency Stipend",
        "organizer": "Simons Laufer Mathematical Sciences Institute (UC Berkeley / NSF)",
        "chairs": "SLMath Scientific Advisory Committee",
        "publisher": "MSRI / SLMath Publications (Cambridge University Press)",
        "url": "https://www.slmath.org/programs",
        "paper_url": "https://www.slmath.org/workshops",
        "tags": ["slmath", "msri", "thematic-program", "algebraic-geometry", "number-theory", "pde", "visiting-fellowship"],
        "description": (
            "Semester-long intensive mathematical research residencies and workshops at SLMath (formerly MSRI) "
            "in Berkeley, supporting visiting professors, postdocs, and hot-topics workshops."
        ),
    },
    {
        "code": "INI-Cambridge",
        "title_tpl": "Isaac Newton Institute {year} — Mathematical Sciences Research Programmes & Workshops",
        "platform": "Isaac Newton Institute (Cambridge)",
        "discipline": "Mathematics",
        "category": "Probability, Stochastic Analysis & PDEs",
        "project_type": "thematic_program",
        "tier": "Research Institute",
        "sub_month": 11,
        "sub_day": 15,
        "start_month": 1,
        "start_day": 12,
        "duration": 150,
        "location": "Cambridge, United Kingdom",
        "format": "Hybrid",
        "funding": "£18,000 Visiting Rothschild / Kirk Fellowship + Accommodation",
        "organizer": "Isaac Newton Institute for Mathematical Sciences, University of Cambridge",
        "chairs": "INI Scientific Steering Committee",
        "publisher": "Cambridge University Press / Newton Institute Series",
        "url": "https://www.newton.ac.uk/programmes/",
        "tags": ["newton-institute", "cambridge", "stochastic-analysis", "mathematical-physics", "fluid-dynamics", "topology"],
        "description": (
            "UK national research institute for the mathematical sciences hosting 4-to-6 month collaborative "
            "research programmes in stochastic PDEs, mathematical data science, number theory, and geometry."
        ),
    },
    {
        "code": "IPAM-UCLA",
        "title_tpl": "IPAM {year} — Institute for Pure and Applied Mathematics Long Programs (UCLA)",
        "platform": "IPAM UCLA (NSF)",
        "discipline": "Mathematics",
        "category": "Formalization, Lean 4 & Automated Theorem Proving",
        "project_type": "thematic_program",
        "tier": "Research Institute",
        "sub_month": 11,
        "sub_day": 28,
        "start_month": 3,
        "start_day": 15,
        "duration": 85,
        "location": "Los Angeles (UCLA), California, USA",
        "format": "In-Person",
        "funding": "$15,000 Travel, Per-Diem & Residence Support (NSF)",
        "organizer": "Institute for Pure and Applied Mathematics (UCLA / NSF DMS)",
        "chairs": "IPAM Science Advisory Board",
        "publisher": "IPAM White Papers & Springer Institute Series",
        "url": "https://www.ipam.ucla.edu/programs/long-programs/",
        "tags": ["ipam", "ucla", "machine-assisted-proofs", "optimal-transport", "high-dimensional-geometry", "nsf"],
        "description": (
            "NSF-funded 3-month mathematical research programs at UCLA bridging pure mathematics, "
            "machine-assisted proofs (Lean 4), optimal transport, PDEs, and scientific computing."
        ),
    },
    {
        "code": "ICERM-Brown",
        "title_tpl": "ICERM {year} — Semester Programs & Topical Workshops in Computational Mathematics",
        "platform": "ICERM Brown University",
        "discipline": "Mathematics",
        "category": "Pure Mathematics, Algebra, Geometry & Number Theory",
        "project_type": "thematic_program",
        "tier": "Research Institute",
        "sub_month": 10,
        "sub_day": 20,
        "start_month": 2,
        "start_day": 1,
        "duration": 100,
        "location": "Providence (Brown University), Rhode Island, USA",
        "format": "Hybrid",
        "funding": "$12,000 Simons / NSF Visiting Researcher Support",
        "organizer": "Institute for Computational and Experimental Research in Mathematics (Brown)",
        "chairs": "ICERM Scientific Board",
        "publisher": "AMS / ICERM Proceedings",
        "url": "https://icerm.brown.edu/programs/",
        "tags": ["icerm", "computational-mathematics", "arithmetic-geometry", "dynamical-systems", "formalization"],
        "description": (
            "Semester programs and Collaborate@ICERM summer research projects exploring computational number theory, "
            "spectral geometry, nonlinear PDEs, and computer-assisted mathematical proofs."
        ),
    },
    # ---------------- STATISTICS CONFERENCES & PROGRAMS ----------------
    {
        "code": "JSM",
        "title_tpl": "JSM {year} — Joint Statistical Meetings (ASA / IMS / IBS / SSC)",
        "platform": "ASA / IMS / JSM",
        "discipline": "Statistics",
        "category": "High-Dimensional, Mathematical & Nonparametric Statistics",
        "project_type": "conference",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 2,
        "sub_day": 3,
        "start_month": 8,
        "start_day": 1,
        "duration": 6,
        "location": "Boston / Nashville / Chicago, North America",
        "format": "In-Person",
        "funding": "ASA/IMS Student Paper Awards & Travel Fellowships ($2,000)",
        "organizer": "American Statistical Association (ASA), IMS, ENAR, WNAR, SSC & IBS",
        "chairs": "JSM Program Committee",
        "publisher": "JASA / Annals of Statistics / JSM Proceedings",
        "url": "https://ww2.amstat.org/meetings/jsm/",
        "tags": ["jsm", "asa", "ims", "statistics", "causal-inference", "biostatistics", "high-dimensional"],
        "description": (
            "The largest statistical science event in the world, uniting mathematical statisticians, "
            "causal inference researchers, biostatisticians, and econometricians across ASA and IMS."
        ),
    },
    {
        "code": "IMS-Annual",
        "title_tpl": "IMS {year} — Institute of Mathematical Statistics Annual Meeting & Wald Lectures",
        "platform": "Institute of Mathematical Statistics (IMS)",
        "discipline": "Statistics",
        "category": "High-Dimensional, Mathematical & Nonparametric Statistics",
        "tier": "CORE A* / Top-Tier",
        "project_type": "conference",
        "sub_month": 1,
        "sub_day": 15,
        "start_month": 7,
        "start_day": 14,
        "duration": 4,
        "location": "Bochum / London / North America",
        "format": "In-Person",
        "funding": "IMS New Researcher Travel Awards ($2,500) + Hannan/Wald Lectures",
        "organizer": "Institute of Mathematical Statistics (IMS)",
        "chairs": "IMS Program Secretary & Committee",
        "publisher": "Annals of Statistics / Annals of Probability",
        "url": "https://imstat.org/meetings-calendar/",
        "tags": ["ims", "mathematical-statistics", "annals-of-statistics", "probability-theory", "nonparametric", "minimax"],
        "description": (
            "Flagship meeting of the Institute of Mathematical Statistics featuring the Wald and Le Cam Lectures, "
            "high-dimensional inference, random matrix theory, conformal prediction, and stochastic processes."
        ),
    },
    {
        "code": "ISBA",
        "title_tpl": "ISBA {year} — World Meeting of the International Society for Bayesian Analysis",
        "platform": "ISBA Bayesian Society",
        "discipline": "Statistics",
        "category": "Bayesian Inference, MCMC & Probabilistic Modeling",
        "project_type": "conference",
        "tier": "Flagship Society",
        "sub_month": 11,
        "sub_day": 25,
        "start_month": 6,
        "start_day": 28,
        "duration": 6,
        "location": "Nagoya / Venice / Montreal",
        "format": "In-Person",
        "funding": "Savage Award ($3,000) + Junior Bayesian Travel Grants",
        "organizer": "International Society for Bayesian Analysis (ISBA)",
        "chairs": "ISBA Scientific Committee",
        "publisher": "Bayesian Analysis (Journal)",
        "url": "https://bayesian.org/",
        "tags": ["isba", "bayesian", "mcmc", "variational-inference", "bayesian-nonparametrics", "uncertainty"],
        "description": (
            "Premier global congress on Bayesian methodology, scalable Markov Chain Monte Carlo, "
            "variational approximations, Bayesian nonparametrics, and decision theory."
        ),
    },
    {
        "code": "RSS",
        "title_tpl": "RSS {year} — Royal Statistical Society International Conference",
        "platform": "Royal Statistical Society (RSS)",
        "discipline": "Statistics",
        "category": "Biostatistics, Spatial & Survival Analysis",
        "project_type": "conference",
        "tier": "Flagship Society",
        "sub_month": 4,
        "sub_day": 5,
        "start_month": 9,
        "start_day": 7,
        "duration": 4,
        "location": "Edinburgh / Bournemouth / Belfast, UK",
        "format": "In-Person",
        "funding": "JRSS Discussion Track + RSS Early Career Bursaries",
        "organizer": "Royal Statistical Society (RSS)",
        "chairs": "RSS Conference Board",
        "publisher": "Journal of the Royal Statistical Society (Series A, B, C)",
        "url": "https://rss.org.uk/training-events/conference/",
        "tags": ["rss", "jrss-b", "statistical-methodology", "biostatistics", "official-statistics", "data-science"],
        "description": (
            "Annual international conference of the Royal Statistical Society featuring Series B methodological "
            "sessions, causal inference, spatial modeling, environmental statistics, and public policy analytics."
        ),
    },
    {
        "code": "ENAR",
        "title_tpl": "ENAR {year} — International Biometric Society Spring Statistical Meetings",
        "platform": "ENAR / International Biometric Society",
        "discipline": "Statistics",
        "category": "Biostatistics, Spatial & Survival Analysis",
        "project_type": "conference",
        "tier": "Flagship Society",
        "sub_month": 10,
        "sub_day": 15,
        "start_month": 3,
        "start_day": 15,
        "duration": 4,
        "location": "Indianapolis / New Orleans / Baltimore, USA",
        "format": "In-Person",
        "funding": "ENAR Distinguished Student Paper Awards ($1,500)",
        "organizer": "Eastern North American Region of the International Biometric Society",
        "chairs": "ENAR Program Committee",
        "publisher": "Biometrics / Biostatistics",
        "url": "https://www.enar.org/meetings/",
        "tags": ["enar", "biostatistics", "clinical-trials", "survival-analysis", "causal-inference", "genomics"],
        "description": (
            "Leading biostatistics and biometric methodology conference covering adaptive clinical trial design, "
            "survival analysis, longitudinal data, and causal inference in observational studies."
        ),
    },
    {
        "code": "CLeaR",
        "title_tpl": "CLeaR {year} — Conference on Causal Learning and Reasoning",
        "platform": "CLeaR / PMLR",
        "discipline": "Statistics",
        "category": "Causal Inference, Experimental Design & Econometric Stats",
        "project_type": "conference",
        "tier": "Flagship Society",
        "sub_month": 10,
        "sub_day": 22,
        "start_month": 4,
        "start_day": 14,
        "duration": 3,
        "location": "Zurich / Boston / Lausanne",
        "format": "Hybrid",
        "funding": "PMLR Archival + Student Travel Fellowships",
        "organizer": "Causal Learning and Reasoning Board",
        "chairs": "CLeaR Program Chairs",
        "publisher": "Proceedings of Machine Learning Research (PMLR)",
        "url": "https://www.cclear.cc/",
        "tags": ["clear", "causal-inference", "causal-discovery", "econometrics", "double-ml", "experimental-design"],
        "description": (
            "Dedicated conference uniting statisticians, econometricians, and machine learning researchers on "
            "causal discovery, semiparametric treatment effect estimation, and structural causal models."
        ),
    },
]


def scrape_math_stats_conferences(today: Optional[date] = None) -> List[ResearchProjectRecord]:
    """Return active and upcoming Mathematics and Statistics conferences and research institute programs."""
    ref = today or datetime.now(timezone.utc).date()
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    records: List[ResearchProjectRecord] = []

    for spec in MATH_STATS_EVENTS:
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

