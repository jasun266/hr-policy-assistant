import os

os.environ["HR_TODAY"] = "2026-11-03"  # a Tuesday; pins date maths in every test
os.environ["HR_FAKE_LLM"] = "1"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.db import init_db, make_engine
from app.llm import FakeLLM
from app.main import create_app
from app.policies import PolicyIndex
from app.seed import seed
from app.tools import ToolContext


@pytest.fixture
def engine():
    eng = make_engine("sqlite://")
    init_db(eng)
    seed(eng)
    return eng


@pytest.fixture
def session(engine):
    with Session(engine) as s:
        yield s


@pytest.fixture(scope="session")
def policies():
    return PolicyIndex()


@pytest.fixture
def ctx(session, policies):
    return ToolContext(session=session, employee_id="E001", policies=policies)


@pytest.fixture
def client():
    with TestClient(create_app("sqlite://", llm=FakeLLM())) as c:
        yield c


def as_user(employee_id: str) -> dict:
    return {"X-Employee-Id": employee_id}
