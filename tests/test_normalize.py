"""Unit tests for discipline classification, deadline status calculation, and funding normalization."""
from __future__ import annotations

from datetime import date

from scraper.normalize import (
    DISCIPLINES,
    canonicalize_url,
    compute_deadline_status,
    infer_discipline_and_category,
    parse_funding,
    parse_iso_date,
)


def test_six_disciplines_defined() -> None:
    assert set(DISCIPLINES) == {
        "Mathematics",
        "Finance",
        "Statistics",
        "Data Science",
        "Artificial Intelligence",
        "Economy",
    }


def test_parse_iso_date() -> None:
    assert parse_iso_date("2027-05-15") == "2027-05-15"
    assert parse_iso_date("2027-05-15T23:59:59Z") == "2027-05-15"
    assert parse_iso_date("Rolling") is None
    assert parse_iso_date(None) is None


def test_compute_deadline_status_active_and_ending_soon() -> None:
    ref = date(2026, 10, 17)
    active, status, days = compute_deadline_status("2026-10-25", "2027-04-20", today=ref)
    assert active is True
    assert status == "ending_soon"
    assert days == 8

    active2, status2, days2 = compute_deadline_status("2027-01-30", "2027-07-13", today=ref)
    assert active2 is True
    assert status2 == "active"
    assert days2 == 105


def test_compute_deadline_status_upcoming_conference_after_cfp() -> None:
    ref = date(2026, 10, 17)
    # CFP closed in May 2026, but conference happens in December 2026
    active, status, days = compute_deadline_status(
        "2026-05-15",
        "2026-12-06",
        "2026-12-12",
        today=ref,
    )
    assert active is True
    assert status == "upcoming"
    assert days == 50


def test_compute_deadline_status_rolling() -> None:
    ref = date(2026, 10, 17)
    active, status, days = compute_deadline_status(None, None, today=ref, is_rolling=True)
    assert active is True
    assert status == "rolling"
    assert days is None


def test_parse_funding_currencies() -> None:
    raw, usd, cur = parse_funding("$250,000 NSF Grant")
    assert usd == 250000.0
    assert cur == "USD"

    raw_eur, usd_eur, cur_eur = parse_funding("€1,500,000 ERC Starting Grant")
    assert cur_eur == "EUR"
    assert usd_eur > 1_500_000.0

    raw_none, usd_none, _ = parse_funding("Peer-Reviewed Archival in NeurIPS 2027")
    assert usd_none == 0.0


def test_infer_discipline_and_category_across_all_six_fields() -> None:
    d_math, c_math = infer_discipline_and_category(
        "Fermat's Last Theorem Formalization in Lean 4 and Mathlib",
        "Algebraic number theory and automated theorem proving",
    )
    assert d_math == "Mathematics"
    assert "Lean 4" in c_math

    d_fin, _ = infer_discipline_and_category(
        "AFA Annual Meeting — Asset Pricing and Market Microstructure",
        "Limit order books and quantitative finance",
    )
    assert d_fin == "Finance"

    d_stat, _ = infer_discipline_and_category(
        "ISBA Bayesian Analysis & Causal Inference Symposium",
        "MCMC and high-dimensional statistics",
    )
    assert d_stat == "Statistics"

    d_ds, _ = infer_discipline_and_category(
        "ACM SIGKDD Conference on Knowledge Discovery and Data Mining",
        "Graph mining and scalable data science",
    )
    assert d_ds == "Data Science"

    d_ai, _ = infer_discipline_and_category(
        "ICLR International Conference on Learning Representations",
        "Large language models and deep learning transformers",
    )
    assert d_ai == "Artificial Intelligence"

    d_econ, _ = infer_discipline_and_category(
        "NBER Summer Institute & Econometric Society Meeting",
        "Macroeconomics, monetary policy, and structural econometrics",
    )
    assert d_econ == "Economy"


def test_canonicalize_url() -> None:
    assert canonicalize_url("https://www.neurips.cc/Conferences/?utm_source=x") == "https://neurips.cc/Conferences"

