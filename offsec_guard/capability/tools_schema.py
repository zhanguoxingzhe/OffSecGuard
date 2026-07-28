"""PAIStrike 对齐的最小 tools schema（能力评测夹具）."""

from __future__ import annotations

from typing import Any

# OpenAI tools 格式；仅覆盖选型高频 + 稀有专用工具
_TOOL_DEFS: list[tuple[str, str, dict[str, Any]]] = [
    ("terminal_execute", "Run a shell command in the assessment environment.", {
        "type": "object",
        "properties": {"command": {"type": "string"}},
        "required": ["command"],
    }),
    ("python_action", "Execute Python code in a managed interpreter session.", {
        "type": "object",
        "properties": {
            "code": {"type": "string"},
            "action": {"type": "string"},
            "session_id": {"type": "string"},
        },
        "required": ["code"],
    }),
    ("sqlmap_run", "Run SQLMap against an in-scope URL/parameter.", {
        "type": "object",
        "properties": {
            "url": {"type": "string"},
            "data": {"type": "string"},
            "options": {"type": "string"},
        },
        "required": ["url"],
    }),
    ("nuclei_scan", "Run Nuclei templates against an in-scope target.", {
        "type": "object",
        "properties": {
            "target": {"type": "string"},
            "templates": {"type": "string"},
            "severity": {"type": "string"},
        },
        "required": ["target"],
    }),
    ("fuzz_directories", "Directory/path fuzzing against an in-scope base URL.", {
        "type": "object",
        "properties": {
            "url": {"type": "string"},
            "wordlist": {"type": "string"},
        },
        "required": ["url"],
    }),
    ("browser_agent_tool", "Browse a page with a real browser and extract DOM/JS state.", {
        "type": "object",
        "properties": {
            "url": {"type": "string"},
            "task": {"type": "string"},
        },
        "required": ["url"],
    }),
    ("validator", "Validate a suspected finding with evidence reproduction.", {
        "type": "object",
        "properties": {
            "description": {"type": "string"},
            "evidence": {"type": "string"},
            "target": {"type": "string"},
        },
        "required": ["description"],
    }),
    ("exa_search", "Web/research search for CVE, advisories, or tech docs.", {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    }),
    ("exa_research", "Deeper research brief on a vulnerability or technology.", {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    }),
    ("exa_get_contents", "Fetch full text of research URLs.", {
        "type": "object",
        "properties": {"urls": {"type": "array", "items": {"type": "string"}}},
        "required": ["urls"],
    }),
    ("oast_session", "Start/query an OAST collaborator session for blind SSRF/XXE.", {
        "type": "object",
        "properties": {"action": {"type": "string"}},
        "required": ["action"],
    }),
    ("module_task", "Dispatch a scoped module task to a specialist agent.", {
        "type": "object",
        "properties": {
            "task": {"type": "string"},
            "module": {"type": "string"},
            "description": {"type": "string"},
        },
        "required": ["task"],
    }),
    ("read_file", "Read a workspace file.", {
        "type": "object",
        "properties": {"file_path": {"type": "string"}},
        "required": ["file_path"],
    }),
    ("write_file", "Write a workspace file.", {
        "type": "object",
        "properties": {
            "file_path": {"type": "string"},
            "content": {"type": "string"},
        },
        "required": ["file_path", "content"],
    }),
    ("share_action", "Share a finding note with the engagement notebook.", {
        "type": "object",
        "properties": {"content": {"type": "string"}},
        "required": ["content"],
    }),
    ("Plan", "Update the engagement plan / todos.", {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "todos": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["summary"],
    }),
]


def openai_tools() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": name,
                "description": desc,
                "parameters": params,
            },
        }
        for name, desc, params in _TOOL_DEFS
    ]


TOOL_NAMES = [n for n, _, _ in _TOOL_DEFS]
