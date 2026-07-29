import os
import yaml
import asyncpg
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from schema import User, APIKey, Workflow, RunHistory, Usage

load_dotenv()

_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        dsn = os.getenv("POSTGRES_URL", "")
        _pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=2,
            max_size=10,
            command_timeout=30,
        )
    return _pool


# DDL

async def init_db() -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT,
                plan TEXT NOT NULL DEFAULT 'free',
                created_at TIMESTAMPTZ NOT NULL,
                updated_at TIMESTAMPTZ NOT NULL
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id),
                hashed_key TEXT NOT NULL UNIQUE,
                name TEXT,
                last_used_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ NOT NULL
            )
        """)
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(hashed_key)"
        )
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id),
                yaml_content TEXT NOT NULL,
                name TEXT,
                description TEXT,
                is_template BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL,
                updated_at TIMESTAMPTZ NOT NULL
            )
        """)
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_workflows_user ON workflows(user_id)"
        )
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS run_history (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL REFERENCES users(id),
                phase TEXT NOT NULL,
                tool TEXT,
                trigger TEXT,
                result TEXT NOT NULL CHECK(result IN ('allowed', 'blocked', 'transitioned')),
                reason TEXT,
                timestamp TIMESTAMPTZ NOT NULL
            )
        """)
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_run_history_session ON run_history(session_id)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_run_history_user ON run_history(user_id)"
        )
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS usage (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id),
                transitions_used INTEGER DEFAULT 0,
                month TEXT NOT NULL,
                plan_limit INTEGER NOT NULL,
                UNIQUE(user_id, month)
            )
        """)


# User operations

async def create_user(user: User) -> None:
    pool = await get_pool()
    await pool.execute(
        """INSERT INTO users (id, email, plan, created_at, updated_at)
           VALUES ($1, $2, $3, $4, $5)
           ON CONFLICT (id) DO UPDATE SET
             email = EXCLUDED.email,
             plan = EXCLUDED.plan,
             updated_at = EXCLUDED.updated_at""",
        user.id, user.email, user.plan.value,
        user.created_at, user.updated_at,
    )


async def update_user(user: User) -> None:
    pool = await get_pool()
    await pool.execute(
        "UPDATE users SET email = $2, plan = $3, updated_at = $4 WHERE id = $1",
        user.id, user.email, user.plan.value, user.updated_at,
    )


async def delete_user(user_id: str) -> None:
    pool = await get_pool()
    await pool.execute("DELETE FROM users WHERE id = $1", user_id)


async def get_user_by_id(user_id: str) -> Optional[User]:
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    return User(**dict(row)) if row else None


async def get_user_by_api_key(hashed_key: str) -> Optional[User]:
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT u.* FROM users u JOIN api_keys k ON u.id = k.user_id WHERE k.hashed_key = $1",
        hashed_key,
    )
    return User(**dict(row)) if row else None


# API Key operations

async def create_api_key(api_key: APIKey) -> None:
    pool = await get_pool()
    await pool.execute(
        "INSERT INTO api_keys (id, user_id, hashed_key, name, last_used_at, created_at) VALUES ($1, $2, $3, $4, $5, $6)",
        api_key.id, api_key.user_id, api_key.hashed_key, api_key.name,
        api_key.last_used_at, api_key.created_at,
    )

async def list_api_keys(user_id: str) -> list[APIKey]:
    pool = await get_pool()
    rows = await pool.fetch("SELECT * FROM api_keys WHERE user_id = $1", user_id)
    return [APIKey(**dict(row)) for row in rows]


async def delete_api_key(key_id: str, user_id: str) -> None:
    pool = await get_pool()
    await pool.execute("DELETE FROM api_keys WHERE id = $1 AND user_id = $2", key_id, user_id)


async def get_api_key_by_hash(hashed_key: str) -> Optional[APIKey]:
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM api_keys WHERE hashed_key = $1", hashed_key)
    return APIKey(**dict(row)) if row else None


async def update_api_key_last_used(api_key_id: str) -> None:
    now = datetime.now(timezone.utc)
    pool = await get_pool()
    await pool.execute("UPDATE api_keys SET last_used_at = $1 WHERE id = $2", now, api_key_id)


#  Workflow operations

async def create_workflow(workflow: Workflow, user_id: str, is_template: bool = False) -> None:
    yaml_content = yaml.safe_dump(workflow.model_dump(mode="json"))
    now = datetime.now(timezone.utc)
    pool = await get_pool()
    await pool.execute(
        "INSERT INTO workflows (id, user_id, yaml_content, name, description, is_template, created_at, updated_at) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
        workflow.id, user_id, yaml_content, workflow.name or workflow.id, workflow.description, is_template, now, now,
    )


async def get_workflow(workflow_id: str) -> Optional[Workflow]:
    pool = await get_pool()
    row = await pool.fetchrow("SELECT id, yaml_content FROM workflows WHERE id = $1", workflow_id)
    if row:
        yaml_data = yaml.safe_load(row["yaml_content"])
        yaml_data["id"] = row["id"]
        return Workflow(**yaml_data)
    return None


async def get_workflow_for_user(workflow_id: str, user_id: str) -> Optional[Workflow]:
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT id, yaml_content FROM workflows WHERE id = $1 AND user_id = $2",
        workflow_id, user_id,
    )
    if row:
        yaml_data = yaml.safe_load(row["yaml_content"])
        yaml_data["id"] = row["id"]
        return Workflow(**yaml_data)
    return None


async def list_workflows(user_id: str) -> list[Workflow]:
    pool = await get_pool()
    rows = await pool.fetch("SELECT id, name, yaml_content FROM workflows WHERE user_id = $1", user_id)
    result = []
    for row in rows:
        yaml_data = yaml.safe_load(row["yaml_content"])
        yaml_data["id"] = row["id"]
        yaml_data["name"] = row["name"]
        result.append(Workflow(**yaml_data))
    return result


async def update_workflow(workflow_id: str, workflow: Workflow, user_id: str) -> None:
    yaml_content = yaml.safe_dump(workflow.model_dump(mode="json"))
    now = datetime.now(timezone.utc)
    pool = await get_pool()
    await pool.execute(
        "UPDATE workflows SET yaml_content = $1, name = $2, description = $3, updated_at = $4 WHERE id = $5 AND user_id = $6",
        yaml_content, workflow.name or workflow.id, workflow.description, now, workflow_id, user_id,
    )

async def delete_workflow(workflow_id: str, user_id: str) -> None:
    pool = await get_pool()
    await pool.execute("DELETE FROM workflows WHERE id = $1 AND user_id = $2", workflow_id, user_id)


# Run History

async def log_run_history(entry: RunHistory) -> None:
    pool = await get_pool()
    await pool.execute(
        "INSERT INTO run_history (id, session_id, user_id, phase, tool, trigger, result, reason, timestamp) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
        entry.id, entry.session_id, entry.user_id, entry.phase, entry.tool,
        entry.trigger, entry.result, entry.reason, entry.timestamp,
    )


async def get_run_history(session_id: str) -> list[RunHistory]:
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT * FROM run_history WHERE session_id = $1 ORDER BY timestamp", session_id
    )
    return [RunHistory(**dict(row)) for row in rows]


#  Usage operations

async def get_usage(user_id: str, month: str) -> Optional[Usage]:
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM usage WHERE user_id = $1 AND month = $2", user_id, month)
    return Usage(**dict(row)) if row else None


async def increment_usage(user_id: str, month: str, plan_limit: int) -> None:
    usage_id = f"{user_id}_{month}"
    pool = await get_pool()
    await pool.execute("""
        INSERT INTO usage (id, user_id, transitions_used, month, plan_limit)
        VALUES ($1, $2, 1, $3, $4)
        ON CONFLICT (user_id, month)
        DO UPDATE SET transitions_used = usage.transitions_used + 1
    """, usage_id, user_id, month, plan_limit)
