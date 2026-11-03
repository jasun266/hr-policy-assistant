"""Model clients. `ClaudeLLM` calls the Claude API; `FakeLLM` is a scripted stand-in with the
same response shape, used for tests and for running the demo without an API key."""

import re
from dataclasses import dataclass, field
from itertools import count

import anthropic

from .config import EFFORT, MODEL


class ClaudeLLM:
    def __init__(self, client: anthropic.Anthropic | None = None, model: str = MODEL, effort: str = EFFORT):
        self.client = client or anthropic.Anthropic()
        self.model = model
        self.effort = effort

    def create(self, *, system: str, messages: list, tools: list):
        # Opus 5.5 thinks adaptively by default; effort is the depth knob.
        # The server-side fallback re-runs a policy-declined request on another model in the same call.
        return self.client.beta.messages.create(
            model=self.model,
            max_tokens=16000,
            system=system,
            messages=messages,
            tools=tools,
            output_config={"effort": self.effort},
            cache_control={"type": "ephemeral"},  # caches the growing conversation prefix turn to turn
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )


# ---- Fake model -------------------------------------------------------------------------

@dataclass
class _Block:
    type: str
    text: str = ""
    id: str = ""
    name: str = ""
    input: dict = field(default_factory=dict)


@dataclass
class _Response:
    content: list
    stop_reason: str
    stop_details: None = None


_ids = count(1)
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _text(content) -> str:
    return content if isinstance(content, str) else ""


class FakeLLM:
    """Deterministic keyword router. It exercises the same tool loop as the real model."""

    def __init__(self):
        self.calls = 0

    def create(self, *, system: str, messages: list, tools: list) -> _Response:
        self.calls += 1
        last = messages[-1]["content"]
        if isinstance(last, list) and last and isinstance(last[0], dict) and last[0].get("type") == "tool_result":
            return self._answer_from(last, messages)
        text = _text(last)
        if re.search(r"\bmy name\b|\bwho am i\b", text.lower()):
            name = re.search(r"helping (.+?) \(", system)
            return _Response([_Block("text", text=f"You're signed in as {name.group(1) if name else 'an Acme employee'}.")],
                             "end_turn")
        return self._route(text)

    def _tool(self, name: str, args: dict) -> _Response:
        return _Response([_Block("tool_use", id=f"toolu_fake_{next(_ids)}", name=name, input=args)], "tool_use")

    def _route(self, text: str) -> _Response:
        low = text.lower()
        dates = _DATE.findall(text)
        if len(dates) >= 1 and any(w in low for w in ("apply", "take", "book", "request")):
            kind = next((k for k in ("sick", "casual") if k in low), "annual")
            return self._tool("draft_leave_request", {"leave_type": kind, "start_date": dates[0],
                                                      "end_date": dates[-1], "reason": ""})
        if "balance" in low or "left" in low or "remaining" in low:
            return self._tool("get_leave_balance", {})
        if "my request" in low or "status" in low:
            return self._tool("list_my_leave_requests", {"status": "all"})
        return self._tool("search_policy", {"query": text})

    def _answer_from(self, results: list, messages: list) -> _Response:
        call = next(b for b in reversed(messages[-2]["content"]) if b.type == "tool_use")
        content = results[0]["content"]
        if results[0].get("is_error"):
            reply = f"I couldn't do that: {content.split(': ', 1)[-1]}"
        elif call.name == "search_policy" and content.startswith("["):
            source, body = content.split("\n", 1)
            reply = f"{body.split(chr(10))[0]} {source.replace('[', '(').replace(']', ')')}"
        elif call.name == "search_policy":  # nothing matched: the tool text is an instruction, not an answer
            reply = ("I couldn't find that in Acme's HR policies. For anything they don't cover, "
                     "please contact HR at hr@acme.example.")
        elif call.name == "draft_leave_request":
            reply = content.split(" It is NOT")[0] + " Please review and confirm it in the panel - it is not submitted yet."
        else:
            reply = content
        return _Response([_Block("text", text=reply)], "end_turn")
