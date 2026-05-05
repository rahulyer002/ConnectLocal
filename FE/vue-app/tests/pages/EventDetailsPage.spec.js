// EventDetailsPage uses raw fetch for /api/events/:id.
import { describe, it, expect } from 'vitest'
import EventDetailsPage from '@/pages/EventDetailsPage.vue'
import { mountWithRouter, makeTestRouter, mockGlobalFetch, flush } from '../helpers'

describe('EventDetailsPage', () => {
  it('mounts cleanly when no event has loaded yet', async () => {
    mockGlobalFetch({})
    const router = makeTestRouter('/events/evt-1')
    const wrapper = await mountWithRouter(EventDetailsPage, { router })
    expect(wrapper.exists()).toBe(true)
  })

  it('calls /api/events/:id with the route param', async () => {
    mockGlobalFetch({
      id: 'evt-42', name: 'Pottery class', is_free: true,
      venue: 'Carlton Studio', suburb: 'Carlton', distance_km: 1.2,
    })
    const router = makeTestRouter('/events/evt-42')
    await mountWithRouter(EventDetailsPage, { router })
    await flush()
    const urls = global.fetch.mock.calls.map(c => c[0]?.toString?.() ?? '')
    expect(urls.some(u => u.includes('/api/events/evt-42'))).toBe(true)
  })

  it('renders event details once the response resolves', async () => {
    mockGlobalFetch({
      id: 'evt-7', name: 'Free guided walk', is_free: true,
      venue: 'Royal Botanic Gardens', suburb: 'South Yarra',
      distance_km: 0.8, datetime_summary: 'Sat 10am',
    })
    const router = makeTestRouter('/events/evt-7')
    const wrapper = await mountWithRouter(EventDetailsPage, { router })
    await flush(); await flush()  // event load + reactive paint
    const html = wrapper.html()
    expect(html).toMatch(/Free guided walk|Royal Botanic Gardens|Free/)
  })
})
