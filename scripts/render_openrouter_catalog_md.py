"""Render a clean human-readable model list from the YAML catalog."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "configs" / "batch" / "openrouter_mainstream_models.yaml"
OUT = ROOT / "docs" / "OPENROUTER_MODEL_LIST.md"

VENDOR_ORDER = [
    "openai",
    "anthropic",
    "google",
    "deepseek",
    "qwen",
    "meta-llama",
    "mistralai",
    "x-ai",
    "moonshotai",
    "z-ai",
    "amazon",
    "minimax",
    "bytedance-seed",
    "cohere",
    "nvidia",
    "tencent",
    "xiaomi",
]

P1_AUTHORS = {
    "amazon",
    "minimax",
    "bytedance-seed",
    "cohere",
    "nvidia",
    "tencent",
    "xiaomi",
}

# 产品线本名含 pro/flash，不算「同代 Pro 变体」
_PRODUCT_TIER_OK = (
    "gemini-",
    "deepseek-v4-pro",
    "deepseek-v4-flash",
    "nova-pro",
    "nova-premier",
    "mimo-v2.5-pro",  # 小米产品档
)


def annotate_batch(mid: str, batch: str | None, author: str) -> tuple[str, str]:
    """返回 (批次标签, 简短说明)."""
    low = mid.lower()
    name = mid.split("/", 1)[-1]

    is_variant = False
    if any(x in low for x in _PRODUCT_TIER_OK):
        is_variant = False
    elif name.endswith("-pro") or "-pro-" in name:
        is_variant = True
    elif name.endswith("-fast") or "-fast-" in name:
        is_variant = True
    elif name.endswith("-mini-high") or name.endswith("-high"):
        # o3-mini-high / o4-mini-high：同代加强变体，延后
        is_variant = True

    if batch == "core":
        return "主跑·基线", "首轮必跑"
    if is_variant:
        return "延后·Pro/Fast", "同代变体，入围后再跑"
    if author in P1_AUTHORS:
        return "扩展·P1厂", "第二批厂商"
    return "扩展·代际", "上一代/对照"


def batch_sort_key(label: str) -> int:
    order = {
        "主跑·基线": 0,
        "延后·Pro/Fast": 1,
        "扩展·代际": 2,
        "扩展·P1厂": 3,
    }
    return order.get(label, 9)


def main() -> None:
    data = yaml.safe_load(SRC.read_text(encoding="utf-8"))
    n_core = len(data.get("batch_select_core") or [])
    n_ext = len(data.get("batch_select_extended") or [])
    n_smoke = len(data.get("batch_width_smoke") or [])
    n_extra = len(data.get("discovered_extras") or [])

    lines: list[str] = [
        "# OpenRouter 选型模型清单（梳理版）",
        "",
        f"> 生成自 `{SRC.relative_to(ROOT).as_posix()}` · `{data.get('generated_at', '')}`  ",
        "> 刷新：`python scripts/refresh_openrouter_catalog.py`",
        "",
        "## 图例（表格「批次」列）",
        "",
        "| 标注 | 含义 | 何时跑 |",
        "|------|------|--------|",
        "| **主跑·基线** | 同代默认款（无 -pro/-fast） | **现在就跑** |",
        "| **延后·Pro/Fast** | 同代加速/高算力变体 | 基线入围后再补 |",
        "| **扩展·代际** | 更旧代际对照 | 需要曲线时再跑 |",
        "| **扩展·P1厂** | 第二批厂商 | core 之后 |",
        "",
        f"规模：主跑基线 **{n_core}** · 扩展合计 **{n_ext}** · 冒烟 {n_smoke} · 自动发现未入选 {n_extra}",
        "",
        "说明：`gemini-*-pro` / `deepseek-v4-pro` 等是**产品档位名**，标为主跑基线，不是同款 Pro 变体。",
        "",
        "---",
        "",
        "## 厂商梯队",
        "",
    ]

    vendors = data.get("vendors") or {}
    for author in VENDOR_ORDER:
        block = vendors.get(author)
        if not block:
            continue
        select_rows = [r for r in block.get("ladder") or [] if r.get("select")]
        if not select_rows:
            continue

        # annotate
        annotated = []
        for r in select_rows:
            label, tip = annotate_batch(r["id"], r.get("batch"), author)
            annotated.append((label, tip, r))

        n_base = sum(1 for lab, _, __ in annotated if lab == "主跑·基线")
        n_var = sum(1 for lab, _, __ in annotated if lab == "延后·Pro/Fast")
        lines.append(f"### {block.get('vendor', author)} (`{author}`)")
        lines.append("")
        lines.append(f"本厂：主跑基线 **{n_base}** · 延后 Pro/Fast **{n_var}** · 其余扩展 {len(annotated)-n_base-n_var}")
        lines.append("")
        lines.append("| 批次 | 代际 | 档位 | OpenRouter ID | $/M in | 说明 |")
        lines.append("|------|------|------|---------------|--------|------|")

        annotated.sort(
            key=lambda t: (
                batch_sort_key(t[0]),
                str(t[2].get("gen") or ""),
                str(t[2].get("role") or ""),
                t[2]["id"],
            )
        )
        for label, tip, r in annotated:
            pin = r.get("price_prompt_per_m", "")
            note = r.get("note") or tip
            # 主跑加粗 ID，延后用普通
            mid = r["id"]
            id_cell = f"**`{mid}`**" if label == "主跑·基线" else f"`{mid}`"
            batch_cell = f"**{label}**" if label == "主跑·基线" else label
            lines.append(
                f"| {batch_cell} | {r.get('gen', '')} | {r.get('role', '')} | "
                f"{id_cell} | {pin} | {note} |"
            )
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## 宽度冒烟（每厂 1 个 · 连通性）",
            "",
        ]
    )
    smoke_ids = {r["id"] for r in (data.get("batch_width_smoke") or [])}
    for r in data.get("batch_width_smoke") or []:
        lines.append(f"- `{r['id']}`")
    ext_rows = data.get("external_non_openrouter") or []
    core_ids = {r["id"] for r in (data.get("batch_select_core") or [])}
    lines.extend(
        [
            "",
            "---",
            "",
            "## 非 OpenRouter（已入主跑·基线）",
            "",
        ]
    )
    for r in ext_rows:
        mid = r["id"]
        tag = "**主跑·基线**" if mid in core_ids else "未入 core"
        note = r.get("note") or "own endpoint"
        lines.append(f"- {tag} `{mid}` — {note}")
    if not ext_rows:
        lines.append("- （无）")
    lines.extend(
        [
            "",
            "## 跑法摘要",
            "",
            "1. 只跑表格里 **主跑·基线**（=`batch_select_core`，含 PaperGuru）",
            "2. 入围后补同一行代际的 **延后·Pro/Fast**",
            "3. 需要代际曲线或更多厂商时再跑其余扩展",
            "",
        ]
    )
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} (smoke={len(smoke_ids)})")


if __name__ == "__main__":
    main()
