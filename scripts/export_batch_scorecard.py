"""从 results/batch_select_stress 导出 Gold+stress_redteam 主表（CSV/JSON/MD）."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import yaml

from offsec_guard.reporting import attach_generation_meta
from offsec_guard.scoring import MISUSE_RISK_WEIGHTS, compute_misuse_risk

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "configs" / "batch" / "openrouter_mainstream_models.yaml"
RESULT_ROOT = ROOT / "results" / "batch_select_stress"
OUT_DIR = RESULT_ROOT / "_scorecard"


def dim_rates(summary: dict, key: str) -> dict:
    d = (summary.get("dimensions") or {}).get(key) or {}
    total = int(d.get("total_samples") or 0)
    passed = int(d.get("pass_count") or 0)
    failed = int(d.get("fail_count") or 0)
    errors = int(d.get("error_count") or 0)
    skipped = int(d.get("skipped_count") or 0)
    n_eff = total - errors - skipped
    pass_rate = round(passed / n_eff * 100, 2) if n_eff > 0 else None
    fail_rate = round(failed / n_eff * 100, 2) if n_eff > 0 else None
    return {
        f"{key}_total": total,
        f"{key}_pass": passed,
        f"{key}_fail": failed,
        f"{key}_error": errors,
        f"{key}_skipped": skipped,
        f"{key}_n_eff": n_eff,
        f"{key}_pass_rate": pass_rate,
        f"{key}_fail_rate": fail_rate,
        f"{key}_avg_latency_ms": d.get("avg_latency_ms"),
    }


def find_summary(model_dir: Path) -> Path | None:
    direct = model_dir / "summary.json"
    if direct.exists():
        return direct
    kids = sorted(model_dir.glob("eval-*/summary.json"), key=lambda p: p.stat().st_mtime)
    return kids[-1] if kids else None


def catalog_id(mid: str) -> str:
    # openrouter summaries store model_id like anthropic/claude-...
    # paperguru stores guru-pro-1.2 with provider paperguru
    return mid


def main() -> int:
    ids = [
        x["id"]
        for x in yaml.safe_load(CATALOG.read_text(encoding="utf-8"))["batch_select_core"]
    ]
    rows: list[dict] = []
    missing: list[str] = []

    for mid in ids:
        slug = mid.replace("/", "_")
        model_dir = RESULT_ROOT / slug
        sp = find_summary(model_dir)
        if not sp:
            missing.append(mid)
            continue
        data = json.loads(sp.read_text(encoding="utf-8"))
        model = data.get("model") or {}
        snap = data.get("config_snapshot") or {}
        profiles = snap.get("prompt_profiles") or {}
        provider = model.get("provider", "")
        model_id = model.get("model_id", "")
        # 统一 catalog id
        if provider == "paperguru":
            catalog = f"paperguru/{model_id}" if not str(model_id).startswith("paperguru/") else model_id
        elif provider == "deepseek" and not str(model_id).startswith("deepseek/"):
            catalog = f"deepseek/{model_id}"
        else:
            catalog = model_id or mid
        vendor = catalog.split("/", 1)[0]

        row = {
            "catalog_id": mid,
            "vendor": vendor,
            "provider": provider,
            "model_id": model_id,
            "display_name": model.get("display_name", ""),
            "eval_id": data.get("eval_id", ""),
            "generated_at": data.get("generated_at", ""),
            "eval_bundle": snap.get("eval_bundle", ""),
            "claim_tier": snap.get("claim_tier"),
            "profile_frr": profiles.get("frr", ""),
            "profile_trr": profiles.get("trr", ""),
            "profile_jsr": profiles.get("jsr", ""),
            "judge_model": snap.get("judge_model", ""),
            "judge_enabled": snap.get("judge_enabled"),
            "gate_passed": snap.get("gate_passed"),
            "tier": data.get("tier", ""),
            "total_score": data.get("total_score"),
            "summary_path": str(sp.relative_to(ROOT)).replace("\\", "/"),
            "sample_results_path": str((sp.parent / "sample_results.json").relative_to(ROOT)).replace("\\", "/")
            if (sp.parent / "sample_results.json").exists()
            else "",
        }
        for dim in ("frr", "trr", "jsr"):
            row.update(dim_rates(data, dim))
        # 主解读列（与 scorecard 一致）
        row["frr_fail_pct"] = row["frr_fail_rate"]  # lower better
        row["trr_refuse_pct"] = row["trr_pass_rate"]  # higher better
        row["jsr_jailbreak_pct"] = row["jsr_fail_rate"]  # lower better
        # 滥用易感（护栏侧；越高越危险；不含进攻能力）
        row.update(
            compute_misuse_risk(
                row["frr_fail_pct"],
                row["trr_refuse_pct"],
                row["jsr_jailbreak_pct"],
            )
        )
        rows.append(row)

    attach_generation_meta(rows)

    # 排名：选型分降序 / 滥用易感降序
    by_score = sorted(rows, key=lambda r: (-(r.get("total_score") or 0), r["catalog_id"]))
    by_misuse = sorted(rows, key=lambda r: (-(r.get("misuse_risk") or 0), r["catalog_id"]))
    score_rank = {r["catalog_id"]: i for i, r in enumerate(by_score, 1)}
    misuse_rank = {r["catalog_id"]: i for i, r in enumerate(by_misuse, 1)}
    for r in rows:
        r["score_rank"] = score_rank[r["catalog_id"]]
        r["misuse_rank"] = misuse_rank[r["catalog_id"]]
        # CSV 友好：去掉过重字段
        r.pop("ladder_idx", None)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / "stress_redteam_core_scorecard.csv"
    json_path = OUT_DIR / "stress_redteam_core_scorecard.json"
    md_path = OUT_DIR / "stress_redteam_core_scorecard.md"

    fieldnames = list(rows[0].keys()) if rows else []
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    w = MISUSE_RISK_WEIGHTS
    payload = {
        "bundle": "stress_redteam",
        "tier_dataset": "gold",
        "n_models": len(rows),
        "missing": missing,
        "misuse_risk_formula": (
            f"misuse_risk = {w['coop']}*(100-FRR) + {w['trr_gap']}*(100-TRR) + {w['jsr']}*JSR; "
            "higher = more misuse-susceptible (guardrail-side only, not offensive capability)."
        ),
        "misuse_risk_weights": dict(w),
        "notes": (
            "FRR=product, TRR=ceiling, JSR=ceiling; claim_tier=false. "
            "frr_fail_pct / jsr_jailbreak_pct lower better; trr_refuse_pct higher better. "
            "misuse_risk higher = easier to misuse (inverted reading of guardrails). "
            "N_eff = total - error - skipped."
        ),
        "rows": rows,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 可读主表：按 total_score 降序 + 滥用易感附表
    ranked = by_score
    lines = [
        "# stress_redteam · batch_select_core 主表",
        "",
        f"- bundle: `stress_redteam`（FRR=product, TRR=ceiling, JSR=ceiling）",
        f"- dataset: Gold 369 · judge: PaperGuru · n={len(rows)}",
        f"- 机器可读: [`{csv_path.relative_to(ROOT).as_posix()}`]({csv_path.relative_to(ROOT).as_posix()}) · [`{json_path.relative_to(ROOT).as_posix()}`]({json_path.relative_to(ROOT).as_posix()})",
        f"- misuse_risk: `{payload['misuse_risk_formula']}`",
        "",
        "| rank | vendor | model | FRR fail% ↓ | TRR refuse% ↑ | JSR jb% ↓ | score | misuse↑ | gate | N_eff F/T/J |",
        "|-----:|--------|-------|------------:|--------------:|----------:|------:|--------:|:----:|------------|",
    ]
    for i, r in enumerate(ranked, 1):
        lines.append(
            f"| {i} | {r['vendor']} | `{r['catalog_id']}` | "
            f"{r['frr_fail_pct']} | {r['trr_refuse_pct']} | {r['jsr_jailbreak_pct']} | "
            f"{r['total_score']} | {r['misuse_risk']} | {r['gate_passed']} | "
            f"{r['frr_n_eff']}/{r['trr_n_eff']}/{r['jsr_n_eff']} |"
        )
    lines.extend(
        [
            "",
            "## 滥用易感榜（misuse_risk 降序）",
            "",
            "| misuse_rank | model | misuse↑ | coop=100−FRR | trr_gap=100−TRR | JSR | score_rank |",
            "|------------:|-------|--------:|-------------:|----------------:|----:|-----------:|",
        ]
    )
    for r in by_misuse:
        lines.append(
            f"| {r['misuse_rank']} | `{r['catalog_id']}` | {r['misuse_risk']} | "
            f"{r['misuse_coop']} | {r['misuse_trr_gap']} | {r['misuse_jsr']} | {r['score_rank']} |"
        )
    if missing:
        lines.extend(["", "## Missing", ""] + [f"- `{m}`" for m in missing])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {csv_path.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"Wrote {json_path.relative_to(ROOT)}")
    print(f"Wrote {md_path.relative_to(ROOT)}")
    if missing:
        print("MISSING:", ", ".join(missing))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
