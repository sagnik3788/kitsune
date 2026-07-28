<template>
  <div class="min-h-screen bg-[#0f0f13] flex items-center justify-center px-4 relative overflow-hidden">
    <!-- Ambient background glow matching HomePage hero -->
    <div class="absolute inset-0 pointer-events-none">
      <div class="absolute top-1/4 left-1/2 -translate-x-1/2 w-[28rem] h-[28rem] bg-amber-500/5 rounded-full blur-3xl"></div>
      <div class="absolute bottom-1/4 left-1/3 w-96 h-96 bg-amber-700/5 rounded-full blur-3xl"></div>
    </div>

    <div class="relative w-full max-w-sm">
      <!-- Branding -->
      <div class="mb-8 text-center">
        <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 mb-4">
          <span class="text-2xl">🦊</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-100 tracking-tight">Kitsune</h1>
      </div>
      <div id="clerk-sign-in"></div>
      <p class="mt-6 text-center text-xs text-gray-600">
        Secure sign-in powered by Clerk
      </p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'

const clerk = inject('clerk')
const router = useRouter()

onMounted(() => {
  if (!clerk) return

  // If already signed in, redirect home
  if (clerk.user) {
    router.push('/')
    return
  }

  const el = document.getElementById('clerk-sign-in')
  if (!el) return

  clerk.mountSignIn(el, {
    appearance: {
      variables: {
        colorPrimary: '#f59e0b',
        colorBackground: '#0f0f13',
        colorText: '#f3f4f6',
        colorInputBackground: '#1a1a1f',
        colorInputText: '#f3f4f6',
        colorInputBorder: '#2e2e35',
        colorTextSecondary: '#9ca3af',
        colorDanger: '#ef4444',
        colorSuccess: '#22c55e',
        borderRadius: '0.75rem',
        fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      },
      elements: {
        card: 'bg-[#131318] border border-[#2e2e35] rounded-xl shadow-xl shadow-black/20 p-6',
        headerTitle: 'text-xl font-bold text-gray-100 tracking-tight mb-1',
        headerSubtitle: 'text-sm text-gray-400 mb-6',
        socialButtonsBlockButton:
          'bg-[#1a1a1f] hover:bg-[#232329] border border-[#2e2e35] text-gray-100 text-sm font-medium rounded-lg !h-10 transition-colors duration-200',
        socialButtonsBlockButtonText: 'text-gray-100 text-sm font-medium',
        socialButtonsBlockButtonText__github: 'text-gray-100 text-sm font-medium',
        socialButtonsBlockButtonText__google: 'text-gray-100 text-sm font-medium',
        socialButtonsIconButton: 'text-gray-100 !w-5 !h-5',
        socialButtonsProviderIcon: 'text-gray-100',
        socialButtonsProviderIcon__github: 'text-gray-100',
        socialButtonsProviderIcon__google: 'text-gray-100',
        badge: 'bg-amber-500/20 text-amber-400 text-xs font-medium px-2 py-0.5 rounded-full border border-amber-500/30',
        badge__lastUsed: 'bg-amber-500/20 text-amber-400 text-xs font-medium px-2 py-0.5 rounded-full border border-amber-500/30',
        formButtonPrimary:
          'bg-amber-500 hover:bg-amber-400 text-[#0f0f13] font-semibold text-sm rounded-lg !h-10 transition-colors duration-200 shadow-none',
        formFieldInput:
          'bg-[#1a1a1f] border border-[#2e2e35] text-gray-100 text-sm rounded-lg h-10 px-3 placeholder-gray-600 focus:border-amber-500/60 focus:ring-1 focus:ring-amber-500/30',
        formFieldLabel: 'text-gray-400 text-xs font-medium mb-1.5',
        formFieldErrorText: 'text-red-400 text-xs mt-1',
        dividerLine: 'bg-[#2e2e35]',
        dividerText: 'text-gray-500 text-xs uppercase tracking-wider',
        footer: 'text-gray-300 text-sm',
        footerActionText: 'text-gray-300',
        footerActionLink: 'text-amber-400 hover:text-amber-300 font-medium transition-colors',
        identityPreview: 'bg-[#1a1a1f] border border-[#2e2e35] text-gray-200 rounded-lg',
        identityPreviewText: 'text-gray-200 text-sm',
        identityPreviewEditButton: 'text-amber-500 hover:text-amber-400',
        alert: 'bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg text-sm',
        alertText: 'text-red-400 text-sm',
        otpCodeFieldInput:
          'bg-[#1a1a1f] border border-[#2e2e35] text-white text-center text-lg font-mono rounded-lg w-10 h-12 focus:border-amber-500 focus:ring-1 focus:ring-amber-500',
        otpCodeFieldInputs: 'gap-2 justify-center',
      },
      layout: {
        socialButtonsPlacement: 'top',
        socialButtonsVariant: 'blockButton',
        showOptionalFields: false,
      },
    },
    redirectUrl: window.location.origin + '/',
    afterSignInUrl: window.location.origin + '/',
  })
})
</script>
