// BestTimeWeekPage — fetches 7-day forecast + nearby green spaces.
import { describe, it, expect, vi } from 'vitest'

const mockFetchForecast    = vi.fn()
const mockFetchGreenSpaces = vi.fn()

vi.mock('@/composables/useResonanceApi', () => ({
  useResonanceApi: () => ({
    fetchForecast:    mockFetchForecast,
    fetchGreenSpaces: mockFetchGreenSpaces,
  }),
  searchSuburbs: vi.fn().mockResolvedValue([]),
}))

import BestTimeWeekPage from '@/pages/BestTimeWeekPage.vue'
import { resonanceStore } from '@/stores/resonanceStore'
import { mountWithRouter, flush } from '../helpers'

describe('BestTimeWeekPage', () => {
  it('mounts cleanly without a location', async () => {
    resonanceStore.reset()
    const wrapper = await mountWithRouter(BestTimeWeekPage)
    expect(wrapper.exists()).toBe(true)
    expect(mockFetchForecast).not.toHaveBeenCalled()
  })

  it('calls forecast + green spaces APIs when location is ready', async () => {
    mockFetchForecast.mockResolvedValue({ forecast_days: ['Monday'], forecast: { Monday: [] } })
    mockFetchGreenSpaces.mockResolvedValue([])

    resonanceStore.setLocation(-37.8, 144.97, 'Carlton')
    await mountWithRouter(BestTimeWeekPage)
    await flush(); await flush()

    expect(mockFetchForecast).toHaveBeenCalled()
    expect(mockFetchForecast.mock.calls[0][0]).toBe(-37.8)
    expect(mockFetchForecast.mock.calls[0][1]).toBe(144.97)
    expect(mockFetchGreenSpaces).toHaveBeenCalled()
  })

  it('persists the forecast result into the resonance store', async () => {
    const forecast = {
      forecast_days: ['Monday', 'Tuesday'],
      forecast: { Monday: [{ hour: 9, crowd_level: 'Low', is_quiet: true }],
                  Tuesday: [{ hour: 10, crowd_level: 'Medium', is_quiet: false }] },
    }
    mockFetchForecast.mockResolvedValue(forecast)
    mockFetchGreenSpaces.mockResolvedValue([])

    resonanceStore.setLocation(-37.8, 144.97, 'Carlton')
    await mountWithRouter(BestTimeWeekPage)
    await flush(); await flush()

    expect(resonanceStore.forecastResult).toEqual(forecast)
  })
})
