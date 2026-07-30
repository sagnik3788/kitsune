<template>
  <div class="min-h-screen bg-[#0f0f13]">
    <div class="max-w-5xl mx-auto px-4 py-12">
      <!-- Header -->
      <div class="mb-8">
        <router-link to="/runs" class="text-sm text-amber-500 hover:underline inline-block mb-4">
          &larr; Back to runs
        </router-link>

        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <!-- Session ID -->
            <div class="flex items-center gap-3 mb-2">
              <span class="font-mono text-lg text-gray-200">{{ sessionId }}</span>
              <button
                @click="copyToClipboard(sessionId)"
                class="text-gray-500 hover:text-amber-500 transition-colors text-xs"
                title="Copy session ID"
              >
                Copy
              </button>
            </div>

            <!-- Stats row -->
            <div class="flex flex-wrap items-center gap-3 text-sm text-gray-500">
              <span>{{ totalCalls }} calls</span>
              <span class="text-[#2e2e35]">·</span>
              <span>{{ totalTransitions }} transitions</span>
              <span class="text-[#2e2e35]">·</span>
              <span :class="totalBlocked > 0 ? 'text-red-400' : ''">
                {{ totalBlocked }} blocked
              </span>
              <span class="text-[#2e2e35]">·</span>
              <span>Last active {{ timeAgo(lastTimestamp) }}</span>
            </div>
          </div>

          <!-- Current phase badge -->
          <span
            v-if="currentPhase"
            class="inline-flex items-center px-3 py-1 rounded-lg text-sm font-semibold border self-start"
            :class="phaseBadgeClass(currentPhase)"
          >
            {{ currentPhase }}
          </span>
        </div>
      </div>

      <!-- Error -->
      <div v-if="error" class="mb-6 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-xs text-red-400">
        {{ error }}
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-gray-500 text-sm py-8">
        Loading runs...
      </div>

      <!-- Empty -->
      <div v-else-if="runs.length === 0" class="text-center py-16">
        <p class="text-gray-400">No tool calls recorded for this session.</p>
      </div>

      <div v-else class="space-y-8">
        <!-- Phase Transition Graph -->
        <div class="bg-[#131318] border border-[#2e2e35] rounded-lg p-6">
          <h2 class="text-sm font-semibold text-gray-300 mb-6 text-center">Phase Transition Graph</h2>

          <div class="flex flex-wrap md:flex-nowrap items-start md:items-center justify-center gap-y-6 gap-x-2">
            <template v-for="(phase, index) in standardPhases" :key="phase">
              <!-- Phase node -->
              <div class="flex flex-col items-center">
                <div
                  class="px-4 py-2 rounded-full border text-sm font-semibold capitalize transition-colors"
                  :class="nodeClass(phase)"
                >
                  {{ phase }}
                </div>
                <div class="mt-2 text-xs text-gray-500 text-center">
                  <span>{{ phaseStats[phase].calls }} calls</span>
                  <span v-if="phaseStats[phase].blocked > 0" class="text-red-400">
                    · {{ phaseStats[phase].blocked }} blocked
                  </span>
                </div>
              </div>

              <!-- Arrow to next phase -->
              <div
                v-if="index < standardPhases.length - 1"
                class="flex flex-col items-center mx-1 md:mx-3"
              >
                <div
                  class="text-xl leading-none"
                  :class="arrowClass(phase, standardPhases[index + 1])"
                >
                  &rarr;
                </div>
                <div
                  v-if="getTransitionTrigger(phase, standardPhases[index + 1])"
                  class="text-xs font-mono mt-1"
                  :class="arrowClass(phase, standardPhases[index + 1])"
                >
                  {{ getTransitionTrigger(phase, standardPhases[index + 1]) }}
                </div>
              </div>
            </template>
          </div>
        </div>

        <!-- Timeline -->
        <div class="bg-[#131318] border border-[#2e2e35] rounded-lg p-6">
          <h2 class="text-sm font-semibold text-gray-300 mb-6">Run Timeline</h2>

          <div class="space-y-1">
            <div
              v-for="(run, index) in runs"
              :key="run.id || (run.session_id + ':' + run.timestamp + ':' + index)"
            >
              <!-- Phase change header -->
              <div
                v-if="index === 0 || run.phase !== runs[index - 1].phase"
                class="flex items-center gap-3 mb-3 mt-6 first:mt-0"
              >
                <span class="text-xs font-semibold text-gray-400 uppercase tracking-wider">{{ run.phase }}</span>
                <div class="flex-1 h-px bg-[#2e2e35]"></div>
              </div>

              <!-- Timeline row: dot + content -->
              <div class="flex items-start gap-3 py-2">
                <!-- Dot + line column -->
                <div class="flex flex-col items-center self-stretch">
                  <!-- Top half-line (hidden for first item) -->
                  <div
                    v-if="index > 0"
                    class="w-px flex-1 bg-[#2e2e35] min-h-[8px]"
                  ></div>
                  <div
                    v-else
                    class="w-px flex-1 min-h-[8px]"
                  ></div>
                  <!-- Dot -->
                  <div
                    class="w-2.5 h-2.5 rounded-full border-2 border-[#131318] shrink-0"
                    :class="resultDotClass(run.result)"
                  ></div>
                  <!-- Bottom half-line (hidden for last item) -->
                  <div
                    v-if="index < runs.length - 1"
                    class="w-px flex-1 bg-[#2e2e35] min-h-[8px]"
                  ></div>
                  <div
                    v-else
                    class="w-px flex-1 min-h-[8px]"
                  ></div>
                </div>

                <!-- Content -->
                <div class="flex-1 min-w-0 pb-2">
                  <div class="flex flex-wrap items-center gap-2">
                    <!-- Result badge -->
                    <span
                      class="text-xs px-1.5 py-0.5 rounded font-semibold border"
                      :class="resultBadgeClass(run.result)"
                    >
                      {{ run.result || '—' }}
                    </span>

                    <!-- Phase -->
                    <span class="text-xs text-gray-500 font-mono">{{ run.phase || '—' }}</span>

                    <!-- Arrow -->
                    <span class="text-gray-600 text-xs">&rarr;</span>

                    <!-- Tool or transition -->
                    <span
                      v-if="run.result === 'transitioned'"
                      class="text-xs font-mono font-semibold text-blue-400"
                    >
                      {{ run.trigger || '—' }}{{ run.next_phase ? ' → ' + run.next_phase : '' }}
                    </span>
                    <span
                      v-else
                      class="text-xs text-amber-500 font-mono font-semibold"
                    >
                      {{ run.tool || '—' }}
                    </span>

                    <!-- Timestamp -->
                    <span class="text-xs text-gray-600 ml-auto">
                      {{ formatDate(run.timestamp) }}
                    </span>
                  </div>

                  <!-- Reason -->
                  <p
                    v-if="run.reason"
                    class="text-xs text-gray-500 italic bg-[#0f0f13] rounded px-3 py-2 border border-[#2e2e35] mt-2"
                  >
                    {{ run.reason }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, inject, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

export default {
  setup() {
    const api = inject('api')
    const route = useRoute()

    const sessionId = ref(route.params.sessionId || '')
    const runs = ref([])
    const loading = ref(false)
    const error = ref('')

    const standardPhases = ['plan', 'implement', 'test', 'done']

    const currentPhase = computed(() => {
      if (!runs.value.length) return null
      return runs.value[runs.value.length - 1].phase
    })

    const lastTimestamp = computed(() => {
      if (!runs.value.length) return null
      return runs.value[runs.value.length - 1].timestamp
    })

    const totalCalls = computed(() => {
      return runs.value.filter(r => r.result !== 'transitioned').length
    })

    const totalTransitions = computed(() => {
      return runs.value.filter(r => r.result === 'transitioned').length
    })

    const totalBlocked = computed(() => {
      return runs.value.filter(r => r.result === 'blocked').length
    })

    const visitedPhases = computed(() => {
      return new Set(runs.value.map(r => r.phase).filter(Boolean))
    })

    const phaseStats = computed(() => {
      const stats = {}
      for (const phase of standardPhases) {
        const phaseRuns = runs.value.filter(r => r.phase === phase)
        stats[phase] = {
          calls: phaseRuns.filter(r => r.result !== 'transitioned').length,
          blocked: phaseRuns.filter(r => r.result === 'blocked').length,
        }
      }
      return stats
    })

    const transitions = computed(() => {
      const trans = []
      for (let i = 0; i < runs.value.length; i++) {
        const run = runs.value[i]
        if (run.result === 'transitioned') {
          const nextPhase = run.next_phase || (runs.value[i + 1]?.phase) || null
          if (nextPhase && run.phase !== nextPhase) {
            trans.push({ from: run.phase, to: nextPhase, trigger: run.trigger })
          }
        }
      }
      return trans
    })

    onMounted(async () => {
      if (!sessionId.value) {
        error.value = 'No session ID provided'
        return
      }
      loading.value = true
      try {
        runs.value = await api.getRuns(sessionId.value)
      } catch (e) {
        console.error('Failed to fetch runs:', e)
        error.value = e.message || 'Failed to load runs'
      }
      loading.value = false
    })

    function nodeClass(phase) {
      const isVisited = visitedPhases.value.has(phase)
      const isCurrent = currentPhase.value === phase

      if (isCurrent) {
        if (phase === 'done') return 'bg-green-500/20 text-green-400 border-green-500/30 ring-2 ring-green-500/20'
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30 ring-2 ring-amber-500/20'
      }

      if (isVisited) {
        if (phase === 'done') return 'bg-green-500/10 text-green-500 border-green-500/20'
        return 'bg-amber-500/10 text-amber-500 border-amber-500/20'
      }

      return 'bg-[#1a1a1f] text-gray-600 border-[#2e2e35]'
    }

    function arrowClass(from, to) {
      const hasTrans = transitions.value.some(t => t.from === from && t.to === to)
      return hasTrans ? 'text-amber-500' : 'text-gray-700'
    }

    function getTransitionTrigger(from, to) {
      const trans = transitions.value.find(t => t.from === from && t.to === to)
      return trans ? trans.trigger : null
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

    function resultBadgeClass(result) {
      if (result === 'allowed') return 'bg-green-500/10 text-green-500 border-green-500/20'
      if (result === 'blocked') return 'bg-red-500/10 text-red-500 border-red-500/20'
      if (result === 'transitioned') return 'bg-blue-500/10 text-blue-500 border-blue-500/20'
      return 'bg-[#2e2e35] text-gray-500 border-[#3e3e45]'
    }

    function resultDotClass(result) {
      if (result === 'allowed') return 'bg-green-500'
      if (result === 'blocked') return 'bg-red-500'
      if (result === 'transitioned') return 'bg-blue-500'
      return 'bg-gray-500'
    }

    function formatDate(d) {
      if (!d) return ''
      return new Date(d).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }

    return {
      sessionId,
      runs,
      loading,
      error,
      standardPhases,
      currentPhase,
      lastTimestamp,
      totalCalls,
      totalTransitions,
      totalBlocked,
      phaseStats,
      nodeClass,
      arrowClass,
      getTransitionTrigger,
      copyToClipboard,
      timeAgo,
      phaseBadgeClass,
      resultBadgeClass,
      resultDotClass,
      formatDate,
    }
  }
}
</script>
