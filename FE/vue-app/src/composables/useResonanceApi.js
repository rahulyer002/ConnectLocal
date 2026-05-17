const BASE_URL = import.meta.env.VITE_RESONANCE_API_URL || 'https://connectlocal.duckdns.org'

/**
 * Standard JSON fetcher. Returns null on any non-2xx response or network error.
 * Used for endpoints where a failure is genuinely an error.
 */
async function getJson(path, params = {}) {
  const url = new URL(`${BASE_URL}${path}`)
  Object.entries(params).forEach(([k, v]) => {
    if (v !== null && v !== undefined && v !== '') url.searchParams.set(k, v)
  })
  try {
    const res = await fetch(url.toString())
    if (!res.ok) throw new Error(`API ${res.status}`)
    return await res.json()
  } catch (err) {
    console.error('API error:', path, err)
    return null
  }
}

/**
 * 404-aware JSON fetcher. For locations outside the City of Melbourne pedestrian
 * sensor coverage area, the backend correctly returns 404 with a `detail` message
 * (e.g. "No sensor data found near this location." or "No pedestrian sensors
 * found within the search radius"). That's not really an error — it's a known
 * coverage limitation we want to render gracefully.
 *
 * On 404 this returns a soft response with `has_data: false` plus the BE's
 * `detail` (logged to console for debug, surfaced as `message`). The page reads
 * `has_data` to decide whether to render the normal layout vs the "outside
 * coverage" state.
 *
 * On 200 this returns the BE payload spread with `has_data: true` so the page
 * can check one flag uniformly regardless of endpoint shape.
 *
 * On any other failure (5xx, network, JSON parse) it returns null, same as
 * getJson — the page treats null as a real error.
 *
 * @param {string} path     API path
 * @param {object} params   Query params
 * @param {object} emptyShape  Empty data shape merged into the soft response so
 *                             downstream code can safely read e.g. `.best_times`,
 *                             `.forecast`, `.recommendations` without optional
 *                             chaining everywhere.
 */
async function getJsonSoft404(path, params = {}, emptyShape = {}) {
  const url = new URL(`${BASE_URL}${path}`)
  Object.entries(params).forEach(([k, v]) => {
    if (v !== null && v !== undefined && v !== '') url.searchParams.set(k, v)
  })
  try {
    const res = await fetch(url.toString())
    if (res.status === 404) {
      let detail = null
      try { const b = await res.json(); detail = b?.detail } catch (_) { /* body wasn't json */ }
      console.info(`[${path}] 404 (out-of-coverage):`, detail || '(no detail)')
      return {
        ...emptyShape,
        has_data: false,
        has_sensor_data: false, // alias for backward compatibility with the page
        coverage_area: 'City of Melbourne CBD and inner suburbs',
        message: detail || 'Live data isn\'t available for this location. Coverage is the City of Melbourne CBD and inner suburbs only.',
        location: { lat: params.lat, lon: params.lon },
      }
    }
    if (!res.ok) throw new Error(`API ${res.status}`)
    const data = await res.json()
    // BE may now return 200 with `has_data: false` for out-of-coverage locations
    // (newer style). If the flag is already set by the BE, respect it. Otherwise
    // assume success (has_data: true).
    if (typeof data?.has_data === 'boolean') {
      return { ...data, has_sensor_data: data.has_data /* keep alias in sync */ }
    }
    return { ...data, has_data: true, has_sensor_data: true }
  } catch (err) {
    console.error('API error:', path, err)
    return null
  }
}

export function useResonanceApi() {
  return {
    // /score 404s for locations with no nearby pedestrian sensors — treat softly
    fetchScore:        (lat, lon)              => getJsonSoft404('/api/resonance/score',   { lat, lon }, { resonance_score: null, grade: null, breakdown: null, weather: null }),
    // /conditions can also 404 outside CoM microclimate sensor coverage
    fetchSafety:       (lat, lon)              => getJsonSoft404('/api/safety/conditions', { lat, lon }, { conditions: null, advice: null }),
    // /besttimes and /forecast — main crowd patterns, 404 outside CoM
    fetchBestTimes:    (lat, lon, top_n = 5)   => getJsonSoft404('/api/resonance/besttimes', { lat, lon, top_n }, { best_times: [] }),
    fetchForecast:     (lat, lon, radius = 2)  => getJsonSoft404('/api/resonance/forecast',  { lat, lon, radius_km: radius }, { forecast: {}, forecast_days: [] }),
    // /gonow is recommendations of green spaces — generally returns 200 with [] if nothing nearby, but be safe
    fetchGoNow:        (lat, lon, radius = 2)  => getJsonSoft404('/api/resonance/gonow',     { lat, lon, radius_km: radius }, { recommendations: [] }),
    // Everything below is data-only / OSM-backed and never depends on CoM sensor coverage
    fetchGreenSpaces:  (lat, lon, radius = 2, hasToilet = null, limit = 10) =>
      getJson('/api/greenspace/nearby', { lat, lon, radius_km: radius, has_toilet: hasToilet, limit }),
    fetchToilets:      (lat, lon, radius = 0.5, wheelchairOnly = false) =>
      getJson('/api/greenspace/toilets', { lat, lon, radius_km: radius, wheelchair_only: wheelchairOnly }),
    fetchNearbyStops:  (lat, lon, radius = 0.5, limit = 10) =>
      getJson('/api/journey/stops/nearby', { lat, lon, radius_km: radius, limit }),
    fetchWelcomingSpaces: (lat, lon, radius = 2, limit = 20) =>
      getJson('/api/landmarks/nearby', { lat, lon, radius_km: radius, theme: 'Community Use', limit }),
  }
}

export async function searchSuburbs(query, limit = 5) {
  if (!query || query.trim().length < 2) return []
  const data = await getJson('/api/suburbs/search', { q: query.trim(), limit })
  if (!data) return []
  return Array.isArray(data) ? data : (data.suburbs || data.results || [])
}
