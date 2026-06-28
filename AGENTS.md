# Kitsune 🦊

A state machine harness for AI agent tool enforcement. Define workflow phases, lock tools to each phase, and your agent cannot flail — it's physically prevented from calling the wrong tool at the wrong time.

---

## How it works

Kitsune wraps your AI coding agent inside a finite state machine. Each phase of a workflow gates which tools are available:

```
Phase: PLAN        → Read, Grep, Glob only
Phase: IMPLEMENT   → Read, Edit, Write unlocked
Phase: TEST        → Read, Bash (pytest, npm test, cargo test only)
Phase: DONE        → workflow complete
```

The agent is trapped in each phase until it produces a valid transition trigger (`READY`, `DONE`, `PASS`, `FAIL`). If the agent tries to call `Edit` during `PLAN`, it's blocked with a message telling it what's available and how to advance. If tests fail during `TEST`, the FSM loops back to `IMPLEMENT` — state machines support retry, DAGs don't.

This is a deterministic finite automaton (DFA). For any `(phase, trigger)` pair, exactly one next phase is defined. The agent cannot skip `TEST`. It cannot deploy from any state because deploy is never in any tool allowlist. The machine prevents it.

---

## Architecture

Four layers, each independently useful:

### Engine (Python)
Pure FSM evaluator. `check(phase, tool, workflow) -> bool`. No state, no network, no dependencies except PyYAML. Takes phase as input rather than looking it up internally — this makes it stateless and embeddable anywhere (gateway, CLI, plugin) without modification.

### MCP Gateway (FastAPI)
The cloud service that agents connect to. Exposes MCP tools (`kitsune_get_state`, `kitsune_check_tool`, `kitsune_transition`, etc.) over HTTP or stdio. Handles authentication via API keys, session management, workflow CRUD, and run history. Owns all session state — which phase each agent is in, edit counts, iteration limits. Stateless in design so it can be horizontally scaled with Redis-backed sessions.

### Dashboard (SPA)
A local web app served by the gateway. Three panels side by side:

- **Visual editor** — drag-and-drop canvas. Add phases as nodes, connect them with transition arrows, pick tools from dropdowns per phase, set limits (max edits, max files, allowed commands). Built in vanilla JS (<500 lines), no framework.
- **YAML editor** — live side panel that stays in sync with the visual canvas. Edit YAML and see nodes update. Edit nodes and see YAML update. Export/download YAML directly.
- **Run history** — timeline of past workflow executions: which phases took longest, where agents got stuck, edit counts, iteration counts.

### Plugins
Thin adapters (<100 lines each) that bridge an agent's plugin protocol to the MCP gateway:

- **opencode** (TypeScript plugin, primary target) — hard enforcement via tool call interception
- **Claude Code** (hooks) — hard enforcement via PreToolUse hook
- **Cursor** (MCP config) — advisory enforcement (MCP alone can't gate tool calls in Cursor's architecture)

The gateway speaks standard MCP. Any agent that supports MCP can connect. We don't rewrite the engine per agent — we write a thin adapter per agent.

---

## Workflow definition (YAML)

Workflows are defined in YAML. Visual editor and hand-editing stay in sync because both target the same format:

```yaml
id: bugfix
description: "Plan → Implement → Test. Classic bugfix loop."
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
    max_files: 3
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

Workflow templates (bugfix, feature, refactor, pr-review, security-audit) ship with the project. Teams fork and customize. The marketplace is a directory, not a platform — discovery via GitHub topics.

---

## Guardrails

Even when a tool is allowed in a phase, extra checks apply:

| Guardrail | What it blocks |
|-----------|---------------|
| Bash discernment | Write-via-redirect (`echo > file`), destructive ops (`rm -rf`, `sudo rm`, `dd if=`), script interpreters (`python`, `node`, `sh -c`), network exfiltration (`curl ... \| bash`) |
| Edit limits | Max lines per edit (`max_edits: 20`), max files touched per phase (`max_files: 3`) |
| Command allowlists | Only prefix-matched commands run (`pytest`, `npm test`, `cargo test`) — arbitrary bash is blocked even in test phase |
| Turn limits | Max iterations per phase (`max_turns: 8`) to break read-loop death spirals |
| Conditional transitions | Guards on context data: "only transition to done if `test_result == pass`" |
| Approval gates | `requires_approval: true` pauses for human review before advancing |
| Environment scoping | `blocked_env: [PROD_DB_URL]`, `env_overrides: {DB_URL: localhost}` |

All guardrails run before the tool call executes. Bash checks use regex patterns — the command is inspected, not executed. Guard failures return a clear message: what was blocked, what's available, how to advance.

---

## How people use it

### Solo dev
```
$ pip install kitsune
$ kitsune editor                          # open visual editor in browser
# design workflow → export bugfix.yaml
$ kitsune activate bugfix.yaml            # install opencode plugin hook
$ opencode "fix the bug in auth.py"       # Kitsune enforces phases silently
```

### Engineering team
```
$ git clone team-repo                     # workflows live in version control
$ kitsune connect --url kitsune.internal  # connect to team gateway
$ opencode "refactor the payment module"  # phases enforced per team policy
```

### Self-hosted
```bash
$ docker compose up                       # gateway + dashboard + DB in one command
# open kitsune.internal:8080 in browser
# create workflows, generate API keys, invite team
```

The agent never "sees" Kitsune unless it tries something it shouldn't. Then it gets a clear block message:

```
🦊 [Kitsune] Edit is not available in phase: plan
   Current: plan → next: implement
   Available: read, grep, glob
   Say READY to advance.
```

---

## Session isolation

Each agent connection creates a session scoped to `(workflow_id, agent_id, run_id)`. Five hundred developers on one gateway sharing the same `bugfix.yaml` means five hundred isolated sessions at different phases — no conflict. Edits, file touches, and iteration counts are tracked per session. File conflicts remain the agent tool's problem (Git), not Kitsune's. Sessions expire after one hour of idle time.

---

## Scalability

The engine is a pure function — it receives `phase` as input, not as internal state:

```python
def check(phase: str, tool: str, workflow: dict) -> bool:
    return tool in workflow["phases"][phase]["tools"]
```

This means:

| Scale | Gateway | Session store | Engine |
|-------|---------|---------------|--------|
| **1 dev** | Local process | In-memory dict | Embedded |
| **5-500 devs** | Single server (Docker) | SQLite or Redis | Same code |
| **500-10k+ devs** | Load-balanced cluster | Redis cluster + Postgres replicas | Same code |

The engine never changes. Only where sessions live and how many gateways serve them change. At scale, the gateway is stateless — any instance can serve any agent because they all read from the same Redis. Adding servers is `docker compose up --scale gateway=5`.

---

## MCP tools exposed

The gateway exposes these tools to connected agents:

| Tool | Purpose |
|------|---------|
| `kitsune_get_state` | Current phase, allowed tools, available transitions, iteration count |
| `kitsune_transition` | Emit a trigger to advance the state machine |
| `kitsune_check_tool` | Validate a tool call before execution |
| `kitsune_load_workflow` | Activate a named workflow |
| `kitsune_list_workflows` | List available workflows |
| `kitsune_create_workflow` | Create a new workflow from YAML |
| `kitsune_pause` | Pause the current run; resume later |
| `kitsune_deactivate` | Turn off enforcement (escape hatch) |
| `kitsune_get_status` | Gateway health + active workflow info |
