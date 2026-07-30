import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('../views/HomePage.vue') },
    { path: '/auth', component: () => import('../views/AuthPage.vue') },
    { path: '/workflows', component: () => import('../views/WorkflowList.vue'), meta: { requiresAuth: true } },
    { path: '/workflows/:id', component: () => import('../views/WorkflowEditor.vue'), meta: { requiresAuth: true } },
    { path: '/runs', component: () => import('../views/WorkflowRuns.vue'), meta: { requiresAuth: true } },
    { path: '/runs/:sessionId', component: () => import('../views/SessionDetail.vue'), meta: { requiresAuth: true } },
    { path: '/keys', component: () => import('../views/ApiKeys.vue'), meta: { requiresAuth: true } },
    { path: '/plugin', component: () => import('../views/PluginPage.vue'), meta: { requiresAuth: true } },
  ],
})

router.beforeEach((to) => {
  if (to.path === '/auth') return true

  if (to.meta.requiresAuth) {
    const clerk = window.__clerk
    if (!clerk || !clerk.user) {
      return '/auth'
    }
  }

  return true
})

export default router
