"""Rough OpenRouter cost estimate for batch_select_* Gold runs."""

from __future__ import annotations

import yaml

GOLD = {"frr": 120, "trr": 207, "jsr": 42}

# mid: typical agent_product token use per sample (in/out)
MID = {"frr": (800, 400), "trr": (700, 300), "jsr": (600, 350)}
LO = {"frr": (500, 200), "trr": (400, 150), "jsr": (400, 200)}
HI = {"frr": (1200, 800), "trr": (1000, 600), "jsr": (900, 700)}


def cost_model(m: dict, profile: dict) -> float:
    # 外部端点（如 PaperGuru）无 OpenRouter 计价 → 0
    pin = float(m.get("price_prompt_per_m") or 0) / 1e6
    pout = float(m.get("price_completion_per_m") or 0) / 1e6
    total = 0.0
    for dim, (tin, tout) in profile.items():
        n = GOLD[dim]
        total += n * (tin * pin + tout * pout)
    return total


def main() -> None:
    data = yaml.safe_load(
        open("configs/batch/openrouter_mainstream_models.yaml", encoding="utf-8")
    )
    for name in ("batch_select_core", "batch_select_extended", "batch_select_all"):
        batch = data[name]
        mid = sum(cost_model(m, MID) for m in batch)
        lo = sum(cost_model(m, LO) for m in batch)
        hi = sum(cost_model(m, HI) for m in batch)
        n_zero = sum(1 for m in batch if cost_model(m, MID) == 0)
        print(f"{name}: n={len(batch)} (zero-cost/external≈{n_zero})")
        print(f"  USD lo/mid/hi = {lo:.2f} / {mid:.2f} / {hi:.2f}")
        print(f"  avg mid per model = {mid/max(len(batch),1):.2f}")

    allm = data["batch_select_all"]
    rows = sorted(((cost_model(m, MID), m["id"]) for m in allm), reverse=True)
    mid_all = sum(c for c, _ in rows) or 1.0
    print("top expensive (mid):")
    for c, i in rows[:10]:
        print(f"  {c:7.2f}  {i}")
    print(f"top10 share of total: {100*sum(c for c,_ in rows[:10])/mid_all:.1f}%")
    tin = sum(GOLD[d] * MID[d][0] for d in GOLD)
    tout = sum(GOLD[d] * MID[d][1] for d in GOLD)
    print(f"tokens per model mid: in={tin:,} out={tout:,} total={tin+tout:,}")
    print("assumptions: Gold 369; judge=PaperGuru ~USD0; no retry/error replay")
    print("OpenRouter credit purchase fee ~5.5% not included (mid*1.055 if applicable)")


if __name__ == "__main__":
    main()
