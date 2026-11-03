"""One test per bug found in code review, so none of them can come back."""

from datetime import date

import pytest

from app import leave
from app.agent import run_turn
from app.db import Employee
from app.llm import _Block, _Response

EMP = Employee(id="E001", name="Rahim Uddin", email="r@a", role="employee")


def test_leave_can_be_planned_into_next_year(session):
    req = leave.create_draft(session, "E001", "annual", date(2027, 1, 3), date(2027, 1, 5))
    leave.confirm(session, "E001", req.id)
    nxt = next(b for b in leave.balances(session, "E001", 2027) if b["leave_type"] == "annual")
    assert (nxt["pending"], nxt["remaining"]) == (3, 17)


def test_overlapping_drafts_cannot_both_be_confirmed(session):
    a = leave.create_draft(session, "E001", "annual", date(2026, 11, 8), date(2026, 11, 9))
    leave.cancel(session, "E001", a.id)  # frees the dates so a second, overlapping draft is allowed...
    b = leave.create_draft(session, "E001", "annual", date(2026, 11, 9), date(2026, 11, 10))
    c = leave.create_draft(session, "E001", "sick", date(2026, 11, 15), date(2026, 11, 15))
    leave.confirm(session, "E001", b.id)
    # ...and a draft that was created before b existed must not slip through on confirm
    session.exec(  # simulate the race: a stale draft whose dates overlap b
        leave.update(leave.LeaveRequest).where(leave.LeaveRequest.id == c.id)
        .values(start_date=date(2026, 11, 10), end_date=date(2026, 11, 10)))
    session.commit()
    with pytest.raises(leave.LeaveError) as e:
        leave.confirm(session, "E001", c.id)
    assert e.value.code == "OVERLAP"


class CrashingToolLLM:
    """Asks for a tool whose execution blows up with an unexpected error."""
    def __init__(self):
        self.calls = 0

    def create(self, *, messages, **_):
        self.calls += 1
        if self.calls == 1:
            return _Response([_Block("tool_use", id="t1", name="get_leave_balance", input={})], "tool_use")
        return _Response([_Block("text", text="Sorry, something went wrong.")], "end_turn")


def test_a_crashing_tool_still_gets_a_tool_result(ctx, monkeypatch):
    monkeypatch.setattr(leave, "balances", lambda *a, **k: 1 / 0)
    messages = []
    turn = run_turn(messages, "balance?", EMP, ctx, CrashingToolLLM())
    result = messages[2]["content"][0]
    assert result["tool_use_id"] == "t1" and result["is_error"] is True
    assert turn.stop_reason == "end_turn"


def test_failed_balance_update_rolls_back_the_cancel(session):
    req = leave.create_draft(session, "E001", "annual", date(2026, 11, 8), date(2026, 11, 8))
    leave.confirm(session, "E001", req.id)
    session.exec(leave.delete(leave.LeaveBalance).where(leave.LeaveBalance.employee_id == "E001"))
    session.commit()
    with pytest.raises(leave.LeaveError) as e:
        leave.cancel(session, "E001", req.id)
    assert e.value.code == "BALANCE_MISSING"
    session.refresh(req)
    assert req.status == "pending"  # the status change was rolled back too


def test_second_turn_on_a_busy_conversation_gets_409(client):
    from conftest import as_user
    conv = client.post("/api/chat", headers=as_user("E001"), json={"message": "hi"}).json()["conversation_id"]
    lock = client.app.state.conversations[conv]["lock"]
    lock.acquire()  # pretend the first turn is still running
    try:
        r = client.post("/api/chat", headers=as_user("E001"), json={"message": "again", "conversation_id": conv})
        assert r.status_code == 409
    finally:
        lock.release()
    assert client.post("/api/chat", headers=as_user("E001"),
                       json={"message": "again", "conversation_id": conv}).status_code == 200


class EmptyRefusalLLM:
    def create(self, **_):
        return _Response([], "refusal")


def test_empty_refusal_is_not_written_into_history(ctx):
    messages = []
    run_turn(messages, "something", EMP, ctx, EmptyRefusalLLM())
    assert [m["role"] for m in messages] == ["user"]
