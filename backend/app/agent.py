"""The agent loop, written by hand rather than with a framework so every step is visible:
call the model -> run the tools it asked for -> send the results back -> repeat until it
answers or the step limit is reached. History is append-only (thinking blocks included),
which keeps prompt caching and thinking-block replay valid."""

import logging
from dataclasses import dataclass, field

from .config import MAX_AGENT_STEPS
from .db import Employee
from .leave import today
from .tools import TOOLS, ToolContext, ToolOutcome, execute_tool

log = logging.getLogger(__name__)

SYSTEM = """You are the HR assistant in Acme Corp's internal HR portal.
Today's date is {today}. You are helping {name} ({employee_id}), {role} in the {office} office.

How to work:
- Answer policy questions only from search_policy results, and name the source like (Leave Policy > Annual leave). If the policies do not cover something, say so and suggest hr@acme.example. Never invent policy.
- For this employee's balance, requests or working days, use the tools instead of guessing.
- You can only DRAFT a leave request. The employee confirms it in the portal, so never say leave was submitted or approved.
- Turn relative dates ("next Sunday") into exact dates using today's date, and say which dates you used. If dates are missing or unclear, ask before drafting.
- Keep replies short, friendly and in plain text."""

REFUSAL_REPLY = "Sorry, I can't help with that request. For anything sensitive, please contact hr@acme.example."
STEP_LIMIT_REPLY = "I couldn't finish that within my step limit. Could you split it into smaller questions?"


@dataclass
class TurnResult:
    reply: str
    stop_reason: str
    steps: list[dict] = field(default_factory=list)
    citations: list[dict] = field(default_factory=list)
    drafts: list[dict] = field(default_factory=list)


def system_prompt(employee: Employee) -> str:
    return SYSTEM.format(today=today().isoformat(), name=employee.name, employee_id=employee.id,
                         role=employee.role, office=employee.office)


def run_turn(messages: list, user_text: str, employee: Employee, ctx: ToolContext, llm,
             max_steps: int = MAX_AGENT_STEPS) -> TurnResult:
    messages.append({"role": "user", "content": user_text})
    result = TurnResult(reply="", stop_reason="")
    system = system_prompt(employee)

    for _ in range(max_steps):
        response = llm.create(system=system, messages=messages, tools=TOOLS)
        if response.content:  # an empty assistant turn (e.g. some refusals) would make the next call a 400
            messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "refusal":
            result.reply, result.stop_reason = REFUSAL_REPLY, "refusal"
            return result

        tool_uses = [b for b in response.content if b.type == "tool_use"]
        if not tool_uses:
            text = "\n".join(b.text for b in response.content if b.type == "text").strip()
            if response.stop_reason == "max_tokens":
                text += "\n\n(My answer was cut short - ask me to continue.)"
            result.reply, result.stop_reason = text, response.stop_reason
            return result

        # All results go back in ONE user message, matching the parallel tool calls they answer.
        tool_results = []
        for call in tool_uses:
            try:
                outcome = execute_tool(call.name, dict(call.input), ctx)
            except Exception:  # every tool_use MUST get a tool_result, or the conversation is broken for good
                log.exception("tool %s crashed", call.name)
                ctx.session.rollback()
                outcome = ToolOutcome("Internal error while running this tool. Apologise and suggest trying again later.",
                                      is_error=True)
            tool_results.append({"type": "tool_result", "tool_use_id": call.id, "content": outcome.content,
                                 **({"is_error": True} if outcome.is_error else {})})
            result.steps.append({"tool": call.name, "input": dict(call.input), "is_error": outcome.is_error,
                                 "output": outcome.content[:300]})
            result.citations += [c for c in outcome.citations if c not in result.citations]
            if outcome.draft:
                result.drafts.append(outcome.draft)
        messages.append({"role": "user", "content": tool_results})

    result.reply, result.stop_reason = STEP_LIMIT_REPLY, "step_limit"
    return result
