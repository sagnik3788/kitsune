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

```mermaid
flowchart TB
    subgraph External["External Actors"]
        A1[AI Agent<br/>opencode]
        A2[AI Agent<br/>Claude Code]
        A3[AI Agent<br/>Cursor]
        D1[Developer]
    end

    subgraph PluginLayer["Plugin Layer — Thin Adapters"]
        P1[opencode Plugin<br/>TypeScript<br/>Tool call interception]
        P2[Claude Code Hook<br/>PreToolUse hook]
        P3[Cursor MCP Config<br/>Advisory enforcement]
    end

    subgraph Gateway["MCP Gateway — FastAPI"]
        direction TB
        API[MCP API Endpoints]
        Auth[Auth Module<br/>API Keys]
        SM[Session Manager<br/>phase / edits / turns]
        WF[Workflow CRUD<br/>YAML load/create/list]
        Hist[Run History<br/>timelines / metrics]
    end

    subgraph Engine["Python Engine — Pure FSM"]
        CK[checkphase, tool, workflow]
        GR[Guardrails]
        Trans[Transition Logic<br/>READY → DONE → PASS → FAIL]
    end

    subgraph Store["Session Store"]
        R1[(Redis<br/>Distributed)]
        R2[(SQLite<br/>Local / Docker)]
        R3[(In-Memory<br/>Single dev)]
    end

    subgraph Dashboard["Dashboard — Vanilla JS SPA"]
        VIS[Visual Editor<br/>Drag-drop phases]
        YAML[YAML Editor<br/>Live sync]
        RUN[Run History<br/>Timeline view]
    end

    A1 -->|MCP over stdio| P1
    A2 -->|PreToolUse hook| P2
    A3 -->|MCP config| P3

    P1 -->|kitsune_check_tool| API
    P2 -->|kitsune_check_tool| API
    P3 -->|kitsune_check_tool| API

    API --> Auth
    Auth --> SM
    SM --> WF
    SM --> Hist

    SM -->|check| CK
    CK --> GR
    CK --> Trans
    CK -->|bool: ALLOW / BLOCK| SM

    SM -->|read/write session| R1
    SM -->|read/write session| R2
    SM -->|read/write session| R3

    D1 -->|HTTP| VIS
    VIS -->|CRUD workflows| API
    YAML -->|load/create workflow| API
    RUN -->|fetch history| Hist

    style External fill:#e1f5fe
    style PluginLayer fill:#fff3e0
    style Gateway fill:#e8f5e9
    style Engine fill:#fce4ec
    style Store fill:#f3e5f5
    style Dashboard fill:#fffde7
```

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

## Quick start

```bash
pip install kitsune
kitsune editor          # open visual workflow editor
kitsune activate workflow.yaml
opencode "fix the bug in auth.py"
```

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
