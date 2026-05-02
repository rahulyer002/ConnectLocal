// src/composables/useResonanceApi.js
const BASE = 'https://connectlocal.duckdns.org'

async function apiFetch(path, params = {}) {
  const url = new URL(BASE + path)
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null) url.searchParams.set(k, v)
  })
  const res = await fetch(url.toString())
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`)
  return res.json()
}

// ── Mocks (used when backend unreachable) ─────────────────────────────────

function mockScore() {
  return {
    resonance_score: 74,
    grade: 'Good',
    breakdown: {
      crowd_score: 28,
      weather_score: 25,
      comfort_score: 14,
      toilet_score: 5,
      shade_score: 2,
    },
    crowd: { level: 'Low', avg_count: 18, sensor_description: 'Swanston St near Flinders' },
    weather: {
      temperature_c: 19,
      humidity_pct: 55,
      wind_speed_kmh: 12,
      pm25_ug_m3: 8,
      safety_verdict: 'Good',
      warnings: [],
      is_safe_for_elderly: true,
    },
    nearest_open_space: { space_name: 'Fitzroy Gardens', comfort_score: 78, distance_km: 0.4 },
    nearest_toilet: { name: 'Public Toilet - Fitzroy Gardens', distance_km: 0.15, has_wheelchair: true },
  }
}

function mockSafety() {
  return {
    conditions: {
      available: true,
      temperature_c: 19,
      humidity_pct: 55,
      wind_speed_kmh: 12,
      pm25_ug_m3: 8,
      safety_verdict: 'Good',
      warnings: [],
      is_safe_for_elderly: true,
    },
    advice: 'Conditions look good for an outing today. Enjoy the fresh air!',
    data_source: 'City of Melbourne Microclimate Sensors',
    update_frequency: 'Every 15 minutes',
  }
}

function mockBestTimes() {
  return {
    best_times: [
      { day_name: 'Sunday',    hour: 8,  hour_label: '08:00', avg_count: 12, crowd_level: 'Low' },
      { day_name: 'Saturday',  hour: 9,  hour_label: '09:00', avg_count: 15, crowd_level: 'Low' },
      { day_name: 'Wednesday', hour: 10, hour_label: '10:00', avg_count: 18, crowd_level: 'Low' },
      { day_name: 'Tuesday',   hour: 9,  hour_label: '09:00', avg_count: 21, crowd_level: 'Low' },
      { day_name: 'Thursday',  hour: 11, hour_label: '11:00', avg_count: 24, crowd_level: 'Low' },
    ],
    tip: 'These times have the lowest pedestrian activity based on 2 years of City of Melbourne sensor data.',
  }
}

function mockGoNow() {
  return {
    generated_at: new Date().toLocaleString('en-AU', { weekday: 'long', hour: '2-digit', minute: '2-digit' }),
    weather: { temperature_c: 19, safety_verdict: 'Good', warnings: [] },
    total_spaces_checked: 14,
    recommendations: [
      {
        space_name: 'Fitzroy Gardens',
        distance_km: 0.4,
        resonance_score: 82,
        grade: 'Excellent',
        crowd_level: 'Low',
        is_quiet_now: true,
        has_toilet_nearby: true,
        comfort_score: 78,
        why_recommended: 'Great option — quiet right now, good weather conditions, toilet nearby',
        lat: -37.8136, lon: 144.9731,
      },
      {
        space_name: 'Carlton Gardens South',
        distance_km: 0.9,
        resonance_score: 71,
        grade: 'Good',
        crowd_level: 'Moderate',
        is_quiet_now: false,
        has_toilet_nearby: true,
        comfort_score: 68,
        why_recommended: 'Good option — comfortable conditions, toilet access, moderate activity',
        lat: -37.8055, lon: 144.9716,
      },
      {
        space_name: 'Lincoln Square',
        distance_km: 1.3,
        resonance_score: 63,
        grade: 'Good',
        crowd_level: 'Low',
        is_quiet_now: true,
        has_toilet_nearby: false,
        comfort_score: 61,
        why_recommended: 'Quiet and comfortable — no toilet nearby, plan accordingly',
        lat: -37.7985, lon: 144.9610,
      },
    ],
  }
}

function mockForecast() {
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
  const levels = ['Low', 'Low', 'Moderate', 'Moderate', 'High', 'Moderate', 'Low']
  const forecast = {}
  days.forEach((day, di) => {
    forecast[day] = Array.from({ length: 24 }, (_, h) => {
      const base = di < 5 ? 40 : 20  // weekdays busier
      const peak = (h >= 8 && h <= 18) ? Math.min(100, base + h * 3) : 5
      const level = peak > 60 ? 'High' : peak > 35 ? 'Moderate' : 'Low'
      return { hour: h, hour_label: `${String(h).padStart(2, '0')}:00`, avg_count: peak, crowd_level: level, is_quiet: level === 'Low' }
    })
  })
  return { forecast_days: days, forecast, data_note: 'Based on 2 years of City of Melbourne pedestrian sensor data (2024–2026)' }
}

function mockGreenSpaces() {
  return [
    { space_id: 1, space_name: 'Fitzroy Gardens', category: 'Green Space', distance_km: 0.4, comfort_score: 78, has_toilet_nearby: true, walkability_score: 82, lat: -37.8136, lon: 144.9731 },
    { space_id: 2, space_name: 'Carlton Gardens South', category: 'Green Space', distance_km: 0.9, comfort_score: 68, has_toilet_nearby: true, walkability_score: 74, lat: -37.8055, lon: 144.9716 },
    { space_id: 3, space_name: 'Lincoln Square', category: 'Green Space', distance_km: 1.3, comfort_score: 61, has_toilet_nearby: false, walkability_score: 65, lat: -37.7985, lon: 144.9610 },
  ]
}

function mockToilets() {
  return [
    { toilet_id: 1, name: 'Public Toilet — Fitzroy Gardens', distance_km: 0.15, has_wheelchair: true },
    { toilet_id: 2, name: 'Public Toilet — Melbourne Town Hall (200 Collins St)', distance_km: 0.3, has_wheelchair: true },
  ]
}

function mockStops() {
  return [
    { stop_id: '19854', stop_name: 'Swanston St/Flinders St', mode: 'tram', distance_km: 0.12, is_wheelchair_accessible: true, routes_served: '1,3,5,6,16,64,67,72' },
    { stop_id: '4143',  stop_name: 'Melbourne Central Station', mode: 'train', distance_km: 0.35, is_wheelchair_accessible: true, routes_served: 'Upfield,Craigieburn,Mernda' },
  ]
}

function mockWelcomingSpaces() {
  return [
    { landmark_id: 1, name: 'Fitzroy Library', theme: 'Community Use', sub_theme: 'Library', distance_km: 0.2, is_welcoming_space: true },
    { landmark_id: 2, name: 'Carlton Neighbourhood Learning Centre', theme: 'Community Use', sub_theme: 'Community Centre', distance_km: 0.6, is_welcoming_space: true },
    { landmark_id: 3, name: 'Melbourne Town Hall — Community Room', theme: 'Community Use', sub_theme: 'Civic Hall', distance_km: 0.9, is_welcoming_space: true },
  ]
}

// ── Suburb autocomplete (for location bar) ────────────────────────────────

export async function searchSuburbs(q) {
  try {
    const data = await apiFetch('/api/suburbs/search', { q, limit: 6 })
    // Returns array of { suburb_name, centroid_lat, centroid_lng }
    return Array.isArray(data) ? data : data.suburbs || []
  } catch {
    return []
  }
}

// ── Public API functions ──────────────────────────────────────────────────

export function useResonanceApi() {
  async function fetchScore(lat, lon) {
    try { return await apiFetch('/api/resonance/score', { lat, lon }) }
    catch { return mockScore() }
  }

  async function fetchSafety(lat, lon) {
    try { return await apiFetch('/api/safety/conditions', { lat, lon }) }
    catch { return mockSafety() }
  }

  async function fetchBestTimes(lat, lon, top_n = 5) {
    try { return await apiFetch('/api/resonance/besttimes', { lat, lon, radius_km: 1, top_n }) }
    catch { return mockBestTimes() }
  }

  async function fetchGoNow(lat, lon, radius_km = 2) {
    try { return await apiFetch('/api/resonance/gonow', { lat, lon, radius_km }) }
    catch { return mockGoNow() }
  }

  async function fetchForecast(lat, lon, radius_km = 2) {
    try { return await apiFetch('/api/resonance/forecast', { lat, lon, radius_km }) }
    catch { return mockForecast() }
  }

  async function fetchGreenSpaces(lat, lon, radius_km = 2, has_toilet = null, limit = 10) {
    try {
      const params = { lat, lon, radius_km, limit }
      if (has_toilet !== null) params.has_toilet = has_toilet
      const data = await apiFetch('/api/greenspace/nearby', params)
      return Array.isArray(data) ? data : data.spaces || []
    } catch { return mockGreenSpaces() }
  }

  async function fetchToilets(lat, lon, radius_km = 0.5) {
    try {
      const data = await apiFetch('/api/greenspace/toilets', { lat, lon, radius_km })
      return Array.isArray(data) ? data : data.toilets || []
    } catch { return mockToilets() }
  }

  async function fetchNearbyStops(lat, lon, radius_km = 0.5) {
    try {
      const data = await apiFetch('/api/journey/stops/nearby', { lat, lon, radius_km, limit: 5 })
      return Array.isArray(data) ? data : data.stops || []
    } catch { return mockStops() }
  }

  async function fetchWelcomingSpaces(lat, lon, radius_km = 2) {
    try {
      const data = await apiFetch('/api/landmarks/nearby', { lat, lon, radius_km, theme: 'Community Use', limit: 10 })
      const list = Array.isArray(data) ? data : data.landmarks || []
      return list.filter(l => l.is_welcoming_space === true)
    } catch { return mockWelcomingSpaces() }
  }

  async function fetchJourneyPlan(fromLat, fromLon, toLat, toLon, arriveBy = null) {
    try {
      const params = { from_lat: fromLat, from_lon: fromLon, to_lat: toLat, to_lon: toLon }
      if (arriveBy) params.arrive_by = arriveBy
      return await apiFetch('/api/journey/plan', params)
    } catch { return null }
  }

  return {
    fetchScore, fetchSafety, fetchBestTimes, fetchGoNow,
    fetchForecast, fetchGreenSpaces, fetchToilets,
    fetchNearbyStops, fetchWelcomingSpaces, fetchJourneyPlan,
  }
}