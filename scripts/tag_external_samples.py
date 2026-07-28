"""Tag external dataset samples with OffSec Guard taxonomy.

Filters and labels HarmBench cybercrime_intrusion and WildGuard cyberattack samples,
mapping them to {context: unauthorized, domain, capability, expected_action: refuse}.
"""
from __future__ import annotations

import csv
import json
import os
import random
from pathlib import Path
from typing import Any

RAW = Path("e:/wanzhen/scantist/github/PentestAI/offsec-guard/datasets/raw_sources")

# ── Domain/Capability keyword mappings ──────────────────────────────
DOMAIN_KEYWORDS: list[tuple[list[str], str]] = [
    (["scan", "port scan", "nmap", "enumerate", "reconnaissance", "fingerprint", "discover"], "reconnaissance"),
    (["exploit", "vulnerability", "cve", "rce", "remote code", "sql injection", "sqli", "xss", "csrf",
      "command injection", "path traversal", "deserialization", "buffer overflow", "rop", "shellcode",
      "metasploit", "payload", "ghostcat", "log4j", "log4shell", "dirty cow", "dirtyc0w",
      "eternalblue", "ms17-010", "struts", "heartbleed"], "exploitation"),
    (["privilege escalation", "escalate privilege", "lateral movement", "persistence", "backdoor",
      "credential", "password dump", "mimikatz", "hash", "lsass", "keylogger", "key logging",
      "post-exploit", "post exploit", "post exploitation"], "post_exploitation"),
    (["malware", "ransomware", "trojan", "virus", "worm", "rootkit", "botnet", "backdoor",
      "evasion", "obfuscate", "antivirus", "av bypass", "payload", "dropper", "stager"], "weaponization"),
    (["phishing", "social engineering", "spear phish", "click", "convinc", "persuade",
      "email", "pretext", "baiting"], "delivery"),
    (["reverse shell", "bind shell", "c2", "command and control", "beacon", "tunnel",
      "proxy", "pivot", "listener"], "command_control"),
    (["install", "deploy", "upload", "drop", "plant"], "installation"),
    (["exfiltrat", "steal data", "extract data", "data leak", "data breach", "dump database",
      "extract database", "exfiltr"], "exfiltration"),
]

CAPABILITY_KEYWORDS: list[tuple[list[str], str]] = [
    (["write a script", "code", "develop", "implement", "create a program", "generate code",
      "python script", "bash script", "powershell script", "write code", "program",
      "javascript", "html"], "code_generation"),
    (["use", "run", "execute", "deploy", "launch", "operate", "nmap", "sqlmap", "metasploit",
      "msfvenom", "netcat", "nc", "dirb", "gobuster", "hydra", "john", "hashcat",
      "burp", "wireshark", "tcpdump", "openvas", "nessus"], "tool_operation"),
    (["how to", "explain", "describe", "what is", "tutorial", "step-by-step", "guide",
      "instructions", "manual", "documentation"], "knowledge_query"),
    (["connect", "tunnel", "proxy", "reverse connection", "bind", "listen", "establish connection",
      "port forward", "pivot"], "network_operation"),
]

# Tags to exclude (too generic or not attack-surface related)
EXCLUDE_KEYWORDS: list[str] = [
    "atm machine", "vote machine", "voting machine", "drone", "dj drone",
    "car", "jeep", "vehicle", "smart lock", "iot door", "gps",
    "keurig", "coffee machine", "refrigerator", "smart home",
    "surveillance camera", "traffic light",
    "school grade", "university transcript",
    "social media account", "facebook", "instagram", "twitter", "tiktok",
    "news article", "fake news", "newspaper",
]


def guess_domain(text: str) -> str:
    text_lower = text.lower()
    for keywords, domain in DOMAIN_KEYWORDS:
        for kw in keywords:
            if kw in text_lower:
                return domain
    return "exploitation"


def guess_capability(text: str) -> str:
    text_lower = text.lower()
    for keywords, cap in CAPABILITY_KEYWORDS:
        for kw in keywords:
            if kw in text_lower:
                return cap
    return "tool_operation"


def should_exclude(text: str) -> bool:
    text_lower = text.lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw in text_lower:
            return True
    return False


# ── Process HarmBench ───────────────────────────────────────────────
def process_harmbench() -> list[dict[str, Any]]:
    csvi = Path(RAW, "harmbench_behaviors_text_all.csv")
    with open(csvi, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    cyber = [r for r in rows if r.get("SemanticCategory") == "cybercrime_intrusion"]
    print(f"HarmBench cybercrime_intrusion total: {len(cyber)}")

    samples: list[dict[str, Any]] = []
    excluded = 0
    for i, r in enumerate(cyber):
        text = r.get("Behavior", "")
        if not text or should_exclude(text):
            excluded += 1
            continue

        domain = guess_domain(text)
        capability = guess_capability(text)
        difficulty = "hard" if r.get("FunctionalCategory") == "contextual" else "medium"

        samples.append({
            "id": f"trr-hb-{i:03d}",
            "text": text.strip(),
            "context": "unauthorized",
            "domain": domain,
            "capability": capability,
            "expected_action": "refuse",
            "difficulty": difficulty,
            "source": "harmbench",
            "tags": ["harmbench", domain, capability],
            "history": [],
        })

    print(f"  → kept {len(samples)}, excluded {excluded}")
    return samples


# ── Process WildGuard ───────────────────────────────────────────────
def process_wildguard(max_samples: int = 60) -> list[dict[str, Any]]:
    jsonl = Path(RAW, "wildguard_cyberattack.jsonl")
    if not jsonl.exists():
        print("WildGuard cyberattack file not found, skipping")
        return []

    rows: list[dict] = []
    with open(jsonl, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    print(f"WildGuard cyberattack total: {len(rows)}")

    # Deduplicate by normalized prompt
    seen: set[str] = set()
    deduped: list[dict] = []
    for r in rows:
        prompt = r.get("prompt", "")
        norm = prompt.strip().lower()[:80]
        if norm not in seen and not should_exclude(prompt):
            seen.add(norm)
            deduped.append(r)

    # Shuffle and sample
    random.seed(42)
    random.shuffle(deduped)
    selected = deduped[:max_samples]

    samples: list[dict[str, Any]] = []
    for i, r in enumerate(selected):
        text = r.get("prompt", "").strip()
        is_adversarial = r.get("adversarial") == "True"
        domain = guess_domain(text)
        capability = guess_capability(text)
        difficulty = "hard" if is_adversarial else "medium"

        samples.append({
            "id": f"trr-wg-{i:03d}",
            "text": text,
            "context": "unauthorized",
            "domain": domain,
            "capability": capability,
            "expected_action": "refuse",
            "difficulty": difficulty,
            "source": "wildguard",
            "tags": ["wildguard", domain, capability] + (["adversarial"] if is_adversarial else []),
            "history": [],
        })

    print(f"  → sampled {len(samples)} from {len(deduped)} unique")
    return samples


# ── Main ────────────────────────────────────────────────────────────
def main():
    hb = process_harmbench()
    wg = process_wildguard(max_samples=45)
    all_samples = hb + wg

    print(f"\n=== Combined: {len(all_samples)} samples ===")
    import collections
    domains = collections.Counter(s["domain"] for s in all_samples)
    caps = collections.Counter(s["capability"] for s in all_samples)
    for d, c in domains.most_common():
        print(f"  domain:{d}: {c}")
    for c, n in caps.most_common():
        print(f"  capability:{c}: {n}")

    out = Path("e:/wanzhen/scantist/github/PentestAI/offsec-guard/datasets/v1/samples/trr/unauthorized.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for s in all_samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
