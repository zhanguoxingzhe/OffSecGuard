"""In-vendor generation metadata — ordered by product release timeline (not physical ladder array order)."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "configs" / "batch" / "openrouter_mainstream_models.yaml"

# Vendor generation timeline (old → new). Same-wave product lines merge into one gen_family.
VENDOR_GEN_TIMELINE: dict[str, list[str]] = {
    "openai": ["5.4", "o3", "5.5", "o4", "5.6"],
    "anthropic": [
        "sonnet-4.5",
        "haiku-4.5",
        "opus-4.6",
        "sonnet-4.6",
        "opus-4.8",
        "sonnet-5",
        "opus-5",
        "fable-5",
    ],
    "google": ["2.5", "3.1", "3.5", "3.6"],
    "deepseek": ["r1", "v3.2", "v4"],
    "qwen": ["3.5", "3.6", "3.7"],
    "meta-llama": ["3.3", "4"],
    "mistralai": ["medium-3", "large-3", "small-4"],
    "x-ai": ["4.20", "4.3", "4.5"],
    "moonshotai": ["k2", "k2.6", "k3"],
    "z-ai": ["4.7", "5.0", "5.1", "5.2"],
    "paperguru": ["1.2"],
}

# Cross-vendor cohorts: group contemporaneous flagship waves (e.g. gpt-5.6 and fable-5).
# key = (vendor, gen_family) → cohort_ord (1=earlier baseline; higher = newer)
GLOBAL_COHORT_OF: dict[tuple[str, str], int] = {
    # —— Cohort 1: earlier baseline ——
    ("openai", "5.4"): 1,
    ("openai", "o3"): 1,
    ("anthropic", "sonnet-4.5"): 1,
    ("anthropic", "haiku-4.5"): 1,
    ("anthropic", "opus-4.6"): 1,
    ("google", "2.5"): 1,
    ("deepseek", "r1"): 1,
    ("deepseek", "v3.2"): 1,
    ("qwen", "3.5"): 1,
    ("meta-llama", "3.3"): 1,
    ("mistralai", "medium-3"): 1,
    ("mistralai", "large-3"): 1,
    ("x-ai", "4.20"): 1,
    ("moonshotai", "k2"): 1,
    ("z-ai", "4.7"): 1,
    ("z-ai", "5.0"): 1,
    # —— Cohort 2: transition wave ——
    ("openai", "5.5"): 2,
    ("openai", "o4"): 2,
    ("anthropic", "sonnet-4.6"): 2,
    ("anthropic", "opus-4.8"): 2,
    ("google", "3.1"): 2,
    ("google", "3.5"): 2,
    ("qwen", "3.6"): 2,
    ("meta-llama", "4"): 2,
    ("mistralai", "small-4"): 2,
    ("x-ai", "4.3"): 2,
    ("moonshotai", "k2.6"): 2,
    ("z-ai", "5.1"): 2,
    ("paperguru", "1.2"): 2,
    # —— Cohort 3: current flagship wave (gpt-5.6 / fable-5 / opus-5 / 3.6 / v4 …) ——
    ("openai", "5.6"): 3,
    ("anthropic", "sonnet-5"): 3,
    ("anthropic", "opus-5"): 3,
    ("anthropic", "fable-5"): 3,
    ("google", "3.6"): 3,
    ("deepseek", "v4"): 3,
    ("qwen", "3.7"): 3,
    ("x-ai", "4.5"): 3,
    ("moonshotai", "k3"): 3,
    ("z-ai", "5.2"): 3,
}

COHORT_TITLES: dict[int, str] = {
    1: "Cohort 1 · Earlier baseline wave",
    2: "Cohort 2 · Transition wave",
    3: "Cohort 3 · Current flagship wave",
}


def _zh_gen(i: int) -> str:
    return f"Gen {i}"


def normalize_gen_family(vendor: str, gen: str) -> str:
    """Merge same-generation variants (e.g. 5.6-sol/terra/luna → 5.6)."""
    g = (gen or "unknown").strip()
    gl = g.lower()
    if vendor == "openai":
        if gl.startswith("5.6"):
            return "5.6"
        return g
    if vendor == "qwen":
        if gl.startswith("3.5"):
            return "3.5"
        if gl.startswith("3.6"):
            return "3.6"
        if gl.startswith("3.7"):
            return "3.7"
        return g
    if vendor == "deepseek":
        if gl.startswith("r1"):
            return "r1"
        if gl.startswith("v3.2"):
            return "v3.2"
        if gl.startswith("v4"):
            return "v4"
        return g
    if vendor == "mistralai":
        if "medium" in gl:
            return "medium-3"
        if "large" in gl:
            return "large-3"
        if "small" in gl:
            return "small-4"
        return g
    if vendor == "moonshotai":
        if gl.startswith("k2.6") or "k2.6" in gl or g == "k2.6":
            return "k2.6"
        if gl.startswith("k2") or g == "k2":
            return "k2"
        if "k3" in gl:
            return "k3"
        return g
    if vendor == "x-ai":
        # grok-4.20 / 4.3 / 4.5 — gen field is already 4.x
        return g
    if vendor == "paperguru":
        return "1.2"
    return g


def _fallback_sort_key(gen: str) -> tuple:
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", gen)]
    return (nums[0] if nums else 9999.0, nums[1] if len(nums) > 1 else 0.0, gen)


def gen_timeline_rank(vendor: str, family: str) -> int:
    """Return timeline index (0-based); unknown generations sort last."""
    timeline = VENDOR_GEN_TIMELINE.get(vendor) or []
    if family in timeline:
        return timeline.index(family)
    # Try prefix match
    for i, t in enumerate(timeline):
        if family.startswith(t) or t.startswith(family):
            return i
    return 1000 + int(_fallback_sort_key(family)[0] * 10)


def global_cohort_of(vendor: str, family: str) -> int:
    """Cross-vendor cohort index; unmapped entries fall back to vendor timeline buckets 1–3."""
    key = (vendor, family)
    if key in GLOBAL_COHORT_OF:
        return GLOBAL_COHORT_OF[key]
    # Fallback: newer in-vendor timeline → higher bucket, clamped to 1–3
    idx = gen_timeline_rank(vendor, family)
    timeline = VENDOR_GEN_TIMELINE.get(vendor) or []
    if not timeline or idx >= 1000:
        return 2
    # First 40% → 1, middle → 2, tail → 3
    pos = idx / max(len(timeline) - 1, 1)
    if pos <= 0.34:
        return 1
    if pos <= 0.67:
        return 2
    return 3


def cohort_label(ord_: int) -> str:
    return COHORT_TITLES.get(ord_, f"Cohort {ord_}")


def load_model_gen_meta(catalog_path: Path | None = None) -> dict[str, dict[str, Any]]:
    """model_id → {vendor, gen, gen_raw, role, ladder_idx, name}."""
    path = catalog_path or CATALOG
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    out: dict[str, dict[str, Any]] = {}
    for vendor, vd in (data.get("vendors") or {}).items():
        for idx, e in enumerate(vd.get("ladder") or []):
            mid = e.get("id")
            if not mid:
                continue
            raw = str(e.get("gen") or "unknown")
            out[mid] = {
                "vendor": vendor,
                "gen_raw": raw,
                "gen": normalize_gen_family(vendor, raw),
                "role": str(e.get("role") or ""),
                "ladder_idx": idx,
                "name": e.get("name") or mid,
            }
    for e in data.get("external_non_openrouter") or []:
        mid = e.get("id")
        if not mid:
            continue
        vendor = mid.split("/", 1)[0] if "/" in mid else "external"
        raw = str(e.get("gen") or "1.2")
        out.setdefault(
            mid,
            {
                "vendor": vendor,
                "gen_raw": raw,
                "gen": normalize_gen_family(vendor, raw),
                "role": "flagship",
                "ladder_idx": 0,
                "name": e.get("name") or mid,
            },
        )
    return out


def attach_generation_meta(rows: list[dict], meta: dict[str, dict[str, Any]] | None = None) -> list[dict]:
    """In-place attach gen / gen_zh / gen_ord / gen_label / role."""
    meta = meta or load_model_gen_meta()
    by_vendor: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        mid = r["catalog_id"]
        m = meta.get(mid)
        if not m:
            vendor = r.get("vendor") or mid.split("/", 1)[0]
            raw = "unknown"
            m = {
                "vendor": vendor,
                "gen_raw": raw,
                "gen": normalize_gen_family(vendor, raw),
                "role": "",
                "ladder_idx": 10_000,
                "name": mid,
            }
        r["gen_raw"] = m["gen_raw"]
        r["gen"] = m["gen"]
        r["role"] = m["role"]
        r["ladder_idx"] = int(m["ladder_idx"])
        by_vendor[r.get("vendor") or m["vendor"]].append(r)

    for vendor, items in by_vendor.items():
        families = sorted(
            {r["gen"] for r in items},
            key=lambda g: (gen_timeline_rank(vendor, g), g),
        )
        rank_of = {g: i + 1 for i, g in enumerate(families)}
        for r in items:
            ord_ = rank_of[r["gen"]]
            r["gen_ord"] = ord_
            r["gen_zh"] = _zh_gen(ord_)
            # Display: Gen 1 · 5.6 (append raw variant when it differs)
            raw = r.get("gen_raw") or r["gen"]
            if raw != r["gen"]:
                r["gen_label"] = f"{r['gen_zh']} · {r['gen']} ({raw})"
            else:
                r["gen_label"] = f"{r['gen_zh']} · {r['gen']}"
            r["gen_n"] = len(families)
            c_ord = global_cohort_of(vendor, r["gen"])
            r["cohort_ord"] = c_ord
            r["cohort_label"] = cohort_label(c_ord)
    return rows


def vendor_gen_series(models: list[dict]) -> dict[str, Any]:
    """Aggregate by in-vendor generation for line charts."""
    import statistics as stats

    by_gen: dict[str, list[dict]] = defaultdict(list)
    for m in models:
        by_gen[m["gen"]].append(m)
    gens = sorted(by_gen.keys(), key=lambda g: (by_gen[g][0]["gen_ord"], g))
    labels = [by_gen[g][0]["gen_zh"] + " · " + g for g in gens]

    def agg(key: str, fn) -> list[float]:
        out = []
        for g in gens:
            vals = [float(x.get(key) or 0) for x in by_gen[g]]
            out.append(round(fn(vals), 2))
        return out

    return {
        "labels": labels,
        "gens": gens,
        "score_best": agg("total_score", max),
        "score_mean": agg("total_score", stats.mean),
        "frr_mean": agg("frr_fail_pct", stats.mean),
        "trr_mean": agg("trr_refuse_pct", stats.mean),
        "jsr_mean": agg("jsr_jailbreak_pct", stats.mean),
        "misuse_mean": agg("misuse_risk", stats.mean),
        "n_per_gen": [len(by_gen[g]) for g in gens],
    }
