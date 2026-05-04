// useJourneyApi.js — All Journey/Discovery endpoints in one place
// Aligns with the existing useResonanceApi.js style.

const BASE_URL = import.meta.env.VITE_RESONANCE_API_URL || 'https://connectlocal.duckdns.org'

async function getJson(path, params = {}) {
  const url = new URL(`${BASE_URL}${path}`)
  Object.entries(params).forEach(([k, v]) => {
    if (v === null || v === undefined || v === '') return
    // Defensively coerce — never let an object/array be stringified into a single param
    if (typeof v === 'object') {
      console.warn(`[Journey API] Skipping param "${k}" — value is an object`, v)
      return
    }
    url.searchParams.set(k, String(v))
  })
  try {
    const res = await fetch(url.toString())
    if (!res.ok) {
      const text = await res.text().catch(() => '')
      throw new Error(`API ${res.status}${text ? ': ' + text.slice(0, 200) : ''}`)
    }
    return await res.json()
  } catch (err) {
    console.error('[Journey API]', path, err)
    throw err
  }
}

/**
 * Decode Google's encoded polyline string into [{lat, lng}, …].
 * Standard algorithm — works for any string returned by Google Directions.
 */
export function decodePolyline(encoded) {
  if (!encoded || typeof encoded !== 'string') return []
  const points = []
  let index = 0, lat = 0, lng = 0
  while (index < encoded.length) {
    let b, shift = 0, result = 0
    do {
      b = encoded.charCodeAt(index++) - 63
      result |= (b & 0x1f) << shift
      shift += 5
    } while (b >= 0x20)
    const dlat = (result & 1) ? ~(result >> 1) : (result >> 1)
    lat += dlat
    shift = 0; result = 0
    do {
      b = encoded.charCodeAt(index++) - 63
      result |= (b & 0x1f) << shift
      shift += 5
    } while (b >= 0x20)
    const dlng = (result & 1) ? ~(result >> 1) : (result >> 1)
    lng += dlng
    points.push({ lat: lat / 1e5, lng: lng / 1e5 })
  }
  return points
}

/**
 * Defensively pull a polyline (encoded string OR coord array) out of any
 * shape the backend might return on a route or leg.
 * Returns [{lat,lng}, …] — empty array if nothing usable found.
 */
export function extractPath(obj) {
  if (!obj) return []
  const candidates = [
    obj.polyline,
    obj.encoded_polyline,
    obj.overview_polyline,
    obj?.overview_polyline?.points,
    obj?.polyline?.points,
    obj.geometry,
    obj?.geometry?.polyline,
  ]
  for (const c of candidates) {
    if (typeof c === 'string' && c.length > 4) {
      const decoded = decodePolyline(c)
      if (decoded.length > 1) return decoded
    }
    if (c && typeof c === 'object' && typeof c.points === 'string') {
      const decoded = decodePolyline(c.points)
      if (decoded.length > 1) return decoded
    }
  }
  const arrays = [obj.path, obj.coords, obj.coordinates, obj.points, obj.geometry]
  for (const a of arrays) {
    if (Array.isArray(a) && a.length > 1) {
      const first = a[0]
      if (Array.isArray(first) && first.length >= 2) {
        return a.map(p => ({ lat: Number(p[0]), lng: Number(p[1]) }))
      }
      if (first && typeof first === 'object') {
        if ('lat' in first && ('lng' in first || 'lon' in first || 'longitude' in first)) {
          return a.map(p => ({ lat: Number(p.lat), lng: Number(p.lng ?? p.lon ?? p.longitude) }))
        }
      }
    }
  }
  return []
}

/* ───────────────────────────────────────────────
   API helpers — exposed via composable
   All accept a SINGLE OBJECT of params.
   ─────────────────────────────────────────────── */

export function useJourneyApi() {
  return {
    /** Multiple route alternatives — powers the "Choose your route" UI. */
    fetchRoutes: ({ from_lat, from_lon, to_lat, to_lon, arrive_by = null } = {}) =>
      getJson('/api/journey/google/routes', {
        from_lat, from_lon, to_lat, to_lon, arrive_by
      }),

    /** Single route plan (any mode). */
    fetchPlan: ({ from_lat, from_lon, to_lat, to_lon, mode = 'transit', arrive_by = null } = {}) =>
      getJson('/api/journey/google/plan', {
        from_lat, from_lon, to_lat, to_lon, mode, arrive_by
      }),

    /** Walking-only route (uses OSRM). */
    fetchWalk: ({ from_lat, from_lon, to_lat, to_lon } = {}) =>
      getJson('/api/journey/walk', { from_lat, from_lon, to_lat, to_lon }),

    /** Public transport stops near a coordinate.
     *  Accepts either { radius_m } (metres) or { radius_km }. */
    fetchNearbyStops: ({ lat, lon, radius_m, radius_km, limit = 12 } = {}) => {
      const radius = radius_km != null ? radius_km : (radius_m != null ? radius_m / 1000 : 0.5)
      return getJson('/api/journey/stops/nearby', { lat, lon, radius_km: radius, limit })
    },

    /** Stop accessibility (elevators / stairs / wheelchair). */
    fetchAccessibility: ({ stop_id } = {}) =>
      getJson('/api/journey/accessibility', { stop_id }),

    /** Public toilets near a coordinate. */
    fetchToilets: ({ lat, lon, radius_m, radius_km, wheelchair_only = false, limit = 30 } = {}) => {
      const radius = radius_km != null ? radius_km : (radius_m != null ? radius_m / 1000 : 0.5)
      return getJson('/api/greenspace/toilets', {
        lat, lon, radius_km: radius, wheelchair_only, limit
      })
    },

    /** Landmarks (libraries, community centres, health, etc). */
    fetchLandmarks: ({ lat, lon, radius_km = 1, theme = null, limit = 25 } = {}) =>
      getJson('/api/landmarks/nearby', {
        lat, lon, radius_km, theme, limit
      }),

    /** Green spaces ranked by comfort score. */
    fetchGreenSpaces: ({ lat, lon, radius_km = 1, has_toilet = null, limit = 15 } = {}) =>
      getJson('/api/greenspace/nearby', {
        lat, lon, radius_km, has_toilet, limit
      }),
  }
}

/* Suburb autocomplete — duplicated from useResonanceApi for self-containment. */
export async function searchSuburbs(query, limit = 6) {
  if (!query || query.trim().length < 2) return []
  try {
    const data = await getJson('/api/suburbs/search', { q: query.trim(), limit })
    if (!data) return []
    return Array.isArray(data) ? data : (data.suburbs || data.results || [])
  } catch {
    return []
  }
}