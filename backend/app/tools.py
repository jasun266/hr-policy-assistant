"""Tools the agent can call. Every tool acts as the signed-in employee: the employee id comes
from the server-side context, never from the model's input, so a prompt cannot reach
someone else's data. The only side-effecting tool creates a *draft* that the employee
must confirm in the UI - the model can never submit leave on its own."""

from dataclasses import dataclass, field
from datetime import date

from sqlmodel import Session, select

from . import leave
from .db import LeaveRequest
from .policies import PolicyIndex


@dataclass
class ToolContext:
    session: Session
    employee_id: str
    policies: PolicyIndex


@dataclass
class ToolOutcome:
    content: str
    is_error: bool = False
    citations: list[dict] = field(default_factory=list)
    draft: dict | None = None


def _schema(properties: dict, required: list[str] | None = None) -> dict:
    return {"type": "object", "properties": properties, "required": required or list(properties), "additionalProperties": False}


DATE = {"type": "string", "format": "date", "description": "ISO date, YYYY-MM-DD"}

TOOLS = [
    {
        "name": "search_policy",
        "description": "Search Acme's HR policy documents (leave, remote work, expenses and travel). Returns the most relevant sections with their document and section titles. Use it for every policy question and cite what it returns.",
        "input_schema": _schema({"query": {"type": "string", "description": "Search terms, e.g. 'carry forward annual leave'"}}),
    },
    {
        "name": "get_leave_balance",
        "description": "Get the signed-in employee's leave balance for the current year: entitled, used, pending and remaining days per leave type.",
        "input_schema": _schema({}),
    },
    {
        "name": "list_my_leave_requests",
        "description": "List the signed-in employee's leave requests, newest first.",
        "input_schema": _schema({"status": {"type": "string", "enum": ["all", "draft", "pending", "approved", "rejected", "cancelled"]}}),
    },
    {
        "name": "count_working_days",
        "description": "Count working days between two dates inclusive, excluding the Friday-Saturday weekend and public holidays.",
        "input_schema": _schema({"start_date": DATE, "end_date": DATE}),
    },
    {
        "name": "draft_leave_request",
        "description": "Create a DRAFT leave request for the signed-in employee after checking dates, overlaps and balance. The draft is not submitted: the employee must confirm it in the portal. Only call this when the employee clearly asked to apply for leave and the dates are known.",
        "input_schema": _schema({
            "leave_type": {"type": "string", "enum": list(leave.ENTITLEMENT)},
            "start_date": DATE,
            "end_date": DATE,
            "reason": {"type": "string", "description": "Short reason in the employee's words, or empty"},
        }),
    },
]
for _tool in TOOLS:
    _tool["strict"] = True


def execute_tool(name: str, args: dict, ctx: ToolContext) -> ToolOutcome:
    try:
        if name == "search_policy":
            hits = ctx.policies.search(args["query"])
            if not hits:
                return ToolOutcome("No policy section matched. Tell the employee the policies do not cover this and suggest hr@acme.example.")
            cites = [{"document": h["document"], "section": h["section"]} for h in hits]
            text = "\n\n".join(f"[{h['document']} > {h['section']}]\n{h['text']}" for h in hits)
            return ToolOutcome(text, citations=cites)

        if name == "get_leave_balance":
            rows = leave.balances(ctx.session, ctx.employee_id)
            return ToolOutcome("\n".join(
                f"{r['leave_type']}: {r['remaining']:g} remaining (entitled {r['entitled']:g}, used {r['used']:g}, pending {r['pending']:g})"
                for r in rows) or "No balance found for this year.")

        if name == "list_my_leave_requests":
            q = select(LeaveRequest).where(LeaveRequest.employee_id == ctx.employee_id)
            if args.get("status", "all") != "all":
                q = q.where(LeaveRequest.status == args["status"])
            rows = ctx.session.exec(q.order_by(LeaveRequest.id.desc()).limit(10)).all()
            return ToolOutcome("\n".join(
                f"#{r.id} {r.leave_type} {r.start_date} to {r.end_date} ({r.days:g} days) - {r.status}" for r in rows)
                or "No leave requests found.")

        if name == "count_working_days":
            start, end = date.fromisoformat(args["start_date"]), date.fromisoformat(args["end_date"])
            if end < start:
                return ToolOutcome("end_date is before start_date.", is_error=True)
            return ToolOutcome(f"{leave.working_days(start, end)} working days from {start} to {end}.")

        if name == "draft_leave_request":
            req = leave.create_draft(
                ctx.session, ctx.employee_id, args["leave_type"],
                date.fromisoformat(args["start_date"]), date.fromisoformat(args["end_date"]), args.get("reason", ""),
            )
            draft = leave.as_dict(req)
            return ToolOutcome(
                f"Draft #{req.id} created: {req.leave_type} leave {req.start_date} to {req.end_date}, {req.days:g} working days. "
                "It is NOT submitted yet - the employee must review and confirm it in the portal.",
                draft=draft,
            )

        return ToolOutcome(f"Unknown tool: {name}", is_error=True)
    except leave.LeaveError as e:
        return ToolOutcome(f"{e.code}: {e.message}", is_error=True)
    except (KeyError, ValueError) as e:
        return ToolOutcome(f"Invalid input: {e}", is_error=True)
