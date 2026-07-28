"""从 OpenRouter /models 刷新主流模型目录（宽度 + 同厂深度 + 自动发现最新）。

用法:
  python scripts/refresh_openrouter_catalog.py
  python scripts/refresh_openrouter_catalog.py --check-only
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT_YAML = ROOT / "configs" / "batch" / "openrouter_mainstream_models.yaml"
OUT_JSON = ROOT / "configs" / "batch" / "openrouter_mainstream_models.json"

_EXCLUDE_SUBSTR = (
    "image",
    "audio",
    "tts",
    "transcri",
    "whisper",
    "search",
    "guard",
    "embed",
    "moderation",
    "lyria",
    "deep-research",
    "voxtral",
    "-vl-",  # 视觉语言模型，主护栏评测用文本 chat
    ":free",
)

# 手工精选（保证角色/代数标注准确）；自动发现会把漏网最新模型补进来。
# 注意：OpenRouter 无裸 slug openai/gpt-5.6，只有 luna/sol/terra 三线。
VENDOR_LADDERS: dict[str, dict] = {
    "openai": {
        "vendor": "OpenAI",
        "auto_prefixes": ["openai/gpt-5", "openai/o1", "openai/o3", "openai/o4"],
        "ladder": [
            # GPT-5.6 三线（最新代，无统一 gpt-5.6）
            {"id": "openai/gpt-5.6-sol", "role": "flagship", "gen": "5.6-sol", "note": "5.6 Sol"},
            {"id": "openai/gpt-5.6-sol-pro", "role": "flagship", "gen": "5.6-sol", "note": "5.6 Sol Pro"},
            {"id": "openai/gpt-5.6-terra", "role": "mid", "gen": "5.6-terra", "note": "5.6 Terra"},
            {"id": "openai/gpt-5.6-terra-pro", "role": "mid", "gen": "5.6-terra", "note": "5.6 Terra Pro"},
            {"id": "openai/gpt-5.6-luna", "role": "lite", "gen": "5.6-luna", "note": "5.6 Luna"},
            {"id": "openai/gpt-5.6-luna-pro", "role": "lite", "gen": "5.6-luna", "note": "5.6 Luna Pro"},
            # 5.5 / 5.4
            {"id": "openai/gpt-5.5", "role": "flagship", "gen": "5.5", "note": "5.5"},
            {"id": "openai/gpt-5.5-pro", "role": "flagship", "gen": "5.5", "note": "5.5 Pro"},
            {"id": "openai/gpt-5.4", "role": "flagship", "gen": "5.4", "note": "基线旗舰"},
            {"id": "openai/gpt-5.4-pro", "role": "flagship", "gen": "5.4", "note": "5.4 Pro"},
            {"id": "openai/gpt-5.4-mini", "role": "mid", "gen": "5.4", "note": "5.4 Mini"},
            {"id": "openai/gpt-5.4-nano", "role": "lite", "gen": "5.4", "note": "5.4 Nano"},
            # 5.3 / 5.2 / 5.1 / 5
            {"id": "openai/gpt-5.3-chat", "role": "previous", "gen": "5.3", "note": "5.3 Chat"},
            {"id": "openai/gpt-5.2", "role": "previous", "gen": "5.2", "note": "5.2"},
            {"id": "openai/gpt-5.2-pro", "role": "previous", "gen": "5.2", "note": "5.2 Pro"},
            {"id": "openai/gpt-5.1", "role": "previous", "gen": "5.1", "note": "5.1"},
            {"id": "openai/gpt-5", "role": "previous", "gen": "5.0", "note": "GPT-5"},
            {"id": "openai/gpt-5-mini", "role": "lite", "gen": "5.0", "note": "GPT-5 Mini"},
            {"id": "openai/gpt-5-nano", "role": "lite", "gen": "5.0", "note": "GPT-5 Nano"},
            {"id": "openai/gpt-5-pro", "role": "previous", "gen": "5.0", "note": "GPT-5 Pro"},
            {"id": "openai/gpt-4o", "role": "previous", "gen": "4o", "note": "GPT-4o 对照"},
            # Reasoning
            {"id": "openai/o3", "role": "reasoning", "gen": "o3", "note": "o3"},
            {"id": "openai/o3-pro", "role": "reasoning", "gen": "o3", "note": "o3 Pro"},
            {"id": "openai/o3-mini", "role": "reasoning", "gen": "o3", "note": "o3 Mini"},
            {"id": "openai/o3-mini-high", "role": "reasoning", "gen": "o3", "note": "o3 Mini High"},
            {"id": "openai/o4-mini", "role": "reasoning", "gen": "o4", "note": "o4 Mini"},
            {"id": "openai/o4-mini-high", "role": "reasoning", "gen": "o4", "note": "o4 Mini High"},
            {"id": "openai/o1", "role": "reasoning", "gen": "o1", "note": "o1"},
            {"id": "openai/o1-pro", "role": "reasoning", "gen": "o1", "note": "o1 Pro"},
        ],
    },
    "anthropic": {
        "vendor": "Anthropic",
        "auto_prefixes": ["anthropic/claude-"],
        "ladder": [
            {"id": "anthropic/claude-opus-5", "role": "flagship", "gen": "opus-5", "note": "Opus 5"},
            {"id": "anthropic/claude-opus-5-fast", "role": "flagship", "gen": "opus-5", "note": "Opus 5 Fast"},
            {"id": "anthropic/claude-fable-5", "role": "flagship", "gen": "fable-5", "note": "Fable 5"},
            {"id": "anthropic/claude-opus-4.8", "role": "flagship", "gen": "opus-4.8", "note": "Opus 4.8"},
            {"id": "anthropic/claude-opus-4.8-fast", "role": "flagship", "gen": "opus-4.8", "note": "Opus 4.8 Fast"},
            {"id": "anthropic/claude-opus-4.7", "role": "flagship", "gen": "opus-4.7", "note": "Opus 4.7"},
            {"id": "anthropic/claude-opus-4.7-fast", "role": "flagship", "gen": "opus-4.7", "note": "Opus 4.7 Fast"},
            {"id": "anthropic/claude-opus-4.6", "role": "flagship", "gen": "opus-4.6", "note": "Opus 4.6"},
            {"id": "anthropic/claude-opus-4.5", "role": "previous", "gen": "opus-4.5", "note": "Opus 4.5"},
            {"id": "anthropic/claude-opus-4.1", "role": "previous", "gen": "opus-4.1", "note": "Opus 4.1"},
            {"id": "anthropic/claude-opus-4", "role": "previous", "gen": "opus-4", "note": "Opus 4"},
            {"id": "anthropic/claude-sonnet-5", "role": "mid", "gen": "sonnet-5", "note": "Sonnet 5"},
            {"id": "anthropic/claude-sonnet-4.6", "role": "mid", "gen": "sonnet-4.6", "note": "Sonnet 4.6"},
            {"id": "anthropic/claude-sonnet-4.5", "role": "previous", "gen": "sonnet-4.5", "note": "Sonnet 4.5"},
            {"id": "anthropic/claude-sonnet-4", "role": "previous", "gen": "sonnet-4", "note": "Sonnet 4"},
            {"id": "anthropic/claude-haiku-4.5", "role": "lite", "gen": "haiku-4.5", "note": "Haiku 4.5"},
            {"id": "anthropic/claude-3-haiku", "role": "lite", "gen": "haiku-3", "note": "Claude 3 Haiku"},
        ],
    },
    "google": {
        "vendor": "Google",
        "auto_prefixes": ["google/gemini-", "google/gemma-4"],
        "ladder": [
            {"id": "google/gemini-3.1-pro-preview", "role": "flagship", "gen": "3.1", "note": "3.1 Pro"},
            {"id": "google/gemini-3.1-pro-preview-customtools", "role": "flagship", "gen": "3.1", "note": "3.1 Pro CustomTools"},
            {"id": "google/gemini-2.5-pro", "role": "flagship", "gen": "2.5", "note": "2.5 Pro"},
            {"id": "google/gemini-3.6-flash", "role": "mid", "gen": "3.6", "note": "3.6 Flash 最新"},
            {"id": "google/gemini-3.5-flash", "role": "mid", "gen": "3.5", "note": "3.5 Flash"},
            {"id": "google/gemini-3-flash-preview", "role": "mid", "gen": "3.0", "note": "3 Flash Preview"},
            {"id": "google/gemini-2.5-flash", "role": "mid", "gen": "2.5", "note": "2.5 Flash"},
            {"id": "google/gemini-3.5-flash-lite", "role": "lite", "gen": "3.5", "note": "3.5 Lite"},
            {"id": "google/gemini-3.1-flash-lite", "role": "lite", "gen": "3.1", "note": "3.1 Lite"},
            {"id": "google/gemini-2.5-flash-lite", "role": "lite", "gen": "2.5", "note": "2.5 Lite"},
            {"id": "google/gemma-4-31b-it", "role": "mid", "gen": "gemma-4", "note": "Gemma 4 31B"},
            {"id": "google/gemma-4-26b-a4b-it", "role": "lite", "gen": "gemma-4", "note": "Gemma 4 26B"},
        ],
    },
    "deepseek": {
        "vendor": "DeepSeek",
        "auto_prefixes": ["deepseek/"],
        "ladder": [
            {"id": "deepseek/deepseek-v4-pro", "role": "flagship", "gen": "v4", "note": "V4 Pro"},
            {"id": "deepseek/deepseek-v4-flash", "role": "lite", "gen": "v4", "note": "V4 Flash"},
            {"id": "deepseek/deepseek-v3.2", "role": "mid", "gen": "v3.2", "note": "V3.2"},
            {"id": "deepseek/deepseek-v3.2-exp", "role": "mid", "gen": "v3.2", "note": "V3.2 Exp"},
            {"id": "deepseek/deepseek-v3.1-terminus", "role": "previous", "gen": "v3.1", "note": "V3.1 Terminus"},
            {"id": "deepseek/deepseek-chat-v3.1", "role": "previous", "gen": "v3.1", "note": "V3.1"},
            {"id": "deepseek/deepseek-chat", "role": "previous", "gen": "v3", "note": "deepseek-chat"},
            {"id": "deepseek/deepseek-r1", "role": "reasoning", "gen": "r1", "note": "R1"},
            {"id": "deepseek/deepseek-r1-0528", "role": "reasoning", "gen": "r1", "note": "R1-0528"},
        ],
    },
    "qwen": {
        "vendor": "Alibaba Qwen",
        "auto_prefixes": ["qwen/qwen3", "qwen/qwen-plus", "qwen/qwen-max"],
        "ladder": [
            {"id": "qwen/qwen3.7-max", "role": "flagship", "gen": "3.7", "note": "3.7 Max"},
            {"id": "qwen/qwen3.7-plus", "role": "mid", "gen": "3.7", "note": "3.7 Plus"},
            {"id": "qwen/qwen3.6-max-preview", "role": "flagship", "gen": "3.6", "note": "3.6 Max Preview"},
            {"id": "qwen/qwen3.6-plus", "role": "mid", "gen": "3.6", "note": "3.6 Plus"},
            {"id": "qwen/qwen3.6-flash", "role": "lite", "gen": "3.6", "note": "3.6 Flash"},
            {"id": "qwen/qwen3.6-27b", "role": "lite", "gen": "3.6-open", "note": "3.6 27B"},
            {"id": "qwen/qwen3.5-plus-20260420", "role": "previous", "gen": "3.5", "note": "3.5 Plus"},
            {"id": "qwen/qwen3.5-397b-a17b", "role": "mid", "gen": "3.5-open", "note": "397B MoE"},
            {"id": "qwen/qwen3.5-122b-a10b", "role": "mid", "gen": "3.5-open", "note": "122B"},
            {"id": "qwen/qwen3.5-27b", "role": "lite", "gen": "3.5-open", "note": "27B"},
            {"id": "qwen/qwen3.5-flash-02-23", "role": "lite", "gen": "3.5", "note": "3.5 Flash"},
            {"id": "qwen/qwen3-max", "role": "previous", "gen": "3-max", "note": "Qwen3 Max"},
            {"id": "qwen/qwen3-max-thinking", "role": "reasoning", "gen": "3-max", "note": "Max Thinking"},
            {"id": "qwen/qwen-plus", "role": "mid", "gen": "plus", "note": "Qwen-Plus"},
        ],
    },
    "meta-llama": {
        "vendor": "Meta",
        "auto_prefixes": ["meta-llama/llama-4", "meta-llama/llama-3"],
        "ladder": [
            {"id": "meta-llama/llama-4-maverick", "role": "flagship", "gen": "4", "note": "Maverick"},
            {"id": "meta-llama/llama-4-scout", "role": "mid", "gen": "4", "note": "Scout"},
            {"id": "meta-llama/llama-3.3-70b-instruct", "role": "previous", "gen": "3.3", "note": "3.3 70B"},
            {"id": "meta-llama/llama-3.1-70b-instruct", "role": "previous", "gen": "3.1", "note": "3.1 70B"},
            {"id": "meta-llama/llama-3.1-8b-instruct", "role": "lite", "gen": "3.1", "note": "3.1 8B"},
            {"id": "meta-llama/llama-3.2-3b-instruct", "role": "lite", "gen": "3.2", "note": "3.2 3B"},
        ],
    },
    "mistralai": {
        "vendor": "Mistral",
        "auto_prefixes": ["mistralai/mistral-", "mistralai/ministral-", "mistralai/devstral-"],
        "ladder": [
            {"id": "mistralai/mistral-large-2512", "role": "flagship", "gen": "large-3", "note": "Large 2512"},
            {"id": "mistralai/mistral-large", "role": "previous", "gen": "large", "note": "Large 旧"},
            {"id": "mistralai/mistral-medium-3.1", "role": "mid", "gen": "medium-3", "note": "Medium 3.1"},
            {"id": "mistralai/mistral-medium-3-5", "role": "mid", "gen": "medium-3.5", "note": "Medium 3.5"},
            {"id": "mistralai/mistral-medium-3", "role": "previous", "gen": "medium-3", "note": "Medium 3"},
            {"id": "mistralai/mistral-small-2603", "role": "lite", "gen": "small-4", "note": "Small 2603"},
            {"id": "mistralai/mistral-small-3.2-24b-instruct", "role": "lite", "gen": "small-3.2", "note": "Small 3.2"},
            {"id": "mistralai/ministral-14b-2512", "role": "lite", "gen": "ministral-3", "note": "Ministral 14B"},
            {"id": "mistralai/devstral-2512", "role": "mid", "gen": "devstral", "note": "Devstral"},
        ],
    },
    "x-ai": {
        "vendor": "xAI",
        "auto_prefixes": ["x-ai/grok-"],
        "ladder": [
            {"id": "x-ai/grok-4.5", "role": "flagship", "gen": "4.5", "note": "Grok 4.5"},
            {"id": "x-ai/grok-4.3", "role": "mid", "gen": "4.3", "note": "Grok 4.3"},
            {"id": "x-ai/grok-4.20", "role": "previous", "gen": "4.20", "note": "Grok 4.20"},
            {"id": "x-ai/grok-4.20-multi-agent", "role": "mid", "gen": "4.20", "note": "4.20 Multi-Agent"},
            {"id": "x-ai/grok-build-0.1", "role": "lite", "gen": "build", "note": "Grok Build"},
        ],
    },
    "moonshotai": {
        "vendor": "Moonshot (Kimi)",
        "auto_prefixes": ["moonshotai/kimi-"],
        "ladder": [
            {"id": "moonshotai/kimi-k3", "role": "flagship", "gen": "k3", "note": "K3"},
            {"id": "moonshotai/kimi-k2.7-code", "role": "mid", "gen": "k2.7", "note": "K2.7 Code"},
            {"id": "moonshotai/kimi-k2.6", "role": "mid", "gen": "k2.6", "note": "K2.6"},
            {"id": "moonshotai/kimi-k2.5", "role": "previous", "gen": "k2.5", "note": "K2.5"},
            {"id": "moonshotai/kimi-k2-0905", "role": "previous", "gen": "k2", "note": "K2 0905"},
            {"id": "moonshotai/kimi-k2", "role": "previous", "gen": "k2", "note": "K2"},
            {"id": "moonshotai/kimi-k2-thinking", "role": "reasoning", "gen": "k2", "note": "K2 Thinking"},
        ],
    },
    "z-ai": {
        "vendor": "Zhipu / Z.ai (GLM)",
        "auto_prefixes": ["z-ai/glm-"],
        "ladder": [
            {"id": "z-ai/glm-5.2", "role": "flagship", "gen": "5.2", "note": "GLM 5.2"},
            {"id": "z-ai/glm-5.1", "role": "mid", "gen": "5.1", "note": "GLM 5.1"},
            {"id": "z-ai/glm-5", "role": "previous", "gen": "5.0", "note": "GLM 5"},
            {"id": "z-ai/glm-5-turbo", "role": "mid", "gen": "5.0", "note": "GLM 5 Turbo"},
            {"id": "z-ai/glm-4.7", "role": "previous", "gen": "4.7", "note": "GLM 4.7"},
            {"id": "z-ai/glm-4.7-flash", "role": "lite", "gen": "4.7", "note": "4.7 Flash"},
            {"id": "z-ai/glm-4.6", "role": "previous", "gen": "4.6", "note": "GLM 4.6"},
            {"id": "z-ai/glm-4.5", "role": "previous", "gen": "4.5", "note": "GLM 4.5"},
            {"id": "z-ai/glm-4.5-air", "role": "lite", "gen": "4.5", "note": "4.5 Air"},
        ],
    },
    "amazon": {
        "vendor": "Amazon",
        "auto_prefixes": ["amazon/nova-"],
        "ladder": [
            {"id": "amazon/nova-premier-v1", "role": "flagship", "gen": "nova-1", "note": "Premier"},
            {"id": "amazon/nova-pro-v1", "role": "mid", "gen": "nova-1", "note": "Pro"},
            {"id": "amazon/nova-2-lite-v1", "role": "lite", "gen": "nova-2", "note": "2 Lite"},
            {"id": "amazon/nova-lite-v1", "role": "lite", "gen": "nova-1", "note": "Lite"},
            {"id": "amazon/nova-micro-v1", "role": "lite", "gen": "nova-1", "note": "Micro"},
        ],
    },
    "minimax": {
        "vendor": "MiniMax",
        "auto_prefixes": ["minimax/minimax-"],
        "ladder": [
            {"id": "minimax/minimax-m3", "role": "flagship", "gen": "m3", "note": "M3"},
            {"id": "minimax/minimax-m2.7", "role": "mid", "gen": "m2.7", "note": "M2.7"},
            {"id": "minimax/minimax-m2.5", "role": "previous", "gen": "m2.5", "note": "M2.5"},
            {"id": "minimax/minimax-m2.1", "role": "previous", "gen": "m2.1", "note": "M2.1"},
            {"id": "minimax/minimax-m2", "role": "previous", "gen": "m2", "note": "M2"},
            {"id": "minimax/minimax-m1", "role": "previous", "gen": "m1", "note": "M1"},
        ],
    },
    "bytedance-seed": {
        "vendor": "ByteDance Seed",
        "auto_prefixes": ["bytedance-seed/"],
        "ladder": [
            {"id": "bytedance-seed/seed-2.0-lite", "role": "mid", "gen": "2.0", "note": "2.0 Lite"},
            {"id": "bytedance-seed/seed-2.0-mini", "role": "lite", "gen": "2.0", "note": "2.0 Mini"},
            {"id": "bytedance-seed/seed-1.6", "role": "previous", "gen": "1.6", "note": "1.6"},
            {"id": "bytedance-seed/seed-1.6-flash", "role": "lite", "gen": "1.6", "note": "1.6 Flash"},
        ],
    },
    "cohere": {
        "vendor": "Cohere",
        "auto_prefixes": ["cohere/command-"],
        "ladder": [
            {"id": "cohere/command-a", "role": "flagship", "gen": "command-a", "note": "Command A"},
            {"id": "cohere/command-r-plus-08-2024", "role": "mid", "gen": "r+", "note": "R+"},
            {"id": "cohere/command-r-08-2024", "role": "lite", "gen": "r", "note": "R"},
            {"id": "cohere/command-r7b-12-2024", "role": "lite", "gen": "r7b", "note": "R7B"},
        ],
    },
    "nvidia": {
        "vendor": "NVIDIA",
        "auto_prefixes": ["nvidia/nemotron-"],
        "ladder": [
            {"id": "nvidia/nemotron-3-ultra-550b-a55b", "role": "flagship", "gen": "3", "note": "Ultra"},
            {"id": "nvidia/nemotron-3-super-120b-a12b", "role": "mid", "gen": "3", "note": "Super"},
            {"id": "nvidia/nemotron-3-nano-30b-a3b", "role": "lite", "gen": "3", "note": "Nano"},
        ],
    },
    "tencent": {
        "vendor": "Tencent",
        "auto_prefixes": ["tencent/"],
        "ladder": [
            {"id": "tencent/hy3", "role": "flagship", "gen": "hy3", "note": "Hy3"},
            {"id": "tencent/hy3-preview", "role": "mid", "gen": "hy3", "note": "Hy3 preview"},
            {"id": "tencent/hunyuan-a13b-instruct", "role": "lite", "gen": "hunyuan", "note": "A13B"},
        ],
    },
    "xiaomi": {
        "vendor": "Xiaomi",
        "auto_prefixes": ["xiaomi/mimo-"],
        "ladder": [
            {"id": "xiaomi/mimo-v2.5-pro", "role": "flagship", "gen": "2.5", "note": "Pro"},
            {"id": "xiaomi/mimo-v2.5", "role": "mid", "gen": "2.5", "note": "标准"},
        ],
    },
}

DEPTH_VENDORS_P0 = [
    "openai", "anthropic", "google", "deepseek", "qwen",
    "meta-llama", "mistralai", "x-ai", "moonshotai", "z-ai",
]
DEPTH_VENDORS_P1 = [
    "amazon", "minimax", "bytedance-seed", "cohere", "nvidia", "tencent", "xiaomi",
]

BATCH_WIDTH_SMOKE = [
    "openai/gpt-5.6-sol",
    "anthropic/claude-sonnet-5",
    "google/gemini-3.6-flash",
    "deepseek/deepseek-v4-pro",
    "qwen/qwen3.7-plus",
    "meta-llama/llama-4-maverick",
    "mistralai/mistral-large-2512",
    "x-ai/grok-4.5",
    "moonshotai/kimi-k3",
    "z-ai/glm-5.2",
    "amazon/nova-pro-v1",
    "minimax/minimax-m3",
    "bytedance-seed/seed-2.0-lite",
    "cohere/command-a",
    "nvidia/nemotron-3-super-120b-a12b",
    "tencent/hy3",
    "xiaomi/mimo-v2.5-pro",
]

# 正式选型主跑：同代只跑基线（不含 -pro / -fast；入围后再补）
# 例外：产品线本名含 Pro/Flash 的（如 gemini-*-pro、deepseek-v4-pro）仍保留——那是档位名不是同款变体。
SELECT_CORE = [
    # OpenAI — 5.6 三线基线 + 5.5/5.4 + 关键推理（无 *-pro）
    "openai/gpt-5.6-sol",
    "openai/gpt-5.6-terra",
    "openai/gpt-5.6-luna",
    "openai/gpt-5.5",
    "openai/gpt-5.4",
    "openai/gpt-5.4-mini",
    "openai/gpt-5.4-nano",
    "openai/o3",
    "openai/o3-mini",
    "openai/o4-mini",
    # Anthropic — 无 *-fast
    "anthropic/claude-opus-5",
    "anthropic/claude-fable-5",
    "anthropic/claude-opus-4.8",
    "anthropic/claude-opus-4.6",
    "anthropic/claude-sonnet-5",
    "anthropic/claude-sonnet-4.6",
    "anthropic/claude-sonnet-4.5",
    "anthropic/claude-haiku-4.5",
    # Google（pro/flash/lite = 产品档位，不是同款 Pro 变体）
    "google/gemini-3.1-pro-preview",
    "google/gemini-3.6-flash",
    "google/gemini-3.5-flash",
    "google/gemini-3.5-flash-lite",
    "google/gemini-2.5-pro",
    "google/gemini-2.5-flash",
    "google/gemini-2.5-flash-lite",
    # DeepSeek
    "deepseek/deepseek-v4-pro",
    "deepseek/deepseek-v4-flash",
    "deepseek/deepseek-v3.2",
    "deepseek/deepseek-r1",
    "deepseek/deepseek-r1-0528",
    # Qwen
    "qwen/qwen3.7-max",
    "qwen/qwen3.7-plus",
    "qwen/qwen3.6-plus",
    "qwen/qwen3.6-flash",
    "qwen/qwen3.5-397b-a17b",
    # Meta / Mistral / xAI / Kimi / GLM
    "meta-llama/llama-4-maverick",
    "meta-llama/llama-4-scout",
    "meta-llama/llama-3.3-70b-instruct",
    "mistralai/mistral-large-2512",
    "mistralai/mistral-medium-3.1",
    "mistralai/mistral-small-2603",
    "x-ai/grok-4.5",
    "x-ai/grok-4.3",
    "x-ai/grok-4.20",
    "moonshotai/kimi-k3",
    "moonshotai/kimi-k2.6",
    "moonshotai/kimi-k2-thinking",
    "z-ai/glm-5.2",
    "z-ai/glm-5.1",
    "z-ai/glm-5",
    "z-ai/glm-4.7-flash",
]

# 扩展：同代 Pro/Fast 变体（入围后补跑）+ 上一代 + P1 厂商
SELECT_EXTENDED = [
    # —— 同代 Pro / Fast（主跑入围后再跑）——
    "openai/gpt-5.6-sol-pro",
    "openai/gpt-5.6-terra-pro",
    "openai/gpt-5.6-luna-pro",
    "openai/gpt-5.5-pro",
    "openai/gpt-5.4-pro",
    "openai/o3-pro",
    "openai/o3-mini-high",
    "openai/o4-mini-high",
    "anthropic/claude-opus-5-fast",
    "anthropic/claude-opus-4.8-fast",
    "anthropic/claude-opus-4.7-fast",
    # —— 更旧代际对照 ——
    "openai/gpt-5.2",
    "openai/gpt-5.1",
    "openai/gpt-5",
    "openai/gpt-4o",
    "anthropic/claude-opus-4.7",
    "anthropic/claude-opus-4.5",
    "anthropic/claude-sonnet-4",
    "google/gemini-3-flash-preview",
    "google/gemini-3.1-flash-lite",
    "google/gemma-4-31b-it",
    "deepseek/deepseek-chat-v3.1",
    "qwen/qwen3.6-max-preview",
    "qwen/qwen3-max-thinking",
    "meta-llama/llama-3.1-8b-instruct",
    "mistralai/mistral-medium-3",
    "mistralai/devstral-2512",
    "moonshotai/kimi-k2.5",
    "z-ai/glm-4.7",
    # —— P1 厂商 ——
    "amazon/nova-premier-v1",
    "amazon/nova-pro-v1",
    "amazon/nova-2-lite-v1",
    "minimax/minimax-m3",
    "minimax/minimax-m2.7",
    "minimax/minimax-m2.5",
    "bytedance-seed/seed-2.0-lite",
    "bytedance-seed/seed-2.0-mini",
    "bytedance-seed/seed-1.6",
    "cohere/command-a",
    "cohere/command-r-plus-08-2024",
    "nvidia/nemotron-3-ultra-550b-a55b",
    "nvidia/nemotron-3-super-120b-a12b",
    "nvidia/nemotron-3-nano-30b-a3b",
    "tencent/hy3",
    "tencent/hy3-preview",
    "xiaomi/mimo-v2.5-pro",
    "xiaomi/mimo-v2.5",
]

# 非 OpenRouter，但仍纳入正式选型主跑（自有端点；刷新时不经 filter_existing）
EXTERNAL_SELECT_CORE = [
    {
        "id": "paperguru/guru-pro-1.2",
        "vendor": "PaperGuru",
        "name": "PaperGuru Guru Pro 1.2",
        "note": "own endpoint via PAPERGURU_*; 主跑·基线",
        "batch": "core",
        "select": True,
        "auto": False,
        "price_prompt_per_m": 0.0,
        "price_completion_per_m": 0.0,
    },
]


def fetch_models() -> dict[str, dict]:
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/models",
        headers={"User-Agent": "OffSecGuard/refresh-catalog"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode())
    return {m["id"]: m for m in payload.get("data", [])}


def _excluded(mid: str) -> bool:
    low = mid.lower()
    return any(x in low for x in _EXCLUDE_SUBSTR) or mid.startswith("~")


def infer_role(mid: str) -> str:
    low = mid.lower()
    if any(k in low for k in ("thinking", "/o1", "/o3", "/o4", "deepseek-r1", "reasoner")):
        return "reasoning"
    if any(k in low for k in ("-pro", "opus", "ultra", "max", "premier", "maverick")):
        return "flagship"
    if any(
        k in low
        for k in (
            "mini", "nano", "lite", "flash", "air", "haiku", "small", "micro",
            "scout", "luna",
        )
    ):
        return "lite"
    if any(k in low for k in ("sonnet", "plus", "medium", "terra")):
        return "mid"
    return "mid"


def infer_gen(mid: str) -> str:
    name = mid.split("/", 1)[-1]
    m = re.search(
        r"(gpt-5\.6-\w+|gpt-5\.\d+|gpt-5|o\d+|claude-(?:opus|sonnet|haiku|fable)-[\w.]+|"
        r"gemini-[\d.]+|gemma-[\d]+|deepseek-v[\d.]+|deepseek-r1|qwen3\.[\d]+|"
        r"llama-[\d.]+|mistral-[\w.-]+|grok-[\d.]+|kimi-[\w.]+|glm-[\d.]+|"
        r"nova|minimax-m[\d.]+|seed-[\d.]+|nemotron-[\d]+|hy3|mimo-[\w.]+)",
        name,
        re.I,
    )
    return m.group(1) if m else name


def enrich_row(entry: dict, models: dict[str, dict]) -> dict:
    mid = entry["id"]
    m = models[mid]
    p = m.get("pricing") or {}
    pin = float(p.get("prompt") or 0) * 1e6
    pout = float(p.get("completion") or 0) * 1e6
    return {
        **entry,
        "name": m.get("name"),
        "context_length": m.get("context_length"),
        "price_prompt_per_m": round(pin, 4),
        "price_completion_per_m": round(pout, 4),
    }


def enrich_id(mid: str, models: dict[str, dict], **extra) -> dict:
    base = {"id": mid, **extra}
    return enrich_row(base, models)


def auto_discover(author: str, block: dict, models: dict[str, dict], known: set[str]) -> list[dict]:
    prefixes = block.get("auto_prefixes") or [f"{author}/"]
    found: list[dict] = []
    for mid in models:
        if mid in known or _excluded(mid):
            continue
        if not any(mid.startswith(p) for p in prefixes):
            continue
        # 跳过 codex/chat 冗余变体（可选保留 chat；codex 对护栏主评次要）
        if "-codex" in mid or mid.endswith("-chat"):
            continue
        if "preview-0" in mid and "gemini-2.5-pro-preview" in mid:
            continue
        found.append({
            "id": mid,
            "role": infer_role(mid),
            "gen": infer_gen(mid),
            "note": "auto-discovered from OpenRouter",
            "auto": True,
        })
    found.sort(key=lambda x: x["id"])
    return found


def build_ladders(models: dict[str, dict], missing: list[str]) -> tuple[dict, list[str]]:
    """手工 ladder 进 vendors；自动发现只进 discovered_extras，不污染选型主表。"""
    out: dict = {}
    auto_added: list[str] = []
    core_set, ext_set = set(SELECT_CORE), set(SELECT_EXTENDED)
    for author, block in VENDOR_LADDERS.items():
        rows: list[dict] = []
        known: set[str] = set()
        for entry in block["ladder"]:
            mid = entry["id"]
            known.add(mid)
            if mid in models:
                if mid in core_set:
                    batch = "core"
                elif mid in ext_set:
                    batch = "extended"
                else:
                    batch = "archive"
                row = {
                    **entry,
                    "auto": False,
                    "select": batch in ("core", "extended"),
                    "batch": batch,
                }
                rows.append(enrich_row(row, models))
            else:
                missing.append(mid)
        for entry in auto_discover(author, block, models, known):
            auto_added.append(entry["id"])
        rows.sort(key=lambda r: (r.get("gen") or "", r.get("role") or "", r["id"]))
        if rows:
            out[author] = {"vendor": block["vendor"], "ladder": rows}
    return out, sorted(set(auto_added))


def filter_existing(ids: list[str], models: dict[str, dict], missing: list[str]) -> list[str]:
    keep: list[str] = []
    for mid in ids:
        if mid in models:
            keep.append(mid)
        else:
            missing.append(mid)
    return keep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    models = fetch_models()
    missing: list[str] = []
    ladders, auto_added = build_ladders(models, missing)

    smoke = filter_existing(list(BATCH_WIDTH_SMOKE), models, missing)
    select_core = filter_existing(list(SELECT_CORE), models, missing)
    select_ext = filter_existing(list(SELECT_EXTENDED), models, missing)
    external_core = [dict(x) for x in EXTERNAL_SELECT_CORE]
    core_enriched = [enrich_id(i, models) for i in select_core] + external_core
    _seen: set[str] = set()
    all_enriched: list[dict] = []
    for row in (
        [enrich_id(i, models) for i in select_core]
        + external_core
        + [enrich_id(i, models) for i in select_ext]
    ):
        mid = row["id"]
        if mid in _seen:
            continue
        _seen.add(mid)
        all_enriched.append(row)
    select_all_ids = [r["id"] for r in all_enriched]
    missing_u = sorted(set(missing))

    print(f"OpenRouter models: {len(models)}")
    print(f"Vendors: {len(ladders)}")
    print(
        f"Smoke: {len(smoke)} | Select core: {len(core_enriched)} "
        f"(OR {len(select_core)} + external {len(external_core)}) | "
        f"Extended: {len(select_ext)} | Select all: {len(select_all_ids)}"
    )
    print(f"Discovered extras (not in select): {len(auto_added)}")
    if missing_u:
        print("MISSING:")
        for mid in missing_u:
            print(f"  - {mid}")

    if args.check_only:
        return 0 if not missing_u else 1

    vendors_out = {}
    for author, block in ladders.items():
        # 人读主表：只放 select/extended；archive 仍保留在 ladder_archive
        select_rows = [r for r in block["ladder"] if r.get("select")]
        archive_rows = [r for r in block["ladder"] if not r.get("select")]
        by_role: dict[str, list[str]] = {}
        for row in select_rows:
            by_role.setdefault(row["role"], []).append(row["id"])
        vendors_out[author] = {
            "vendor": block["vendor"],
            "families_by_role": by_role,
            "ladder": select_rows,
            "ladder_archive": archive_rows,
        }

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "https://openrouter.ai/api/v1/models",
        "openrouter_total_models": len(models),
        "notes": [
            "OpenRouter 无裸 openai/gpt-5.6；最新代为 gpt-5.6-{luna,sol,terra}[+pro]",
            "batch_select_core = 正式选型主跑（含 paperguru/guru-pro-1.2）；batch_select_extended = 扩展代际/P1厂",
            "discovered_extras = 自动发现，默认不进主跑",
            "跨厂比同 role；同厂比 gen 梯队",
        ],
        "vendors": vendors_out,
        "batch_width_smoke": [enrich_id(i, models) for i in smoke],
        "batch_select_core": core_enriched,
        "batch_select_extended": [enrich_id(i, models) for i in select_ext],
        "batch_select_all": all_enriched,
        # 兼容旧字段
        "batch_depth_p0": list(core_enriched),
        "batch_depth_p1": [enrich_id(i, models) for i in select_ext],
        "batch_depth_all": list(all_enriched),
        "batch_p0_core": list(core_enriched),
        "batch_p1_expand": [enrich_id(i, models) for i in select_ext],
        "discovered_extras": [enrich_id(i, models, auto=True, select=False, batch="extra") for i in auto_added],
        "external_non_openrouter": list(EXTERNAL_SELECT_CORE),
        "missing_at_refresh": missing_u,
    }

    OUT_YAML.parent.mkdir(parents=True, exist_ok=True)
    OUT_YAML.write_text(yaml.safe_dump(out, allow_unicode=True, sort_keys=False), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_YAML.relative_to(ROOT)}")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")

    # 渲染人读清单
    render = ROOT / "scripts" / "render_openrouter_catalog_md.py"
    if render.exists():
        import subprocess

        subprocess.run([sys.executable, str(render)], check=False)
    return 0 if not missing_u else 1


if __name__ == "__main__":
    sys.exit(main())
