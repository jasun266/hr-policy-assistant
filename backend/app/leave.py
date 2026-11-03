"""Leave rules. Everything that changes a balance is a conditional UPDATE, so two
concurrent requests can never overdraw a balance or decide the same request twice."""

import os
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import delete, update  # noqa: F401  (delete is used by tests via leave.delete)
from sqlmodel import Session, select

from .db import Employee, LeaveBalance, LeaveRequest

ENTITLEMENT = {"annual": 20, "sick": 14, "casual": 10}
MAX_CASUAL_DAYS = 3
WEEKEND = {4, 5}  # Friday, Saturday (Dhaka office)
FIXED_HOLIDAYS = {(2, 21), (3, 26), (4, 14), (5, 1), (12, 16), (12, 25)}
OPEN_STATUSES = ("draft", "pending", "approved")
DHAKA = timezone(timedelta(hours=6))  # Bangladesh has no daylight saving


class LeaveError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def today() -> date:
    override = os.getenv("HR_TODAY")  # lets tests and demos pin "today"
    return date.fromisoformat(override) if override else datetime.now(DHAKA).date()


def is_working_day(d: date) -> bool:
    return d.weekday() not in WEEKEND and (d.month, d.day) not in FIXED_HOLIDAYS


def working_days(start: date, end: date) -> int:
    return sum(is_working_day(start + timedelta(n)) for n in range((end - start).days + 1))


def balances(s: Session, employee_id: str, year: int | None = None) -> list[dict]:
    year = year or today().year
    rows = s.exec(
        select(LeaveBalance).where(LeaveBalance.employee_id == employee_id, LeaveBalance.year == year)
    ).all()
    return [
        {
            "leave_type": b.leave_type,
            "entitled": b.entitled,
            "used": b.used,
            "pending": b.pending,
            "remaining": b.entitled - b.used - b.pending,
        }
        for b in sorted(rows, key=lambda b: list(ENTITLEMENT).index(b.leave_type))
    ]


def create_draft(s: Session, employee_id: str, leave_type: str, start: date, end: date, reason: str = "") -> LeaveRequest:
    if leave_type not in ENTITLEMENT:
        raise LeaveError("UNKNOWN_LEAVE_TYPE", f"Leave type must be one of {', '.join(ENTITLEMENT)}.")
    if end < start:
        raise LeaveError("BAD_RANGE", "The end date is before the start date.")
    if start < today():
        raise LeaveError("PAST_DATE", "Leave cannot start in the past.")
    if start.year != end.year:
        raise LeaveError("CROSS_YEAR", "A request cannot span two calendar years; split it into two requests.")
    days = working_days(start, end)
    if days == 0:
        raise LeaveError("NO_WORKING_DAYS", "Those dates are all weekends or public holidays, so no leave is needed.")
    if leave_type == "casual" and days > MAX_CASUAL_DAYS:
        raise LeaveError("CASUAL_TOO_LONG", f"A casual leave request may not exceed {MAX_CASUAL_DAYS} working days.")

    clash = _find_clash(s, employee_id, start, end)
    if clash:
        raise LeaveError("OVERLAP", f"These dates overlap your {clash.status} request #{clash.id} ({clash.start_date} to {clash.end_date}).")

    remaining = next((b["remaining"] for b in balances(s, employee_id, start.year) if b["leave_type"] == leave_type), 0)
    if days > remaining:
        raise LeaveError("INSUFFICIENT_BALANCE", f"This needs {days} {leave_type} leave days but only {remaining:g} remain.")

    req = LeaveRequest(employee_id=employee_id, leave_type=leave_type, start_date=start, end_date=end, days=days, reason=reason)
    s.add(req)
    s.commit()
    s.refresh(req)
    return req


def _find_clash(s: Session, employee_id: str, start: date, end: date, exclude_id: int | None = None,
                statuses: tuple = OPEN_STATUSES) -> LeaveRequest | None:
    q = select(LeaveRequest).where(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.status.in_(statuses),
        LeaveRequest.start_date <= end,
        LeaveRequest.end_date >= start,
    )
    if exclude_id is not None:
        q = q.where(LeaveRequest.id != exclude_id)
    return s.exec(q).first()


def _get_own(s: Session, employee_id: str, request_id: int) -> LeaveRequest:
    req = s.get(LeaveRequest, request_id)
    if not req or req.employee_id != employee_id:  # someone else's request looks exactly like a missing one
        raise LeaveError("NOT_FOUND", f"Leave request #{request_id} was not found.")
    return req


def _move(s: Session, req: LeaveRequest, *, pending: float = 0, used: float = 0, need_remaining: float = 0) -> bool:
    """Adjust a balance only if enough days remain. Returns False when the guard fails."""
    stmt = (
        update(LeaveBalance)
        .where(
            LeaveBalance.employee_id == req.employee_id,
            LeaveBalance.leave_type == req.leave_type,
            LeaveBalance.year == req.start_date.year,
            LeaveBalance.entitled - LeaveBalance.used - LeaveBalance.pending >= need_remaining,
        )
        .values(pending=LeaveBalance.pending + pending, used=LeaveBalance.used + used)
    )
    return s.exec(stmt).rowcount == 1


def _set_status(s: Session, req: LeaveRequest, old: str, new: str, decided_by: str | None = None) -> bool:
    stmt = (
        update(LeaveRequest)
        .where(LeaveRequest.id == req.id, LeaveRequest.status == old)
        .values(status=new, decided_by=decided_by)
    )
    return s.exec(stmt).rowcount == 1


def confirm(s: Session, employee_id: str, request_id: int) -> LeaveRequest:
    req = _get_own(s, employee_id, request_id)
    if req.status != "draft" or not _set_status(s, req, "draft", "pending"):
        s.rollback()
        raise LeaveError("NOT_A_DRAFT", f"Request #{request_id} is {req.status}, not a draft.")
    # Two drafts can be created for the same days; only one of them may go forward.
    clash = _find_clash(s, employee_id, req.start_date, req.end_date, exclude_id=req.id, statuses=("pending", "approved"))
    if clash:
        s.rollback()
        raise LeaveError("OVERLAP", f"These dates overlap your {clash.status} request #{clash.id}.")
    if not _move(s, req, pending=req.days, need_remaining=req.days):
        s.rollback()
        raise LeaveError("INSUFFICIENT_BALANCE", "Your balance changed and no longer covers this request.")
    s.commit()
    s.refresh(req)
    return req


def cancel(s: Session, employee_id: str, request_id: int) -> LeaveRequest:
    req = _get_own(s, employee_id, request_id)
    old = req.status
    if old not in ("draft", "pending") or not _set_status(s, req, old, "cancelled"):
        s.rollback()
        raise LeaveError("CANNOT_CANCEL", f"Request #{request_id} is {old}; approved leave must be cancelled through your manager.")
    if old == "pending" and not _move(s, req, pending=-req.days):
        s.rollback()
        raise LeaveError("BALANCE_MISSING", "The balance for this request could not be updated; contact HR.")
    s.commit()
    s.refresh(req)
    return req


def decide(s: Session, manager_id: str, request_id: int, approve: bool) -> LeaveRequest:
    req = s.get(LeaveRequest, request_id)
    owner = s.get(Employee, req.employee_id) if req else None
    if not req or not owner or owner.manager_id != manager_id:
        raise LeaveError("NOT_FOUND", f"Leave request #{request_id} was not found in your team.")
    new = "approved" if approve else "rejected"
    if not _set_status(s, req, "pending", new, decided_by=manager_id):
        s.rollback()
        raise LeaveError("NOT_PENDING", f"Request #{request_id} is {req.status}, not pending.")
    if not _move(s, req, pending=-req.days, used=req.days if approve else 0):
        s.rollback()
        raise LeaveError("BALANCE_MISSING", "The balance for this request could not be updated; contact HR.")
    s.commit()
    s.refresh(req)
    return req


def as_dict(req: LeaveRequest) -> dict:
    return {
        "id": req.id,
        "employee_id": req.employee_id,
        "leave_type": req.leave_type,
        "start_date": req.start_date.isoformat(),
        "end_date": req.end_date.isoformat(),
        "days": req.days,
        "reason": req.reason,
        "status": req.status,
    }
