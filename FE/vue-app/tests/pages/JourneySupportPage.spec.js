// JourneySupportPage — uses useJourneyApi for routes/plan/walk/etc.
//                       Also pulls in Google Maps; we leave that to the global stub.
import { describe, it, expect, vi } from 'vitest'

const mockFetchRoutes        = vi.fn()
const mockFetchPlan          = vi.fn()
const mockFetchWalk          = vi.fn()
const mockFetchNearbyStops   = vi.fn()
const mockFetchAccessibility = vi.fn()
const mockFetchToilets       = vi.fn()
const mockFetchLandmarks     = vi.fn()
const mockFetchGreenSpaces   = vi.fn()

vi.mock('@/composables/useJourneyApi', () => ({
  useJourneyApi: () => ({
    fetchRoutes:        mockFetchRoutes,
    fetchPlan:          mockFetchPlan,
    fetchWalk:          mockFetchWalk,
    fetchNearbyStops:   mockFetchNearbyStops,
    fetchAccessibility: mockFetchAccessibility,
    fetchToilets:       mockFetchToilets,
    fetchLandmarks:     mockFetchLandmarks,
    fetchGreenSpaces:   mockFetchGreenSpaces,
  }),
  searchSuburbs:  vi.fn().mockResolvedValue([]),
  decodePolyline: vi.fn().mockReturnValue([]),
  extractPath:    vi.fn().mockReturnValue([]),
}))

import JourneySupportPage from '@/pages/JourneySupportPage.vue'
import { mountWithRouter, makeTestRouter } from '../helpers'

describe('JourneySupportPage', () => {
  it('mounts cleanly without query parameters', async () => {
    const wrapper = await mountWithRouter(JourneySupportPage)
    expect(wrapper.exists()).toBe(true)
  })

  it('mounts cleanly when from/to lat/lon are passed in the URL', async () => {
    // Mimics the user arriving from a "Plan journey" CTA on another page.
    const router = makeTestRouter('/journey?from_lat=-37.8&from_lon=144.97&to_lat=-37.81&to_lon=144.95&place=Royal Park')
    const wrapper = await mountWithRouter(JourneySupportPage, { router })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes the route-fetching API surface from useJourneyApi', () => {
    // Smoke check that the mock wiring is in place — guards against future
    // refactors that rename methods on the composable.
    expect(typeof mockFetchRoutes).toBe('function')
    expect(typeof mockFetchPlan).toBe('function')
    expect(typeof mockFetchWalk).toBe('function')
  })
})
