<template>
  <MainLayout>
    <div class="journey-page">
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
  </MainLayout>
</template>

<script setup>
import 'leaflet/dist/leaflet.css'
import MainLayout from '../layouts/MainLayout.vue'
import L from 'leaflet'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useLocationState } from '../composables/useLocationState'

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
const { detectedLocationText, setDetectedLocation, setDetectedUnavailable } = useLocationState()
const LOCATION_UNAVAILABLE_TEXT = 'Location not available'
const MELBOURNE_NOT_FOUND = 'The location you specified was not found in Melbourne.'

watch(
  detectedLocationText,
  (value) => {
    const normalized = (value || '').trim()
    if (normalized && normalized !== LOCATION_UNAVAILABLE_TEXT) {
      fromLocation.value = normalized
      fromLocationConfirmed.value = true
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
  return state.includes('victoria') && name.includes('melbourne')
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

const searchSuggestions = async (query) => {
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
.journey-page {
  min-height: 100vh;
  background: #f5f5fa;
}

.hero-banner {
  background: radial-gradient(circle at 92% 20%, #2b7e71 0 160px, transparent 161px),
    linear-gradient(180deg, #0a7468 0%, #07685d 100%);
  color: #f4f8f8;
  padding: 26px 44px 40px;
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
  .hero-banner {
    padding: 24px 18px 30px;
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
