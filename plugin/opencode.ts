import type { Plugin } from "@opencode-ai/plugin"
import { z } from "zod"

interface KitsuneState {
  current_phase: string
  available_tools: string[]
  available_transitions: string[]
  turn_count: number
  counters: Record<string, number>
}

interface KitsuneCheckResponse {
  allowed: boolean
  reason?: string
  current_phase: string
  next_phase?: string
  available_tools: string[]
  available_transitions: string[]
  message: string
}

interface KitsuneTransitionResponse {
  success: boolean
  previous_phase: string
  new_phase?: string
  message: string
}

interface SessionState {
  kitsuneSessionId: string | null
  initError: string | null
  initPromise?: Promise<void>
}

const GATEWAY_URL = process.env.KITSUNE_GATEWAY_URL || "https://kitsune-fofq.onrender.com"
const API_KEY = process.env.KITSUNE_API_KEY
const WORKFLOW_NAME = process.env.KITSUNE_WORKFLOW

const sessions = new Map<string, SessionState>()

function getSessionState(openCodeSessionId: string): SessionState {
  let state = sessions.get(openCodeSessionId)
  if (!state) {
    state = { kitsuneSessionId: null, initError: null }
    sessions.set(openCodeSessionId, state)
  }
  return state
}

async function kitsuneRequest<T>(
  endpoint: string,
  body?: Record<string, unknown>,
  method: string = "POST"
): Promise<T | null> {
  try {
    const url = `${GATEWAY_URL}/mcp/${endpoint}`
    const opts: RequestInit = {
      method,
      headers: {
        "api-key": API_KEY || "",
      },
    }
    if (body) {
      opts.headers = {
        ...opts.headers,
        "Content-Type": "application/json",
      }
      opts.body = JSON.stringify(body)
    }
    const resp = await fetch(url, opts)
    if (!resp.ok) {
      const text = await resp.text()
      console.error(`[kitsune] ${endpoint} failed: ${resp.status} - ${text}`)
      return null
    }
    return (await resp.json()) as T
  } catch (e: any) {
    console.error(`[kitsune] ${endpoint} error:`, e.message || e)
    return null
  }
}

async function initSession(state: SessionState): Promise<void> {
  if (!API_KEY || !WORKFLOW_NAME) {
    state.initError = "KITSUNE_API_KEY or KITSUNE_WORKFLOW not set"
    console.warn(`[kitsune] ${state.initError}`)
    return
  }

  const listRes = await kitsuneRequest<{
    workflows: Array<{ id: string; name?: string; description?: string }>
  }>("list_workflows", undefined, "GET")

  if (!listRes) {
    state.initError = "Failed to list workflows"
    console.warn(`[kitsune] ${state.initError}`)
    return
  }

  const workflow = listRes.workflows.find(
    (w) => w.name === WORKFLOW_NAME || w.id === WORKFLOW_NAME || w.description === WORKFLOW_NAME
  )

  if (!workflow) {
    const names = listRes.workflows.map(w => w.description || w.name || w.id).join(", ")
    state.initError = `Workflow '${WORKFLOW_NAME}' not found. Available: ${names}`
    console.warn(`[kitsune] ${state.initError}`)
    return
  }

  const loadRes = await kitsuneRequest<{
    session_id: string
    current_phase: string
  }>("load_workflow", { workflow_id: workflow.id })

  if (!loadRes) {
    state.initError = "Failed to load workflow"
    console.warn(`[kitsune] ${state.initError}`)
    return
  }

  state.kitsuneSessionId = loadRes.session_id
  console.log(`[kitsune] Session ${state.kitsuneSessionId} — phase: ${loadRes.current_phase}`)
}

async function ensureSession(openCodeSessionId: string): Promise<SessionState> {
  const state = getSessionState(openCodeSessionId)
  if (!state.kitsuneSessionId && !state.initError) {
    state.initPromise ??= initSession(state).finally(() => {
      state.initPromise = undefined
    })
    await state.initPromise
  }
  return state
}

export const KitsunePlugin: Plugin = async ({ client }) => {
  return {
    event: async ({ event }) => {
      if (event.type === "session.deleted") {
        // Release the Kitsune state when OpenCode removes the conversation.
        sessions.delete(event.properties.info.id)
      }
    },

    tool: {
      kitsune_transition: {
        description: "Transition to the next phase in the Kitsune workflow. Call this when you want to advance: READY (plan→implement), DONE (implement→test), PASS (test→done), or FAIL (test→implement or implement→plan).",
        args: {
          trigger: z.enum(["READY", "DONE", "PASS", "FAIL"]).describe("The transition trigger word")
        },
        execute: async (args, context) => {
          const state = await ensureSession(context.sessionID)
          if (!state.kitsuneSessionId) {
            return "[kitsune] Not initialized"
          }

          const res = await kitsuneRequest<KitsuneTransitionResponse>("transition", {
            session_id: state.kitsuneSessionId,
            trigger: args.trigger,
          })

          if (res?.success) {
            return `[kitsune] ${res.message}\nCurrent phase: ${res.new_phase}`
          } else {
            return `[kitsune] Transition failed: ${res?.message || "Invalid trigger"}`
          }
        }
      },

      kitsune_get_state: {
        description: "Get current Kitsune workflow state: phase, allowed tools, available transitions.",
        args: {},
        execute: async (_args, context) => {
          const sessionState = await ensureSession(context.sessionID)
          if (!sessionState.kitsuneSessionId) {
            return "[kitsune] Not initialized"
          }

          const state = await kitsuneRequest<KitsuneState>("get_state", {
            session_id: sessionState.kitsuneSessionId,
          })

          if (!state) {
            return "[kitsune] Failed to get state"
          }

          return `[kitsune] Current phase: ${state.current_phase}\nAllowed tools: ${state.available_tools.join(", ")}\nTransitions: ${state.available_transitions.join(", ") || "none"}\nTurn count: ${state.turn_count}`
        }
      }
    },

    "tool.execute.before": async (
      input: { tool: string; sessionID: string; callID: string },
      output: { args: any }
    ) => {
      // Keep a separate Kitsune session for every OpenCode conversation.
      const state = await ensureSession(input.sessionID)
      if (!state.kitsuneSessionId) {
        console.warn(`[kitsune] Not initialized (${state.initError}), allowing tool`)
        return
      }

      // Skip check for plugin's own tools
      if (input.tool === "kitsune_transition" || input.tool === "kitsune_get_state") {
        console.log(`[kitsune] Allowing internal tool: ${input.tool}`)
        return
      }

      const result = await kitsuneRequest<KitsuneCheckResponse>("check", {
        session_id: state.kitsuneSessionId,
        tool: input.tool.toLowerCase(),
        args: output.args,
      })

      if (!result) {
        console.warn("[kitsune] Check failed, allowing tool")
        return
      }

      if (!result.allowed) {
        throw new Error(
          `[kitsune] BLOCKED: ${result.reason || "Tool not available"}\n${result.message}`
        )
      }

      console.log(`[kitsune] ${result.message}`)
    },
  }
}

export default KitsunePlugin
