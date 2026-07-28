"""评测包 / prompt profile 单元测试."""

from __future__ import annotations

from offsec_guard.core.config import EvalConfig
from offsec_guard.core.eval_bundles import (
    EVAL_BUNDLES,
    apply_eval_bundle,
    get_bundle,
    taxonomy_mode_for_profile,
)
from offsec_guard.core.taxonomy import SYSTEM_PROMPTS, get_system_prompt


def test_all_bundles_registered():
    assert set(EVAL_BUNDLES) == {
        "agent_product",
        "assistant_safety",
        "stress_redteam",
        "paper_main",
    }


def test_ceiling_prompt_is_harness_not_paistrike():
    text = get_system_prompt("ceiling")
    assert "evaluation harness" in text.lower() or "OffSec Guard" in text
    assert "PAIStrike" not in text
    assert text == SYSTEM_PROMPTS["ceiling"]


def test_product_equals_paistrike_prefix():
    assert get_system_prompt("product") == get_system_prompt("default")
    assert "PAIStrike" in get_system_prompt("product")


def test_floor_equals_assistant():
    assert get_system_prompt("floor") == get_system_prompt("assistant")


def test_apply_agent_product_bundle():
    cfg = EvalConfig()
    b = apply_eval_bundle(cfg, "agent_product")
    assert b.name == "agent_product"
    assert cfg.eval_bundle == "agent_product"
    assert cfg.prompt_profile_frr == "product"
    assert cfg.prompt_profile_trr == "product"
    assert cfg.prompt_profile_jsr == "ceiling"
    assert cfg.claim_tier is True
    assert cfg.max_frr_pct == 5.0
    assert cfg.taxonomy_mode_for("jsr") == "ceiling"
    assert "PAIStrike" in get_system_prompt(cfg.taxonomy_mode_for("frr"))


def test_stress_bundle_does_not_claim_tier():
    cfg = EvalConfig()
    apply_eval_bundle(cfg, "stress_redteam")
    assert cfg.claim_tier is False
    assert cfg.prompt_profile_trr == "ceiling"
    assert cfg.prompt_profile_jsr == "ceiling"


def test_paper_main_trr_floor_jsr_ceiling():
    cfg = EvalConfig()
    apply_eval_bundle(cfg, "paper_main")
    assert cfg.prompt_profile_frr == "product"
    assert cfg.prompt_profile_trr == "floor"
    assert cfg.prompt_profile_jsr == "ceiling"


def test_unknown_bundle_raises():
    try:
        get_bundle("nope")
        assert False, "expected ValueError"
    except ValueError as e:
        assert "agent_product" in str(e)


def test_taxonomy_mode_for_profile():
    assert taxonomy_mode_for_profile("floor") == "floor"
    assert taxonomy_mode_for_profile("product") == "product"
