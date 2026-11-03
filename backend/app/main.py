import threading
import uuid
from contextlib import asynccontextmanager
from typing import Annotated

import anthropic
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from . import leave
from .agent import run_turn
from .config import CORS_ORIGINS, DATABASE_URL, USE_FAKE_LLM
from .db import Employee, LeaveRequest, init_db, make_engine
from .llm import ClaudeLLM, FakeLLM
from .policies import PolicyIndex
from .seed import seed
from .tools import ToolContext


def create_app(database_url: str = DATABASE_URL, llm=None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        init_db(app.state.engine)
        seed(app.state.engine)
        yield

    app = FastAPI(title="HR Policy Assistant", lifespan=lifespan)
    app.state.engine = make_engine(database_url)
    app.state.policies = PolicyIndex()
    app.state.llm = llm or (FakeLLM() if USE_FAKE_LLM else ClaudeLLM())
    # ponytail: conversations live in process memory - lost on restart and not shared across
    # instances. Move them to Redis or a table before running more than one replica.
    app.state.conversations = {}
    app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])

    def get_session(request: Request):
        with Session(request.app.state.engine) as s:
            yield s

    SessionDep = Annotated[Session, Depends(get_session)]

    # Demo auth: the UI picks a seeded user and sends its id. Swap for real JWT/SSO in production.
    def current_employee(s: SessionDep, x_employee_id: Annotated[str, Header()]) -> Employee:
        emp = s.get(Employee, x_employee_id)
        if not emp:
            raise HTTPException(401, "Unknown employee")
        return emp

    Me = Annotated[Employee, Depends(current_employee)]

    def leave_call(fn, *args):
        try:
            return leave.as_dict(fn(*args))
        except leave.LeaveError as e:
            raise HTTPException(404 if e.code == "NOT_FOUND" else 409, detail={"code": e.code, "message": e.message})

    class ChatIn(BaseModel):
        message: str = Field(min_length=1, max_length=2000)
        conversation_id: str | None = None

    @app.get("/api/health")
    def health(request: Request):
        return {"status": "ok", "llm": type(request.app.state.llm).__name__}

    @app.get("/api/employees")
    def employees(s: SessionDep):
        return [e.model_dump(include={"id", "name", "role"}) for e in s.exec(select(Employee).order_by(Employee.id))]

    @app.get("/api/me/balance")
    def my_balance(s: SessionDep, me: Me):
        return leave.balances(s, me.id)

    @app.get("/api/me/requests")
    def my_requests(s: SessionDep, me: Me):
        rows = s.exec(select(LeaveRequest).where(LeaveRequest.employee_id == me.id).order_by(LeaveRequest.id.desc()))
        return [leave.as_dict(r) for r in rows]

    @app.post("/api/me/requests/{request_id}/confirm")
    def confirm(request_id: int, s: SessionDep, me: Me):
        return leave_call(leave.confirm, s, me.id, request_id)

    @app.post("/api/me/requests/{request_id}/cancel")
    def cancel(request_id: int, s: SessionDep, me: Me):
        return leave_call(leave.cancel, s, me.id, request_id)

    @app.get("/api/team/requests")
    def team_requests(s: SessionDep, me: Me):
        q = (select(LeaveRequest, Employee.name).join(Employee, Employee.id == LeaveRequest.employee_id)
             .where(Employee.manager_id == me.id, LeaveRequest.status == "pending").order_by(LeaveRequest.start_date))
        return [{**leave.as_dict(r), "employee_name": name} for r, name in s.exec(q)]

    @app.post("/api/team/requests/{request_id}/{decision}")
    def decide(request_id: int, decision: str, s: SessionDep, me: Me):
        if decision not in ("approve", "reject"):
            raise HTTPException(404)
        return leave_call(leave.decide, s, me.id, request_id, decision == "approve")

    @app.post("/api/chat")
    def chat(body: ChatIn, request: Request, s: SessionDep, me: Me):
        convs = request.app.state.conversations
        conv_id = body.conversation_id or uuid.uuid4().hex
        conv = convs.setdefault(conv_id, {"employee_id": me.id, "messages": [], "lock": threading.Lock()})
        if conv["employee_id"] != me.id:  # never let one employee continue another's conversation
            raise HTTPException(404, "Conversation not found")
        # Two turns at once would interleave writes into the same history list.
        if not conv["lock"].acquire(blocking=False):
            raise HTTPException(409, "Still answering your previous message.")
        ctx = ToolContext(session=s, employee_id=me.id, policies=request.app.state.policies)
        try:
            turn = run_turn(conv["messages"], body.message, me, ctx, request.app.state.llm)
        except anthropic.RateLimitError:
            raise HTTPException(429, "The assistant is busy right now. Please try again in a minute.")
        except (anthropic.APIStatusError, anthropic.APIConnectionError):
            raise HTTPException(503, "The assistant is unavailable right now. Please try again shortly.")
        finally:
            conv["lock"].release()
        return {"conversation_id": conv_id, "reply": turn.reply, "stop_reason": turn.stop_reason,
                "steps": turn.steps, "citations": turn.citations, "drafts": turn.drafts}

    return app


app = create_app()
