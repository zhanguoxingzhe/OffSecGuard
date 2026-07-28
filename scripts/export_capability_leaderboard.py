"""汇总 batch_capability 结果为 leaderboard JSON/MD."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = ROOT / "results" / "batch_capability_v02"


def main() -> None:
    root = DEFAULT_ROOT
    manifest = json.loads((root / "batch_manifest.json").read_text(encoding="utf-8"))
    meta = {m["catalog_id"]: m for m in manifest["models"]}
    rows = []
    for d in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith("_")):
        sums = list(d.glob("capability_*_summary.json"))
        if not sums:
            continue
        s = json.loads(sums[0].read_text(encoding="utf-8"))
        mid = s["model"]
        cid = None
        for c in meta:
            if c.replace("/", "_") == d.name:
                cid = c
                break
        if cid is None:
            parts = d.name.split("_", 1)
            cid = f"{parts[0]}/{parts[1]}" if len(parts) == 2 else d.name
        m = meta.get(cid, {})
        rates = s.get("rates") or {}
        rows.append({
            "catalog_id": cid,
            "model": mid,
            "cohort_ord": m.get("cohort_ord"),
            "cohort_label": m.get("cohort_label"),
            "tsr": rates.get("tsr", 0.0),
            "oar": rates.get("oar", 0.0),
            "pqr": rates.get("pqr", 0.0),
            "cap_score": s.get("cap_score"),
            "n_samples": s.get("n_samples"),
        })
    rows.sort(key=lambda r: (-(r["cap_score"] if r["cap_score"] is not None else -1), r["catalog_id"]))
    out_dir = root / "_scorecard"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "gold": "cap-gold-v0.2",
        "min_cohort": manifest.get("min_cohort"),
        "n_models": len(rows),
        "ranking": rows,
    }
    (out_dir / "capability_cohort2plus_leaderboard.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    lines = [
        "# Capability Leaderboard (cap-gold-v0.2)",
        "",
        f"- Gold: **cap-gold-v0.2** (60)",
        f"- Models: **{len(rows)}**（含一代–三代；min_cohort={manifest.get('min_cohort')}）",
        "",
        "| # | cap_score | TSR | OAR | PQR | Model | Cohort |",
        "|--:|--:|--:|--:|--:|:---|:---|",
    ]
    for i, r in enumerate(rows, 1):
        lines.append(
            f"| {i} | {r['cap_score']} | {r['tsr']} | {r['oar']} | {r['pqr']} | "
            f"`{r['catalog_id']}` | {r.get('cohort_label') or ''} |"
        )
    (out_dir / "capability_cohort2plus_leaderboard.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8",
    )
    print(f"wrote {out_dir}")
    for i, r in enumerate(rows[:15], 1):
        print(f"{i:2d}  {r['cap_score']:6.2f}  {r['catalog_id']}")


if __name__ == "__main__":
    main()
