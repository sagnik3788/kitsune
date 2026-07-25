import os
import hashlib
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, Header, HTTPException
from engine import check, next_phase
import redis.asyncio as redis
from schema import (
    Session,
    Workflow,
    MCPRequest,
    MCPResponse,
    TransitionRequest,
    TransitionResponse,
    RunHistory,
)
from db import get_workflow, get_user_by_api_key, log_run_history, increment_usage
from dotenv import load_dotenv

# rough
PLAN_LIMITS = {"free": 200, "pro": 2500, "team": 10000}

load_dotenv()

# redis cluster from upstash cloud
redis_client = redis.from_url(os.getenv("REDIS_URL") or "", decode_responses=True)


async def get_session(session_id: str) -> Session:
    data = await redis_client.get(f"session:{session_id}")
    if data is None:
        raise ValueError(f"session {session_id} not found or expired")

    return Session.model_validate_json(data)


async def save_session(session: Session) -> None:
    json_data = session.model_dump_json()
    await redis_client.setex(f"session:{session.session_id}", 3600, json_data)


async def create_session(
    session_id: str, workflow: Workflow, agent_id: str, run_id: str, plan_limit: int = 200
) -> Session:
    session = Session(
        session_id=session_id,
        workflow_id=workflow.id,
        agent_id=agent_id,
        run_id=run_id,
        current_phase=workflow.initial,
        turn_count=0,
        counters={},
        files_touched=[],
        plan_limit=plan_limit,
    )
    await save_session(session)
    return session


# build_context from the session
def build_context(session: Session, tool: str, args: dict) -> dict:
    return {
        "tool": tool,
        "turn_count": session.turn_count,
        **session.counters,
        "files_touched_count": len(session.files_touched),
        "files_touched": session.files_touched,
        "args": args,
    }


def increment_turn(session: Session) -> None:
    session.turn_count += 1


def increment_counter(session: Session, tool: str) -> None:
    session.counters[tool] = session.counters.get(tool, 0) + 1


def record_file(session: Session, file_path: str) -> None:
    if file_path not in session.files_touched:
        session.files_touched.append(file_path)


# auth with api key from turso
async def authenticate(api_key: str):
    hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
    user = await get_user_by_api_key(hashed_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user

async def load_workflow(workflow_id: str) -> Workflow:
    workflow = await get_workflow(workflow_id)
    if not workflow:
        raise ValueError(f"Workflow {workflow_id} not found")
    return workflow

# tool call handler
async def handle_tool_call(session_id: str, tool: str, args: dict, workflow: Workflow, user_id: str):
    session = await get_session(session_id)


    increment_turn(session)
    increment_counter(session, tool)
    if "file" in args:
        record_file(session, args["file"])

    context = build_context(session, tool, args)
    result = check(session.current_phase, tool, workflow, context)
    await save_session(session)

    # LOG TO TURSO (both allowed and blocked)
    entry = RunHistory(
        id=str(uuid.uuid4()),
        session_id=session_id,
        user_id=user_id,
        phase=session.current_phase,
        tool=tool,
        result="allowed" if result["allowed"] else "blocked",
        reason=result.get("reason"),
        timestamp=datetime.now(timezone.utc)
    )
    await log_run_history(entry)

    return result


# transition
async def handle_transition(session_id: str, trigger: str, workflow: Workflow, user_id: str):
    session = await get_session(session_id)
    old_phase = session.current_phase

    next_p = next_phase(old_phase, trigger, workflow)
    if next_p is None:
        return {
            "success": False,
            "previous_phase": old_phase,
            "new_phase": None,
            "message": f"Invalid trigger '{trigger}' from phase '{old_phase}'",
        }

    session.current_phase = next_p
    session.turn_count = 0
    session.counters = {}
    session.files_touched = []

    await save_session(session)

    #track usage
    month = datetime.now().strftime("%Y-%m")
    await increment_usage(user_id, month, session.plan_limit)

    return {
        "success": True,
        "previous_phase": old_phase,
        "new_phase": next_p,
        "message": f"Transitioned from '{old_phase}' to '{next_p}'",
    }


app = FastAPI()


@app.post("/mcp/load_workflow")
async def mcp_load_workflow(workflow_id: str, api_key: str = Header(...)):
    user = await authenticate(api_key)
    plan_limit = PLAN_LIMITS.get(user.plan.value, 200)
    workflow = await load_workflow(workflow_id)
    session = await create_session(
        session_id=str(uuid.uuid4()),
        workflow=workflow,
        agent_id=user.id,
        run_id=str(uuid.uuid4()),
        plan_limit=plan_limit
    )
    return {"session_id": session.session_id, "current_phase": workflow.initial}


@app.post("/mcp/check")
async def mcp_check(request: MCPRequest, api_key: str = Header(...)):
    user = await authenticate(api_key)
    session = await get_session(request.session_id)
    workflow = await load_workflow(session.workflow_id)
    result = await handle_tool_call(
        request.session_id, request.tool, request.args, workflow, user.id
    )
    return MCPResponse(**result)

@app.post("/mcp/transition")
async def mcp_transition(request: TransitionRequest, api_key: str = Header(...)):
    user = await authenticate(api_key)
    session = await get_session(request.session_id)
    workflow = await load_workflow(session.workflow_id)
    result = await handle_transition(request.session_id, request.trigger, workflow, user.id)
    return TransitionResponse(**result)


@app.post("/mcp/get_state")
async def mcp_get_state(request: MCPRequest, api_key: str = Header(...)):
    #user = await authenticate(api_key)
    session = await get_session(request.session_id)
    workflow = await load_workflow(session.workflow_id)
    phase = workflow.phases[session.current_phase]
    return {
        "current_phase": session.current_phase,
        "available_tools": phase.tools,
        "available_transitions": list(phase.on.keys()),
        "turn_count": session.turn_count,
        "counters": session.counters,
    }


# TODO: Remaining MCP endpoints

# @app.get("/mcp/list_workflows")

# @app.post("/mcp/create_workflow")

# @app.post("/mcp/pause")

# @app.post("/mcp/deactivate")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
