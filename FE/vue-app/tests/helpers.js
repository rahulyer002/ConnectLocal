// tests/helpers.js — shared mounting + mocking utilities for page tests.
import { mount } from '@vue/test-utils'
import { vi } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'

/**
 * Build a tiny router that satisfies <RouterLink> and useRoute()/useRouter()
 * without pulling in the real route table. Tests can override the initial path.
 */
export function makeTestRouter(initialPath = '/', extraRoutes = []) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/',                component: { template: '<div />' } },
      { path: '/home',            component: { template: '<div />' } },
      { path: '/discover',        component: { template: '<div />' } },
      { path: '/checkin',         component: { template: '<div />' } },
      { path: '/checkin-form',    component: { template: '<div />' } },
      { path: '/results',         component: { template: '<div />' } },
      { path: '/journey',         component: { template: '<div />' } },
      { path: '/best-time',       component: { template: '<div />' } },
      { path: '/best-time/now',   component: { template: '<div />' } },
      { path: '/best-time/week',  component: { template: '<div />' } },
      { path: '/welcoming-spaces',component: { template: '<div />' } },
      { path: '/events/:id',      component: { template: '<div />' } },
      ...extraRoutes,
    ],
  })
  router.push(initialPath)
  return router
}

/**
 * Mount a component with the test router pre-installed.
 * Returns @vue/test-utils wrapper.
 */
export async function mountWithRouter(Component, opts = {}) {
  const router = opts.router || makeTestRouter(opts.initialPath || '/')
  await router.isReady()
  return mount(Component, {
    global: {
      plugins: [router],
      stubs: {
        // Avoid trying to resolve actual nested components — keeps tests focused.
        BestTimeNav: true,
        BestTimeLocationBar: true,
        TextSizeSlider: true,
        ...opts.stubs,
      },
    },
    ...opts.mountOpts,
  })
}

/**
 * Convenience: make global fetch return a specific JSON payload once.
 * Pass an array to queue multiple responses in order.
 */
export function mockGlobalFetch(payloadOrPayloads, { ok = true, status = 200 } = {}) {
  const queue = Array.isArray(payloadOrPayloads) ? [...payloadOrPayloads] : [payloadOrPayloads]
  global.fetch = vi.fn(() => {
    const next = queue.length > 1 ? queue.shift() : queue[0]
    return Promise.resolve({
      ok,
      status,
      json: () => Promise.resolve(next),
      text: () => Promise.resolve(typeof next === 'string' ? next : JSON.stringify(next)),
    })
  })
  return global.fetch
}

/** Wait for next tick + flush microtasks. Useful after triggering an async action. */
export const flush = () => new Promise(r => setTimeout(r, 0))
