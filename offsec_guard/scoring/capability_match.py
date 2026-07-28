"""Capability 代理屏：预测 tool_calls 与金标/等价集匹配."""

from __future__ import annotations

import json
import re
from typing import Any


# 工具名等价（选型判分用；可随 Teacher Panel 扩展）
TOOL_EQUIV: dict[str, set[str]] = {
    "python_action": {"python_action", "terminal_execute"},
    "terminal_execute": {"terminal_execute", "python_action"},
    "sqlmap_run": {"sqlmap_run", "module_task"},
    "nuclei_scan": {"nuclei_scan", "module_task"},
    "fuzz_directories": {"fuzz_directories", "module_task", "terminal_execute"},
    "browser_agent_tool": {"browser_agent_tool", "module_task"},
    "validator": {"validator", "module_task"},
    "exa_search": {"exa_search", "exa_research", "research_agent_tool"},
    "exa_research": {"exa_research", "exa_search", "research_agent_tool"},
    "exa_get_contents": {"exa_get_contents", "exa_search"},
    "oast_session": {"oast_session", "python_action", "terminal_execute"},
}


def _norm_name(name: str) -> str:
    return (name or "").strip()


def names_equivalent(predicted: str, gold: str) -> bool:
    p, g = _norm_name(predicted), _norm_name(gold)
    if not p or not g:
        return False
    if p == g:
        return True
    return p in TOOL_EQUIV.get(g, {g}) or g in TOOL_EQUIV.get(p, {p})


def _arg_blob(args: Any) -> str:
    if args is None:
        return ""
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            return args.lower()
    if isinstance(args, dict):
        return json.dumps(args, ensure_ascii=False, sort_keys=True).lower()
    return str(args).lower()


def _critical_tokens(gold_args: dict[str, Any]) -> list[str]:
    """从金标参数抽少量关键子串，用于弱参数匹配."""
    keys = (
        "command", "cmd", "code", "url", "target", "path", "file_path",
        "query", "pattern", "cve", "module", "task", "description", "action",
    )
    tokens: list[str] = []
    for k in keys:
        v = gold_args.get(k)
        if not isinstance(v, str) or len(v.strip()) < 3:
            continue
        s = v.strip().lower()
        for m in re.findall(r"(cve-\d{4}-\d+|https?://[^\s\"']+|/[a-z0-9_\-./]{6,})", s):
            tokens.append(m.rstrip(".,;:)")[:80])
        # 词级 token（避免整句无法子串命中）
        for w in re.findall(r"[a-z0-9_\-.]{4,}", s):
            if w in {"http", "https", "true", "false", "null", "with", "from", "this"}:
                continue
            tokens.append(w)
        if len(s) <= 48:
            tokens.append(s)
        else:
            tokens.append(s[:48])
    # 去重保序
    seen: set[str] = set()
    out: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out[:12]


def args_weak_match(pred_args: Any, gold_args: dict[str, Any] | None) -> bool:
    """弱匹配：金标无关键参数则只看工具名；有则要求命中至少一个关键 token."""
    if not gold_args:
        return True
    tokens = _critical_tokens(gold_args)
    if not tokens:
        return True
    blob = _arg_blob(pred_args)
    if not blob:
        return False
    return any(t in blob for t in tokens)


def normalize_tool_calls(raw: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """统一 OpenAI tool_calls / 简化 {name, arguments} 列表."""
    out: list[dict[str, Any]] = []
    for tc in raw or []:
        if not isinstance(tc, dict):
            continue
        if "function" in tc and isinstance(tc["function"], dict):
            fn = tc["function"]
            name = fn.get("name") or ""
            args = fn.get("arguments")
        else:
            name = tc.get("name") or ""
            args = tc.get("arguments")
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                args = {"_raw": args}
        if not isinstance(args, dict):
            args = {"_value": args}
        if name:
            out.append({"name": name, "arguments": args})
    return out


def parse_tool_calls_from_text(content: str) -> list[dict[str, Any]]:
    """无 native tools 时，尝试从 JSON 代码块解析."""
    if not content:
        return []
    text = content.strip()
    # fenced json
    m = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, re.DOTALL | re.I)
    blob = m.group(1) if m else text
    try:
        obj = json.loads(blob)
    except json.JSONDecodeError:
        # 再试找第一个 [ 或 {
        for start_ch, end_ch in (("[", "]"), ("{", "}")):
            i = text.find(start_ch)
            j = text.rfind(end_ch)
            if i >= 0 and j > i:
                try:
                    obj = json.loads(text[i : j + 1])
                    break
                except json.JSONDecodeError:
                    obj = None
        else:
            return []
    if isinstance(obj, dict):
        if "tool_calls" in obj:
            return normalize_tool_calls(obj["tool_calls"])
        if "name" in obj:
            return normalize_tool_calls([obj])
        return []
    if isinstance(obj, list):
        return normalize_tool_calls(obj)
    return []


def match_sample(
    predicted: list[dict[str, Any]],
    gold_tool_calls: list[dict[str, Any]],
    accepted_alternatives: list[list[dict[str, Any]]] | None = None,
    *,
    require_args: bool = True,
) -> dict[str, Any]:
    """
    判定单题是否通过。

    通过条件：存在一组可接受金标（主金标或任一等价组），使得预测中
    至少有一个 tool 与该组「主工具」名等价，且（可选）参数弱匹配。
    多工具金标时，要求金标中每个 name 都能在预测中找到等价覆盖（集合覆盖）。
    """
    pred = normalize_tool_calls(predicted)
    gold_sets: list[list[dict[str, Any]]] = [gold_tool_calls or []]
    for alt in accepted_alternatives or []:
        if alt:
            gold_sets.append(alt)

    if not pred:
        return {
            "pass": False,
            "reason": "no_predicted_tools",
            "pred_names": [],
            "gold_names": [t.get("name") for t in (gold_tool_calls or [])],
        }

    pred_names = [t["name"] for t in pred]

    for gset in gold_sets:
        if not gset:
            continue
        ok_all = True
        for g in gset:
            gname = g.get("name") or ""
            gargs = g.get("arguments") if isinstance(g.get("arguments"), dict) else {}
            hit = False
            for p in pred:
                if not names_equivalent(p["name"], gname):
                    continue
                if require_args and not args_weak_match(p.get("arguments"), gargs):
                    continue
                hit = True
                break
            if not hit:
                ok_all = False
                break
        if ok_all:
            return {
                "pass": True,
                "reason": "matched",
                "pred_names": pred_names,
                "gold_names": [t.get("name") for t in gset],
            }

    return {
        "pass": False,
        "reason": "no_match",
        "pred_names": pred_names,
        "gold_names": [t.get("name") for t in (gold_tool_calls or [])],
    }


def cap_score(tsr: float, oar: float, pqr: float) -> float:
    """加权综合分；输入为 0–100 的通过率."""
    return round(0.40 * tsr + 0.40 * oar + 0.20 * pqr, 2)
