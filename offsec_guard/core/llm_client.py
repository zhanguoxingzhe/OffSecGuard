"""模型无关的 LLM 客户端 — 零框架依赖，纯 httpx."""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import httpx

from .models import ModelIdentity

_RETRYABLE = {408, 429, 500, 502, 503, 504}


@dataclass
class LLMResponse:
    """统一的大模型响应."""
    content: str
    finish_reason: str = ""
    model: str = ""
    latency_ms: float = 0.0
    raw_response: dict[str, Any] = field(default_factory=dict, repr=False)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)


class LLMClient(ABC):
    """LLM 客户端抽象基类."""

    def __init__(self, identity: ModelIdentity, timeout_s: float = 120.0):
        self.identity = identity
        self.timeout_s = timeout_s

    @abstractmethod
    async def chat(self, messages, *, temperature=0.0, max_tokens=4096, tools=None) -> LLMResponse: ...
    @abstractmethod
    def chat_sync(self, messages, *, temperature=0.0, max_tokens=4096, tools=None) -> LLMResponse: ...


class OpenAICompatibleClient(LLMClient):
    """OpenAI API 兼容客户端 — 覆盖 OpenAI / OpenRouter / Ollama / vLLM 等."""

    def __init__(self, identity, *, base_url="https://api.openai.com/v1", api_key="",
                 timeout_s=120.0, extra_headers=None, max_retries: int = 2):
        super().__init__(identity, timeout_s)
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.extra_headers = extra_headers or {}
        self.max_retries = max(0, int(max_retries))

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        h.update(self.extra_headers)
        return h

    def _parse(self, raw: dict, elapsed_ms: float) -> LLMResponse:
        choice = raw.get("choices", [{}])[0]
        msg = choice.get("message", {})
        content = msg.get("content") or ""
        if isinstance(content, list):
            content = "".join(
                b.get("text", "") if isinstance(b, dict) else str(b) for b in content
            )
        return LLMResponse(
            content=str(content).strip(),
            finish_reason=choice.get("finish_reason", ""),
            model=raw.get("model", self.identity.model_id),
            latency_ms=round(elapsed_ms, 2),
            raw_response=raw,
            tool_calls=msg.get("tool_calls") or [],
        )

    def _payload(self, messages, temperature, max_tokens, tools):
        p: dict[str, Any] = {
            "model": self.identity.model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            p["tools"] = tools
        return p

    def _should_retry(self, exc: BaseException) -> bool:
        if isinstance(exc, httpx.TimeoutException):
            return True
        if isinstance(exc, httpx.TransportError):
            return True
        if isinstance(exc, httpx.HTTPStatusError):
            return exc.response.status_code in _RETRYABLE
        return False

    def _retry_delay_s(self, exc: BaseException, attempt: int) -> float:
        """429 用更长指数退避，并尊重 Retry-After。"""
        if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 429:
            ra = exc.response.headers.get("Retry-After") or exc.response.headers.get(
                "retry-after"
            )
            if ra:
                try:
                    return min(120.0, max(1.0, float(ra)))
                except ValueError:
                    pass
            # 2, 4, 8, 16, 32... 封顶 60s
            return min(60.0, float(2 ** (attempt + 1)))
        return min(20.0, 1.5 * (attempt + 1))

    def _retry_budget(self, exc: BaseException) -> int:
        # 限流多给几次机会
        if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 429:
            return max(self.max_retries, 5)
        return self.max_retries

    async def chat(self, messages, *, temperature=0.0, max_tokens=4096, tools=None):
        started = time.monotonic()
        last_exc: BaseException | None = None
        attempt = 0
        budget = self.max_retries
        while True:
            try:
                async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                    resp = await client.post(
                        f"{self.base_url}/chat/completions",
                        json=self._payload(messages, temperature, max_tokens, tools),
                        headers=self._headers(),
                    )
                    resp.raise_for_status()
                return self._parse(resp.json(), (time.monotonic() - started) * 1000)
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                budget = max(budget, self._retry_budget(exc))
                if attempt >= budget or not self._should_retry(exc):
                    raise
                delay = self._retry_delay_s(exc, attempt)
                print(
                    f"  [llm-retry] attempt={attempt+1}/{budget} "
                    f"sleep={delay:.1f}s err={type(exc).__name__}: {exc}",
                    flush=True,
                )
                await asyncio.sleep(delay)
                attempt += 1
        assert last_exc is not None
        raise last_exc

    def chat_sync(self, messages, *, temperature=0.0, max_tokens=4096, tools=None):
        started = time.monotonic()
        last_exc: BaseException | None = None
        attempt = 0
        budget = self.max_retries
        while True:
            try:
                with httpx.Client(timeout=self.timeout_s) as client:
                    resp = client.post(
                        f"{self.base_url}/chat/completions",
                        json=self._payload(messages, temperature, max_tokens, tools),
                        headers=self._headers(),
                    )
                    resp.raise_for_status()
                return self._parse(resp.json(), (time.monotonic() - started) * 1000)
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                budget = max(budget, self._retry_budget(exc))
                if attempt >= budget or not self._should_retry(exc):
                    raise
                delay = self._retry_delay_s(exc, attempt)
                print(
                    f"  [llm-retry] attempt={attempt+1}/{budget} "
                    f"sleep={delay:.1f}s err={type(exc).__name__}: {exc}",
                    flush=True,
                )
                time.sleep(delay)
                attempt += 1
        assert last_exc is not None
        raise last_exc


def create_client(identity: ModelIdentity, *, base_url="", api_key="",
                  provider="openai", timeout_s=120.0,
                  extra_headers: dict[str, str] | None = None,
                  max_retries: int = 2) -> LLMClient:
    """工厂函数：根据 provider 创建客户端."""
    if provider == "openrouter":
        headers = {
            "HTTP-Referer": "https://github.com/scantist/offsec-guard",
            "X-Title": "OffSec Guard Evaluator",
        }
        if extra_headers:
            headers.update(extra_headers)
        return OpenAICompatibleClient(
            identity=identity, base_url="https://openrouter.ai/api/v1",
            api_key=api_key, timeout_s=timeout_s, extra_headers=headers,
            max_retries=max_retries,
        )
    if provider == "deepseek":
        return OpenAICompatibleClient(
            identity=identity,
            base_url=(base_url or "https://api.deepseek.com").rstrip("/"),
            api_key=api_key,
            timeout_s=timeout_s,
            extra_headers=extra_headers,
            max_retries=max_retries,
        )
    return OpenAICompatibleClient(
        identity=identity,
        base_url=base_url or "https://api.openai.com/v1",
        api_key=api_key, timeout_s=timeout_s, extra_headers=extra_headers,
        max_retries=max_retries,
    )
