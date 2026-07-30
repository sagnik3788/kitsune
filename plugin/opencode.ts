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

const GATEWAY_URL = process.env.KITSUNE_GATEWAY_URL || "https://kitsune-ai.duckdns.org"
const API_KEY = process.env.KITSUNE_API_KEY
const WORKFLOW_NAME = process.env.KITSUNE_WORKFLOW

let sessionId: string | null = null
let initError: string | null = null

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

async function initSession(): Promise<boolean> {
  if (!API_KEY || !WORKFLOW_NAME) {
    initError = "KITSUNE_API_KEY or KITSUNE_WORKFLOW not set"
    console.warn(`[kitsune] ${initError}`)
    return false
  }

  const listRes = await kitsuneRequest<{
    workflows: Array<{ id: string; name?: string }>
  }>("list_workflows", undefined, "GET")

  if (!listRes) {
    initError = "Failed to list workflows"
    console.warn(`[kitsune] ${initError}`)
    return false
  }

  const workflow = listRes.workflows.find(
    (w) => w.name === WORKFLOW_NAME || w.id === WORKFLOW_NAME
  )

  if (!workflow) {
    const names = listRes.workflows.map(w => w.name || w.id).join(", ")
    initError = `Workflow '${WORKFLOW_NAME}' not found. Available: ${names}`
    console.warn(`[kitsune] ${initError}`)
    return false
  }

  const loadRes = await kitsuneRequest<{
    session_id: string
    current_phase: string
  }>("load_workflow", { workflow_id: workflow.id })

  if (!loadRes) {
    initError = "Failed to load workflow"
    console.warn(`[kitsune] ${initError}`)
    return false
  }

  sessionId = loadRes.session_id
  console.log(`[kitsune] Session ${sessionId} — phase: ${loadRes.current_phase}`)
  return true
}

export const KitsunePlugin: Plugin = async ({ client }) => {
  return {
    tool: {
      kitsune_transition: {
        description: "Transition to the next phase in the Kitsune workflow. Call this when you want to advance: READY (plan→implement), DONE (implement→test), PASS (test→done), or FAIL (test→implement or implement→plan).",
        args: {
          trigger: z.enum(["READY", "DONE", "PASS", "FAIL"]).describe("The transition trigger word")
        },
        execute: async (args, context) => {
          if (!sessionId) {
            return "[kitsune] Not initialized"
          }

          const res = await kitsuneRequest<KitsuneTransitionResponse>("transition", {
            session_id: sessionId,
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
        execute: async () => {
          if (!sessionId) {
            return "[kitsune] Not initialized"
          }

          const state = await kitsuneRequest<KitsuneState>("get_state", {
            session_id: sessionId,
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
      if (!sessionId && !initError) {
        await initSession()
      }
      if (!sessionId) {
        console.warn(`[kitsune] Not initialized (${initError}), allowing tool`)
        return
      }

      // Skip check for plugin's own tools
      if (input.tool === "kitsune_transition" || input.tool === "kitsune_get_state") {
        console.log(`[kitsune] Allowing internal tool: ${input.tool}`)
        return
      }

      const result = await kitsuneRequest<KitsuneCheckResponse>("check", {
        session_id: sessionId,
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
