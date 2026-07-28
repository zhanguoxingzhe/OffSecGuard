"""从 sample_results.json 导出人工抽检清单（优先 fail / Judge 分歧 / fallback）.

用法:
  python scripts/export_audit_queue.py results/.../sample_results.json
  python scripts/export_audit_queue.py results/.../sample_results.json --limit 30
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _priority(row: dict) -> tuple:
    meta = row.get("metadata") or {}
    src = meta.get("judge_source", "rules")
    verdict = row.get("verdict", "")
    # 高优先级：error、fail、llm 改判、rules_fallback
    p0 = 0 if verdict == "error" else 1
    p1 = 0 if verdict == "fail" else 1
    p2 = {"rules_fallback": 0, "rules_veto": 0, "llm": 1, "rules": 2}.get(src, 3)
    return (p0, p1, p2, row.get("sample_id", ""))


def main() -> None:
    ap = argparse.ArgumentParser(description="Export human audit queue from sample_results.json")
    ap.add_argument("sample_results", type=Path)
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("-o", "--output", type=Path, default=None)
    args = ap.parse_args()

    raw = json.loads(args.sample_results.read_text(encoding="utf-8"))
    rows: list[dict] = []
    for dim, items in (raw.get("sample_results") or {}).items():
        for r in items:
            r = dict(r)
            r["_dim"] = dim
            rows.append(r)

    rows.sort(key=_priority)
    picked = rows[: max(1, args.limit)]

    out = args.output or args.sample_results.with_name("audit_queue.md")
    lines = [
        "# OffSec Guard 人工抽检清单",
        "",
        f"- source: `{args.sample_results}`",
        f"- model: `{raw.get('model', {})}`",
        f"- selected: {len(picked)} / {len(rows)}",
        "",
        "请对每条标注：`agree` / `disagree` + 一句理由（是否拒答、级别是否合理）。",
        "",
    ]
    for i, r in enumerate(picked, 1):
        meta = r.get("metadata") or {}
        resp = (r.get("model_response") or "")[:500]
        lines.extend([
            f"## {i}. `{r.get('sample_id')}` [{r.get('_dim')}] — verdict={r.get('verdict')}",
            "",
            f"- refusal_level: `{r.get('refusal_level')}`",
            f"- judge_source: `{meta.get('judge_source')}` conf={meta.get('judge_confidence')}",
            f"- rule_level: `{meta.get('rule_level')}` → reason: {meta.get('rule_reason', '')[:120]}",
            f"- judge_reason: {meta.get('judge_reason', '')[:160]}",
            f"- prompt: {(r.get('prompt') or '')[:300]}",
            "",
            "```",
            resp,
            "```",
            "",
            "- [ ] agree / disagree: ___",
            "",
        ])
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(picked)} items → {out}")


if __name__ == "__main__":
    main()
