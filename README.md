<p align="center">
  <img src="./assets/kitsune-logo.png" width="260" alt="Kitsune">
</p>

<h1 align="center">Kitsune</h1>

<p align="center">A state machine harness for AI agent tool enforcement.</p>

<p align="center">
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MPL--2.0-blue.svg" alt="License"></a>
</p>

---

## Architecture

<p align="center">
  <img src="./assets/kitsune-architecture.png" width="900" alt="Kitsune Architecture">
</p>

**6 layers, left-to-right data flow:**

1. **External Actors** — AI agents (opencode, Claude Code, Cursor) + Developers
2. **Plugin Layer** — Thin adapters (<100 lines each) that intercept tool calls
3. **MCP Gateway** — MCP Streamable HTTP server plus FastAPI services for auth, session management, workflow CRUD, and run history
4. **Python Engine** — Pure FSM function `check(phase, tool, workflow) → bool`
5. **Session Store** — Redis (hot sessions), Turso (persistent data), horizontally scalable
6. **Dashboard** — Vanilla JS SPA: visual editor, YAML editor, run history

---

## What it does

Kitsune wraps your AI coding agent in a finite state machine. Each workflow phase gates which tools are available.

```
PLAN       → read, grep, glob
IMPLEMENT  → read, edit, write
TEST       → read, bash (pytest, npm test, cargo test)
DONE       → workflow complete
```

The agent must emit triggers (`READY`, `DONE`, `PASS`, `FAIL`) to advance. Try the wrong tool in the wrong phase? Blocked. Tests fail? Loops back to `IMPLEMENT`.

---

## Visual workflow editor

Design workflows on a canvas, lock tools to each phase, and export to YAML — all from your browser.

<p align="center">
  <img src="./assets/dashboard.jpeg" width="900" alt="Kitsune visual workflow editor showing phases, tools, and transitions">
</p>

---

## Quick start

```bash
# 1. Sign up at kitsune.ai → Generate API key
# 2. Install plugin
opencode plugin install kitsune
opencode configure kitsune --key sk_live_abc123

# 3. Design workflow in browser, then run agent
opencode "fix the bug in auth.py"
```

## MCP tools

Connect an MCP client to the Streamable HTTP endpoint at `/mcp/` and send the
Kitsune API key in the `api-key` header. The server exposes:

- `kitsune_check_tool` — checks a proposed agent tool call against the active phase
- `kitsune_transition` — applies a workflow transition trigger
- `kitsune_get_state` — returns the active phase and session counters

The previous REST endpoints remain available at `/internal/mcp/check`,
`/internal/mcp/transition`, and `/internal/mcp/get_state` for debugging and a
gradual client migration. Their original `/mcp/...` aliases are temporarily
retained for backward compatibility.

---

## Workflow example

```yaml
id: bugfix
initial: plan

phases:
  plan:
    tools: [read, grep, glob]
    max_turns: 8
    on:
      READY: implement

  implement:
    tools: [read, edit, write]
    max_edits: 20
    on:
      DONE: test

  test:
    tools: [read, bash]
    commands: [pytest, cargo test, npm test]
    on:
      PASS: done
      FAIL: implement

  done:
    type: final
```

---

## Guardrails

- **Bash discernment** — blocks redirects, destructive ops, script interpreters
- **Edit limits** — max lines per edit, max files per phase
- **Command allowlists** — only allowed test commands
- **Turn limits** — breaks read-loop death spirals
- **Approval gates** — human review before advancing

---

## License

[MPL-2.0](./LICENSE)
