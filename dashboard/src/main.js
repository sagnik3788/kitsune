import { createApp } from 'vue'
import { Clerk } from '@clerk/clerk-js'
import api from './api-client.js'
import App from './App.vue'
import router from './router'
import './assets/main.css'

const publishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY || ''

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = src
    script.async = true
    script.crossOrigin = 'anonymous'
    script.onload = resolve
    script.onerror = () => reject(new Error(`Failed to load ${src}`))
    document.head.appendChild(script)
  })
}

function getFapiDomain(key) {
  try {
    const encoded = key.split('_')[2]
    if (!encoded) return null
    return atob(encoded.replace(/-/g, '+').replace(/_/g, '/')).slice(0, -1)
  } catch {
    return null
  }
}

async function init() {
  try {
    if (!publishableKey) {
      throw new Error('Missing VITE_CLERK_PUBLISHABLE_KEY')
    }

    const fapiDomain = getFapiDomain(publishableKey)
    if (!fapiDomain) {
      throw new Error('Invalid Clerk publishable key')
    }

    // Load the Clerk UI component bundle first.
    await loadScript(`https://${fapiDomain}/npm/@clerk/ui@1/dist/ui.browser.js`)

    const clerk = new Clerk(publishableKey)
    await clerk.load({
      ui: { ClerkUI: window.__internal_ClerkUICtor },
    })

    window.__clerk = clerk

    const app = createApp(App)
    app.provide('clerk', clerk)
    app.provide('api', api)
    app.use(router)
    app.mount('#app')
  } catch (e) {
    console.error('Failed to initialize Clerk:', e)
    const app = createApp(App)
    app.provide('clerk', null)
    app.provide('api', api)
    app.use(router)
    app.mount('#app')
  }
}

init()