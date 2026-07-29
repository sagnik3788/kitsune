<template>
  <div class="min-h-screen bg-[#0f0f13]">
    <template v-if="isHomePage">
      <router-view />
    </template>
    <template v-else>
      <nav class="border-b border-[#2e2e35] px-6 py-3">
        <div class="max-w-5xl mx-auto flex items-center justify-between">
          <router-link to="/" class="font-bold text-lg text-gray-100">Kitsune</router-link>
          <div class="flex items-center gap-6 text-sm">
            <template v-if="isSignedIn">
              <span v-if="sessionLoading" class="text-gray-500 text-xs">Loading session...</span>
              <template v-else>
                <router-link to="/workflows" class="text-gray-500 hover:text-gray-100" active-class="text-amber-500 font-medium">Workflows</router-link>
                <router-link to="/runs" class="text-gray-500 hover:text-gray-100" active-class="text-amber-500 font-medium">Runs</router-link>
                <router-link to="/keys" class="text-gray-500 hover:text-gray-100" active-class="text-amber-500 font-medium">API Keys</router-link>
                <router-link to="/plugin" class="text-gray-500 hover:text-gray-100" active-class="text-amber-500 font-medium">Plugin</router-link>
              </template>
              <button @click="signOut" class="text-gray-500 hover:text-red-400 transition-colors">Sign Out</button>
              <div id="clerk-user-button" class="ml-2"></div>
            </template>
            <template v-else>
              <router-link to="/auth" class="text-gray-500 hover:text-gray-100" active-class="text-amber-500 font-medium">Sign In</router-link>
            </template>
          </div>
        </div>
      </nav>
      <router-view />
      <footer class="border-t border-[#1a1a1f] py-4 text-center text-xs text-gray-500">
        Powered by <a href="https://kitsune.ai" class="text-amber-500 hover:underline" target="_blank">Kitsune</a>
        <span class="mx-1">&middot;</span>
        Anonymous usage analytics via <a href="https://umami.is" class="hover:underline" target="_blank">Umami</a>
      </footer>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, inject, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { waitForSession } from './api-client'

const clerk = inject('clerk')
const router = useRouter()
const isSignedIn = ref(false)
const sessionLoading = ref(false)
const isHomePage = computed(() => router.currentRoute.value.path === '/')

async function signOut() {
  if (!clerk) return
  await clerk.signOut()
}

async function ensureSessionReady() {
  if (!clerk || !clerk.user) return
  sessionLoading.value = true
  try {
    await waitForSession(8000)
  } catch (e) {
    console.warn('[App] Session not ready:', e)
  } finally {
    sessionLoading.value = false
  }
}

function updateAuthState() {
  isSignedIn.value = !!clerk?.user
  if (isSignedIn.value) {
    // Mount user button
    const el = document.getElementById('clerk-user-button')
    if (el && clerk) {
      clerk.mountUserButton(el, {
        appearance: {
          variables: {
            colorPrimary: '#f59e0b',
            colorBackground: '#0f0f13',
            colorText: '#f3f4f6',
          },
        },
        afterSignOutUrl: '/auth',
      })
    }
    // Ensure session token is ready before allowing API calls
    ensureSessionReady()
  } else {
    sessionLoading.value = false
  }
}

onMounted(() => {
  if (!clerk) return
  updateAuthState()
  clerk.addListener(updateAuthState)
})

watch(() => router.currentRoute.value.path, () => {
  updateAuthState()
})
</script>
