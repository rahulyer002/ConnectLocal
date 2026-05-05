// BestTimePage — uses useResonanceApi composable. We mock the composable directly.
import { describe, it, expect, vi } from 'vitest'

const mockFetchScore     = vi.fn()
const mockFetchSafety    = vi.fn()
const mockFetchBestTimes = vi.fn()

vi.mock('@/composables/useResonanceApi', () => ({
  useResonanceApi: () => ({
    fetchScore:     mockFetchScore,
    fetchSafety:    mockFetchSafety,
    fetchBestTimes: mockFetchBestTimes,
  }),
  searchSuburbs: vi.fn().mockResolvedValue([]),
}))

import BestTimePage from '@/pages/BestTimePage.vue'
import { resonanceStore } from '@/stores/resonanceStore'
import { mountWithRouter, flush } from '../helpers'

describe('BestTimePage', () => {
  it('mounts without throwing when no location is set', async () => {
    resonanceStore.reset()
    const wrapper = await mountWithRouter(BestTimePage)
    expect(wrapper.exists()).toBe(true)
    // Without locationReady, no API calls fire.
    expect(mockFetchScore).not.toHaveBeenCalled()
  })

  it('calls the three APIs in parallel when location becomes ready', async () => {
    mockFetchScore.mockResolvedValue({ resonance_score: 88, grade: 'A',
      breakdown: { crowd_score: 30, weather_score: 32, comfort_score: 18, toilet_score: 5, shade_score: 3 }})
    mockFetchSafety.mockResolvedValue({ conditions: { safety_verdict: 'Good' } })
    mockFetchBestTimes.mockResolvedValue({ best_times: [] })

    resonanceStore.setLocation(-37.8, 144.97, 'Carlton')
    await mountWithRouter(BestTimePage)
    await flush(); await flush()

    expect(mockFetchScore).toHaveBeenCalledWith(-37.8, 144.97)
    expect(mockFetchSafety).toHaveBeenCalledWith(-37.8, 144.97)
    expect(mockFetchBestTimes).toHaveBeenCalledWith(-37.8, 144.97, 6)
  })

  it('stores the API results into resonanceStore', async () => {
    const score = { resonance_score: 75, grade: 'B',
      breakdown: { crowd_score: 25, weather_score: 28, comfort_score: 15, toilet_score: 4, shade_score: 3 }}
    mockFetchScore.mockResolvedValue(score)
    mockFetchSafety.mockResolvedValue(null)
    mockFetchBestTimes.mockResolvedValue(null)

    resonanceStore.setLocation(-37.8, 144.97, 'Carlton')
    await mountWithRouter(BestTimePage)
    await flush(); await flush()

    expect(resonanceStore.scoreResult).toEqual(score)
  })
})
