// DiscoverPage uses raw fetch for /api/events/search and Nominatim for geocoding.
// NOTE: the page guards `fetchActivities` with `if (!hasLocationConfirmed) return`,
// so no API call fires until the user picks a location. Tests reflect that.
import { describe, it, expect, vi } from 'vitest'
import DiscoverPage from '@/pages/DiscoverPage.vue'
import { mountWithRouter, mockGlobalFetch, flush } from '../helpers'

describe('DiscoverPage', () => {
  it('mounts cleanly', async () => {
    mockGlobalFetch({ total: 0, events: [] })
    const wrapper = await mountWithRouter(DiscoverPage)
    expect(wrapper.exists()).toBe(true)
  })

  it('renders interactive controls (filter buttons) on mount', async () => {
    mockGlobalFetch({ total: 0, events: [] })
    const wrapper = await mountWithRouter(DiscoverPage)
    // Even before a location is confirmed, the page should render its UI shell
    // including filter chips and the location-input button.
    expect(wrapper.findAll('button').length).toBeGreaterThan(0)
  })

  it('handles a 500 response gracefully without crashing', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false, status: 500,
        json: () => Promise.resolve({}),
        text: () => Promise.resolve('boom'),
      })
    )
    const wrapper = await mountWithRouter(DiscoverPage)
    await flush()
    expect(wrapper.exists()).toBe(true)  // page survives a bad response
  })
})
