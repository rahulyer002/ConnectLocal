// BestTimeNowPage — pulls go-now recommendations + safety + toilets + stops in parallel.
import { describe, it, expect, vi } from 'vitest'

const mockFetchGoNow       = vi.fn()
const mockFetchSafety      = vi.fn()
const mockFetchToilets     = vi.fn()
const mockFetchNearbyStops = vi.fn()

vi.mock('@/composables/useResonanceApi', () => ({
  useResonanceApi: () => ({
    fetchGoNow:       mockFetchGoNow,
    fetchSafety:      mockFetchSafety,
    fetchToilets:     mockFetchToilets,
    fetchNearbyStops: mockFetchNearbyStops,
  }),
  searchSuburbs: vi.fn().mockResolvedValue([]),
}))

import BestTimeNowPage from '@/pages/BestTimeNowPage.vue'
import { resonanceStore } from '@/stores/resonanceStore'
import { mountWithRouter, flush } from '../helpers'

describe('BestTimeNowPage', () => {
  it('mounts without firing API calls when location is not set', async () => {
    resonanceStore.reset()
    const wrapper = await mountWithRouter(BestTimeNowPage)
    expect(wrapper.exists()).toBe(true)
    expect(mockFetchGoNow).not.toHaveBeenCalled()
  })

  it('calls all four APIs once location is ready', async () => {
    mockFetchGoNow.mockResolvedValue({ recommendations: [] })
    mockFetchSafety.mockResolvedValue({ conditions: {} })
    mockFetchToilets.mockResolvedValue([])
    mockFetchNearbyStops.mockResolvedValue([])

    resonanceStore.setLocation(-37.8, 144.97, 'Carlton')
    await mountWithRouter(BestTimeNowPage)
    await flush(); await flush()

    expect(mockFetchGoNow).toHaveBeenCalledWith(-37.8, 144.97, 2)
    expect(mockFetchSafety).toHaveBeenCalledWith(-37.8, 144.97)
    expect(mockFetchToilets).toHaveBeenCalledWith(-37.8, 144.97, 0.5)
    expect(mockFetchNearbyStops).toHaveBeenCalledWith(-37.8, 144.97, 0.5)
  })

  it('writes go-now recommendations into the resonance store', async () => {
    const payload = {
      recommendations: [
        { space_id: 's1', space_name: 'Carlton Gardens', resonance_score: 88,
          grade: 'A', lat: -37.8, lon: 144.97, distance_km: 0.4 },
      ],
    }
    mockFetchGoNow.mockResolvedValue(payload)
    mockFetchSafety.mockResolvedValue(null)
    mockFetchToilets.mockResolvedValue([])
    mockFetchNearbyStops.mockResolvedValue([])

    resonanceStore.setLocation(-37.8, 144.97, 'Carlton')
    await mountWithRouter(BestTimeNowPage)
    await flush(); await flush()

    expect(resonanceStore.goNowResult).toEqual(payload)
  })
})
