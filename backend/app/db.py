from datetime import date, datetime, timezone

from sqlalchemy.pool import StaticPool
from sqlmodel import Field, Session, SQLModel, create_engine


class Employee(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    email: str
    role: str  # "employee" | "manager"
    manager_id: str | None = Field(default=None, foreign_key="employee.id")
    office: str = "Dhaka"


class LeaveBalance(SQLModel, table=True):
    employee_id: str = Field(foreign_key="employee.id", primary_key=True)
    leave_type: str = Field(primary_key=True)
    year: int = Field(primary_key=True)
    entitled: float
    used: float = 0
    pending: float = 0  # reserved by confirmed requests awaiting the manager


class LeaveRequest(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    employee_id: str = Field(foreign_key="employee.id", index=True)
    leave_type: str
    start_date: date
    end_date: date
    days: float
    reason: str = ""
    # draft -> pending -> approved | rejected; draft and pending can also become cancelled
    status: str = Field(default="draft", index=True)
    decided_by: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def make_engine(url: str):
    if url == "sqlite://":  # in-memory DB shared across threads (tests)
        return create_engine(url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    return create_engine(url, connect_args={"check_same_thread": False})


def init_db(engine) -> None:
    SQLModel.metadata.create_all(engine)


__all__ = ["Employee", "LeaveBalance", "LeaveRequest", "Session", "make_engine", "init_db"]
