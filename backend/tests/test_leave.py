from datetime import date

import pytest

from app import leave


def remaining(session, employee_id, leave_type):
    return next(b for b in leave.balances(session, employee_id) if b["leave_type"] == leave_type)


def test_working_days_skip_weekend_and_holiday():
    assert leave.working_days(date(2026, 11, 8), date(2026, 11, 12)) == 5   # Sun-Thu
    assert leave.working_days(date(2026, 11, 5), date(2026, 11, 8)) == 2    # Thu, Fri+Sat weekend, Sun
    assert leave.working_days(date(2026, 12, 13), date(2026, 12, 17)) == 4  # 16 Dec is a holiday


def test_draft_does_not_touch_balance(session):
    req = leave.create_draft(session, "E001", "annual", date(2026, 11, 8), date(2026, 11, 12))
    assert (req.status, req.days) == ("draft", 5)
    assert remaining(session, "E001", "annual")["pending"] == 0


@pytest.mark.parametrize("args, code", [
    (("annual", date(2026, 11, 1), date(2026, 11, 2)), "PAST_DATE"),
    (("annual", date(2026, 11, 12), date(2026, 11, 8)), "BAD_RANGE"),
    (("annual", date(2026, 11, 6), date(2026, 11, 7)), "NO_WORKING_DAYS"),
    (("annual", date(2026, 12, 30), date(2027, 1, 3)), "CROSS_YEAR"),
    (("casual", date(2026, 11, 8), date(2026, 11, 12)), "CASUAL_TOO_LONG"),
    (("bonus", date(2026, 11, 8), date(2026, 11, 8)), "UNKNOWN_LEAVE_TYPE"),
])
def test_draft_validation(session, args, code):
    with pytest.raises(leave.LeaveError) as e:
        leave.create_draft(session, "E001", *args)
    assert e.value.code == code


def test_insufficient_balance(session):
    # E002 has 5 annual days left; 8-19 Nov is 10 working days
    with pytest.raises(leave.LeaveError) as e:
        leave.create_draft(session, "E002", "annual", date(2026, 11, 8), date(2026, 11, 19))
    assert e.value.code == "INSUFFICIENT_BALANCE"


def test_overlap_with_open_request(session):
    leave.create_draft(session, "E001", "annual", date(2026, 11, 8), date(2026, 11, 12))
    with pytest.raises(leave.LeaveError) as e:
        leave.create_draft(session, "E001", "sick", date(2026, 11, 10), date(2026, 11, 10))
    assert e.value.code == "OVERLAP"


def test_full_lifecycle_confirm_then_approve(session):
    req = leave.create_draft(session, "E001", "annual", date(2026, 11, 8), date(2026, 11, 12))
    leave.confirm(session, "E001", req.id)
    b = remaining(session, "E001", "annual")
    assert (b["pending"], b["remaining"]) == (5, 9)

    with pytest.raises(leave.LeaveError):            # confirming twice must fail
        leave.confirm(session, "E001", req.id)

    leave.decide(session, "M001", req.id, approve=True)
    b = remaining(session, "E001", "annual")
    assert (b["used"], b["pending"], b["remaining"]) == (11, 0, 9)

    with pytest.raises(leave.LeaveError) as e:       # deciding twice must fail
        leave.decide(session, "M001", req.id, approve=False)
    assert e.value.code == "NOT_PENDING"


def test_reject_and_cancel_release_days(session):
    a = leave.create_draft(session, "E001", "annual", date(2026, 11, 8), date(2026, 11, 9))
    leave.confirm(session, "E001", a.id)
    leave.decide(session, "M001", a.id, approve=False)
    b = leave.create_draft(session, "E001", "annual", date(2026, 11, 15), date(2026, 11, 16))
    leave.confirm(session, "E001", b.id)
    leave.cancel(session, "E001", b.id)
    assert remaining(session, "E001", "annual")["remaining"] == 14


def test_confirm_rechecks_balance(session):
    # Two drafts each fit alone (5 days left), but not together.
    a = leave.create_draft(session, "E002", "annual", date(2026, 11, 8), date(2026, 11, 10))   # 3 days
    b = leave.create_draft(session, "E002", "annual", date(2026, 11, 15), date(2026, 11, 17))  # 3 days
    leave.confirm(session, "E002", a.id)
    with pytest.raises(leave.LeaveError) as e:
        leave.confirm(session, "E002", b.id)
    assert e.value.code == "INSUFFICIENT_BALANCE"
    assert remaining(session, "E002", "annual")["pending"] == 3  # failed confirm rolled back fully


def test_cannot_touch_other_peoples_requests(session):
    req = leave.create_draft(session, "E001", "annual", date(2026, 11, 8), date(2026, 11, 8))
    for fn, args in [(leave.confirm, ("E002", req.id)), (leave.cancel, ("E002", req.id)),
                     (leave.decide, ("E002", req.id, True))]:
        with pytest.raises(leave.LeaveError) as e:
            fn(session, *args)
        assert e.value.code == "NOT_FOUND"
