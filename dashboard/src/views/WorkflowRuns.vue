<template>
  <div class="min-h-screen bg-[#0f0f13]">
    <div class="max-w-6xl mx-auto px-4 py-12">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-2xl font-bold text-gray-100">Run History</h1>
          <p class="text-gray-500 text-sm mt-1">
            {{ sessions.length }} session{{ sessions.length !== 1 ? 's' : '' }}
          </p>
        </div>
        <router-link to="/workflows" class="text-sm text-amber-500 hover:underline">
          &larr; Workflows
        </router-link>
      </div>

      <!-- Search -->
      <div class="mb-4">
        <input
          v-model="searchQuery"
          placeholder="Search sessions..."
          class="w-full bg-[#131318] border border-[#2e2e35] rounded-lg px-4 py-2.5 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-colors"
        />
      </div>

      <!-- Error -->
      <div v-if="error" class="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-xs text-red-400">
        {{ error }}
      </div>

      <!-- Loading sessions -->
      <div v-if="loadingSessions" class="text-gray-500 text-sm py-8">
        Loading recent sessions...
      </div>

      <!-- No sessions at all -->
      <div v-else-if="sessions.length === 0" class="text-center py-16">
        <p class="text-gray-400 mb-2">No run history yet.</p>
        <p class="text-gray-500 text-sm">Start using the plugin and your sessions will appear here.</p>
      </div>

      <!-- No search results -->
      <div v-else-if="filteredSessions.length === 0" class="text-center py-16">
        <p class="text-gray-400">No sessions match your search.</p>
      </div>

      <!-- Session cards grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="session in filteredSessions"
          :key="session.session_id"
          class="bg-[#131318] border border-[#2e2e35] rounded-lg overflow-hidden cursor-pointer transition-colors hover:bg-[#1a1a1f] hover:border-[#3e3e45] group"
          @click="$router.push('/runs/' + session.session_id)"
        >
          <!-- Card body -->
          <div class="p-4">
            <!-- Session ID with copy -->
            <div class="flex items-center justify-between mb-3">
              <span class="font-mono text-sm text-gray-300">
                {{ truncateSessionId(session.session_id) }}
              </span>
              <div class="flex items-center gap-2">
                <button
                  @click.stop="copyToClipboard(session.session_id)"
                  class="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-amber-500 transition-opacity text-xs"
                  title="Copy full session ID"
                >
                  Copy
                </button>
                <span class="text-gray-600 text-sm group-hover:text-amber-500 transition-colors">&rarr;</span>
              </div>
            </div>

            <!-- Last active -->
            <p class="text-xs text-gray-500 mb-3">
              Last active: {{ timeAgo(session.last_active) }}
            </p>

            <!-- Stats -->
            <div class="flex items-center gap-2 text-xs text-gray-500 mb-3">
              <span>{{ session.total_calls }} calls</span>
              <span class="text-[#2e2e35]">·</span>
              <span>{{ session.transitions }} transitions</span>
              <span class="text-[#2e2e35]">·</span>
              <span :class="session.blocked_calls > 0 ? 'text-red-400' : ''">
                {{ session.blocked_calls }} blocked
              </span>
            </div>

            <!-- Phase badge -->
            <span
              class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border"
              :class="phaseBadgeClass(session.latest_phase)"
            >
              {{ session.latest_phase || 'unknown' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, inject, computed, onMounted } from 'vue'

export default {
  setup() {
    const api = inject('api')

    const sessions = ref([])
    const loadingSessions = ref(false)
    const error = ref('')
    const searchQuery = ref('')

    const filteredSessions = computed(() => {
      if (!searchQuery.value.trim()) return sessions.value
      const q = searchQuery.value.toLowerCase()
      return sessions.value.filter(s => s.session_id.toLowerCase().includes(q))
    })

    onMounted(async () => {
      loadingSessions.value = true
      try {
        sessions.value = await api.getSessions(20)
      } catch (e) {
        console.error('Failed to fetch sessions:', e)
        error.value = e.message || 'Failed to load sessions'
      }
      loadingSessions.value = false
    })

    function truncateSessionId(id) {
      if (!id) return '—'
      return id.length > 8 ? id.slice(0, 8) + '...' : id
    }

    function copyToClipboard(text) {
      navigator.clipboard.writeText(text).catch(err => console.error('Copy failed:', err))
    }

    function timeAgo(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      const now = new Date()
      const seconds = Math.floor((now - date) / 1000)

      if (seconds < 60) return 'just now'
      const minutes = Math.floor(seconds / 60)
      if (minutes < 60) return `${minutes} min${minutes !== 1 ? 's' : ''} ago`
      const hours = Math.floor(minutes / 60)
      if (hours < 24) return `${hours} hour${hours !== 1 ? 's' : ''} ago`
      const days = Math.floor(hours / 24)
      if (days === 1) return 'yesterday'
      if (days < 7) return `${days} days ago`
      if (days < 30) return `${Math.floor(days / 7)} weeks ago`
      if (days < 365) return `${Math.floor(days / 30)} months ago`
      return `${Math.floor(days / 365)} years ago`
    }

    function phaseBadgeClass(phase) {
      const activePhases = ['plan', 'implement', 'test']
      if (activePhases.includes(phase)) return 'bg-amber-500/10 text-amber-500 border-amber-500/20'
      if (phase === 'done') return 'bg-green-500/10 text-green-500 border-green-500/20'
      return 'bg-[#2e2e35] text-gray-500 border-[#3e3e45]'
    }

    function formatDate(d) {
      if (!d) return ''
      return new Date(d).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }

    return {
      sessions,
      loadingSessions,
      error,
      searchQuery,
      filteredSessions,
      truncateSessionId,
      copyToClipboard,
      timeAgo,
      phaseBadgeClass,
      formatDate,
    }
  }
}
</script>
