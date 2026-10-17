"""Normalization, 6-discipline classification, date calculation, and grant/funding parsing."""
from __future__ import annotations

import hashlib
import re
from datetime import date, datetime, timezone
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse, urlunparse

from scraper.fx import FALLBACK_FX_TO_USD, convert_to_usd

DISCIPLINES: Tuple[str, ...] = (
    "Mathematics",
    "Finance",
    "Statistics",
    "Data Science",
    "Artificial Intelligence",
    "Economy",
)

# Sub-category taxonomy across the 6 disciplines
SUBCATEGORIES: Dict[str, List[Tuple[str, List[str]]]] = {
    "Mathematics": [
        (
            "Formalization, Lean 4 & Automated Theorem Proving",
            ["lean", "mathlib", "formalization", "theorem proving", "aimo", "imo", "isabelle", "coq", "proof"],
        ),
        (
            "Optimization, Operations Research & Control",
            ["optimization", "convex", "combinatorial", "integer programming", "operations research", "siam opt", "soda"],
        ),
        (
            "Probability, Stochastic Analysis & PDEs",
            ["stochastic", "pde", "partial differential", "probability", "ergodic", "random matrix", "spde", "dynamical"],
        ),
        (
            "Pure Mathematics, Algebra, Geometry & Number Theory",
            ["algebraic", "number theory", "topology", "geometry", "combinatorics", "polymath", "erdos", "langlands", "arithmetic"],
        ),
    ],
    "Finance": [
        (
            "Asset Pricing, Factor Alpha & Portfolio Theory",
            ["asset pricing", "portfolio", "alpha", "equity", "factor", "cross-sectional", "afa", "wfa", "efa", "sfs"],
        ),
        (
            "Market Microstructure, Order Books & Algorithmic Finance",
            ["microstructure", "order book", "lob", "high-frequency", "market making", "execution", "liquidity", "hawkes"],
        ),
        (
            "Derivatives, Quantitative Risk & Mathematical Finance",
            ["derivatives", "volatility", "options", "bachelier", "siam fm", "credit risk", "actuarial", "stochastic volatility"],
        ),
        (
            "FinTech, Decentralized Finance & Financial AI",
            ["icaif", "fintech", "defi", "crypto", "financial nlp", "blockchain", "digital assets", "crunchdao"],
        ),
    ],
    "Statistics": [
        (
            "Causal Inference, Experimental Design & Econometric Stats",
            ["causal", "treatment effect", "counterfactual", "experimental design", "instrumental", "double ml"],
        ),
        (
            "Bayesian Inference, MCMC & Probabilistic Modeling",
            ["bayesian", "isba", "mcmc", "variational", "nonparametric", "posterior", "uncertainty quantification"],
        ),
        (
            "High-Dimensional, Mathematical & Nonparametric Statistics",
            ["high-dimensional", "annals of statistics", "ims", "bernoulli", "minimax", "conformal prediction", "hypothesis"],
        ),
        (
            "Biostatistics, Spatial & Survival Analysis",
            ["biostatistics", "jsm", "rss", "enar", "survival", "clinical trial", "spatial", "epidemiological"],
        ),
    ],
    "Data Science": [
        (
            "Data Mining, Graph Analytics & Knowledge Discovery",
            ["kdd", "data mining", "wsdm", "icdm", "cikm", "graph mining", "knowledge graph", "anomaly detection"],
        ),
        (
            "Data Systems, VLDB/SIGMOD & Scalable Analytics",
            ["vldb", "sigmod", "icde", "database", "query optimization", "data engineering", "lakehouse", "stream"],
        ),
        (
            "Time Series Forecasting & Spatio-Temporal Modeling",
            ["time series", "forecasting", "spatio-temporal", "sensor", "tabular", "gbdt", "structural break"],
        ),
        (
            "Recommender Systems, Information Retrieval & Web Science",
            ["recsys", "sigir", "information retrieval", "search", "ranking", "web", "personalization"],
        ),
    ],
    "Artificial Intelligence": [
        (
            "Large Language Models, Reasoning & Autonomous Agents",
            ["llm", "language model", "nlp", "acl", "emnlp", "naacl", "reasoning", "agent", "rag", "alignment"],
        ),
        (
            "Deep Learning, Foundation Models & Representation Learning",
            ["neurips", "icml", "iclr", "aaai", "ijcai", "deep learning", "foundation model", "transformer", "diffusion"],
        ),
        (
            "Computer Vision, Multimodal & Scientific AI",
            ["cvpr", "iccv", "eccv", "vision", "multimodal", "ai4science", "medical imaging", "3d"],
        ),
        (
            "Statistical Learning Theory, RL & Algorithmic Game Theory",
            ["colt", "aistats", "uai", "reinforcement learning", "bandits", "learning theory", "game theory"],
        ),
    ],
    "Economy": [
        (
            "Macroeconomics, Monetary Policy & Central Banking",
            ["macroeconomics", "monetary", "central bank", "inflation", "ecb", "federal reserve", "nber", "dsge", "sed"],
        ),
        (
            "Econometrics, Panel Data & Structural Estimation",
            ["econometric", "econometrica", "panel data", "structural estimation", "time series econometrics", "identification"],
        ),
        (
            "Microeconomic Theory, Market Design & Game Theory",
            ["microeconomics", "market design", "auction", "mechanism design", "game theory", "acm ec", "social choice"],
        ),
        (
            "Labor, Development, Public & Climate Economics",
            ["development economics", "labor", "public economics", "trade", "climate economics", "cepr", "aea", "assa"],
        ),
    ],
}


def make_id(prefix: str, key: str) -> str:
    digest = hashlib.sha1(key.strip().lower().encode("utf-8")).hexdigest()[:12]
    clean_prefix = re.sub(r"[^a-z0-9]+", "-", prefix.lower()).strip("-") or "proj"
    return f"{clean_prefix}-{digest}"


def canonicalize_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url.strip())
    scheme = parsed.scheme.lower() or "https"
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((scheme, netloc, path, "", "", ""))


def parse_iso_date(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    s = str(raw).strip()
    if not s or s.lower() in ("tba", "tbd", "rolling", "continuous", "ongoing", "none"):
        return None

    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    for fmt in ("%Y/%m/%d", "%d %b %Y", "%b %d, %Y", "%B %d, %Y", "%d %B %Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def compute_deadline_status(
    submission_deadline: Optional[str],
    event_start_date: Optional[str] = None,
    event_end_date: Optional[str] = None,
    *,
    today: Optional[date] = None,
    is_rolling: bool = False,
) -> Tuple[bool, str, Optional[int]]:
    """Return (is_active, status_label, days_remaining).

    - If `is_rolling` or both dates are None: active, status="rolling", days_remaining=None.
    - If `submission_deadline` is in the future or today: uses days until submission_deadline.
      If <= 14 days -> "ending_soon", else -> "active".
    - If `submission_deadline` passed, but `event_end_date` (or `event_start_date`) is today or in the future:
      the conference/program is upcoming or currently running -> status="upcoming", days_remaining = days to event.
    - Otherwise -> inactive (False, "ended", negative days).
    """
    ref_today = today or datetime.now(timezone.utc).date()

    sub_iso = parse_iso_date(submission_deadline)
    start_iso = parse_iso_date(event_start_date)
    end_iso = parse_iso_date(event_end_date) or start_iso

    if sub_iso:
        try:
            sub_dt = date.fromisoformat(sub_iso)
            delta = (sub_dt - ref_today).days
            if delta >= 0:
                status = "ending_soon" if delta <= 14 else "active"
                return True, status, delta
        except ValueError:
            pass

    if end_iso:
        try:
            end_dt = date.fromisoformat(end_iso)
            start_dt = date.fromisoformat(start_iso) if start_iso else end_dt
            if end_dt >= ref_today:
                days_to_event = max(0, (start_dt - ref_today).days)
                return True, "upcoming", days_to_event
            return False, "ended", (end_dt - ref_today).days
        except ValueError:
            pass

    if is_rolling or (not sub_iso and not end_iso):
        return True, "rolling", None

    return False, "ended", -1


def parse_funding(
    raw: Optional[str],
    fx_to_usd: Optional[Dict[str, float]] = None,
) -> Tuple[str, float, str]:
    """Parse funding, grant, fellowship, or award string into (display_str, usd_amount, currency)."""
    if not raw or not str(raw).strip():
        return "Peer-Reviewed / Academic Track", 0.0, "USD"

    text = str(raw).strip()
    currency = "USD"
    if "€" in text or re.search(r"\bEUR\b", text, re.I):
        currency = "EUR"
    elif "£" in text or re.search(r"\bGBP\b", text, re.I):
        currency = "GBP"
    elif "CHF" in text:
        currency = "CHF"
    elif "CAD" in text or "C$" in text:
        currency = "CAD"
    elif "USDC" in text.upper():
        currency = "USDC"

    m = re.search(r"(\d[\d,]*(?:\.\d+)?)\s*([kKmM])?\b", text)
    if not m:
        return text, 0.0, currency

    num_str = m.group(1).replace(",", "")
    try:
        val = float(num_str)
    except ValueError:
        return text, 0.0, currency

    suffix = (m.group(2) or "").lower()
    if suffix == "m":
        val *= 1_000_000
    elif suffix == "k":
        val *= 1_000

    # Require an explicit currency symbol, currency code, or funding keyword
    has_currency_marker = bool(
        re.search(
            r"[\$€£]|\b(?:USD|EUR|GBP|CHF|CAD|USDC|grants?|prizes?|awards?|stipends?|fellowships?|funding)\b",
            text,
            re.I,
        )
    )
    if not has_currency_marker:
        return text, 0.0, "USD"

    usd_val = convert_to_usd(val, currency, fx_to_usd or FALLBACK_FX_TO_USD)
    return text, usd_val, currency


def infer_discipline_and_category(
    title: str,
    description: str = "",
    tags: Optional[Iterable[str]] = None,
    default_discipline: Optional[str] = None,
) -> Tuple[str, str]:
    """Classify a research project or conference into one of the 6 core disciplines and a specialized sub-category."""
    hay = " ".join([title or "", description or "", " ".join(tags or [])]).lower()

    discipline = default_discipline if default_discipline in DISCIPLINES else None

    if not discipline:
        if any(
            k in hay
            for k in [
                "econometric",
                "macroeconom",
                "microeconom",
                "monetary policy",
                "central bank",
                "nber",
                "cepr",
                "assa",
                "econometrica",
                "economic",
                "economy",
            ]
        ):
            discipline = "Economy"
        elif any(
            k in hay
            for k in [
                "asset pricing",
                "quantitative finance",
                "order book",
                "market microstructure",
                "derivatives",
                "bachelier",
                "siam fm",
                "wfa",
                "afa ",
                "efa ",
                "sfs cavalcade",
                "icaif",
                "portfolio",
                "hedge fund",
                "financial",
                "finance",
            ]
        ):
            discipline = "Finance"
        elif any(
            k in hay
            for k in [
                "biostatistics",
                "bayesian",
                "causal inference",
                "annals of statistics",
                "jsm",
                "royal statistical",
                "isba",
                "bernoulli",
                "statistical",
                "statistics",
            ]
        ):
            discipline = "Statistics"
        elif any(
            k in hay
            for k in [
                "algebraic",
                "number theory",
                "topology",
                "pde",
                "partial differential",
                "mathlib",
                "lean 4",
                "theorem proving",
                "siam",
                "ams ",
                "msri",
                "slmath",
                "oberwolfach",
                "newton institute",
                "icerm",
                "ipam",
                "fields institute",
                "mathematics",
                "mathematical",
            ]
        ):
            discipline = "Mathematics"
        elif any(
            k in hay
            for k in [
                "kdd",
                "vldb",
                "sigmod",
                "wsdm",
                "cikm",
                "icdm",
                "recsys",
                "sigir",
                "data mining",
                "data science",
                "time series forecasting",
            ]
        ):
            discipline = "Data Science"
        else:
            discipline = "Artificial Intelligence"

    subcats = SUBCATEGORIES.get(discipline, [])
    best_cat = subcats[0][0] if subcats else discipline
    best_hits = 0
    for cat_name, keywords in subcats:
        hits = sum(1 for kw in keywords if kw in hay)
        if hits > best_hits:
            best_hits = hits
            best_cat = cat_name

    return discipline, best_cat
