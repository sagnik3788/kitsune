<template>
  <div class="min-h-screen bg-[#0f0f13]">
    <div class="max-w-5xl mx-auto px-4 py-12">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-2xl font-bold text-gray-100">Run History</h1>
          <p class="text-gray-500 text-sm mt-1">{{ runs.length }} entr{{ runs.length !== 1 ? 'ies' : 'y' }}</p>
        </div>
        <router-link to="/workflows" class="text-sm text-amber-500 hover:underline">&larr; Workflows</router-link>
      </div>

      <!-- Session ID input -->
      <div class="mb-8 bg-[#131318] border border-[#2e2e35] rounded-lg p-4">
        <label class="text-xs font-semibold text-gray-500 block mb-2">Session ID</label>
        <div class="flex gap-2">
          <input
            v-model="sessionId"
            @keyup.enter="fetchRuns"
            placeholder="paste a session_id to inspect its run history"
            class="flex-1 font-mono text-xs bg-[#0f0f13] border border-[#404049] rounded-lg px-3 py-2 text-gray-100 focus:ring-amber-500 focus:border-amber-500"
            spellcheck="false"
          />
          <button
            @click="fetchRuns"
            :disabled="loading"
            class="px-4 py-2 bg-amber-950/200 hover:bg-amber-600 text-gray-100 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
          >
            {{ loading ? 'Loading...' : 'Load' }}
          </button>
        </div>
        <p v-if="error" class="text-xs text-red-400 mt-2">{{ error }}</p>
      </div>

      <div v-if="loading" class="text-gray-500 text-sm">Loading runs...</div>

      <div v-else-if="!sessionId" class="text-center py-12">
        <p class="text-gray-500 mb-2">Enter a session ID above to view its run history.</p>
        <p class="text-gray-500 text-sm">The gateway records every tool call and transition per session.</p>
      </div>

      <div v-else-if="runs.length === 0" class="text-center py-12">
        <p class="text-gray-500 mb-2">No run history for this session.</p>
      </div>

      <div v-else class="space-y-2">
        <div
          v-for="run in runs"
          :key="run.id || (run.session_id + ':' + run.timestamp)"
          class="bg-[#131318] border border-[#2e2e35] rounded-lg px-5 py-3"
        >
          <div class="flex items-center gap-3 flex-wrap">
            <span class="text-xs px-2 py-0.5 rounded font-semibold"
              :class="{
                'bg-green-100 text-green-700': run.result === 'allowed',
                'bg-red-100 text-red-700': run.result === 'blocked',
                'bg-blue-100 text-blue-700': run.result === 'transition',
                'bg-[#2e2e35] text-gray-500': !['allowed', 'blocked', 'transition'].includes(run.result),
              }">{{ run.result || '—' }}</span>
            <span class="text-xs text-gray-500 font-mono">{{ run.phase || '—' }}</span>
            <span class="text-gray-500 text-xs">&rarr;</span>
            <span class="text-xs text-amber-500 font-mono font-semibold">{{ run.tool || '—' }}</span>
            <span class="text-xs text-gray-500 ml-auto">{{ formatDate(run.timestamp) }}</span>
          </div>
          <p v-if="run.reason" class="text-xs text-gray-500 mt-1.5 italic bg-[#1a1a1f] rounded px-3 py-1.5 border border-[#2e2e35]">
            {{ run.reason }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, inject } from 'vue'

export default {
  setup() {
    const api = inject('api')
    const sessionId = ref('')
    const runs = ref([])
    const loading = ref(false)
    const error = ref('')

    async function fetchRuns() {
      const sid = sessionId.value.trim()
      if (!sid) {
        error.value = 'Enter a session ID first.'
        return
      }
      error.value = ''
      loading.value = true
      try {
        runs.value = await api.getRuns(sid)
      } catch (e) {
        console.error('Failed to fetch runs:', e)
        error.value = e.message || 'Failed to load runs'
        runs.value = []
      }
      loading.value = false
    }

    function formatDate(d) {
      if (!d) return ''
      return new Date(d).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }

    return { sessionId, runs, loading, error, fetchRuns, formatDate }
  }
}
</script>