from app.agent import STEP_LIMIT_REPLY, run_turn
from app.db import Employee
from app.llm import FakeLLM, _Block, _Response
from app.tools import TOOLS, execute_tool


def test_policy_search_finds_the_right_section(policies):
    top = policies.search("how many days can I carry forward annual leave")[0]
    assert (top["document"], top["section"]) == ("Leave Policy", "Annual leave")
    assert policies.search("quantum spaceship") == []


def test_tool_schemas_are_strict():
    for tool in TOOLS:
        schema = tool["input_schema"]
        assert tool["strict"] and schema["additionalProperties"] is False
        assert set(schema["required"]) == set(schema["properties"])


def test_tools_act_as_the_signed_in_employee(ctx):
    out = execute_tool("get_leave_balance", {}, ctx)
    assert "annual: 14 remaining" in out.content  # E001, not anyone else


def test_draft_tool_never_submits(ctx):
    out = execute_tool("draft_leave_request", {"leave_type": "annual", "start_date": "2026-11-08",
                                               "end_date": "2026-11-12", "reason": "family trip"}, ctx)
    assert not out.is_error and out.draft["status"] == "draft"
    assert "NOT submitted" in out.content


def test_bad_tool_input_is_reported_not_raised(ctx):
    out = execute_tool("count_working_days", {"start_date": "next monday", "end_date": "2026-11-12"}, ctx)
    assert out.is_error


EMP = Employee(id="E001", name="Rahim Uddin", email="r@a", role="employee")


def test_agent_answers_policy_question_with_citation(ctx):
    messages = []
    turn = run_turn(messages, "What is the carry forward rule for annual leave?", EMP, ctx, FakeLLM())
    assert turn.stop_reason == "end_turn"
    assert {"document": "Leave Policy", "section": "Annual leave"} in turn.citations
    assert [m["role"] for m in messages] == ["user", "assistant", "user", "assistant"]


def test_agent_drafts_but_does_not_submit(ctx):
    turn = run_turn([], "Please apply annual leave from 2026-11-08 to 2026-11-12", EMP, ctx, FakeLLM())
    assert turn.drafts and turn.drafts[0]["status"] == "draft"
    assert "confirm" in turn.reply.lower()


def test_tool_errors_are_fed_back_to_the_model(ctx):
    messages = []
    turn = run_turn(messages, "Take sick leave 2026-11-06 to 2026-11-07", EMP, ctx, FakeLLM())  # weekend only
    tool_result = messages[2]["content"][0]
    assert tool_result["is_error"] is True and "NO_WORKING_DAYS" in tool_result["content"]
    assert "couldn't" in turn.reply


def test_fake_model_never_shows_tool_instructions_to_the_user(ctx):
    turn = run_turn([], "quantum spaceship rules?", EMP, ctx, FakeLLM())
    assert "Tell the employee" not in turn.reply and "hr@acme.example" in turn.reply
    assert run_turn([], "whats my name", EMP, ctx, FakeLLM()).reply == "You're signed in as Rahim Uddin."


class LoopingLLM:
    """A model that never stops calling tools - the step limit must end the turn."""
    def __init__(self):
        self.calls = 0

    def create(self, **_):
        self.calls += 1
        return _Response([_Block("tool_use", id=f"t{self.calls}", name="get_leave_balance", input={})], "tool_use")


def test_step_limit_stops_runaway_loops(ctx):
    llm = LoopingLLM()
    turn = run_turn([], "hi", EMP, ctx, llm, max_steps=3)
    assert (turn.stop_reason, turn.reply, llm.calls) == ("step_limit", STEP_LIMIT_REPLY, 3)


class RefusingLLM:
    def create(self, **_):
        return _Response([], "refusal")


def test_refusal_is_handled(ctx):
    assert run_turn([], "something", EMP, ctx, RefusingLLM()).stop_reason == "refusal"
