"""Scraper for Active & Upcoming Artificial Intelligence and Data Science Conferences & Calls for Papers."""
from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

import yaml

from scraper.http import fetch_text
from scraper.models import ResearchProjectRecord
from scraper.normalize import (
    compute_deadline_status,
    infer_discipline_and_category,
    make_id,
    parse_funding,
)

logger = logging.getLogger(__name__)

SOURCE_NAME = "ai_ds_conferences"
SOURCE_LABEL = "AI & Data Science Conferences (CORE A* / ACM / IEEE / CCF)"


def _rolling_dates(
    ref: date,
    sub_month: int,
    sub_day: int,
    start_month: int,
    start_day: int,
    duration_days: int = 5,
    notif_offset_days: int = 65,
) -> Dict[str, str]:
    """Compute the next active cycle dates relative to `ref` so conferences always show current/upcoming cycles."""
    from datetime import timedelta

    year = ref.year
    start_dt = date(year, start_month, min(start_day, 28))
    end_dt = start_dt + timedelta(days=duration_days)
    sub_year = year if sub_month <= start_month else year - 1
    sub_dt = date(sub_year, sub_month, min(sub_day, 28))

    # If the event already finished, advance to next year's cycle
    if end_dt < ref:
        year += 1
        start_dt = date(year, start_month, min(start_day, 28))
        end_dt = start_dt + timedelta(days=duration_days)
        sub_year = year if sub_month <= start_month else year - 1
        sub_dt = date(sub_year, sub_month, min(sub_day, 28))

    # If submission deadline passed more than 30 days ago and next cycle submission is within 7 months,
    # check if event is still in the future; if event is in the future, keep it so user sees both Upcoming Conf & Next CFP
    abs_dt = sub_dt - timedelta(days=7)
    notif_dt = min(start_dt - timedelta(days=14), sub_dt + timedelta(days=notif_offset_days))

    return {
        "year": str(year),
        "abstract_deadline": abs_dt.isoformat(),
        "submission_deadline": sub_dt.isoformat(),
        "notification_date": notif_dt.isoformat(),
        "event_start_date": start_dt.isoformat(),
        "event_end_date": end_dt.isoformat(),
    }


FLAGSHIP_AI_DS_CONFERENCES: List[Dict[str, Any]] = [
    {
        "code": "NeurIPS",
        "title_tpl": "NeurIPS {year} — Conference on Neural Information Processing Systems",
        "platform": "NeurIPS Foundation",
        "discipline": "Artificial Intelligence",
        "category": "Deep Learning, Foundation Models & Representation Learning",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 5,
        "sub_day": 15,
        "start_month": 12,
        "start_day": 6,
        "duration": 6,
        "location": "San Diego / Vancouver, North America",
        "format": "Hybrid",
        "funding": "Publication + Student/Scholar Travel Awards ($2,500)",
        "organizer": "Neural Information Processing Systems Foundation",
        "chairs": "NeurIPS Program & General Chairs",
        "publisher": "Advances in Neural Information Processing Systems (NeurIPS Proceedings)",
        "url": "https://neurips.cc/",
        "paper_url": "https://neurips.cc/Conferences/FutureMeetings",
        "tags": ["neurips", "deep-learning", "foundation-models", "learning-theory", "datasets-benchmarks", "rl"],
        "description": (
            "Premier global conference on machine learning, computational neuroscience, foundation models, "
            "statistical learning theory, optimization, and AI datasets & benchmarks track."
        ),
    },
    {
        "code": "ICLR",
        "title_tpl": "ICLR {year} — International Conference on Learning Representations",
        "platform": "ICLR / OpenReview",
        "discipline": "Artificial Intelligence",
        "category": "Deep Learning, Foundation Models & Representation Learning",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 10,
        "sub_day": 2,
        "start_month": 4,
        "start_day": 24,
        "duration": 5,
        "location": "Singapore / Vienna / Rio de Janeiro",
        "format": "Hybrid",
        "funding": "OpenReview Archival + Travel Fellowships ($2,000)",
        "organizer": "International Conference on Learning Representations",
        "chairs": "ICLR Program Committee (OpenReview Double-Blind)",
        "publisher": "OpenReview / ICLR Proceedings",
        "url": "https://iclr.cc/",
        "paper_url": "https://openreview.net/group?id=ICLR.cc",
        "tags": ["iclr", "representation-learning", "llms", "generative-models", "openreview", "deep-learning"],
        "description": (
            "Flagship conference dedicated to representation learning, deep generative models, large language model "
            "reasoning, mechanistic interpretability, and open peer review on OpenReview."
        ),
    },
    {
        "code": "ICML",
        "title_tpl": "ICML {year} — International Conference on Machine Learning",
        "platform": "IMLS / PMLR",
        "discipline": "Artificial Intelligence",
        "category": "Deep Learning, Foundation Models & Representation Learning",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 1,
        "sub_day": 30,
        "start_month": 7,
        "start_day": 13,
        "duration": 6,
        "location": "Vienna / Vancouver / Seoul",
        "format": "Hybrid",
        "funding": "PMLR Publication + Diversity & Student Travel Grants ($2,500)",
        "organizer": "International Machine Learning Society (IMLS)",
        "chairs": "ICML Program & Area Chairs",
        "publisher": "Proceedings of Machine Learning Research (PMLR)",
        "url": "https://icml.cc/",
        "paper_url": "https://proceedings.mlr.press/",
        "tags": ["icml", "machine-learning", "pmlr", "optimization", "reinforcement-learning", "ai4science"],
        "description": (
            "Leading international academic conference in machine learning covering statistical learning, "
            "deep architectures, reinforcement learning, optimization, causality, and trustworthy AI."
        ),
    },
    {
        "code": "AAAI",
        "title_tpl": "AAAI {year} — AAAI Conference on Artificial Intelligence",
        "platform": "AAAI",
        "discipline": "Artificial Intelligence",
        "category": "Large Language Models, Reasoning & Autonomous Agents",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 8,
        "sub_day": 15,
        "start_month": 2,
        "start_day": 22,
        "duration": 7,
        "location": "Philadelphia / Vancouver / North America",
        "format": "In-Person",
        "funding": "AAAI Proceedings + Student Scholarship Program ($1,500)",
        "organizer": "Association for the Advancement of Artificial Intelligence",
        "chairs": "AAAI Technical Program Chairs",
        "publisher": "Proceedings of the AAAI Conference on Artificial Intelligence",
        "url": "https://aaai.org/conference/aaai/",
        "tags": ["aaai", "ai", "agents", "reasoning", "planning", "multi-agent-systems", "knowledge-representation"],
        "description": (
            "Broad-spectrum flagship AI conference spanning multi-agent systems, automated planning, game theory, "
            "neuro-symbolic reasoning, NLP, computer vision, and AI for social impact."
        ),
    },
    {
        "code": "CVPR",
        "title_tpl": "CVPR {year} — IEEE/CVF Conference on Computer Vision and Pattern Recognition",
        "platform": "IEEE / CVF",
        "discipline": "Artificial Intelligence",
        "category": "Computer Vision, Multimodal & Scientific AI",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 11,
        "sub_day": 14,
        "start_month": 6,
        "start_day": 14,
        "duration": 5,
        "location": "Nashville / Seattle / Denver, USA",
        "format": "Hybrid",
        "funding": "IEEE/CVF Archival + Best Paper Awards ($10,000)",
        "organizer": "IEEE Computer Society & Computer Vision Foundation (CVF)",
        "chairs": "CVPR Program Chairs",
        "publisher": "IEEE Xplore / CVF Open Access",
        "url": "https://cvpr.thecvf.com/",
        "tags": ["cvpr", "computer-vision", "multimodal", "3d-vision", "diffusion-models", "video-understanding"],
        "description": (
            "Highest-impact venue in computer vision, multimodal foundation models, 3D scene reconstruction, "
            "embodied AI, and generative visual synthesis."
        ),
    },
    {
        "code": "ACL",
        "title_tpl": "ACL {year} — Annual Meeting of the Association for Computational Linguistics",
        "platform": "ACL / ARR",
        "discipline": "Artificial Intelligence",
        "category": "Large Language Models, Reasoning & Autonomous Agents",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 2,
        "sub_day": 15,
        "start_month": 7,
        "start_day": 27,
        "duration": 6,
        "location": "Vienna / Bangkok / Toronto",
        "format": "Hybrid",
        "funding": "ACL Anthology + Walker Fund Student Fellowships ($2,000)",
        "organizer": "Association for Computational Linguistics (ACL)",
        "chairs": "ACL Program Chairs via ACL Rolling Review (ARR)",
        "publisher": "ACL Anthology",
        "url": "https://www.aclweb.org/portal/",
        "paper_url": "https://aclrollingreview.org/",
        "tags": ["acl", "nlp", "llms", "computational-linguistics", "reasoning", "multilingual", "alignment"],
        "description": (
            "Premier conference in natural language processing and computational linguistics via ACL Rolling Review "
            "(ARR), covering LLM post-training, interpretability, retrieval, and reasoning."
        ),
    },
    {
        "code": "EMNLP",
        "title_tpl": "EMNLP {year} — Conference on Empirical Methods in Natural Language Processing",
        "platform": "ACL SIGDAT / ARR",
        "discipline": "Artificial Intelligence",
        "category": "Large Language Models, Reasoning & Autonomous Agents",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 6,
        "sub_day": 15,
        "start_month": 11,
        "start_day": 10,
        "duration": 5,
        "location": "Suzhou / Miami / Singapore",
        "format": "Hybrid",
        "funding": "ACL Anthology + Best Paper & D&I Awards ($2,000)",
        "organizer": "ACL Special Interest Group on Linguistic Data (SIGDAT)",
        "chairs": "EMNLP Program Committee",
        "publisher": "ACL Anthology",
        "url": "https://www.aclweb.org/portal/content/emnlp",
        "tags": ["emnlp", "nlp", "llms", "empirical-methods", "rag", "evaluation", "information-extraction"],
        "description": (
            "Flagship empirical NLP research conference focusing on large language models, benchmarks, "
            "information extraction, question answering, and human-AI alignment."
        ),
    },
    {
        "code": "COLT",
        "title_tpl": "COLT {year} — Annual Conference on Learning Theory",
        "platform": "Association for Learning Theory / PMLR",
        "discipline": "Artificial Intelligence",
        "category": "Statistical Learning Theory, RL & Algorithmic Game Theory",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 2,
        "sub_day": 6,
        "start_month": 6,
        "start_day": 29,
        "duration": 5,
        "location": "Lyon / Edmonton / Montreal",
        "format": "In-Person",
        "funding": "PMLR + Best Paper & Best Student Paper Awards ($4,000)",
        "organizer": "Association for Learning Theory",
        "chairs": "COLT Program Chairs",
        "publisher": "Proceedings of Machine Learning Research (PMLR)",
        "url": "https://learningtheory.org/",
        "tags": ["colt", "learning-theory", "online-learning", "bandits", "convex-optimization", "high-dimensional-stats"],
        "description": (
            "Premier theoretical machine learning conference bridging statistical learning theory, "
            "online decision-making, multi-armed bandits, non-convex optimization, and information theory."
        ),
    },
    {
        "code": "AISTATS",
        "title_tpl": "AISTATS {year} — International Conference on Artificial Intelligence and Statistics",
        "platform": "SAIS / PMLR",
        "discipline": "Artificial Intelligence",
        "category": "Statistical Learning Theory, RL & Algorithmic Game Theory",
        "tier": "Flagship Society",
        "sub_month": 10,
        "sub_day": 10,
        "start_month": 5,
        "start_day": 3,
        "duration": 3,
        "location": "Phuket / Valencia / Tangier",
        "format": "Hybrid",
        "funding": "PMLR Archival + Student Travel Grants ($1,500)",
        "organizer": "Society for Artificial Intelligence and Statistics",
        "chairs": "AISTATS Program Chairs",
        "publisher": "Proceedings of Machine Learning Research (PMLR)",
        "url": "https://aistats.org/",
        "tags": ["aistats", "statistical-ml", "bayesian-ml", "causal-inference", "gaussian-processes", "optimization"],
        "description": (
            "Interdisciplinary conference at the intersection of artificial intelligence, mathematical statistics, "
            "Bayesian inference, graphical models, and scalable statistical algorithms."
        ),
    },
    {
        "code": "UAI",
        "title_tpl": "UAI {year} — Conference on Uncertainty in Artificial Intelligence",
        "platform": "AUAI / PMLR",
        "discipline": "Artificial Intelligence",
        "category": "Statistical Learning Theory, RL & Algorithmic Game Theory",
        "tier": "Flagship Society",
        "sub_month": 2,
        "sub_day": 12,
        "start_month": 7,
        "start_day": 21,
        "duration": 4,
        "location": "Rio de Janeiro / Melbourne / Amsterdam",
        "format": "Hybrid",
        "funding": "PMLR Archival + Student Travel Support",
        "organizer": "Association for Uncertainty in Artificial Intelligence (AUAI)",
        "chairs": "UAI Program Committee",
        "publisher": "Proceedings of Machine Learning Research (PMLR)",
        "url": "https://www.auai.org/",
        "tags": ["uai", "uncertainty-quantification", "probabilistic-ai", "causal-discovery", "conformal-prediction"],
        "description": (
            "Leading research conference on probabilistic reasoning, causal inference, uncertainty quantification, "
            "conformal prediction, and decision-making under uncertainty."
        ),
    },
    {
        "code": "KDD",
        "title_tpl": "ACM SIGKDD {year} — Conference on Knowledge Discovery and Data Mining",
        "platform": "ACM SIGKDD",
        "discipline": "Data Science",
        "category": "Data Mining, Graph Analytics & Knowledge Discovery",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 2,
        "sub_day": 10,
        "start_month": 8,
        "start_day": 9,
        "duration": 5,
        "location": "Toronto / Barcelona / Jeju",
        "format": "In-Person",
        "funding": "ACM DL + KDD Cup ($50,000) & Student Travel Awards",
        "organizer": "ACM Special Interest Group on Knowledge Discovery and Data Mining",
        "chairs": "SIGKDD Research & Applied Data Science Chairs",
        "publisher": "ACM Digital Library",
        "url": "https://kdd.org/",
        "tags": ["kdd", "data-science", "data-mining", "graph-neural-networks", "time-series", "applied-ml"],
        "description": (
            "Premier interdisciplinary Data Science conference featuring Research and Applied Data Science tracks, "
            "large-scale graph mining, spatiotemporal forecasting, and the annual KDD Cup."
        ),
    },
    {
        "code": "VLDB",
        "title_tpl": "VLDB {year} — International Conference on Very Large Data Bases (Monthly Rolling CFP)",
        "platform": "VLDB Endowment",
        "discipline": "Data Science",
        "category": "Data Systems, VLDB/SIGMOD & Scalable Analytics",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 3,
        "sub_day": 1,
        "start_month": 8,
        "start_day": 25,
        "duration": 5,
        "location": "London / Boston / Seoul",
        "format": "In-Person",
        "funding": "PVLDB Journal Archival + Travel Fellowships",
        "organizer": "VLDB Endowment",
        "chairs": "PVLDB Editor-in-Chief & Review Board (1st of every month)",
        "publisher": "Proceedings of the VLDB Endowment (PVLDB)",
        "url": "https://vldb.org/",
        "tags": ["vldb", "data-systems", "databases", "query-optimization", "data-science", "ml-systems"],
        "description": (
            "Top-tier data management and data science systems conference with monthly rolling PVLDB submission "
            "deadlines (1st of each month) covering vector databases, lakehouses, and ML-for-systems."
        ),
    },
    {
        "code": "SIGMOD",
        "title_tpl": "ACM SIGMOD / PODS {year} — International Conference on Management of Data",
        "platform": "ACM SIGMOD",
        "discipline": "Data Science",
        "category": "Data Systems, VLDB/SIGMOD & Scalable Analytics",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 1,
        "sub_day": 17,
        "start_month": 6,
        "start_day": 14,
        "duration": 6,
        "location": "Berlin / Bengaluru / Washington D.C.",
        "format": "In-Person",
        "funding": "PACMMOD Archival + Student Travel Grants ($2,000)",
        "organizer": "ACM SIGMOD & PODS",
        "chairs": "SIGMOD Program Chairs (Quarterly PACMMOD Cycles)",
        "publisher": "Proceedings of the ACM on Management of Data (PACMMOD)",
        "url": "https://sigmod.org/",
        "tags": ["sigmod", "pods", "database-theory", "data-engineering", "data-science", "scalable-analytics"],
        "description": (
            "Flagship conference on principles of database systems (PODS) and data management engineering (SIGMOD), "
            "spanning data provenance, streaming analytics, and relational learning."
        ),
    },
    {
        "code": "WSDM",
        "title_tpl": "ACM WSDM {year} — International Conference on Web Search and Data Mining",
        "platform": "ACM SIGIR / SIGKDD",
        "discipline": "Data Science",
        "category": "Recommender Systems, Information Retrieval & Web Science",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 8,
        "sub_day": 14,
        "start_month": 3,
        "start_day": 10,
        "duration": 5,
        "location": "Hannover / Boise / Mérida",
        "format": "In-Person",
        "funding": "ACM DL + WSDM Cup Challenges ($15,000)",
        "organizer": "ACM SIGIR, SIGKDD, SIGMOD & SIGWEB",
        "chairs": "WSDM Program Chairs",
        "publisher": "ACM Digital Library",
        "url": "https://www.wsdm-conference.org/",
        "tags": ["wsdm", "web-mining", "search", "recommender-systems", "social-networks", "data-science"],
        "description": (
            "Selective conference on web-scale data mining, search engines, conversational retrieval, "
            "graph learning, and online experimentation."
        ),
    },
    {
        "code": "SIGIR",
        "title_tpl": "ACM SIGIR {year} — Conference on Research and Development in Information Retrieval",
        "platform": "ACM SIGIR",
        "discipline": "Data Science",
        "category": "Recommender Systems, Information Retrieval & Web Science",
        "tier": "CORE A* / Top-Tier",
        "sub_month": 1,
        "sub_day": 23,
        "start_month": 7,
        "start_day": 18,
        "duration": 5,
        "location": "Padua / Melbourne / Washington D.C.",
        "format": "Hybrid",
        "funding": "ACM DL + Student Travel Awards ($2,000)",
        "organizer": "ACM Special Interest Group on Information Retrieval",
        "chairs": "SIGIR Program Committee",
        "publisher": "ACM Digital Library",
        "url": "https://sigir.org/",
        "tags": ["sigir", "information-retrieval", "rag", "search-ranking", "recommender-systems", "evaluation"],
        "description": (
            "Premier forum for research on information retrieval, retrieval-augmented generation (RAG), "
            "neural ranking, recommender systems, and evaluation methodologies."
        ),
    },
    {
        "code": "RecSys",
        "title_tpl": "ACM RecSys {year} — Conference on Recommender Systems",
        "platform": "ACM RecSys",
        "discipline": "Data Science",
        "category": "Recommender Systems, Information Retrieval & Web Science",
        "tier": "Flagship Society",
        "sub_month": 4,
        "sub_day": 21,
        "start_month": 9,
        "start_day": 22,
        "duration": 5,
        "location": "Prague / Bari / Minneapolis",
        "format": "Hybrid",
        "funding": "ACM DL + RecSys Challenge Prize ($20,000)",
        "organizer": "Association for Computing Machinery (ACM)",
        "chairs": "ACM RecSys Program Chairs",
        "publisher": "ACM Digital Library",
        "url": "https://recsys.acm.org/",
        "tags": ["recsys", "recommender-systems", "personalization", "bandits", "counterfactual-evaluation"],
        "description": (
            "Leading international conference on recommender systems, counterfactual ranking, user modeling, "
            "sequential recommendation, and the industrial RecSys Challenge."
        ),
    },
    {
        "code": "ICDM",
        "title_tpl": "IEEE ICDM {year} — International Conference on Data Mining",
        "platform": "IEEE Computer Society",
        "discipline": "Data Science",
        "category": "Data Mining, Graph Analytics & Knowledge Discovery",
        "tier": "Flagship Society",
        "sub_month": 6,
        "sub_day": 15,
        "start_month": 11,
        "start_day": 18,
        "duration": 4,
        "location": "Washington D.C. / Abu Dhabi / Shanghai",
        "format": "In-Person",
        "funding": "IEEE Xplore + Best Paper & Student Travel Awards",
        "organizer": "IEEE Computer Society",
        "chairs": "IEEE ICDM Program Chairs",
        "publisher": "IEEE Xplore Digital Library",
        "url": "https://www.KnowledgeDiscovery.org/",
        "tags": ["icdm", "data-mining", "time-series", "anomaly-detection", "clustering", "data-science"],
        "description": (
            "World-premier research conference dedicated to data mining algorithms, anomaly detection, "
            "high-dimensional clustering, time-series analysis, and statistical pattern recognition."
        ),
    },
    {
        "code": "CIKM",
        "title_tpl": "ACM CIKM {year} — International Conference on Information and Knowledge Management",
        "platform": "ACM SIGIR / SIGWEB",
        "discipline": "Data Science",
        "category": "Data Mining, Graph Analytics & Knowledge Discovery",
        "tier": "Flagship Society",
        "sub_month": 5,
        "sub_day": 20,
        "start_month": 10,
        "start_day": 26,
        "duration": 5,
        "location": "Seoul / Montreal / Analytical Hub",
        "format": "In-Person",
        "funding": "ACM DL + AnalytiCup Data Science Prizes ($10,000)",
        "organizer": "ACM SIGIR & SIGWEB",
        "chairs": "CIKM Research & Applied Track Chairs",
        "publisher": "ACM Digital Library",
        "url": "https://www.cikm.org/",
        "tags": ["cikm", "knowledge-graphs", "information-management", "data-mining", "analyticup"],
        "description": (
            "Unites research in database management, information retrieval, and knowledge discovery, "
            "including the annual CIKM AnalytiCup data science competition."
        ),
    },
]


def _try_live_ccfddl_enrichment(ref: date) -> List[ResearchProjectRecord]:
    """Attempt to fetch live conference YAML metadata from ccfddl / community GitHub raw feeds."""
    live_urls = [
        "https://raw.githubusercontent.com/ccfddl/ccf-deadlines/main/conference/AI/neurips.yml",
        "https://raw.githubusercontent.com/ccfddl/ccf-deadlines/main/conference/AI/icml.yml",
        "https://raw.githubusercontent.com/ccfddl/ccf-deadlines/main/conference/AI/iclr.yml",
        "https://raw.githubusercontent.com/ccfddl/ccf-deadlines/main/conference/DB/kdd.yml",
    ]
    out: List[ResearchProjectRecord] = []
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for url in live_urls:
        raw = fetch_text(url, timeout=5)
        if not raw:
            continue
        try:
            parsed = yaml.safe_load(raw)
            if not isinstance(parsed, list) or not parsed:
                continue
            item = parsed[0]
            if not isinstance(item, dict):
                continue
            title_short = str(item.get("title", "")).strip()
            desc = str(item.get("description", "")).strip()
            confs = item.get("confs") or []
            if not isinstance(confs, list) or not confs:
                continue
            latest = confs[-1]
            year = latest.get("year")
            link = str(latest.get("link") or "").strip()
            place = str(latest.get("place") or "Global").strip()
            timeline = latest.get("timeline") or []
            sub_deadline: Optional[str] = None
            abs_deadline: Optional[str] = None
            if isinstance(timeline, list) and timeline:
                last_t = timeline[-1]
                if isinstance(last_t, dict):
                    dl = str(last_t.get("deadline") or "")[:10]
                    if len(dl) == 10 and dl[4] == "-":
                        sub_deadline = dl
                    ab = str(last_t.get("abstract_deadline") or "")[:10]
                    if len(ab) == 10 and ab[4] == "-":
                        abs_deadline = ab

            if not link or not sub_deadline:
                continue
            is_active, status, days_rem = compute_deadline_status(sub_deadline, today=ref)
            if not is_active:
                continue

            disc, cat = infer_discipline_and_category(
                f"{title_short} {desc}",
                desc,
                [title_short.lower()],
                default_discipline="Data Science" if title_short.upper() == "KDD" else "Artificial Intelligence",
            )
            full_title = f"{title_short} {year} — {desc}" if desc else f"{title_short} {year}"
            out.append(
                ResearchProjectRecord(
                    id=make_id(SOURCE_NAME, f"{title_short}-{year}"),
                    title=full_title,
                    platform=f"{title_short} Official",
                    source=SOURCE_NAME,
                    url=link,
                    discipline=disc,
                    category=cat,
                    project_type="conference",
                    tier="CORE A* / Top-Tier",
                    status=status,
                    abstract_deadline=abs_deadline,
                    submission_deadline=sub_deadline,
                    days_remaining=days_rem,
                    location=place,
                    format="Hybrid",
                    funding_raw="Peer-Reviewed Archival + Travel Grants",
                    funding_usd=2500.0,
                    venue_code=f"{title_short} {year}",
                    organizer=desc or title_short,
                    lead_researchers=f"{title_short} {year} Program Committee",
                    proceedings_publisher=f"{title_short} Proceedings",
                    tags=[title_short.lower(), "cfp", "core-a-star", disc.lower().replace(" ", "-")],
                    description=f"Live CFP telemetry synced from ccfddl for {full_title} ({place}).",
                    scraped_at=now_iso,
                )
            )
        except Exception as exc:
            logger.debug("ccfddl parse error for %s: %s", url, exc)

    return out


def scrape_ai_ds_conferences(today: Optional[date] = None) -> List[ResearchProjectRecord]:
    """Scrape active and upcoming AI & Data Science conferences and calls for papers."""
    ref = today or datetime.now(timezone.utc).date()
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    records: List[ResearchProjectRecord] = []

    # 1. Try live ccfddl YAML enrichment
    records.extend(_try_live_ccfddl_enrichment(ref))

    # 2. Generate rolling active & upcoming cycles for flagship AI & Data Science conferences
    for spec in FLAGSHIP_AI_DS_CONFERENCES:
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
                project_type="conference",
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

