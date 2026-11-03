import os

# `or` (not a getenv default) so an empty variable, e.g. from docker compose, falls back too.
MODEL = os.getenv("HR_AGENT_MODEL") or "claude-opus-5-5"
EFFORT = os.getenv("HR_AGENT_EFFORT") or "medium"
MAX_AGENT_STEPS = int(os.getenv("HR_AGENT_MAX_STEPS") or "6")
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./hr.db"
CORS_ORIGINS = (os.getenv("CORS_ORIGINS") or "http://localhost:3000").split(",")

# Without credentials the app runs on a scripted fake model, so the demo and tests cost nothing.
USE_FAKE_LLM = os.getenv("HR_FAKE_LLM") == "1" or not (
    os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")
)
