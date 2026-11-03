from sqlmodel import Session, select

from .db import Employee, LeaveBalance
from .leave import ENTITLEMENT, today

EMPLOYEES = [
    Employee(id="M001", name="Nadia Karim", email="nadia@acme.example", role="manager"),
    Employee(id="E001", name="Rahim Uddin", email="rahim@acme.example", role="employee", manager_id="M001"),
    Employee(id="E002", name="Sadia Islam", email="sadia@acme.example", role="employee", manager_id="M001"),
]
USED = {"E001": {"annual": 6, "sick": 2, "casual": 3}, "E002": {"annual": 15, "sick": 0, "casual": 8}}


def seed(engine) -> None:
    with Session(engine) as s:
        if s.exec(select(Employee)).first():
            return
        s.add_all(Employee.model_validate(e.model_dump()) for e in EMPLOYEES)
        year = today().year
        for e in EMPLOYEES:
            for leave_type, entitled in ENTITLEMENT.items():
                s.add(LeaveBalance(employee_id=e.id, leave_type=leave_type, year=year, entitled=entitled,
                                   used=USED.get(e.id, {}).get(leave_type, 0)))
                # next year's entitlement too, so leave can be planned across New Year
                s.add(LeaveBalance(employee_id=e.id, leave_type=leave_type, year=year + 1, entitled=entitled))
        s.commit()
