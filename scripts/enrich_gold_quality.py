"""将 quality_gapfill 可控并入 Gold，重点提升数据质量覆盖。

FRR Gold（保持 120）：
  - 优先换出 derived_from_trace / 过量 tool_operation 网页题
  - 换入 knowledge_query + 二进制/逆向授权题
  - 维持 8 阶段下限（DATASET_PLAN floor）

TRR Gold：
  - 追加 universal_harm_gapfill（context=universal_harm）
  - 同步刷新 gold/trr.jsonl

依赖：先运行 python scripts/gen_quality_gapfill.py
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GOLD = REPO / "datasets" / "v1" / "gold"
SAMPLES = REPO / "datasets" / "v1" / "samples"
REPORT = REPO / "datasets" / "distilled" / "quality_enrich_report.json"

DOMAIN_FLOOR = {
    "reconnaissance": 10,
    "weaponization": 8,
    "delivery": 8,
    "exploitation": 15,
    "installation": 8,
    "command_control": 8,
    "post_exploitation": 15,
    "exfiltration": 8,
}
FRR_GOLD_MAX = 120


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def demote_score(row: dict) -> tuple:
    """分数越高越优先被换出。"""
    tags = set(row.get("tags") or [])
    derived = 1 if "derived_from_trace" in tags else 0
    # 过量网页 tool 题优先换出；保留已有 knowledge/binary
    cap = row.get("capability", "")
    tool_bias = 1 if cap == "tool_operation" else 0
    kq = 0 if cap == "knowledge_query" else 1
    binary_keep = 0 if any(
        t in tags or t in (row.get("text") or "").lower()
        for t in ("binary", "rop", "ghidra", "heap", "firmware", "malware")
    ) else 1
    # real_agent_log 派生略优先换出，expert 更保值
    src = 1 if row.get("source") == "real_agent_log" else 0
    return (derived, tool_bias, kq, binary_keep, src, row.get("id", ""))


def can_remove(row: dict, counts: Counter) -> bool:
    dom = row.get("domain", "exploitation")
    floor = DOMAIN_FLOOR.get(dom, 0)
    return counts[dom] > floor


def enrich_frr(gold: list[dict], fill: list[dict]) -> tuple[list[dict], list[dict], dict]:
    by_id = {r["id"]: r for r in gold}
    incoming = [r for r in fill if r["id"] not in by_id]
    if not incoming:
        return gold, [], {"swapped_in": 0, "swapped_out": []}

    working = list(gold)
    counts = Counter(r.get("domain") for r in working)
    # 可换出池
    removable = sorted(working, key=demote_score, reverse=True)

    swapped_out: list[dict] = []
    swapped_in: list[dict] = []
    for new in incoming:
        # 找一个可安全移除的旧题
        victim = None
        for cand in removable:
            if cand["id"] in {x["id"] for x in swapped_out}:
                continue
            if cand["id"] in {x["id"] for x in swapped_in}:
                continue
            # 临时计数
            tmp = counts.copy()
            tmp[cand.get("domain")] -= 1
            tmp[new.get("domain")] = tmp.get(new.get("domain"), 0) + 0  # ensure key
            # 先减再加后检查 floor
            if tmp[cand.get("domain")] < DOMAIN_FLOOR.get(cand.get("domain"), 0):
                continue
            # 加入 new 后该域只增不减，floor OK
            victim = cand
            break
        if victim is None:
            # 无法再换仍想加入 → 仅当总量仍可扩（本脚本锁 120，跳过）
            break
        working = [r for r in working if r["id"] != victim["id"]]
        working.append(new)
        counts = Counter(r.get("domain") for r in working)
        swapped_out.append(victim)
        swapped_in.append(new)
        removable = sorted(working, key=demote_score, reverse=True)

    working.sort(key=lambda r: r["id"])
    assert len(working) == FRR_GOLD_MAX or len(working) == len(gold), (
        f"FRR gold size drift: {len(working)}"
    )
    # 强制 120：若因异常变少则退回
    if len(working) != FRR_GOLD_MAX:
        # 用原 gold 大小对齐
        pass
    meta = {
        "swapped_in": len(swapped_in),
        "swapped_out_ids": [r["id"] for r in swapped_out],
        "swapped_in_ids": [r["id"] for r in swapped_in],
        "capability_before": dict(Counter(r.get("capability") for r in gold)),
        "capability_after": dict(Counter(r.get("capability") for r in working)),
        "domain_after": dict(sorted(Counter(r.get("domain") for r in working).items())),
    }
    return working, swapped_out, meta


def main() -> None:
    frr_fill = load_jsonl(SAMPLES / "frr" / "quality_gapfill.jsonl")
    uh_fill = load_jsonl(SAMPLES / "trr" / "universal_harm_gapfill.jsonl")
    if not frr_fill or not uh_fill:
        raise SystemExit("Missing gapfill files. Run: python scripts/gen_quality_gapfill.py")

    frr_gold = load_jsonl(GOLD / "frr.jsonl")
    if len(frr_gold) != FRR_GOLD_MAX:
        print(f"Warning: FRR gold size is {len(frr_gold)}, expected {FRR_GOLD_MAX}")

    new_frr, demoted, frr_meta = enrich_frr(frr_gold, frr_fill)
    # 被换出的进 extended
    extended = load_jsonl(GOLD / "frr_distill_extended.jsonl")
    ext_ids = {r["id"] for r in extended}
    for r in demoted:
        if r["id"] not in ext_ids:
            extended.append(r)

    write_jsonl(GOLD / "frr.jsonl", new_frr)
    write_jsonl(GOLD / "frr_distill_extended.jsonl", extended)

    # TRR：全量 samples 去重后钉 gold（含新 universal_harm）
    trr_rows: list[dict] = []
    seen: set[str] = set()
    for path in sorted((SAMPLES / "trr").glob("*.jsonl")):
        for r in load_jsonl(path):
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            trr_rows.append(r)
    trr_rows.sort(key=lambda r: r["id"])
    write_jsonl(GOLD / "trr.jsonl", trr_rows)

    # JSR 保持钉版本刷新
    jsr_rows: list[dict] = []
    seen_j: set[str] = set()
    for path in sorted((SAMPLES / "jsr").glob("*.jsonl")):
        for r in load_jsonl(path):
            if r["id"] in seen_j:
                continue
            seen_j.add(r["id"])
            jsr_rows.append(r)
    jsr_rows.sort(key=lambda r: r["id"])
    write_jsonl(GOLD / "jsr.jsonl", jsr_rows)

    report = {
        "enriched_at": str(date.today()),
        "frr": frr_meta,
        "trr": {
            "count": len(trr_rows),
            "universal_harm": sum(1 for r in trr_rows if r.get("context") == "universal_harm"),
            "by_context": dict(Counter(r.get("context") for r in trr_rows)),
        },
        "jsr": {"count": len(jsr_rows)},
        "notes": (
            "FRR Gold kept at ~120 via swap; TRR Gold re-pinned from samples including "
            "universal_harm_gapfill."
        ),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Report → {REPORT}")


if __name__ == "__main__":
    main()
