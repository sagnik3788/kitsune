// API client for the Kitsune gateway.
// All endpoints require Clerk session token in Authorization header.

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

function getAuthToken() {
  const clerk = window.__clerk
  if (!clerk || !clerk.session) {
    throw new Error('Not authenticated. Please sign in.')
  }
  return clerk.session.getToken()
}

// Wait for Clerk session to be fully ready before making API calls
export async function waitForSession(maxWaitMs = 10000) {
  const clerk = window.__clerk
  if (!clerk) {
    throw new Error('Clerk not initialized')
  }
  const start = Date.now()
  while (!clerk.session) {
    if (Date.now() - start > maxWaitMs) {
      throw new Error('Clerk session timeout — please sign in again')
    }
    await new Promise(r => setTimeout(r, 100))
  }
  // Ensure token is fetchable
  const token = await clerk.session.getToken()
  if (!token) {
    throw new Error('Clerk session token unavailable')
  }
  return true
}

async function request(method, path, body) {
  const token = await getAuthToken()
  const headers = { 'Authorization': `Bearer ${token}` }
  let payload
  if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
    payload = JSON.stringify(body)
  }
  const res = await fetch(API_BASE + path, { method, headers, body: payload })
  if (!res.ok) {
    let detail = ''
    let body = null
    try {
      body = await res.json()
      detail = body?.detail || JSON.stringify(body, null, 2)
    } catch (_) {}
    console.error('API error response body:', body)
    throw new Error(`API ${method} ${path} failed: ${res.status} ${res.statusText}${detail ? ' — ' + detail : ''}`)
  }
  const text = await res.text()
  return text ? JSON.parse(text) : null
}

// --- Bidirectional translation between dashboard internal format and gateway Workflow schema ---
function toGateway(internal) {
  const def = internal.definition || internal
  const id = internal.id || def.id || ''
  const name = internal.name || def.description || id

  const phases = {}
  const states = def.states || def.phases || {}
  for (const [phaseName, phase] of Object.entries(states)) {
    const normalized = {
      tools: phase.allowed_tools || phase.tools || [],
      commands: phase.allowed_commands || phase.commands || null,
      on: phase.on || {},
      type: phase.type || null,
      blocked_env: phase.blocked_env || null,
      guards: [],
      tool_guards: {},
      requires_approval: false,
      env_overrides: null,
    }
    if (phase.max_iterations != null) {
      normalized.guards.push({ field: 'turn_count', op: 'lt', value: phase.max_iterations })
    }
    if (phase.max_files_per_state != null) {
      normalized.guards.push({ field: 'files_touched_count', op: 'lt', value: phase.max_files_per_state })
    }
    if (phase.max_edit_lines != null) {
      normalized.tool_guards.edit = [{ field: 'edit_count', op: 'lt', value: phase.max_edit_lines }]
    }
    phases[phaseName] = normalized
  }

  return { id, description: name, initial: def.initial || '', phases }
}

function fromGateway(gateway) {
  const states = {}
  for (const [phaseName, phase] of Object.entries(gateway.phases || {})) {
    const denormalized = {
      allowed_tools: phase.tools || [],
      allowed_commands: phase.commands || null,
      on: phase.on || {},
      type: phase.type || null,
      blocked_env: phase.blocked_env || null,
      guards: {},
    }
    for (const guard of phase.guards || []) {
      if (guard.field === 'turn_count' && guard.op === 'lt') {
        denormalized.max_iterations = guard.value
      }
      if (guard.field === 'files_touched_count' && guard.op === 'lt') {
        denormalized.max_files_per_state = guard.value
      }
    }
    for (const [tool, guards] of Object.entries(phase.tool_guards || {})) {
      for (const guard of guards) {
        if (guard.field === 'edit_count' && guard.op === 'lt') {
          denormalized.max_edit_lines = guard.value
        }
      }
    }
    states[phaseName] = denormalized
  }

  return {
    id: gateway.id,
    name: gateway.description || gateway.id,
    definition: {
      id: gateway.id,
      initial: gateway.initial,
      states,
      guards: {},
      meta: {},
    },
    active: false,
    template_source: null,
    updated: null,
  }
}

const api = {
  async getWorkflows() {
    const data = await request('GET', '/workflows')
    const list = data.workflows || []
    return list.map(fromGateway)
  },
  async getWorkflow(id) {
    const data = await request('GET', '/workflows/' + encodeURIComponent(id))
    return fromGateway(data)
  },
  async createWorkflow(data) {
    return await request('POST', '/workflows', toGateway(data))
  },
  async updateWorkflow(id, data) {
    return await request('PUT', '/workflows/' + encodeURIComponent(id), toGateway(data))
  },
  async deleteWorkflow(id) {
    return await request('DELETE', '/workflows/' + encodeURIComponent(id))
  },
  async getRuns(sessionId) {
    const data = await request('GET', '/runs?session_id=' + encodeURIComponent(sessionId))
    return data.runs || []
  },
  async getSessions(limit = 20) {
    const data = await request('GET', '/sessions?limit=' + encodeURIComponent(limit))
    return data.sessions || []
  },
  async getKeys() {
    const data = await request('GET', '/keys')
    return data.keys || []
  },
  async createKey() {
    return await request('POST', '/keys')
  },
  async deleteKey(id) {
    return await request('DELETE', '/keys/' + encodeURIComponent(id))
  },
}

export default api
