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

          <button type="button" class="primary-btn" :disabled="!canFindRoute">
            Find My Route
          </button>
        </article>

        <article class="route-card">
          <div class="map-shell">
            <div ref="mapContainer" class="route-map"></div>
          </div>

          <div class="route-head">
            <p class="route-chip">Most comfortable for you</p>
            <p class="route-time">Depart 8:47 AM</p>
          </div>

          <h3>42 min</h3>

          <div class="steps">
            <p><strong>Walk to Hampshire Rd / Sunshine Rd</strong></p>
            <p>5 min · 350 m · Flat footpath, no crossings</p>
            <p><strong>Tram Route 57 towards City</strong></p>
            <p>Departs 8:52 AM · 9 stops · 28 min · Sit down, no transfers</p>
            <p><strong>Walk to Fitzroy Library</strong></p>
            <p>9 min · 600 m · Mostly flat, one gentle slope</p>
            <p><strong>Arrive Fitzroy Library</strong></p>
            <p>9:29 AM · 1 minute before the event starts</p>
          </div>

          <button type="button" class="primary-btn">Start this journey</button>
        </article>
    </section>
  </div>
</template>

<script setup>
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
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
let fromTimer = null
let toTimer = null
const mapContainer = ref(null)
let map = null
let previewLayer = null
let resizeObserver = null
const scrollY = ref(0)
const textScale = ref(100)
const { detectedLocationText, setDetectedLocation, setDetectedUnavailable } = useLocationState()
const LOCATION_UNAVAILABLE_TEXT = 'Location not available'
const MELBOURNE_NOT_FOUND = 'The location you specified was not found in Melbourne.'
const handleScroll = () => { scrollY.value = window.scrollY }

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
    .filter(item => item.label)
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

const drawMapPreview = () => {
  if (!map || !previewLayer) return
  previewLayer.clearLayers()

  const hasFrom = fromLat.value != null && fromLon.value != null
  const hasTo = toLat.value != null && toLon.value != null

  if (!hasFrom && !hasTo) return

  const points = []
  if (hasFrom) {
    const start = [fromLat.value, fromLon.value]
    L.marker(start).addTo(previewLayer).bindTooltip('Start')
    points.push(start)
  }

  if (hasTo) {
    const end = [toLat.value, toLon.value]
    L.marker(end).addTo(previewLayer).bindTooltip('Destination')
    points.push(end)
  }

  if (hasFrom && hasTo) {
    L.polyline(points, {
      color: '#0b7a6d',
      weight: 5,
      opacity: 0.9,
    }).addTo(previewLayer)
  }

  map.fitBounds(points, { padding: [28, 28], maxZoom: 14 })
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  if (!mapContainer.value) return
  map = L.map(mapContainer.value, { zoomControl: true }).setView([-37.8136, 144.9631], 11)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map)
  previewLayer = L.layerGroup().addTo(map)
  drawMapPreview()

  nextTick(() => {
    map?.invalidateSize()
  })

  resizeObserver = new ResizeObserver(() => {
    map?.invalidateSize()
  })
  resizeObserver.observe(mapContainer.value)
})

watch([fromLat, fromLon, toLat, toLon], () => {
  drawMapPreview()
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
  if (fromTimer) clearTimeout(fromTimer)
  if (toTimer) clearTimeout(toTimer)
  if (map) {
    map.remove()
    map = null
  }
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

.steps p {
  margin: 8px 0;
  color: #5d5f78;
  font-size: calc(18px * var(--font-scale));
}

.steps p strong {
  color: #2f3045;
  font-size: calc(20px * var(--font-scale));
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
