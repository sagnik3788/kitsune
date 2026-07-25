from pydantic import BaseModel, Field
from enum import Enum
from typing import Any, Optional, Literal

from datetime import datetime, timezone, timedelta

# full user model as per the flow:-

# opencode plugin sends req to mcp gateway (with session id, tools, args etc means mcp-req model) as a mcp-client,
# then gateway checks auth (user and api key)
# gateway fetch the state (means the session state from the redis)
# gateway load rules from turso(yaml) and engine evaluate [workflow model]
# gateway build the response and send the mcp_response model
# the same gateway save the logs like session_id , tool and phase all [history model]
# update the user profile biling usage in turso [usage model]


class GuardOp(str, Enum):
    equal = "eq"
    not_equal = "neq"
    greater_than = "gt"
    greater_than_equal = "gte"
    less_than = "lt"
    less_than_equal = "lte"
    in_ = "in"
    contains = "contains"
    exists = "exists"
    not_exists = "not_exists"

# usage:
# Guard(field="turn_count", op="lt", value=8) rule//
# if turn_count becomes 9 , block
class Guard(BaseModel):
    field: str
    op: GuardOp
    value: Any
    message: Optional[str] = None

class MCPRequest(BaseModel):
    session_id: str
    tool: str
    args: dict[str, Any] = Field(default_factory=dict)


class Session(BaseModel):
    session_id: str
    workflow_id: str
    agent_id: str
    run_id: str
    current_phase: str
    turn_count: int = 0
    counters: dict[str, int] = Field(default_factory=dict)
    files_touched: list[str] = Field(default_factory=list)
    plan_limit: int = 200  # default free plan limit
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=1)
    )


class PlanTier(str, Enum):
    free = "free"
    pro = "pro"
    team = "team"


class User(BaseModel):
    id: str
    email: str
    github_id: Optional[str] = None
    plan: PlanTier = PlanTier.free
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class APIKey(BaseModel):
    id: str
    user_id: str
    hashed_key: str
    name: Optional[str] = None
    last_used_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Phase(BaseModel):
    """
        Example:
            phases:
              plan:
                tools: ["read", "grep", "glob"]
                guards:
                  - field: turn_count
                    op: less_than
                    value: 8
                  - field: max_turn
                    op: equal
                    value: 20
                on:
                  READY: "implement"

              implement:
                tools: ["read", "edit", "write"]
                tool_guards:
                  edit:
                    - field: edit_count
                      op: less_than
                      value: 20
                on:
                  DONE: "test"
        """

    tools: list[str] = Field(default_factory=list)
    # max_turns: Optional[int] = None
    # max_edits: Optional[int] = None
    # max_files: Optional[int] = None
    commands: Optional[list[str]] = None
    # guards are for in general all the tools in a phase
    # tool_guards are a specific tool
    guards: list[Guard] = Field(default_factory=list)
    tool_guards: dict[str, list[Guard]] = Field(default_factory=dict)
    on: dict[str, str] = Field(default_factory=dict)
    type: Optional[str] = None
    requires_approval: bool = False
    blocked_env: Optional[list[str]] = None
    env_overrides: Optional[dict[str, str]] = None


class Workflow(BaseModel):
    id: str
    description: Optional[str] = None
    initial: str
    phases: dict[str, Phase]


class TransitionRequest(BaseModel):
    session_id: str
    trigger: str


class TransitionResponse(BaseModel):
    success: bool
    previous_phase: str
    new_phase: Optional[str] = None
    message: str


class MCPResponse(BaseModel):
    allowed: bool
    reason: Optional[str] = None
    current_phase: str
    next_phase: Optional[str] = None
    available_tools: list[str] = Field(default_factory=list)
    available_transitions: list[str] = Field(default_factory=list)
    message: str


class RunHistory(BaseModel):
    id: str
    session_id: str
    user_id: str
    phase: str
    tool: Optional[str] = None
    trigger: Optional[str] = None
    result: Literal["allowed", "blocked", "transitioned"]
    reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Usage(BaseModel):
    id: str
    user_id: str
    transitions_used: int = 0
    month: str
    plan_limit: int
