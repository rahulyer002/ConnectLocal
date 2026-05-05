// WelcomingSpacesPage — fetches landmarks themed 'Community Use'.
// NOTE: the page filters results by `is_welcoming_space === true` before
// storing them, so test fixtures must include that flag.
import { describe, it, expect, vi } from 'vitest'

const mockFetchWelcomingSpaces = vi.fn()

vi.mock('@/composables/useResonanceApi', () => ({
  useResonanceApi: () => ({ fetchWelcomingSpaces: mockFetchWelcomingSpaces }),
  searchSuburbs: vi.fn().mockResolvedValue([]),
}))

import WelcomingSpacesPage from '@/pages/WelcomingSpacesPage.vue'
import { resonanceStore } from '@/stores/resonanceStore'
import { mountWithRouter, flush } from '../helpers'

describe('WelcomingSpacesPage', () => {
  it('mounts cleanly with no location set', async () => {
    resonanceStore.reset()
    const wrapper = await mountWithRouter(WelcomingSpacesPage)
    expect(wrapper.exists()).toBe(true)
  })

  it('fetches welcoming-spaces with the user lat/lon when ready', async () => {
    mockFetchWelcomingSpaces.mockResolvedValue([
      { landmark_id: 'l1', name: 'Carlton Library', theme: 'Community Use',
        is_welcoming_space: true },
    ])
    resonanceStore.setLocation(-37.8, 144.97, 'Carlton')
    await mountWithRouter(WelcomingSpacesPage)
    await flush(); await flush()

    expect(mockFetchWelcomingSpaces).toHaveBeenCalled()
    const args = mockFetchWelcomingSpaces.mock.calls[0]
    expect(args[0]).toBe(-37.8)
    expect(args[1]).toBe(144.97)
  })

  it('stores the welcoming spaces in the resonance store', async () => {
    // The page filters out anything without `is_welcoming_space: true`,
    // so the test fixtures must mark the entries as welcoming.
    const spaces = [
      { landmark_id: 'l1', name: 'Carlton Library',   is_welcoming_space: true },
      { landmark_id: 'l2', name: 'Fitzroy Town Hall', is_welcoming_space: true },
    ]
    mockFetchWelcomingSpaces.mockResolvedValue(spaces)
    resonanceStore.setLocation(-37.8, 144.97, 'Carlton')
    await mountWithRouter(WelcomingSpacesPage)
    await flush(); await flush()

    expect(resonanceStore.welcomingSpaces).toEqual(spaces)
  })
})
