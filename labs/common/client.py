"""Shared client layer for Ground-Up AI Labs.

Two clients with the same interface:

- ``StandInClient`` — the default. A deterministic, offline stand-in
  for a hosted LLM. It does not generate language; it returns a
  templated completion whose *length* depends on the prompt, counts
  tokens with the estimator below, and reports a modelled latency
  drawn from a fixed distribution seeded per call. The labs are about
  accounting and failure modes, and for those the stand-in is the
  honest tool: every number it produces is reproducible on any
  machine, and its latency figures are labelled as modelled, never
  measured from a network.

- ``HTTPClient`` — an optional swap for any OpenAI-compatible chat
  endpoint. Configure with environment variables GUAL_BASE_URL,
  GUAL_API_KEY and GUAL_MODEL. With it, the same lab code measures
  real latency and real usage. Nothing in the labs requires it.

Token estimation: ``estimate_tokens`` splits text into word runs and
single punctuation marks. That tracks real tokenisers closely enough
for cost accounting (within roughly 10-20% on English prose) and —
more importantly for a lab — it is *the same* estimator on every run,
so comparisons inside a lab are exact even if the absolute counts are
approximate.
"""

from __future__ import annotations

import json
import os
import random
import re
import time
import urllib.request
from dataclasses import dataclass

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+|[^\sA-Za-z0-9]")


def estimate_tokens(text: str) -> int:
    """Approximate token count: word runs + individual punctuation."""
    return len(_TOKEN_RE.findall(text))


@dataclass
class Response:
    text: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    source: str  # "stand-in (modelled latency)" or "http (measured)"


class StandInClient:
    """Deterministic offline stand-in. See module docstring."""

    BASE_LATENCY_MS = 160.0
    MS_PER_COMPLETION_TOKEN = 3.2

    def __init__(self, seed: int = 1234) -> None:
        self._rng = random.Random(seed)
        self._calls = 0

    def complete(self, prompt: str, system: str = "") -> Response:
        self._calls += 1
        full_prompt = f"{system}\n{prompt}" if system else prompt
        prompt_tokens = estimate_tokens(full_prompt)
        # Completion length: a stable function of the prompt, so the
        # same prompt always costs the same on every machine.
        digest = sum((i + 1) * ord(c) for i, c in enumerate(prompt))
        completion_tokens = 24 + digest % 160
        text = self._render(prompt, completion_tokens)
        jitter = self._rng.uniform(0.85, 1.3)
        latency = (self.BASE_LATENCY_MS
                   + self.MS_PER_COMPLETION_TOKEN * completion_tokens) * jitter
        return Response(
            text=text,
            prompt_tokens=prompt_tokens,
            completion_tokens=estimate_tokens(text),
            latency_ms=round(latency, 1),
            source="stand-in (modelled latency)",
        )

    @staticmethod
    def _render(prompt: str, target_tokens: int) -> str:
        opener = "Here is a direct answer to the request. "
        body = ("The key point is to separate what the system must do "
                "from how it happens to be phrased, handle the common "
                "case first, and measure the result rather than "
                "assuming it worked. ")
        text = opener
        while estimate_tokens(text) < target_tokens:
            text += body
        return text.strip()


class HTTPClient:
    """OpenAI-compatible chat endpoint, configured by environment."""

    def __init__(self) -> None:
        self.base = os.environ["GUAL_BASE_URL"].rstrip("/")
        self.key = os.environ.get("GUAL_API_KEY", "")
        self.model = os.environ["GUAL_MODEL"]

    def complete(self, prompt: str, system: str = "") -> Response:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = json.dumps(
            {"model": self.model, "messages": messages}).encode()
        req = urllib.request.Request(
            f"{self.base}/chat/completions", data=payload, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.key}",
            })
        start = time.perf_counter()
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        latency = (time.perf_counter() - start) * 1000.0
        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        full_prompt = f"{system}\n{prompt}" if system else prompt
        return Response(
            text=text,
            prompt_tokens=usage.get("prompt_tokens",
                                    estimate_tokens(full_prompt)),
            completion_tokens=usage.get("completion_tokens",
                                        estimate_tokens(text)),
            latency_ms=round(latency, 1),
            source="http (measured)",
        )


def default_client(seed: int = 1234):
    """HTTPClient when configured, otherwise the stand-in."""
    if os.environ.get("GUAL_BASE_URL") and os.environ.get("GUAL_MODEL"):
        return HTTPClient()
    return StandInClient(seed=seed)
