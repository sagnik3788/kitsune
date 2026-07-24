import os
import yaml
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv

from libsql_client import create_client
from schema import User, APIKey, Workflow, RunHistory, Usage

load_dotenv()

# connection
async def get_db():
    url = os.getenv("TURSO_DB_URL") or ""
    auth_token = os.getenv("TURSO_AUTH_TOKEN")
    return create_client(url=url, auth_token=auth_token)


# DDL(startup table create)
async def init_db(db):
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            github_id TEXT,
            plan TEXT NOT NULL DEFAULT 'free',
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id),
            hashed_key TEXT NOT NULL UNIQUE,
            name TEXT,
            last_used_at DATETIME,
            created_at DATETIME NOT NULL
        )
    """)

    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(hashed_key)
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS workflows (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id),
            yaml_content TEXT NOT NULL,
            name TEXT,
            description TEXT,
            is_template BOOLEAN DEFAULT FALSE,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    """)

    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_workflows_user ON workflows(user_id)
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS run_history (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            user_id TEXT NOT NULL REFERENCES users(id),
            phase TEXT NOT NULL,
            tool TEXT,
            trigger TEXT,
            result TEXT NOT NULL CHECK(result IN ('allowed', 'blocked', 'transitioned')),
            reason TEXT,
            timestamp DATETIME NOT NULL
        )
    """)

    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_run_history_session ON run_history(session_id)
    """)

    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_run_history_user ON run_history(user_id)
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id),
            transitions_used INTEGER DEFAULT 0,
            month TEXT NOT NULL,
            plan_limit INTEGER NOT NULL,
            UNIQUE(user_id, month)
        )
    """)


# dml
# user


async def create_user(db, user: User) -> None:
    await db.execute(
        """
        INSERT INTO users (id, email, github_id, plan, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            user.id,
            user.email,
            user.github_id,
            user.plan.value,
            user.created_at.isoformat(),
            user.updated_at.isoformat(),
        ],
    )


async def get_user_by_id(db, user_id: str) -> Optional[User]:
    result = await db.execute("SELECT * FROM users WHERE id = ?", [user_id])
    if result.rows:
        return User(**result.rows[0].asdict())
    return None


async def get_user_by_email(db, email: str) -> Optional[User]:
    result = await db.execute("SELECT * FROM users WHERE email = ?", [email])
    if result.rows:
        return User(**result.rows[0].asdict())
    return None


async def get_user_by_api_key(db, hashed_key: str) -> Optional[User]:
    result = await db.execute(
        """
        SELECT u.* FROM users u
        JOIN api_keys k ON u.id = k.user_id
        WHERE k.hashed_key = ?
        """,
        [hashed_key],
    )
    if result.rows:
        return User(**result.rows[0].asdict())
    return None


# API Keys


async def create_api_key(db, api_key: APIKey) -> None:
    await db.execute(
        """
        INSERT INTO api_keys (id, user_id, hashed_key, name, last_used_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            api_key.id,
            api_key.user_id,
            api_key.hashed_key,
            api_key.name,
            api_key.last_used_at.isoformat() if api_key.last_used_at else None,
            api_key.created_at.isoformat(),
        ],
    )


async def get_api_key_by_hash(db, hashed_key: str) -> Optional[APIKey]:
    result = await db.execute(
        "SELECT * FROM api_keys WHERE hashed_key = ?", [hashed_key]
    )
    if result.rows:
        return APIKey(**result.rows[0].asdict())
    return None


async def update_api_key_last_used(db, api_key_id: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        "UPDATE api_keys SET last_used_at = ? WHERE id = ?", [now, api_key_id]
    )


# Workflows


async def create_workflow(
    db, workflow: Workflow, user_id: str, is_template: bool = False
) -> None:
    yaml_content = yaml.dump(workflow.model_dump())
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        """
        INSERT INTO workflows (id, user_id, yaml_content, name, description, is_template, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            workflow.id,
            user_id,
            yaml_content,
            workflow.id,
            workflow.description,
            is_template,
            now,
            now,
        ],
    )


async def get_workflow(db, workflow_id: str) -> Optional[Workflow]:
    result = await db.execute(
        "SELECT yaml_content FROM workflows WHERE id = ?", [workflow_id]
    )
    if result.rows:
        yaml_data = yaml.safe_load(result.rows[0]["yaml_content"])
        return Workflow(**yaml_data)
    return None


async def list_workflows(db, user_id: str) -> list[Workflow]:
    result = await db.execute(
        "SELECT yaml_content FROM workflows WHERE user_id = ?", [user_id]
    )
    workflows = []
    for row in result.rows:
        yaml_data = yaml.safe_load(row["yaml_content"])
        workflows.append(Workflow(**yaml_data))
    return workflows


async def delete_workflow(db, workflow_id: str) -> None:
    await db.execute("DELETE FROM workflows WHERE id = ?", [workflow_id])


# Run History


async def log_run_history(db, entry: RunHistory) -> None:
    await db.execute(
        """
        INSERT INTO run_history
        (id, session_id, user_id, phase, tool, trigger, result, reason, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            entry.id,
            entry.session_id,
            entry.user_id,
            entry.phase,
            entry.tool,
            entry.trigger,
            entry.result,
            entry.reason,
            entry.timestamp.isoformat(),
        ],
    )


async def get_run_history(db, session_id: str) -> list[RunHistory]:
    result = await db.execute(
        "SELECT * FROM run_history WHERE session_id = ? ORDER BY timestamp",
        [session_id],
    )
    return [RunHistory(**row.asdict()) for row in result.rows]


# Usage


async def get_usage(db, user_id: str, month: str) -> Optional[Usage]:
    result = await db.execute(
        "SELECT * FROM usage WHERE user_id = ? AND month = ?", [user_id, month]
    )
    if result.rows:
        return Usage(**result.rows[0].asdict())
    return None


async def increment_usage(db, user_id: str, month: str, plan_limit: int) -> None:
    usage_id = f"{user_id}_{month}"
    await db.execute(
        """
        INSERT INTO usage (id, user_id, transitions_used, month, plan_limit)
        VALUES (?, ?, 1, ?, ?)
        ON CONFLICT(user_id, month) DO UPDATE SET
            transitions_used = transitions_used + 1
        """,
        [usage_id, user_id, month, plan_limit],
    )
