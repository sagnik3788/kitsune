import os
import hashlib
import json
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from engine import check, next_phase
import redis.asyncio as redis
from schema import (
    Session,
    Workflow,
    MCPRequest,
    MCPResponse,
    LoadWorkflowRequest,
    TransitionRequest,
    TransitionResponse,
    RunHistory,
    APIKey,
    User,
    PlanTier,
)

from db import (
    get_workflow as db_get_workflow,
    get_workflow_for_user as db_get_workflow_for_user,
    get_user_by_api_key,
    log_run_history,
    increment_usage,
    list_workflows as db_list_workflows,
    create_workflow as db_create_workflow,
    update_workflow as db_update_workflow,
    delete_workflow as db_delete_workflow,
    get_run_history as db_get_run_history,
    create_api_key as db_create_api_key,
    list_api_keys as db_list_api_keys,
    delete_api_key as db_delete_api_key,
    create_user,
    update_user,
    delete_user,
    get_user_by_id,
)
from dotenv import load_dotenv

# Clerk imports
from clerk_backend_api import Clerk
from svix import Webhook

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


# Clerk client
clerk_client = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))

# auth with Clerk session JWT
async def authenticate(request: Request):
    try:
        from clerk_backend_api.security.types import AuthenticateRequestOptions

        # Clerk's SDK expects a request-like object with a .headers dict
        class Requestish:
            def __init__(self, headers):
                self.headers = headers

        requestish = Requestish(dict(request.headers))
        options = AuthenticateRequestOptions(secret_key=os.getenv("CLERK_SECRET_KEY"))

        result = await clerk_client.authenticate_request_async(requestish, options)

        if not result.is_authenticated:
            raise HTTPException(
                status_code=401,
                detail=f"Authentication failed: {result.reason or result.message or 'unknown'}",
            )

        user_id = result.payload.get("sub") if result.payload else None
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: no user ID")

        # Check if user exists in our DB, create if not
        user = await get_user_by_id(user_id)
        if not user:
            # Fetch user details from Clerk API (JWT session token doesn't contain email)
            try:
                clerk_user = await clerk_client.users.get_async(user_id=user_id)
                user_email = clerk_user.email_addresses[0].email_address if clerk_user.email_addresses else None
                user_name = f"{clerk_user.first_name or ''} {clerk_user.last_name or ''}".strip() or None
            except Exception:
                user_email = None
                user_name = None

            user = User(
                id=user_id,
                email=user_email,
                name=user_name,
                plan=PlanTier.free,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            try:
                await create_user(user)
            except Exception as ce:
                import traceback
                print(f"[AUTH] Failed to create user in DB: {ce}")
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"Failed to create user: {str(ce)}")

        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

# Legacy API key auth (for agents)
async def authenticate_api_key(api_key: str):
    hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
    user = await get_user_by_api_key(hashed_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user

async def load_workflow(workflow_id: str) -> Workflow:
    workflow = await db_get_workflow(workflow_id)
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
async def mcp_load_workflow(request: LoadWorkflowRequest, api_key: str = Header(...)):
    user = await authenticate_api_key(api_key)
    plan_limit = PLAN_LIMITS.get(user.plan.value, 200)
    workflow = await load_workflow(request.workflow_id)
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
    user = await authenticate_api_key(api_key)
    session = await get_session(request.session_id)
    workflow = await load_workflow(session.workflow_id)
    result = await handle_tool_call(
        request.session_id, request.tool, request.args, workflow, user.id
    )
    return MCPResponse(**result)

@app.post("/mcp/transition")
async def mcp_transition(request: TransitionRequest, api_key: str = Header(...)):
    user = await authenticate_api_key(api_key)
    session = await get_session(request.session_id)
    workflow = await load_workflow(session.workflow_id)
    result = await handle_transition(request.session_id, request.trigger, workflow, user.id)
    return TransitionResponse(**result)


@app.post("/mcp/get_state")
async def mcp_get_state(request: MCPRequest, api_key: str = Header(...)):
    user = await authenticate_api_key(api_key)
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


@app.get("/mcp/list_workflows")
async def mcp_list_workflows(api_key: str = Header(...)):
    user = await authenticate_api_key(api_key)
    from db import list_workflows as db_list
    workflows = await db_list(user.id)
    return {"workflows": [w.model_dump() for w in workflows]}

@app.post("/mcp/create_workflow")
async def mcp_create_workflow(body: Workflow, api_key: str = Header(...)):
    user = await authenticate_api_key(api_key)
    body.id = str(uuid.uuid4())
    from db import create_workflow as db_create
    await db_create(body, user.id)
    return {"id": body.id}


# temporary arch gateway tied with dashboard(tough to scale)
#  Dashboard API endpoints

@app.get("/api/workflows")
async def api_list_workflows(req: Request):
    user = await authenticate(req)
    workflows = await db_list_workflows(user.id)
    return {"workflows": [w.model_dump() for w in workflows]}

@app.post("/api/workflows")
async def api_create_workflow(body: Workflow, req: Request):
    user = await authenticate(req)
    body.id = str(uuid.uuid4())
    await db_create_workflow(body, user.id)
    return {"id": body.id}

@app.get("/api/workflows/{workflow_id}")
async def api_get_workflow(workflow_id: str, req: Request):
    user = await authenticate(req)
    workflow = await db_get_workflow_for_user(workflow_id, user.id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow.model_dump()

@app.put("/api/workflows/{workflow_id}")
async def api_update_workflow(workflow_id: str, body: Workflow, req: Request):
    user = await authenticate(req)
    await db_update_workflow(workflow_id, body, user.id)
    return {"ok": True}

@app.delete("/api/workflows/{workflow_id}")
async def api_delete_workflow(workflow_id: str, req: Request):
    user = await authenticate(req)
    await db_delete_workflow(workflow_id, user.id)
    return {"ok": True}

@app.get("/api/runs")
async def api_get_runs(session_id: str, req: Request):
    user = await authenticate(req)
    runs = await db_get_run_history(session_id)
    return {"runs": [r.model_dump() for r in runs]}

@app.get("/api/keys")
async def api_list_keys(req: Request):
    user = await authenticate(req)
    keys = await db_list_api_keys(user.id)
    return {"keys": [k.model_dump() for k in keys]}

@app.post("/api/keys")
async def api_create_key(req: Request):
    user = await authenticate(req)
    raw_key = f"sk_{uuid.uuid4().hex}"
    hashed = hashlib.sha256(raw_key.encode()).hexdigest()
    key = APIKey(id=str(uuid.uuid4()), user_id=user.id, hashed_key=hashed, name="dashboard")
    await db_create_api_key(key)
    return {"key": raw_key, "id": key.id}

@app.delete("/api/keys/{key_id}")
async def api_delete_key(key_id: str, req: Request):
    user = await authenticate(req)
    await db_delete_api_key(key_id, user.id)
    return {"ok": True}

# Serve static assets
app.mount("/assets", StaticFiles(directory="dashboard/dist/assets"), name="assets")

# Serve root-level static files from the dist directory (e.g. public/ assets)
@app.get("/dashboard.jpeg")
async def serve_dashboard_image():
    return FileResponse("dashboard/dist/dashboard.jpeg")

@app.get("/favicon.svg")
async def serve_favicon():
    return FileResponse("dashboard/dist/favicon.svg")

# SPA fallback: serve index.html for all non-API routes (Vue Router handles client-side routing)
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # API and MCP routes are handled above, this catches everything else
    return FileResponse("dashboard/dist/index.html")


# Webhook endpoint for Clerk events (user.created, user.updated, user.deleted)
@app.post("/api/webhooks/clerk")
async def clerk_webhook(request: Request):
    """Handle Clerk webhook events to keep Neon DB in sync with Clerk users."""
    payload = await request.body()
    headers = dict(request.headers)

    # Verify webhook signature using Svix
    webhook_secret = os.getenv("CLERK_WEBHOOK_SECRET")
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="CLERK_WEBHOOK_SECRET not configured")

    wh = Webhook(webhook_secret)
    try:
        event = wh.verify(payload, headers)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid webhook signature: {e}")

    event_type = event.get("type")
    data = event.get("data", {})
    user_id = data.get("id")

    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user ID in webhook payload")

    if event_type == "user.created":
        email = None
        if data.get("email_addresses"):
            email = data["email_addresses"][0].get("email_address")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        name = f"{first_name} {last_name}".strip() or None

        user = User(
            id=user_id,
            email=email,
            name=name,
            plan=PlanTier.free,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        await create_user(user)
        return {"ok": True, "event": "user.created", "user_id": user_id}

    elif event_type == "user.updated":
        email = None
        if data.get("email_addresses"):
            email = data["email_addresses"][0].get("email_address")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        name = f"{first_name} {last_name}".strip() or None

        user = User(
            id=user_id,
            email=email,
            name=name,
            plan=PlanTier.free,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        await update_user(user)
        return {"ok": True, "event": "user.updated", "user_id": user_id}

    elif event_type == "user.deleted":
        await delete_user(user_id)
        return {"ok": True, "event": "user.deleted", "user_id": user_id}

    # Ignore other events (session.created, etc.)
    return {"ok": True, "event": event_type, "ignored": True}


# TODO: mcp_pause, mcp_deactivate

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
