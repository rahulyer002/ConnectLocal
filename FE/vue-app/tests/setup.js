// tests/setup.js — global mocks loaded before every test file.
import { vi, beforeEach } from 'vitest'

// 1. fetch — never actually hit the network.
//    Tests that need a specific response should use mockGlobalFetch() from helpers.js.
beforeEach(() => {
  global.fetch = vi.fn(() =>
    Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve({}),
      text: () => Promise.resolve(''),
    })
  )
})

// 2. IntersectionObserver — used by every page for [data-reveal] animations.
//    jsdom doesn't ship this, so we stub it with no-op methods.
class IntersectionObserverStub {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
  takeRecords() { return [] }
}
global.IntersectionObserver = IntersectionObserverStub

// 3. window.google — JourneySupportPage references this when the Maps script callback fires.
//    We pre-populate a minimal stub so the page doesn't crash on mount.
global.google = {
  maps: {
    Map: vi.fn(),
    Marker: vi.fn(),
    LatLng: vi.fn(),
    Polyline: vi.fn(),
    DirectionsService: vi.fn(),
    DirectionsRenderer: vi.fn(),
    places: { Autocomplete: vi.fn() },
    geometry: {},
    SymbolPath: { CIRCLE: 0 },
  },
}

// 4. Stub URL.createObjectURL/revokeObjectURL — Leaflet sometimes touches these.
global.URL.createObjectURL = vi.fn(() => 'blob:mock')
global.URL.revokeObjectURL = vi.fn()

// 5. Geolocation — pages that call navigator.geolocation should not auto-resolve.
//    Tests that need it can override per-test.
Object.defineProperty(global.navigator, 'geolocation', {
  value: {
    getCurrentPosition: vi.fn(),
    watchPosition: vi.fn(),
    clearWatch: vi.fn(),
  },
  configurable: true,
})

// 6. Silence console noise from intentional error paths in tests.
//    (Comment these out if you're debugging a real failure.)
vi.spyOn(console, 'error').mockImplementation(() => {})
vi.spyOn(console, 'warn').mockImplementation(() => {})
