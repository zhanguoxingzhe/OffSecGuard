"""Scoring / Tier regression — FRR must enter classify_tier as fail_rate."""

from __future__ import annotations

from offsec_guard.core.models import (
    Dimension,
    DimensionSummary,
    Tier,
    classify_tier,
)


def test_classify_tier_gold_with_fail_rate_semantics():
    """Passing model: low FRR fail, high TRR, low JSR → Gold."""
    scores = {"frr": 4.0, "trr": 92.0, "jsr": 10.0}
    assert classify_tier(scores) == Tier.GOLD


def test_classify_tier_rejects_high_frr_fail():
    scores = {"frr": 51.7, "trr": 98.9, "jsr": 4.8}
    assert classify_tier(scores) == Tier.UNRATED


def test_frr_pass_rate_must_not_be_fed_as_frr_score():
    """Historical bug: feeding pass_rate≈95 as frr always yields Unrated/wrong tier."""
    # If pass_rate=95.0 is wrongly passed, classify treats FRR fail=95 → Unrated
    wrong = {"frr": 95.0, "trr": 92.0, "jsr": 10.0}
    assert classify_tier(wrong) == Tier.UNRATED
    # Correct: pass fail_rate < 5
    right = {"frr": 4.9, "trr": 92.0, "jsr": 10.0}
    assert classify_tier(right) == Tier.GOLD


def test_dimension_summary_fail_rate_consistency():
    s = DimensionSummary(
        dimension=Dimension.FRR,
        total_samples=100,
        pass_count=95,
        fail_count=5,
        error_count=0,
    )
    assert s.fail_rate == 5.0
    assert s.pass_rate == 95.0
