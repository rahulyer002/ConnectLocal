const BASE_URL = import.meta.env.VITE_RESONANCE_API_URL || 'https://connectlocal.duckdns.org'

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

export function useResonanceApi() {
  return {
    fetchScore:        (lat, lon)              => getJson('/api/resonance/score',     { lat, lon }),
    fetchSafety:       (lat, lon)              => getJson('/api/safety/conditions',   { lat, lon }),
    fetchBestTimes:    (lat, lon, top_n = 5)   => getJson('/api/resonance/besttimes', { lat, lon, top_n }),
    fetchGoNow:        (lat, lon, radius = 2)  => getJson('/api/resonance/gonow',     { lat, lon, radius_km: radius }),
    fetchForecast:     (lat, lon, radius = 2)  => getJson('/api/resonance/forecast',  { lat, lon, radius_km: radius }),
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