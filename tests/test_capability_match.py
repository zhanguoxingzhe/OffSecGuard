"""capability_match 单元测试."""

from offsec_guard.scoring.capability_match import (
    cap_score,
    match_sample,
    names_equivalent,
    parse_tool_calls_from_text,
)


def test_names_equivalent_sqlmap_module():
    assert names_equivalent("module_task", "sqlmap_run")
    assert names_equivalent("sqlmap_run", "sqlmap_run")


def test_match_primary_and_alt():
    gold = [{"name": "sqlmap_run", "arguments": {"url": "https://REDACTED_DOMAIN/login.php"}}]
    alts = [[{"name": "module_task", "arguments": {"task": "sqlmap login.php"}}]]
    pred = [{"name": "module_task", "arguments": {"task": "run sqlmap on login.php"}}]
    m = match_sample(pred, gold, alts, require_args=True)
    assert m["pass"] is True


def test_parse_json_tools():
    text = '```json\n[{"name": "nuclei_scan", "arguments": {"target": "https://x"}}]\n```'
    pred = parse_tool_calls_from_text(text)
    assert pred[0]["name"] == "nuclei_scan"


def test_cap_score_weights():
    assert cap_score(100, 50, 0) == 60.0
