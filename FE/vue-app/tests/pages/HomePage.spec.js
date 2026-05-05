// HomePage uses raw fetch to /api/suburbs/psychological-distress on mount.
import { describe, it, expect } from 'vitest'
import HomePage from '@/pages/HomePage.vue'
import { mountWithRouter, mockGlobalFetch, flush } from '../helpers'

describe('HomePage', () => {
  it('mounts without throwing', async () => {
    mockGlobalFetch({ data: [] })
    const wrapper = await mountWithRouter(HomePage)
    expect(wrapper.exists()).toBe(true)
  })

  it('calls the psychological-distress endpoint on mount', async () => {
    mockGlobalFetch({ data: [{ age_group: '65+', psychological_distress_percent: 9.9 }] })
    await mountWithRouter(HomePage)
    await flush()
    const calledUrls = global.fetch.mock.calls.map(c => c[0])
    expect(calledUrls.some(u => u.includes('/api/suburbs/psychological-distress'))).toBe(true)
  })

  it('renders the navigation links to key pages', async () => {
    mockGlobalFetch({ data: [] })
    const wrapper = await mountWithRouter(HomePage)
    const html = wrapper.html()
    expect(html).toMatch(/discover/i)
    expect(html).toMatch(/journey/i)
  })
})
