<template>
  <div class="max-w-4xl mx-auto px-6 py-12">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-100 mb-2">OpenCode Plugin</h1>
      <p class="text-gray-400">Install the Kitsune plugin to enforce workflow phases in your OpenCode agent.</p>
    </div>

    <!-- Install Section -->
    <div class="bg-[#1a1a1f] rounded-lg border border-[#2e2e35] p-6 mb-6">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-8 h-8 rounded bg-amber-500/10 flex items-center justify-center">
          <svg class="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-gray-100">Quick Install</h2>
      </div>
      
      <p class="text-gray-400 mb-4">One command to install the plugin:</p>
      
      <div class="bg-[#0f0f13] rounded-lg p-4 font-mono text-sm relative group">
        <code class="text-green-400">curl -L https://kitsune-ai.duckdns.org/plugin.js > ~/.opencode/plugins/kitsune.js</code>
        <button 
          @click="copyCommand"
          class="absolute right-2 top-2 px-3 py-1 bg-[#2e2e35] hover:bg-[#3e3e45] rounded text-xs text-gray-300 transition-colors"
        >
          {{ copied ? 'Copied!' : 'Copy' }}
        </button>
      </div>
    </div>

    <!-- Setup Section -->
    <div class="bg-[#1a1a1f] rounded-lg border border-[#2e2e35] p-6 mb-6">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-8 h-8 rounded bg-blue-500/10 flex items-center justify-center">
          <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-gray-100">Environment Setup</h2>
      </div>

      <p class="text-gray-400 mb-4">Add these to your shell profile (~/.bashrc, ~/.zshrc, etc.):</p>

      <div class="bg-[#0f0f13] rounded-lg p-4 font-mono text-sm relative group mb-4">
        <code class="text-amber-400 block">export KITSUNE_API_KEY={{ apiKey || 'your-api-key-here' }}</code>
        <code class="text-amber-400 block">export KITSUNE_WORKFLOW=bugfix</code>
        <code class="text-amber-400 block"># Optional: export KITSUNE_GATEWAY_URL=https://kitsune-ai.duckdns.org</code>
        <button 
          @click="copyEnv"
          class="absolute right-2 top-2 px-3 py-1 bg-[#2e2e35] hover:bg-[#3e3e45] rounded text-xs text-gray-300 transition-colors"
        >
          {{ copiedEnv ? 'Copied!' : 'Copy' }}
        </button>
      </div>

      <div class="bg-amber-500/10 border border-amber-500/20 rounded-lg p-4">
        <p class="text-amber-400 text-sm flex items-start gap-2">
          <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <span>
            <strong>Get your API key</strong> from the <router-link to="/keys" class="underline hover:text-amber-300">API Keys</router-link> page. 
            Set <code class="bg-amber-500/20 px-1 rounded">KITSUNE_WORKFLOW</code> to the name of the workflow you want to enforce.
          </span>
        </p>
      </div>
    </div>

    <!-- Usage Section -->
    <div class="bg-[#1a1a1f] rounded-lg border border-[#2e2e35] p-6 mb-6">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-8 h-8 rounded bg-green-500/10 flex items-center justify-center">
          <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-gray-100">Usage</h2>
      </div>

      <p class="text-gray-400 mb-4">Once installed, just use OpenCode normally:</p>

      <div class="bg-[#0f0f13] rounded-lg p-4 font-mono text-sm">
        <code class="text-gray-300">opencode "fix the bug in auth.py"</code>
      </div>

      <p class="text-gray-400 mt-4">The plugin will automatically:</p>
      <ul class="mt-2 space-y-2 text-gray-400">
        <li class="flex items-start gap-2">
          <span class="text-amber-500 mt-1">🦊</span>
          <span>Block tools that aren't allowed in the current phase</span>
        </li>
        <li class="flex items-start gap-2">
          <span class="text-amber-500 mt-1">🦊</span>
          <span>Show which tools are available and how to advance</span>
        </li>
        <li class="flex items-start gap-2">
          <span class="text-amber-500 mt-1">🦊</span>
          <span>Track turn limits and guardrails per phase</span>
        </li>
      </ul>
    </div>

    <!-- Workflow Tools Section -->
    <div class="bg-[#1a1a1f] rounded-lg border border-[#2e2e35] p-6">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-8 h-8 rounded bg-purple-500/10 flex items-center justify-center">
          <svg class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/>
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-gray-100">Workflow Tools</h2>
      </div>

      <p class="text-gray-400 mb-4">The plugin adds these tools to your agent:</p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-[#0f0f13] rounded-lg p-4 border border-[#2e2e35]">
          <h3 class="text-amber-500 font-mono text-sm mb-2">kitsune_transition</h3>
          <p class="text-gray-400 text-sm">Advance to the next phase. Triggers: READY, DONE, PASS, FAIL</p>
        </div>
        <div class="bg-[#0f0f13] rounded-lg p-4 border border-[#2e2e35]">
          <h3 class="text-amber-500 font-mono text-sm mb-2">kitsune_get_state</h3>
          <p class="text-gray-400 text-sm">Check current phase, allowed tools, and available transitions</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '../api-client'

const apiKey = ref('')
const copied = ref(false)
const copiedEnv = ref(false)

async function loadApiKey() {
  try {
    const res = await apiClient.get('/api/keys')
    if (res.data.keys && res.data.keys.length > 0) {
      apiKey.value = res.data.keys[0].id
    }
  } catch (e) {
    console.error('Failed to load API key:', e)
  }
}

function copyCommand() {
  navigator.clipboard.writeText('curl -L https://kitsune-ai.duckdns.org/plugin.js > ~/.opencode/plugins/kitsune.js')
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}

function copyEnv() {
  const env = `export KITSUNE_API_KEY=${apiKey.value || 'your-api-key-here'}
export KITSUNE_WORKFLOW=bugfix
# Optional: export KITSUNE_GATEWAY_URL=https://kitsune-ai.duckdns.org`
  navigator.clipboard.writeText(env)
  copiedEnv.value = true
  setTimeout(() => copiedEnv.value = false, 2000)
}

onMounted(() => {
  loadApiKey()
})
</script>
