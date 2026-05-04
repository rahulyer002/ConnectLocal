<template>
  <div class="journey-page">
    <div class="noise" aria-hidden="true"></div>
    <div class="orb orb-1" aria-hidden="true"></div>
    <div class="orb orb-2" aria-hidden="true"></div>

    <nav class="nav" :class="{ scrolled: scrollY > 60 }">
      <div class="nav-brand">
        <div class="nav-logo">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/>
            <circle cx="12" cy="10" r="2.5"/>
          </svg>
        </div>
        <span class="nav-wordmark"><em>Connect</em>Local</span>
      </div>
      <div class="nav-links" role="navigation" aria-label="Main navigation">
        <RouterLink to="/home">Home</RouterLink>
        <RouterLink to="/discover">Events</RouterLink>
        <RouterLink to="/journey">Journey</RouterLink>
        <RouterLink to="/best-time">Best Time</RouterLink>
      </div>
      <RouterLink to="/checkin" class="nav-cta" aria-label="Start your wellbeing check-in">
        Start Check-in
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M5 12h14M13 5l7 7-7 7"/>
        </svg>
      </RouterLink>
    </nav>

    <div class="a11y-bar" role="region" aria-label="Accessibility options">
      <div class="a11y-inner">
        <div class="text-size-control" role="group" aria-label="Adjust text size">
          <span class="a-small" aria-hidden="true">A</span>
          <input
            type="range"
            class="text-slider"
            min="90"
            max="140"
            step="5"
            v-model.number="textScale"
            aria-label="Text size"
            aria-valuemin="90"
            aria-valuemax="140"
            :aria-valuenow="textScale"
            :aria-valuetext="`Text size ${textScale}%`"
          />
          <span class="a-large" aria-hidden="true">A</span>
          <span class="scale-pct" aria-hidden="true">{{ textScale }}%</span>
        </div>
      </div>
    </div>

    <section class="hero-banner">
        <h2>
          Get there
          <span>comfortably</span>
        </h2>
        <p class="hero-copy">
          Step-by-step travel guidance from your front door. Fewer transfers, less
          walking, and a clear time to leave home.
        </p>
    </section>

    <section class="main-content">
        <article class="journey-form-card">
          <h3>Your Location</h3>
          <form class="location-picker" @submit.prevent="applyManualLocation">
            <div class="field destination input-row">
              <input
                v-model="fromLocation"
                @focus="handleLocationInputFocus"
                @input="onFromInput"
                class="input-field"
                type="text"
                placeholder="Please enter suburb or postcode in Melbourne."
              />
              <ul v-if="showFromSuggestions" class="suggestions-list">
                <li v-for="item in fromSuggestions" :key="item.id">
                  <button type="button" class="suggestion-item" @mousedown.prevent="selectFromSuggestion(item)">
                    {{ item.label }}
                  </button>
                </li>
              </ul>
              <button type="button" class="secondary-btn" :disabled="isLocating" @click="getLocation">
                {{ isLocating ? 'Locating...' : 'Locate' }}
              </button>
              <button type="submit" class="secondary-btn" :disabled="isApplying || !fromLocation.trim()">
                {{ isApplying ? 'Updating...' : 'Change' }}
              </button>
            </div>
          </form>

          <h3>Going To</h3>
          <div class="destination-wrap">
            <input
              v-model.trim="toLocation"
              class="field destination input-field"
              type="text"
              placeholder="Enter destination"
              @input="onToInput"
              @blur="hideToSuggestions"
              @focus="reopenToSuggestions"
            />
            <ul v-if="showToSuggestions" class="suggestions-list">
              <li v-for="item in toSuggestions" :key="item.id">
                <button type="button" class="suggestion-item" @mousedown.prevent="selectToSuggestion(item)">
                  {{ item.label }}
                </button>
              </li>
            </ul>
          </div>

          <button type="button" class="primary-btn" :disabled="!canFindRoute || isPlanning" @click="findRoute">
            Find My Route
          </button>
        </article>

        <article class="route-card">
          <div class="map-shell">
            <div ref="mapContainer" class="route-map"></div>
            <p v-if="mapError" class="map-error">{{ mapError }}</p>
            <p v-if="planError" class="map-error">{{ planError }}</p>
          </div>

          <div class="route-head">
            <p class="route-chip">Most comfortable for you</p>
            <p class="route-time">{{ planData.departure_time || '--:--' }} → {{ planData.arrival_time || '--:--' }}</p>
          </div>

          <h3>{{ planData.total_duration_label || 'Route not loaded' }}</h3>
          <p class="route-meta">{{ planData.total_distance_label || '--' }} · {{ planData.total_walk_label || '--' }}</p>
          <p class="route-meta" v-if="planData.mode || planData.provider">
            {{ planData.mode || 'mode n/a' }} · {{ planData.provider || 'provider n/a' }} · Route {{ planData.route_index + 1 }}
          </p>
          <p class="route-meta" v-if="planData.total_duration_mins || planData.total_duration_secs">
            {{ planData.total_duration_mins || '--' }} mins · {{ planData.total_duration_secs || '--' }} secs
          </p>
          <p class="route-meta" v-if="planData.summary">{{ planData.summary }}</p>
          <p class="route-meta" v-if="planData.waypoints?.origin"><strong>From:</strong> {{ planData.waypoints.origin }}</p>
          <p class="route-meta" v-if="planData.waypoints?.destination"><strong>To:</strong> {{ planData.waypoints.destination }}</p>
          <div class="trip-key-info" v-if="planData.total_duration_label">
            <p>
              <strong>{{ planData.leave_home_by ? 'Leave home:' : 'Suggested start time:' }}</strong>
              {{ planData.leave_home_by || planData.departure_time || '--:--' }}
            </p>
            <p><strong>Vehicle:</strong> {{ firstTransitVehicle || 'No transit leg' }}</p>
            <p><strong>Transit departs:</strong> {{ firstTransitDeparture || '--:--' }}</p>
          </div>

          <h4 class="section-title" v-if="displayLegs.length">Route Summary</h4>
          <div class="steps" v-if="displayLegs.length">
            <p v-for="(leg, idx) in displayLegs" :key="`leg-${idx}`">
              <strong>{{ leg?.label || leg?.type || 'Leg' }}</strong>
              <span v-if="leg?.duration_label"> · {{ leg.duration_label }}</span>
              <span v-if="leg?.distance_label"> · {{ leg.distance_label }}</span>
              <span v-if="leg?.num_stops != null"> · {{ leg.num_stops }} stops</span>
              <span v-if="leg?.departure_time"> · departs {{ leg.departure_time }}</span>
            </p>
          </div>

          <p class="warning-note" v-if="displayWarnings.length">
            {{ displayWarnings.join(' · ') }}
          </p>

          <h4 class="section-title" v-if="displaySteps.length">Step-by-step Directions</h4>
          <div class="steps" v-if="displaySteps.length">
            <div v-for="(step, idx) in displaySteps" :key="`step-${idx}`" class="step-item">
              <p>
                <strong>{{ step?.instruction || step?.label || step?.type || 'Step' }}</strong>
                <span v-if="step?.duration_label"> · {{ step.duration_label }}</span>
                <span v-if="step?.distance_label"> · {{ step.distance_label }}</span>
              </p>
              <p v-if="step?.transit_info" class="step-transit">
                {{ step.transit_info.vehicle_name || step.transit_info.vehicle_type || 'Transit' }}
                {{ step.transit_info.line_name ? ` ${step.transit_info.line_name}` : '' }}
                <span v-if="step.transit_info.departure_stop || step.transit_info.arrival_stop">
                  · {{ step.transit_info.departure_stop || '--' }} → {{ step.transit_info.arrival_stop || '--' }}
                </span>
                <span v-if="step.transit_info.departure_time || step.transit_info.arrival_time">
                  · {{ step.transit_info.departure_time || '--:--' }} → {{ step.transit_info.arrival_time || '--:--' }}
                </span>
                <span v-if="step.transit_info.num_stops != null"> · {{ step.transit_info.num_stops }} stops</span>
              </p>
              <ul v-if="filteredSubSteps(step).length" class="sub-steps">
                <li v-for="(sub, subIdx) in filteredSubSteps(step)" :key="`sub-${idx}-${subIdx}`">
                  {{ sub.instruction }}
                  <span v-if="sub.distance_label"> · {{ sub.distance_label }}</span>
                </li>
              </ul>
            </div>
          </div>
          <div class="steps" v-else>
            <p>Find route to load step-by-step guidance.</p>
          </div>

        </article>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useLocationState } from '../composables/useLocationState'

const route = useRoute()
const fromLocation = ref('')
const toLocation = ref('')
const fromLat = ref(null)
const fromLon = ref(null)
const toLat = ref(null)
const toLon = ref(null)
const isLocating = ref(false)
const isApplying = ref(false)
const fromLocationConfirmed = ref(false)
const fromSuggestions = ref([])
const toSuggestions = ref([])
const showFromSuggestions = ref(false)
const showToSuggestions = ref(false)
const isPlanning = ref(false)
const mapError = ref('')
const planError = ref('')
const planData = ref({
  mode: '',
  provider: '',
  route_index: 0,
  summary: '',
  total_duration_secs: null,
  total_duration_mins: null,
  total_duration_label: '',
  total_distance_label: '',
  total_walk_m: null,
  total_walk_label: '',
  departure_time: '',
  arrival_time: '',
  leave_home_by: '',
  warnings: [],
  legs_summary: [],
  steps: [],
  waypoints: null,
})

let fromTimer = null
let toTimer = null
const mapContainer = ref(null)
let map = null
let startMarker = null
let endMarker = null
let routePolyline = null
let resizeObserver = null
let googleMapsPromise = null

const scrollY = ref(0)
const textScale = ref(100)
const { detectedLocationText, setDetectedLocation, setDetectedUnavailable } = useLocationState()

const LOCATION_UNAVAILABLE_TEXT = 'Location not available'
const MELBOURNE_NOT_FOUND = 'The location you specified was not found in Melbourne.'
const JOURNEY_BASE_URL = import.meta.env.VITE_ACTIVITIES_API_URL || 'https://connectlocal.duckdns.org'
const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''

const handleScroll = () => {
  scrollY.value = window.scrollY
}

const n = (v) => (Number.isFinite(+v) ? +v : null)
const isPostcodeInput = (q) => /^\d{4}$/.test(q)
const isSuburbInput = (q) => /^[A-Za-z][A-Za-z\s'-]{1,59}$/.test(q)

const isValidManualLocation = (q) => {
  if (isPostcodeInput(q)) {
    const code = Number(q)
    return Number.isInteger(code) && code >= 3000 && code <= 3999
  }
  return isSuburbInput(q)
}

const isInMelbourne = (address = {}, displayName = '') => {
  const state = String(address.state || '').toLowerCase()
  const name = String(displayName || '').toLowerCase()
  const city = String(address.city || address.town || address.village || '').toLowerCase()
  const county = String(address.county || '').toLowerCase()
  const postcode = Number(String(address.postcode || ''))
  const metroPostcode = Number.isInteger(postcode) && postcode >= 3000 && postcode <= 3999

  if (!state.includes('victoria')) return false
  return (
    name.includes('melbourne') ||
    city.includes('melbourne') ||
    county.includes('melbourne') ||
    metroPostcode
  )
}

const formatSuburbPostcode = (address = {}) => {
  const suburb =
    address.suburb || address.neighbourhood || address.city_district || address.town || address.village || address.city || ''
  const postcode = address.postcode || ''
  return [suburb, postcode].filter(Boolean).join(', ').trim()
}

const setLocation = (text, lat = null, lon = null) => {
  fromLocation.value = text
  fromLocationConfirmed.value = true
  fromLat.value = n(lat)
  fromLon.value = n(lon)
  setDetectedLocation(text)
}

const setLocationUnavailable = () => {
  fromLocationConfirmed.value = false
  fromLat.value = null
  fromLon.value = null
  fromLocation.value = MELBOURNE_NOT_FOUND
  setDetectedUnavailable()
}

const handleLocationInputFocus = () => {
  if (fromLocation.value === MELBOURNE_NOT_FOUND) fromLocation.value = ''
}

const loadGoogleMaps = () => {
  if (window.google?.maps) return Promise.resolve(window.google.maps)
  if (!GOOGLE_MAPS_API_KEY) return Promise.reject(new Error('Missing VITE_GOOGLE_MAPS_API_KEY'))
  if (googleMapsPromise) return googleMapsPromise

  googleMapsPromise = new Promise((resolve, reject) => {
    const existing = document.getElementById('google-maps-sdk')
    if (existing) {
      existing.addEventListener('load', () => resolve(window.google.maps), { once: true })
      existing.addEventListener('error', reject, { once: true })
      return
    }

    const script = document.createElement('script')
    script.id = 'google-maps-sdk'
    script.async = true
    script.defer = true
    script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(GOOGLE_MAPS_API_KEY)}`
    script.onload = () => resolve(window.google.maps)
    script.onerror = reject
    document.head.appendChild(script)
  })

  return googleMapsPromise
}

const clearOverlays = () => {
  if (startMarker) {
    startMarker.setMap(null)
    startMarker = null
  }
  if (endMarker) {
    endMarker.setMap(null)
    endMarker = null
  }
  if (routePolyline) {
    routePolyline.setMap(null)
    routePolyline = null
  }
}

const drawMapPreview = () => {
  if (!map || !window.google?.maps) return
  clearOverlays()

  const hasFrom = fromLat.value != null && fromLon.value != null
  const hasTo = toLat.value != null && toLon.value != null
  if (!hasFrom && !hasTo) return

  const bounds = new window.google.maps.LatLngBounds()
  const path = []

  if (hasFrom) {
    const start = { lat: Number(fromLat.value), lng: Number(fromLon.value) }
    startMarker = new window.google.maps.Marker({ position: start, map, title: 'Start' })
    bounds.extend(start)
    path.push(start)
  }

  if (hasTo) {
    const end = { lat: Number(toLat.value), lng: Number(toLon.value) }
    endMarker = new window.google.maps.Marker({ position: end, map, title: 'Destination' })
    bounds.extend(end)
    path.push(end)
  }

  if (path.length === 2) {
    routePolyline = new window.google.maps.Polyline({
      path,
      map,
      strokeColor: '#0b7a6d',
      strokeWeight: 5,
      strokeOpacity: 0.9,
    })
  }

  map.fitBounds(bounds)
}

const drawGeometry = (geometry, waypoints = null) => {
  if (!map || !window.google?.maps) return

  const coords = geometry?.coordinates
  if (!Array.isArray(coords) || !coords.length) {
    drawMapPreview()
    return
  }

  clearOverlays()

  const path = coords
    .filter((pair) => Array.isArray(pair) && pair.length >= 2)
    .map(([lon, lat]) => ({ lat: Number(lat), lng: Number(lon) }))
    .filter((p) => Number.isFinite(p.lat) && Number.isFinite(p.lng))

  if (!path.length) {
    drawMapPreview()
    return
  }

  const originCoords = waypoints?.origin_coords
  const destinationCoords = waypoints?.destination_coords

  const start =
    originCoords && Number.isFinite(+originCoords.lat) && Number.isFinite(+originCoords.lon)
      ? { lat: Number(originCoords.lat), lng: Number(originCoords.lon) }
      : path[0]

  const end =
    destinationCoords && Number.isFinite(+destinationCoords.lat) && Number.isFinite(+destinationCoords.lon)
      ? { lat: Number(destinationCoords.lat), lng: Number(destinationCoords.lon) }
      : path[path.length - 1]

  startMarker = new window.google.maps.Marker({ position: start, map, title: 'Start' })
  endMarker = new window.google.maps.Marker({ position: end, map, title: 'Destination' })

  routePolyline = new window.google.maps.Polyline({
    path,
    map,
    strokeColor: '#0b7a6d',
    strokeWeight: 5,
    strokeOpacity: 0.9,
  })

  const bounds = new window.google.maps.LatLngBounds()
  path.forEach((p) => bounds.extend(p))
  map.fitBounds(bounds)
}

async function geocodePlace(query) {
  try {
    const text = `${query}, Melbourne, Victoria, Australia`
    const r = await fetch(
      `https://nominatim.openstreetmap.org/search?format=jsonv2&q=${encodeURIComponent(
        text
      )}&addressdetails=1&limit=5&accept-language=en&countrycodes=au`
    )
    const list = (await r.json()) || []
    const top = list.find((item) => isInMelbourne(item?.address, item?.display_name))
    if (!top) return null
    return { lat: n(top.lat), lon: n(top.lon) }
  } catch {
    return null
  }
}

async function searchSuggestions(query) {
  const text = `${query}, Melbourne, Victoria, Australia`
  const r = await fetch(
    `https://nominatim.openstreetmap.org/search?format=jsonv2&q=${encodeURIComponent(
      text
    )}&addressdetails=1&limit=6&accept-language=en&countrycodes=au`
  )
  const list = (await r.json()) || []
  return list
    .filter((item) => isInMelbourne(item?.address, item?.display_name))
    .map((item, index) => ({
      id: `${item.place_id || index}-${index}`,
      label: (item.display_name || '').trim(),
      lat: n(item.lat),
      lon: n(item.lon),
    }))
    .filter((item) => item.label)
}

const getLocation = () => {
  if (!navigator.geolocation) return setLocationUnavailable()

  isLocating.value = true
  navigator.geolocation.getCurrentPosition(
    async ({ coords }) => {
      try {
        const r = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${coords.latitude}&lon=${coords.longitude}&accept-language=en`
        )
        const top = await r.json()
        if (!isInMelbourne(top?.address, top?.display_name)) {
          setLocationUnavailable()
        } else {
          const label = (top?.display_name || '').trim() || formatSuburbPostcode(top?.address)
          label ? setLocation(label, coords.latitude, coords.longitude) : setLocationUnavailable()
        }
      } catch {
        setLocationUnavailable()
      } finally {
        isLocating.value = false
      }
    },
    () => {
      setLocationUnavailable()
      isLocating.value = false
    }
  )
}

const applyManualLocation = async () => {
  const q = fromLocation.value.trim()
  if (!q || !isValidManualLocation(q)) return setLocationUnavailable()

  isApplying.value = true
  try {
    const queryText = isPostcodeInput(q)
      ? `${q}, Victoria, Australia`
      : `${q}, Melbourne, Victoria, Australia`
    const r = await fetch(
      `https://nominatim.openstreetmap.org/search?format=jsonv2&q=${encodeURIComponent(
        queryText
      )}&addressdetails=1&limit=8&accept-language=en&countrycodes=au`
    )
    const list = (await r.json()) || []
    const top = list.find((item) => isInMelbourne(item?.address, item?.display_name))
    if (!top) {
      setLocationUnavailable()
    } else {
      const label = (top?.display_name || '').trim() || formatSuburbPostcode(top?.address)
      label ? setLocation(label, top?.lat, top?.lon) : setLocationUnavailable()
    }
  } catch {
    setLocationUnavailable()
  } finally {
    isApplying.value = false
  }
}

const onFromInput = () => {
  fromLocationConfirmed.value = false
  const q = fromLocation.value.trim()
  if (fromTimer) clearTimeout(fromTimer)

  if (q.length < 3 || q === MELBOURNE_NOT_FOUND) {
    showFromSuggestions.value = false
    fromSuggestions.value = []
    return
  }

  showFromSuggestions.value = true
  fromTimer = setTimeout(async () => {
    try {
      fromSuggestions.value = await searchSuggestions(q)
    } catch {
      fromSuggestions.value = []
    }
  }, 250)
}

const selectFromSuggestion = (item) => {
  setLocation(item.label, item.lat, item.lon)
  showFromSuggestions.value = false
}

const onToInput = () => {
  toLat.value = null
  toLon.value = null
  const q = toLocation.value.trim()
  if (toTimer) clearTimeout(toTimer)

  if (q.length < 3) {
    showToSuggestions.value = false
    toSuggestions.value = []
    return
  }

  showToSuggestions.value = true
  toTimer = setTimeout(async () => {
    try {
      toSuggestions.value = await searchSuggestions(q)
    } catch {
      toSuggestions.value = []
    }
  }, 250)
}

const selectToSuggestion = (item) => {
  toLocation.value = item.label
  toLat.value = n(item.lat)
  toLon.value = n(item.lon)
  showToSuggestions.value = false
}

const hideToSuggestions = () => {
  setTimeout(() => {
    showToSuggestions.value = false
  }, 120)
}

const reopenToSuggestions = () => {
  if (toSuggestions.value.length) showToSuggestions.value = true
}

const emptyPlanState = () => ({
  mode: '',
  provider: '',
  route_index: 0,
  summary: '',
  total_duration_secs: null,
  total_duration_mins: null,
  total_duration_label: '',
  total_distance_label: '',
  total_walk_m: null,
  total_walk_label: '',
  departure_time: '',
  arrival_time: '',
  leave_home_by: '',
  warnings: [],
  legs_summary: [],
  steps: [],
  waypoints: null,
})

const filteredSubSteps = (step) => {
  const raw = Array.isArray(step?.sub_steps) ? step.sub_steps : []
  return raw.filter((sub) => {
    const instruction = String(sub?.instruction || '').trim()
    return instruction.length > 0
  })
}

const findRoute = async () => {
  if (fromLat.value == null || fromLon.value == null || toLat.value == null || toLon.value == null) return

  isPlanning.value = true
  planError.value = ''
  planData.value = emptyPlanState()
  clearOverlays()
  try {
    const u = new URL(`${JOURNEY_BASE_URL}/api/journey/google/plan`)
    u.searchParams.set('from_lat', String(fromLat.value))
    u.searchParams.set('from_lon', String(fromLon.value))
    u.searchParams.set('to_lat', String(toLat.value))
    u.searchParams.set('to_lon', String(toLon.value))
    u.searchParams.set('mode', 'transit')

    const res = await fetch(u.toString())
    if (!res.ok) throw new Error(`Plan API failed: ${res.status}`)
    const data = await res.json()

    planData.value = {
      ...emptyPlanState(),
      mode: data?.mode || '',
      provider: data?.provider || '',
      route_index: Number.isFinite(+data?.route_index) ? Number(data.route_index) : 0,
      summary: data?.summary || '',
      total_duration_secs: Number.isFinite(+data?.total_duration_secs) ? Number(data.total_duration_secs) : null,
      total_duration_mins: Number.isFinite(+data?.total_duration_mins) ? Number(data.total_duration_mins) : null,
      total_duration_label: data?.total_duration_label || '',
      total_distance_label: data?.total_distance_label || '',
      total_walk_m: Number.isFinite(+data?.total_walk_m) ? Number(data.total_walk_m) : null,
      total_walk_label: data?.total_walk_label || '',
      departure_time: data?.departure_time || '',
      arrival_time: data?.arrival_time || '',
      leave_home_by: data?.leave_home_by || data?.leave_by || '',
      warnings: Array.isArray(data?.warnings) ? data.warnings.filter(Boolean) : [],
      legs_summary: Array.isArray(data?.legs_summary) ? data.legs_summary.filter(Boolean) : [],
      steps: Array.isArray(data?.steps) ? data.steps.filter(Boolean) : [],
      waypoints: data?.waypoints || null,
    }

    drawGeometry(data?.geometry, data?.waypoints)
  } catch (err) {
    planError.value = 'Route data failed to render. Please try again.'
    console.error('[Journey] findRoute failed:', err)
    drawMapPreview()
  } finally {
    isPlanning.value = false
  }
}

watch(
  detectedLocationText,
  async (value) => {
    const normalized = (value || '').trim()
    if (normalized && normalized !== LOCATION_UNAVAILABLE_TEXT) {
      fromLocation.value = normalized
      fromLocationConfirmed.value = true
      if (fromLat.value == null || fromLon.value == null) {
        const point = await geocodePlace(normalized)
        if (point) {
          fromLat.value = point.lat
          fromLon.value = point.lon
        }
      }
    }
  },
  { immediate: true }
)

watch(
  () => route.query.destination,
  async (value) => {
    const destination = String(value || '').trim()
    if (!destination) return
    toLocation.value = destination
    const point = await geocodePlace(destination)
    if (point) {
      toLat.value = point.lat
      toLon.value = point.lon
    }
  },
  { immediate: true }
)

const canFindRoute = computed(() => {
  return fromLocationConfirmed.value && toLocation.value.trim().length >= 3
})

const displayLegs = computed(() =>
  Array.isArray(planData.value.legs_summary) ? planData.value.legs_summary.filter(Boolean) : []
)
const displayWarnings = computed(() =>
  Array.isArray(planData.value.warnings) ? planData.value.warnings.filter(Boolean) : []
)
const displaySteps = computed(() =>
  Array.isArray(planData.value.steps) ? planData.value.steps.filter(Boolean) : []
)

const firstTransitLeg = computed(() => {
  if (!displayLegs.value.length) return null
  return displayLegs.value.find((leg) => String(leg?.type || '').toLowerCase() === 'transit') || null
})

const firstTransitStep = computed(() => {
  if (!displaySteps.value.length) return null
  return displaySteps.value.find((step) => String(step?.travel_mode || '').toLowerCase() === 'transit') || null
})

const firstTransitVehicle = computed(() => {
  const leg = firstTransitLeg.value
  if (leg?.label) return leg.label
  const info = firstTransitStep.value?.transit_info
  if (!info) return ''
  const vehicle = info.vehicle_name || info.vehicle_type || 'Transit'
  const line = info.line_name ? ` ${info.line_name}` : ''
  return `${vehicle}${line}`.trim()
})

const firstTransitDeparture = computed(() => {
  const leg = firstTransitLeg.value
  if (leg?.departure_time) return leg.departure_time
  const info = firstTransitStep.value?.transit_info
  return info?.departure_time || ''
})

watch([fromLat, fromLon, toLat, toLon], () => {
  drawMapPreview()
})

onMounted(async () => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  if (!mapContainer.value) return

  try {
    await loadGoogleMaps()
  } catch {
    mapError.value = 'Google Map failed to load. Check VITE_GOOGLE_MAPS_API_KEY and API key restrictions.'
    return
  }

  map = new window.google.maps.Map(mapContainer.value, {
    center: { lat: -37.8136, lng: 144.9631 },
    zoom: 11,
    mapTypeControl: false,
    streetViewControl: false,
    fullscreenControl: false,
  })

  drawMapPreview()

  nextTick(() => {
    window.google?.maps?.event.trigger(map, 'resize')
  })

  resizeObserver = new ResizeObserver(() => {
    window.google?.maps?.event.trigger(map, 'resize')
  })
  resizeObserver.observe(mapContainer.value)
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
  if (fromTimer) clearTimeout(fromTimer)
  if (toTimer) clearTimeout(toTimer)
  clearOverlays()
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
})
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.journey-page {
  min-height: 100vh;
  background: #f2faf0;
  color: #1a2e1e;
  font-family: system-ui, sans-serif;
  position: relative;
  overflow-x: hidden;
}

.noise {
  position: fixed; inset: 0; z-index: 1000; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  background-size: 180px; opacity: 0.45;
}

.orb { position: fixed; border-radius: 50%; pointer-events: none; z-index: 0; filter: blur(80px); }
.orb-1 { width: 500px; height: 500px; background: rgba(90,180,110,0.18); top: -100px; left: -80px; animation: orb-drift 22s ease-in-out infinite alternate; }
.orb-2 { width: 380px; height: 380px; background: rgba(255,180,140,0.12); bottom: 5%; right: -60px; animation: orb-drift 28s ease-in-out infinite alternate-reverse; }
@keyframes orb-drift { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(40px,50px) scale(1.1)} }

.nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 24px 52px; transition: background 0.4s, padding 0.4s, box-shadow 0.4s;
}
.nav.scrolled { background: rgba(242,250,240,0.9); backdrop-filter: blur(18px); padding: 16px 52px; box-shadow: 0 1px 0 rgba(29,113,105,0.12); }
.nav-brand { display: flex; align-items: center; gap: 12px; }
.nav-logo { width: 38px; height: 38px; border-radius: 50%; background: linear-gradient(135deg,#0a9b8a,#056b5e); color: white; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 16px rgba(7,141,127,0.3); }
.nav-wordmark { font-family: Georgia,serif; font-size: 20px; color: #1a2e1e; }
.nav-wordmark em { color: #0a9b8a; font-style: italic; }
.nav-links { display: flex; gap: 32px; align-items: center; }
.nav-links a { font-size: 15px; font-weight: 600; color: #3a5a3e; text-decoration: none; transition: color 0.2s; }
.nav-links a:hover { color: #0a9b8a; }
.nav-links .router-link-active { color: #0a9b8a; }
.nav-cta { display: inline-flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 700; color: #0a9b8a; text-decoration: none; padding: 10px 22px; border: 1.5px solid #0a9b8a; border-radius: 999px; transition: all 0.3s; }
.nav-cta:hover { background: #0a9b8a; color: white; }

.a11y-bar {
  position: fixed; top: 86px; right: 0; left: 0; z-index: 90;
  background: rgba(255,255,255,0.92); backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(29,113,105,0.1);
  box-shadow: 0 4px 16px rgba(0,0,0,0.04);
}
.a11y-inner { display: flex; align-items: center; justify-content: flex-end; padding: 10px 52px; }
.text-size-control {
  display: inline-flex; align-items: center; gap: 12px;
  background: rgba(255,255,255,0.9); backdrop-filter: blur(10px);
  border: 1.5px solid rgba(29,113,105,0.18); border-radius: 999px; padding: 8px 18px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.06);
}
.a-small { font-family: Georgia,serif; font-size: 13px; font-weight: 700; color: #0a9b8a; line-height: 1; }
.a-large { font-family: Georgia,serif; font-size: 22px; font-weight: 700; color: #0a9b8a; line-height: 1; }
.text-slider { -webkit-appearance: none; appearance: none; width: 120px; height: 4px; background: #d1e8d4; border-radius: 999px; outline: none; cursor: pointer; }
.text-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 22px; height: 22px; border-radius: 50%; background: #0a9b8a; box-shadow: 0 2px 8px rgba(10,155,138,0.4); cursor: pointer; }
.scale-pct { font-size: 13px; font-weight: 700; color: #6a8e6e; min-width: 38px; }

.hero-banner {
  background: radial-gradient(circle at 92% 20%, #2b7e71 0 160px, transparent 161px),
    linear-gradient(180deg, #0a7468 0%, #07685d 100%);
  color: #f4f8f8;
  padding: 190px 44px 40px;
  position: relative;
  z-index: 1;
}

.hero-banner h2 {
  margin: 0;
  font-family: 'Fraunces', serif;
  font-size: clamp(calc(36px * var(--font-scale)), calc(4vw * var(--font-scale)), calc(56px * var(--font-scale)));
  line-height: 1;
}

.hero-banner h2 span {
  display: block;
  color: #f4bf2c;
  font-style: italic;
}

.hero-copy {
  margin: 18px 0 0;
  max-width: 1200px;
  font-size: clamp(calc(18px * var(--font-scale)), calc(2.2vw * var(--font-scale)), calc(34px * var(--font-scale)));
  color: #d1ece6;
}

.main-content {
  padding: 22px 40px 40px;
  display: grid;
  gap: 22px;
  position: relative;
  z-index: 1;
}

.journey-form-card,
.route-card {
  border: 2px solid #cbccdf;
  border-radius: 20px;
  background: var(--panel-2);
  padding: 20px;
}

.route-card {
  border-color: #0b7a6d;
}

.map-shell {
  margin-bottom: 16px;
}

.map-error {
  margin-top: 8px;
  color: #b13030;
  font-size: 14px;
  font-weight: 700;
}

.route-map {
  width: 100%;
  height: 580px;
  border: 2px solid #0b7a6d;
  border-radius: 14px;
  overflow: hidden;
}

h3 {
  margin: 0 0 14px;
  color: #585a7b;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-size: calc(18px * var(--font-scale));
}

.field {
  border: 2px solid #c7c8dc;
  border-radius: 16px;
  background: #fff;
  padding: 12px 14px;
  color: #2f3148;
  font-size: clamp(calc(18px * var(--font-scale)), calc(2vw * var(--font-scale)), calc(28px * var(--font-scale)));
  font-weight: 800;
  margin-bottom: 16px;
}

.field.destination {
  background: #dfebe8;
  border-color: #0b7a6d;
}

.location-picker {
  width: 100%;
  display: block;
  margin-bottom: 16px;
}

.input-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 0;
  position: relative;
}

.primary-btn {
  border-radius: 22px;
  border: 4px solid #0b7a6d;
  font-size: calc(20px * var(--font-scale));
  font-weight: 800;
  cursor: pointer;
}

.primary-btn {
  width: 100%;
  background: #0b7a6d;
  color: #fff;
  padding: 24px 20px;
  box-shadow: 0 12px 26px rgba(6, 110, 98, 0.18);
}

.secondary-btn {
  border: 2px solid #c7c8dc;
  border-radius: 999px;
  background: transparent;
  color: #616580;
  font-size: calc(16px * var(--font-scale));
  font-weight: 800;
  padding: 10px 18px;
  cursor: pointer;
  height: fit-content;
}

.secondary-btn:disabled {
  opacity: 0.75;
  cursor: wait;
}

.primary-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  box-shadow: none;
}

.input-field {
  width: 100%;
}

.input-field::placeholder {
  color: #9a9db3;
}

.location-picker .input-field {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  padding: 0;
  margin: 0;
  font-family: 'Manrope', sans-serif;
  font-size: clamp(calc(18px * var(--font-scale)), calc(2vw * var(--font-scale)), calc(28px * var(--font-scale)));
  font-weight: 800;
  line-height: 1.2;
  color: #2f3148;
}

.destination-wrap {
  position: relative;
}

.suggestions-list {
  position: absolute;
  left: 0;
  right: 0;
  top: calc(100% - 10px);
  margin: 0;
  padding: 8px;
  list-style: none;
  background: #fff;
  border: 2px solid #c7c8dc;
  border-radius: 14px;
  box-shadow: 0 8px 20px rgba(42, 46, 68, 0.12);
  z-index: 20;
  max-height: 240px;
  overflow: auto;
}

.suggestion-item {
  width: 100%;
  border: none;
  background: transparent;
  text-align: left;
  font-family: 'Manrope', sans-serif;
  color: #2f3148;
  font-size: calc(16px * var(--font-scale));
  border-radius: 10px;
  padding: 10px 8px;
  cursor: pointer;
}

.suggestion-item:hover {
  background: #eef3fb;
}

.route-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.route-chip {
  margin: 0;
  border-radius: 999px;
  background: #d6ece8;
  color: #0b7a6d;
  padding: 8px 18px;
  font-size: calc(16px * var(--font-scale));
  font-weight: 800;
}

.route-time {
  margin: 0;
  color: #0b7a6d;
  font-size: calc(16px * var(--font-scale));
  font-weight: 800;
}

.route-card h3 {
  margin-top: 14px;
  text-transform: none;
  letter-spacing: 0;
  color: #2e3047;
  font-family: 'Fraunces', serif;
  font-size: clamp(calc(30px * var(--font-scale)), calc(3vw * var(--font-scale)), calc(46px * var(--font-scale)));
}

.route-meta {
  margin: 0 0 10px;
  color: #5d5f78;
  font-size: calc(16px * var(--font-scale));
  font-weight: 700;
}

.section-title {
  margin: 12px 0 6px;
  color: #4f5271;
  font-size: calc(16px * var(--font-scale));
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.warning-note {
  margin: 8px 0 10px;
  color: #7a6a35;
  background: #fff5d6;
  border: 1px solid #ecdca3;
  border-radius: 10px;
  padding: 8px 10px;
  font-size: calc(14px * var(--font-scale));
}

.trip-key-info {
  margin: 0 0 12px;
  padding: 10px 12px;
  border: 1px solid #d5d8e8;
  border-radius: 12px;
  background: #f7f9ff;
}

.trip-key-info p {
  margin: 6px 0;
  color: #3d405b;
  font-size: calc(16px * var(--font-scale));
}

.steps p {
  margin: 8px 0;
  color: #5d5f78;
  font-size: calc(18px * var(--font-scale));
}

.steps p strong {
  color: #2f3045;
  font-size: calc(20px * var(--font-scale));
}

.step-item {
  margin: 8px 0 10px;
}

.step-transit {
  margin: 2px 0 0;
  color: #4e6f65;
  font-size: calc(15px * var(--font-scale));
  font-weight: 700;
}

.sub-steps {
  margin: 6px 0 0 18px;
  color: #5d5f78;
}

.sub-steps li {
  margin: 4px 0;
  font-size: calc(15px * var(--font-scale));
}

@media (max-width: 980px) {
  .nav { padding: 16px 18px; }
  .nav-links { display: none; }
  .a11y-inner { padding: 10px 18px; }

  .hero-banner {
    padding: 24px 18px 30px;
    margin-top: 132px;
  }

  .main-content {
    padding: 16px;
  }

  .location-picker {
    display: block;
  }

  .input-row {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
