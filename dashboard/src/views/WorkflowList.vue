<template>
  <div class="min-h-screen bg-[#0f0f13]">
    <div class="max-w-5xl mx-auto px-4 py-12">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-2xl font-bold text-gray-100">Workflows</h1>
          <p class="text-gray-500 text-sm mt-1">
            {{ workflows.length }} workflow{{ workflows.length !== 1 ? 's' : '' }}
          </p>
        </div>
        <div class="flex gap-3">
          <button
            @click="showTemplates = !showTemplates"
            class="px-4 py-2 border border-brand-300 text-amber-500 hover:bg-amber-950/30 rounded-lg text-sm font-medium transition-colors"
          >
            {{ showTemplates ? 'Hide Templates' : 'From Template' }}
          </button>
          <button
            @click="showYamlImport = !showYamlImport"
            class="px-4 py-2 border border-[#404049] text-gray-500 hover:bg-[#131318] rounded-lg text-sm font-medium transition-colors"
          >
            From YAML
          </button>
          <button
            @click="$router.push('/workflows/new')"
            class="px-4 py-2 bg-amber-950/200 hover:bg-amber-600 text-gray-100 rounded-lg text-sm font-semibold transition-colors"
          >
            New Workflow
          </button>
        </div>
      </div>

      <!-- Templates -->
      <div v-if="showTemplates" class="mb-8 grid md:grid-cols-2 gap-4">
        <div
          v-for="t in templates"
          :key="t.name"
          class="bg-amber-950/30 border border-amber-800/50 rounded-lg p-4 cursor-pointer hover:border-brand-400 transition-colors"
          @click="forkTemplate(t)"
        >
          <h3 class="font-semibold text-brand-900 text-sm">{{ t.name }}</h3>
          <p class="text-gray-500 text-xs mt-1">{{ t.description }}</p>
          <div class="flex gap-1 mt-2 flex-wrap">
              <span
                v-for="phase in Object.keys(t.definition.states).filter(s => t.definition.states[s].type !== 'final').slice(0, 4)"
                :key="phase"
                class="text-xs bg-amber-950/20 text-amber-500 px-2 py-0.5 rounded"
              >{{ phase }}</span>
              <span
                v-if="Object.keys(t.definition.states).filter(s => t.definition.states[s].type !== 'final').length > 4"
                class="text-xs bg-amber-950/20 text-amber-500 px-2 py-0.5 rounded cursor-default"
              >& {{ Object.keys(t.definition.states).filter(s => t.definition.states[s].type !== 'final').length - 4 }} more...</span>
          </div>
        </div>
      </div>

      <!-- YAML Import -->
      <div v-if="showYamlImport" class="mb-8 bg-[#131318] border border-[#2e2e35] rounded-lg p-4">
        <label class="text-xs font-semibold text-gray-500 block mb-2">Paste workflow YAML:</label>
        <textarea
          v-model="yamlImportText"
          rows="6"
          class="w-full font-mono text-xs bg-[#0f0f13] border border-[#404049] rounded-lg p-3 text-gray-100 resize-none focus:ring-amber-500 focus:border-amber-500 mb-3"
          placeholder='id: my-workflow&#10;initial: start&#10;phases:&#10;  plan:&#10;    tools: [Read, Grep, Glob]&#10;    on:&#10;      READY: implement'
          spellcheck="false"
        ></textarea>
        <div class="flex gap-2">
          <button @click="importFromYaml" class="px-4 py-2 bg-amber-950/200 hover:bg-amber-600 text-gray-100 rounded-lg text-sm font-semibold transition-colors">
            Import
          </button>
          <span v-if="yamlImportError" class="text-xs text-red-400 self-center">{{ yamlImportError }}</span>
        </div>
      </div>

      <div v-if="loading" class="text-gray-500 text-sm">Loading workflows...</div>

      <div v-else-if="workflows.length === 0" class="text-center py-12">
        <p class="text-gray-500 mb-4">No workflows yet. Create one or start from a template.</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="wf in workflows"
          :key="wf.id"
          class="bg-[#131318] border border-[#2e2e35] rounded-lg px-5 py-4 hover:border-brand-300 transition-colors"
        >
          <div class="flex items-center justify-between">
            <router-link :to="'/workflows/' + wf.id" class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="font-semibold text-gray-100">{{ wf.name }}</span>
                <span v-if="wf.active" class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">active</span>
                <span v-if="wf.definition?.meta?.capture_output" class="text-xs bg-amber-100 text-amber-600 px-2 py-0.5 rounded">logging</span>
                <span v-if="wf.template_source" class="text-xs text-gray-500">from {{ wf.template_source }}</span>
              </div>
              <div class="flex gap-1 mt-1 flex-wrap">
                <span
                  v-for="phase in getStateNames(wf.definition).slice(0, 4)"
                  :key="phase"
                  class="text-xs bg-[#2e2e35] text-gray-500 px-2 py-0.5 rounded"
                >{{ phase }}</span>
                <span
                  v-if="getStateNames(wf.definition).length > 4"
                  class="text-xs bg-[#2e2e35] text-gray-500 px-2 py-0.5 rounded cursor-default"
                >& {{ getStateNames(wf.definition).length - 4 }} more...</span>
              </div>
            </router-link>
            <div class="flex items-center gap-3 shrink-0 ml-4">
              <span v-if="wf.updated" class="text-xs text-gray-500">{{ formatDate(wf.updated) }}</span>
              <button
                @click.stop="deleteWorkflow(wf)"
                class="text-xs text-red-400/60 hover:text-red-400 transition-colors"
              >Delete</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, inject, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { load as yamlLoad } from 'js-yaml'

export default {
  setup() {
    const api = inject('api')
    const router = useRouter()
    const workflows = ref([])
    const templates = ref([])
    const loading = ref(true)
    const showTemplates = ref(false)
    const showYamlImport = ref(false)
    const yamlImportText = ref('')
    const yamlImportError = ref('')

    async function fetchWorkflows() {
      loading.value = true
      try {
        const records = await api.getWorkflows()
        workflows.value = records
      } catch (e) {
        console.error('Failed to fetch workflows:', e)
      }
      loading.value = false
    }

    async function fetchTemplates() {
      // Built-in Kitsune templates — hardcoded, not from external store
      templates.value = [
        {
          name: 'Bug Fix Loop',
          description: 'Plan → Implement → Test → Review. Classic debugging with rollback guard.',
          definition: {
            id: 'bugfix',
            initial: 'plan',
            states: {
              plan: {
                allowed_tools: ['Read', 'Grep', 'Glob'],
                instructions: 'Understand the bug before writing code. Search logs, traces, and related files.',
                max_iterations: 8,
                max_files_per_state: 5,
                on: { READY: 'implement', GIVE_UP: 'escalate', FAIL: 'failed' }
              },
              implement: {
                allowed_tools: ['Read', 'Edit', 'Write'],
                instructions: 'Make the minimal surgical fix. One bug, one change.',
                max_iterations: 10,
                max_edit_lines: 20,
                max_files_per_state: 3,
                on: { DONE: 'test', NEED_REVIEW: 'review', FAIL: 'failed' }
              },
              test: {
                allowed_tools: ['Read', 'Bash'],
                instructions: 'Run relevant tests. If tests pass, move to review. If they fail, go back to implement.',
                max_iterations: 6,
                allowed_commands: ['pytest', 'cargo test', 'npm test', 'go test'],
                on: { PASS: 'review', FAIL: 'implement', TIMEOUT: 'escalate' }
              },
              review: {
                allowed_tools: ['Read', 'Grep'],
                instructions: 'Review the diff for correctness, edge cases, and regressions.',
                max_iterations: 5,
                on: { APPROVE: 'done', REQUEST_CHANGES: 'implement', FAIL: 'failed' }
              },
              escalate: {
                allowed_tools: ['Read', 'Write'],
                instructions: 'Document what was attempted and why it failed. Hand off to human.',
                max_iterations: 3,
                on: { DONE: 'failed' }
              },
              done: { type: 'final' },
              failed: { type: 'final' }
            },
            guards: {}
          }
        },
        {
          name: 'Feature Development',
          description: 'Spec → Design → Implement → Test → Review → Deploy. Full product flow.',
          definition: {
            id: 'feature',
            initial: 'spec',
            states: {
              spec: {
                allowed_tools: ['Read', 'Glob', 'Grep', 'Agent'],
                instructions: 'Gather requirements from issues, PRs, and docs. Write a clear spec before coding.',
                max_iterations: 8,
                max_files_per_state: 8,
                on: { READY: 'design', BLOCKED: 'blocked', FAIL: 'abandoned' }
              },
              design: {
                allowed_tools: ['Read', 'Write', 'Edit'],
                instructions: 'Design the architecture. Write ADR or design doc. Get structure right before implementation.',
                max_iterations: 6,
                max_files_per_state: 4,
                on: { APPROVE: 'implement', NEED_CLARITY: 'spec', FAIL: 'abandoned' }
              },
              implement: {
                allowed_tools: ['Read', 'Edit', 'Write', 'Bash'],
                instructions: 'Build the feature. Follow the design doc. Keep PR size reasonable.',
                max_iterations: 15,
                max_edit_lines: 40,
                max_files_per_state: 8,
                on: { DONE: 'test', STUCK: 'design', FAIL: 'abandoned' }
              },
              test: {
                allowed_tools: ['Read', 'Bash', 'Edit'],
                instructions: 'Write and run tests. Aim for coverage of new paths and edge cases.',
                max_iterations: 8,
                allowed_commands: ['pytest', 'cargo test', 'npm test', 'go test', 'jest'],
                on: { PASS: 'review', FAIL: 'implement', FLAKY: 'investigate' }
              },
              investigate: {
                allowed_tools: ['Read', 'Bash', 'Grep'],
                instructions: 'Debug flaky tests. Check for race conditions, timing issues, or environment deps.',
                max_iterations: 5,
                on: { FIXED: 'test', NEED_HELP: 'blocked', FAIL: 'abandoned' }
              },
              review: {
                allowed_tools: ['Read', 'Edit'],
                instructions: 'Self-review the PR. Check for lint, types, docs, and leftover debug code.',
                max_iterations: 5,
                on: { APPROVE: 'deploy', REQUEST_CHANGES: 'implement', FAIL: 'abandoned' }
              },
              deploy: {
                allowed_tools: ['Bash', 'Read'],
                instructions: 'Deploy to staging or production per playbook. Monitor metrics post-deploy.',
                max_iterations: 4,
                allowed_commands: ['docker compose up', 'kubectl apply', 'npm run deploy'],
                on: { SUCCESS: 'done', ROLLBACK: 'implement', FAIL: 'blocked' }
              },
              blocked: {
                allowed_tools: ['Read', 'Write'],
                instructions: 'Document blockers and hand off to human for decision.',
                max_iterations: 3,
                on: { DONE: 'abandoned' }
              },
              done: { type: 'final' },
              abandoned: { type: 'final' }
            },
            guards: {}
          }
        },
        {
          name: 'Security Audit',
          description: 'Recon → Analyze → Exploit → Fix → Verify → Report. Penetration testing flow.',
          definition: {
            id: 'security-audit',
            initial: 'recon',
            states: {
              recon: {
                allowed_tools: ['Read', 'Grep', 'Glob', 'Bash'],
                instructions: 'Map attack surface. List endpoints, deps, secrets, and config files.',
                max_iterations: 8,
                allowed_commands: ['find', 'grep', 'npm audit', 'cargo audit'],
                on: { SCOPE_CLEAR: 'analyze', NOTHING_FOUND: 'done', FAIL: 'failed' }
              },
              analyze: {
                allowed_tools: ['Read', 'Grep', 'Bash', 'Agent'],
                instructions: 'Analyze code for injection, auth bypass, serialization, and crypto issues.',
                max_iterations: 10,
                max_files_per_state: 10,
                on: { VULN_FOUND: 'exploit', CLEAN: 'report', NEED_TOOL: 'recon', FAIL: 'failed' }
              },
              exploit: {
                allowed_tools: ['Bash', 'Read', 'Write'],
                instructions: 'Build a proof-of-concept exploit. Do NOT cause damage. Document reproduction steps.',
                max_iterations: 6,
                allowed_commands: ['python3', 'node', 'curl'],
                blocked_env: ['PROD_DB_URL', 'STRIPE_KEY', 'AWS_SECRET'],
                on: { CONFIRMED: 'fix', FALSE_POSITIVE: 'analyze', FAIL: 'failed' }
              },
              fix: {
                allowed_tools: ['Read', 'Edit', 'Write'],
                instructions: 'Patch the vulnerability. Add regression tests. Update docs if public API changes.',
                max_iterations: 10,
                max_edit_lines: 30,
                max_files_per_state: 6,
                on: { DONE: 'verify', NEED_REVIEW: 'report', FAIL: 'failed' }
              },
              verify: {
                allowed_tools: ['Bash', 'Read', 'Grep'],
                instructions: 'Re-run exploit PoC against patched code. Verify fix holds. Run security tests.',
                max_iterations: 5,
                allowed_commands: ['pytest', 'npm test', 'cargo test'],
                on: { PASS: 'report', FAIL: 'fix', NEED_DEEPER: 'analyze' }
              },
              report: {
                allowed_tools: ['Read', 'Write'],
                instructions: 'Write security report: severity, reproduction, fix, verification. Hand off to security team.',
                max_iterations: 4,
                on: { DONE: 'done', NEED_FIX: 'fix', FAIL: 'failed' }
              },
              done: { type: 'final' },
              failed: { type: 'final' }
            },
            guards: {}
          }
        },
        {
          name: 'Refactor & Modernize',
          description: 'Audit → Plan → Migrate → Test → Benchmark. Large-scale codebase migration.',
          definition: {
            id: 'refactor',
            initial: 'audit',
            states: {
              audit: {
                allowed_tools: ['Read', 'Glob', 'Grep', 'Bash'],
                instructions: 'Map all files using deprecated patterns. Measure current coverage and build times.',
                max_iterations: 8,
                allowed_commands: ['find', 'grep', 'wc -l', 'npm run build', 'cargo build'],
                on: { SCOPE_KNOWN: 'plan', TOO_BIG: 'slice', FAIL: 'failed' }
              },
              slice: {
                allowed_tools: ['Read', 'Write', 'Edit'],
                instructions: 'Break the refactor into independent chunks. Write a migration roadmap.',
                max_iterations: 5,
                max_files_per_state: 4,
                on: { CHUNKS_READY: 'plan', FAIL: 'failed' }
              },
              plan: {
                allowed_tools: ['Read', 'Write', 'Edit'],
                instructions: 'Write the migration plan per chunk. Define rollback strategy and success criteria.',
                max_iterations: 6,
                max_files_per_state: 4,
                on: { APPROVE: 'migrate', NEED_CLARITY: 'audit', FAIL: 'failed' }
              },
              migrate: {
                allowed_tools: ['Read', 'Edit', 'Write', 'Bash'],
                instructions: 'Execute one chunk at a time. Keep commits atomic. Run lint after each chunk.',
                max_iterations: 15,
                max_edit_lines: 50,
                max_files_per_state: 10,
                on: { CHUNK_DONE: 'test', ALL_DONE: 'benchmark', FAIL: 'rollback' }
              },
              rollback: {
                allowed_tools: ['Bash', 'Read'],
                instructions: 'Revert to last known good state. Fix the issue that caused failure, then retry.',
                max_iterations: 4,
                allowed_commands: ['git reset', 'git checkout', 'git stash'],
                on: { FIXED: 'migrate', GIVE_UP: 'failed', FAIL: 'failed' }
              },
              test: {
                allowed_tools: ['Read', 'Bash'],
                instructions: 'Run full test suite on migrated chunk. Check for regressions.',
                max_iterations: 6,
                allowed_commands: ['pytest', 'cargo test', 'npm test', 'go test'],
                on: { PASS: 'migrate', FAIL: 'rollback' }
              },
              benchmark: {
                allowed_tools: ['Bash', 'Read', 'Write'],
                instructions: 'Measure build time, bundle size, and runtime performance before vs after. Document wins.',
                max_iterations: 4,
                allowed_commands: ['npm run build', 'cargo bench', 'hyperfine'],
                on: { IMPROVED: 'done', REGRESSED: 'migrate', FAIL: 'failed' }
              },
              done: { type: 'final' },
              failed: { type: 'final' }
            },
            guards: {}
          }
        }
      ]
    }

    async function forkTemplate(template) {
      try {
        const { id } = await api.createWorkflow({
          name: template.name,
          definition: template.definition,
          template_source: template.name,
          active: false
        })
        router.push('/workflows/' + id)
      } catch (e) {
        // Retry with a unique suffix on name-collision-style failures
        try {
          const { id } = await api.createWorkflow({
            name: template.name + '-' + Date.now().toString(36).slice(-4),
            definition: template.definition,
            template_source: template.name,
            active: false
          })
          router.push('/workflows/' + id)
        } catch (e2) {
          console.error('Failed to fork template:', e2)
        }
      }
    }

    async function deleteWorkflow(wf) {
      try {
        await api.deleteWorkflow(wf.id)
        workflows.value = workflows.value.filter(w => w.id !== wf.id)
      } catch (e) {
        console.error('Failed to delete workflow:', e)
      }
    }

    async function importFromYaml() {
      yamlImportError.value = ''
      try {
        const def = yamlLoad(yamlImportText.value)
        if (!def.states || !def.initial) throw new Error('Missing phases or initial')
        const name = def.id || 'imported-' + Date.now().toString(36).slice(-4)
        const { id } = await api.createWorkflow({
          name,
          definition: def,
          active: false
        })
        router.push('/workflows/' + id)
      } catch (e) {
        yamlImportError.value = e.message || 'Invalid YAML'
      }
    }

    function getStateNames(def) {
      if (!def?.states) return []
      return Object.keys(def.states).filter(s => def.states[s]?.type !== 'final')
    }

    function formatDate(d) {
      if (!d) return ''
      return new Date(d).toLocaleDateString()
    }

    onMounted(() => {
      fetchWorkflows()
      fetchTemplates()
    })

    return { workflows, templates, loading, showTemplates, showYamlImport, yamlImportText, yamlImportError, forkTemplate, importFromYaml, deleteWorkflow, getStateNames, formatDate }
  }
}
</script>
