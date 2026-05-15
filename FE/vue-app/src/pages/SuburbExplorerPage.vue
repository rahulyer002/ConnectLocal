<template>
  <MainLayout>
    <main class="suburb-explorer-page">
      <section class="map-card">

        <section class="map-area">
          <div class="legend">
            <h4>Crowd Level</h4>
            <p><span class="dot very-quiet"></span> Very Quiet</p>
            <p><span class="dot quiet"></span> Quiet</p>
            <p><span class="dot moderate"></span> Moderate</p>
            <p><span class="dot busy"></span> Busy</p>
          </div>

          <div class="map-title-pill">📍 Melbourne Suburb Explorer</div>
          <div class="epic-pill">EPIC 6.0</div>

          <div v-if="loadingMap" class="map-message">
            Loading suburbs...
          </div>

          <div v-else-if="mapError" class="map-message error">
            {{ mapError }}
          </div>

          <div v-else class="suburb-map">
            <button
              v-for="(suburb, index) in visibleSuburbs"
              :key="getSuburbId(suburb) || index"
              class="suburb-hex"
              :class="[
                crowdClass(getCrowdLevel(suburb)),
                { active: selectedSuburbId === getSuburbId(suburb) }
              ]"
              :style="getSuburbPosition(index)"
              @click="selectSuburb(suburb)"
            >
              {{ shortName(getSuburbName(suburb)) }}
            </button>
          </div>

          <div class="water-shape"></div>

          <footer class="bottom-tabs">
            <RouterLink to="/home">🏠 Home</RouterLink>
            <RouterLink to="/discover">🎟 Events</RouterLink>
            <RouterLink to="/journey">🚌 Journey</RouterLink>
            <RouterLink to="/best-time">⏰ Best Time</RouterLink>
            <RouterLink to="/checkin">✅ Check-in</RouterLink>
            <span>🤖 AI Guide</span>
            <strong>🌏 Suburbs</strong>
          </footer>
        </section>
      </section>

      <aside class="detail-panel">
        <div v-if="!selectedSuburb" class="empty-state">
          <div class="empty-icon">🗺️</div>
          <h2>Select a suburb</h2>
          <p>
            Click any suburb on the map to see live crowd levels, weather,
            pedestrian counts, and nearby events.
          </p>

          <div class="mini-legend">
            <p><span class="dot very-quiet"></span> Very Quiet — Great time to visit</p>
            <p><span class="dot quiet"></span> Quiet — Good conditions</p>
            <p><span class="dot moderate"></span> Moderate — Fairly busy</p>
            <p><span class="dot busy"></span> Busy — Consider visiting later</p>
          </div>
        </div>

        <div v-else>
          <button class="back-button" @click="clearSelection">
            ← Back to map
          </button>

          <h2 class="suburb-title">{{ selectedSuburbName }}</h2>

          <div v-if="loadingDetails" class="detail-message">
            Loading suburb details...
          </div>

          <div v-if="detailError" class="detail-message error">
            {{ detailError }}
          </div>

          <section class="info-card">
            <h3>Live pedestrian data</h3>
            <p class="big-number">{{ pedestrianPeopleText }}</p>
            <p>{{ pedestrianLevelText }}</p>
          </section>

          <section class="info-card">
            <h3>Weather right now</h3>
            <p>{{ weatherText }}</p>
          </section>

          <section class="info-card">
            <h3>Nearby events</h3>

            <p v-if="events.length === 0">
              No nearby events found.
            </p>

            <ul v-else class="event-list">
              <li v-for="event in events.slice(0, 3)" :key="event.id || event.title || event.name">
                <strong>{{ event.title || event.name || 'Untitled event' }}</strong>
                <span>
                  {{ event.date || event.start_time || event.time || event.venue || '' }}
                </span>
              </li>
            </ul>
          </section>

          <section class="info-card">
            <h3>Accessibility</h3>
            <p>{{ accessibilityText }}</p>
          </section>

          <section class="action-list">
            <button @click="goToDiscover">
              🎟 Find events in this suburb →
            </button>
            <button @click="goToJourney">
              🚌 Plan a journey here →
            </button>
            <button @click="goToBestTime">
              ⏰ Check best time to visit →
            </button>
          </section>
        </div>
      </aside>
    </main>
  </MainLayout>
</template>

<script setup>
import MainLayout from '../layouts/MainLayout.vue'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import {
  fetchSuburbAccessibility,
  fetchSuburbEvents,
  fetchSuburbMap,
  fetchSuburbPedestrian,
  fetchSuburbSnapshot,
  fetchSuburbWeather,
} from '../composables/suburbExplorerApi'

const router = useRouter()

const suburbs = ref([])
const selectedSuburb = ref(null)
const selectedSuburbId = ref(null)

const snapshot = ref(null)
const pedestrian = ref(null)
const weather = ref(null)
const events = ref([])
const accessibility = ref(null)

const loadingMap = ref(false)
const loadingDetails = ref(false)
const mapError = ref('')
const detailError = ref('')

const preferredSuburbs = [
  'Melbourne CBD - East',
  'Melbourne CBD - West',
  'Carlton',
  'Docklands',
  'Southbank',
  'North Melbourne',
  'East Melbourne',
  'Richmond',
  'Collingwood',
  'Fitzroy',
  'Parkville',
  'St Kilda',
  'Prahran',
  'Hawthorn',
  'Kew',
  'Camberwell',
  'Footscray',
  'Preston',
  'Coburg',
  'Brunswick',
  'Northcote',
  'Toorak',
  'Port Melbourne',
  'South Yarra',
]

const visibleSuburbs = computed(() => {
  const preferred = suburbs.value.filter((suburb) =>
    preferredSuburbs.some((name) =>
      getSuburbName(suburb).toLowerCase().includes(name.toLowerCase())
    )
  )

  if (preferred.length >= 10) {
    return preferred.slice(0, 24)
  }

  return suburbs.value.slice(0, 24)
})

const selectedSuburbName = computed(() => {
  if (!selectedSuburb.value) return ''
  return getSuburbName(selectedSuburb.value)
})

const pedestrianPeopleText = computed(() => {
  const data = pedestrian.value

  if (!data || data.available === false || data.people_per_hour == null) {
    return 'No live count available'
  }

  return `${data.people_per_hour} people/hr`
})

const pedestrianLevelText = computed(() => {
  const data = pedestrian.value

  if (!data || data.available === false) {
    return 'Crowd level not available'
  }

  const level = data.crowd_level || data.raw_crowd_label || 'Crowd level not available'
  const trend = data.trend ? ` · ${data.trend}` : ''

  return `${level}${trend}`
})

const weatherText = computed(() => {
  const data = weather.value || snapshot.value

  const temp =
    data?.temperature_c ??
    data?.temperature ??
    data?.current?.temperature

  const feelsLike =
    data?.feels_like_c ??
    data?.feels_like ??
    data?.current?.feels_like

  const humidity =
    data?.humidity_pct ??
    data?.humidity ??
    data?.current?.humidity

  const windSpeed =
    data?.wind_speed_kmh ??
    data?.wind_speed ??
    data?.current?.wind_speed

  const condition =
    data?.summary ||
    data?.condition ||
    data?.weather_description ||
    data?.current?.condition

  if (
    temp === undefined &&
    feelsLike === undefined &&
    humidity === undefined &&
    windSpeed === undefined &&
    !condition
  ) {
    return 'Weather information not available.'
  }

  const parts = []

  if (temp !== undefined && temp !== null) {
    parts.push(`${temp}°C`)
  }

  if (feelsLike !== undefined && feelsLike !== null) {
    parts.push(`Feels like ${feelsLike}°C`)
  }

  if (humidity !== undefined && humidity !== null) {
    parts.push(`Humidity ${humidity}%`)
  }

  if (windSpeed !== undefined && windSpeed !== null) {
    parts.push(`Wind ${windSpeed} km/h`)
  }

  if (condition) {
    parts.push(condition)
  }

  return parts.join(' - ')
})

const accessibilityText = computed(() => {
  const data = accessibility.value

  if (!data) return 'Accessibility information not available.'

  const benches = data.benches
  const toilets = data.accessible_toilets
  const wheelchairPlaces = data.wheelchair_places
  const placesByCategory = data.places_by_category

  const parts = []

  if (benches !== undefined) parts.push(`${benches} benches`)
  if (toilets !== undefined) parts.push(`${toilets} accessible toilets`)
  if (wheelchairPlaces !== undefined) parts.push(`${wheelchairPlaces} wheelchair-friendly places`)

  if (parts.length > 0) {
    return parts.join(', ')
  }

  if (placesByCategory) {
    return 'Accessibility places are available for this suburb.'
  }

  return 'No accessibility summary available for this suburb.'
})

function getSuburbId(suburb) {
  return (
    suburb.suburb_id ||
    suburb.id ||
    suburb.sa2_code ||
    suburb.SA2_CODE21 ||
    suburb.properties?.suburb_id ||
    suburb.properties?.id ||
    suburb.properties?.SA2_CODE21
  )
}

function getSuburbName(suburb) {
  return (
    suburb.suburb_name ||
    suburb.name ||
    suburb.suburb ||
    suburb.SA2_NAME21 ||
    suburb.properties?.suburb_name ||
    suburb.properties?.name ||
    suburb.properties?.SA2_NAME21 ||
    'Unknown suburb'
  )
}

function getCrowdLevel(suburb) {
  return (
    suburb.crowd_level ||
    suburb.crowd?.level ||
    suburb.pedestrian?.crowd_level ||
    suburb.properties?.crowd_level ||
    'Quiet'
  )
}

function crowdClass(level) {
  const value = String(level || '').toLowerCase()

  if (value.includes('very')) return 'very-quiet'
  if (value.includes('busy') || value.includes('high')) return 'busy'
  if (value.includes('moderate')) return 'moderate'
  return 'quiet'
}

function shortName(name) {
  return name
    .replace('Melbourne CBD - ', 'CBD ')
    .replace(' - ', '\n')
}

function getSuburbPosition(index) {
  const positions = [
    [48, 16], [58, 20], [40, 22], [52, 28], [62, 30],
    [34, 32], [45, 36], [56, 38], [68, 39], [28, 46],
    [39, 48], [50, 50], [61, 52], [72, 54], [34, 61],
    [46, 62], [57, 64], [67, 66], [42, 75], [53, 76],
    [63, 78], [31, 72], [74, 71], [22, 58],
  ]

  const [left, top] = positions[index % positions.length]

  return {
    left: `${left}%`,
    top: `${top}%`,
  }
}

async function loadSuburbs() {
  loadingMap.value = true
  mapError.value = ''

  try {
    const data = await fetchSuburbMap()

    suburbs.value =
      data.suburbs ||
      data.features ||
      data.items ||
      data.results ||
      data ||
      []
  } catch (error) {
    console.error(error)
    mapError.value = 'Could not load suburb map data.'
  } finally {
    loadingMap.value = false
  }
}

async function selectSuburb(suburb) {
  selectedSuburb.value = suburb
  selectedSuburbId.value = getSuburbId(suburb)

  if (!selectedSuburbId.value) {
    detailError.value = 'This suburb does not have a valid suburb ID.'
    return
  }

  await loadSuburbDetails(selectedSuburbId.value)
}

async function loadSuburbDetails(suburbId) {
  loadingDetails.value = true
  detailError.value = ''

  snapshot.value = null
  pedestrian.value = null
  weather.value = null
  events.value = []
  accessibility.value = null

  try {
    const [
      snapshotResult,
      pedestrianResult,
      weatherResult,
      eventsResult,
      accessibilityResult,
    ] = await Promise.allSettled([
      fetchSuburbSnapshot(suburbId),
      fetchSuburbPedestrian(suburbId),
      fetchSuburbWeather(suburbId),
      fetchSuburbEvents(suburbId, 10),
      fetchSuburbAccessibility(suburbId, 10),
    ])

    if (snapshotResult.status === 'fulfilled') {
      snapshot.value = snapshotResult.value
    }

    if (pedestrianResult.status === 'fulfilled') {
      pedestrian.value = pedestrianResult.value
    }

    if (weatherResult.status === 'fulfilled') {
      weather.value = weatherResult.value
    }

    if (eventsResult.status === 'fulfilled') {
      const eventData = eventsResult.value

      events.value =
        eventData.events ||
        eventData.items ||
        eventData.results ||
        eventData ||
        []
    }

    if (accessibilityResult.status === 'fulfilled') {
      accessibility.value = accessibilityResult.value
    }

    console.log('Snapshot:', snapshot.value)
    console.log('Pedestrian:', pedestrian.value)
    console.log('Weather:', weather.value)
    console.log('Events:', events.value)
    console.log('Accessibility:', accessibility.value)
  } catch (error) {
    console.error(error)
    detailError.value = 'Could not load suburb details.'
  } finally {
    loadingDetails.value = false
  }
}

function clearSelection() {
  selectedSuburb.value = null
  selectedSuburbId.value = null
}

function goToDiscover() {
  router.push({
    path: '/discover',
    query: {
      suburb: selectedSuburbName.value,
    },
  })
}

function goToJourney() {
  router.push({
    path: '/journey',
    query: {
      suburb: selectedSuburbName.value,
    },
  })
}

function goToBestTime() {
  router.push({
    path: '/best-time',
    query: {
      suburb: selectedSuburbName.value,
    },
  })
}

onMounted(() => {
  loadSuburbs()
})
</script>

<style scoped>
.suburb-explorer-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(680px, 1.5fr) minmax(320px, 0.7fr);
  gap: 28px;
  padding: 32px;
  background: #f2f5f1;
  color: #17213d;
}

.map-card,
.detail-panel {
  background: #ffffff;
  border-radius: 24px;
  border: 1px solid #dce9df;
  box-shadow: 0 20px 60px rgba(0, 60, 40, 0.08);
  overflow: hidden;
}

.map-area {
  position: relative;
  min-height: 700px;
  overflow: hidden;
  border-radius: 24px;
  background:
    linear-gradient(rgba(224, 238, 222, 0.85), rgba(224, 238, 222, 0.85)),
    radial-gradient(circle at 40% 40%, #d7ead6, #cbdccf);
}

.legend {
  position: absolute;
  z-index: 4;
  top: 38px;
  left: 70px;
  width: 150px;
  padding: 14px 16px;
  border-radius: 10px;
  background: #ffffff;
  box-shadow: 0 8px 20px rgba(0, 50, 30, 0.08);
}

.legend h4 {
  margin: 0 0 8px;
  font-size: 11px;
  text-transform: uppercase;
  color: #6c7a73;
}

.legend p,
.mini-legend p {
  margin: 6px 0;
  font-size: 12px;
  font-weight: 700;
}

.dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 999px;
  margin-right: 6px;
}

.dot.very-quiet,
.suburb-hex.very-quiet {
  background: #48b86b;
}

.dot.quiet,
.suburb-hex.quiet {
  background: #72c77d;
}

.dot.moderate,
.suburb-hex.moderate {
  background: #f2c94c;
}

.dot.busy,
.suburb-hex.busy {
  background: #f9734d;
}

.map-title-pill {
  position: absolute;
  top: 40px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 4;
  background: #ffffff;
  color: #24413a;
  border-radius: 999px;
  padding: 9px 18px;
  font-size: 13px;
  font-weight: 800;
  box-shadow: 0 8px 20px rgba(0, 50, 30, 0.08);
}

.epic-pill {
  position: absolute;
  top: 40px;
  right: 34px;
  z-index: 4;
  background: #0f8a72;
  color: #ffffff;
  border-radius: 999px;
  padding: 9px 16px;
  font-size: 12px;
  font-weight: 800;
}

.suburb-map {
  position: absolute;
  inset: 75px 40px 110px 40px;
  z-index: 3;
}

.suburb-hex {
  position: absolute;
  transform: translate(-50%, -50%);
  width: 108px;
  min-height: 58px;
  border: none;
  color: #ffffff;
  font-size: 12px;
  line-height: 1.15;
  font-weight: 900;
  white-space: pre-line;
  cursor: pointer;
  clip-path: polygon(18% 0%, 82% 0%, 100% 50%, 82% 100%, 18% 100%, 0% 50%);
  box-shadow: 0 7px 14px rgba(0, 55, 35, 0.12);
  transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
}

.suburb-hex:hover,
.suburb-hex.active {
  transform: translate(-50%, -50%) scale(1.08);
  box-shadow: 0 12px 24px rgba(0, 80, 50, 0.22);
  filter: brightness(1.03);
  outline: 4px solid rgba(255, 255, 255, 0.85);
}

.water-shape {
  position: absolute;
  z-index: 1;
  left: 10%;
  right: 10%;
  bottom: -52px;
  height: 165px;
  background: #b9ddea;
  opacity: 0.85;
  border-radius: 50% 50% 0 0;
  transform: rotate(2deg);
}

.bottom-tabs {
  position: absolute;
  z-index: 5;
  left: 50%;
  bottom: 30px;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 14px 24px;
  border-radius: 999px;
  background: #ffffff;
  box-shadow: 0 18px 40px rgba(0, 50, 35, 0.15);
  white-space: nowrap;
}

.bottom-tabs a,
.bottom-tabs span {
  color: #1e3d36;
  text-decoration: none;
  font-size: 12px;
  font-weight: 800;
}

.bottom-tabs strong {
  background: #0f8a72;
  color: #ffffff;
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 12px;
}

.map-message {
  position: absolute;
  z-index: 6;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: #ffffff;
  border-radius: 16px;
  padding: 18px 24px;
  font-weight: 800;
}

.detail-panel {
  padding: 32px;
  overflow-y: auto;
}

.empty-state {
  min-height: 620px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}

.empty-icon {
  width: 58px;
  height: 58px;
  margin: 0 auto 16px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: #eaf7ef;
  font-size: 28px;
}

.empty-state h2,
.suburb-title {
  margin: 0 0 12px;
  font-size: 30px;
  color: #252948;
}

.empty-state p {
  max-width: 330px;
  margin: 0 auto 24px;
  color: #53635d;
  line-height: 1.5;
}

.mini-legend {
  border-top: 1px solid #e4eee8;
  padding-top: 18px;
  text-align: left;
}

.back-button {
  border: none;
  background: #0f8a72;
  color: #ffffff;
  border-radius: 16px;
  padding: 13px 20px;
  font-size: 15px;
  font-weight: 800;
  cursor: pointer;
  margin-bottom: 26px;
}

.info-card {
  margin-top: 18px;
  padding: 22px;
  border: 1px solid #dce9df;
  border-radius: 20px;
  background: #f8fcf9;
}

.info-card h3 {
  margin: 0 0 16px;
  font-size: 21px;
  color: #252948;
}

.big-number {
  margin: 0 0 12px;
  color: #0f8a72;
  font-size: 34px;
  font-weight: 900;
}

.event-list {
  padding-left: 18px;
  margin: 0;
}

.event-list li {
  margin-bottom: 12px;
}

.event-list span {
  display: block;
  margin-top: 3px;
  color: #62706a;
  font-size: 13px;
}

.action-list {
  display: grid;
  gap: 12px;
  margin-top: 20px;
}

.action-list button {
  border: none;
  border-radius: 14px;
  padding: 15px 18px;
  background: #0f8a72;
  color: #ffffff;
  font-weight: 900;
  text-align: left;
  cursor: pointer;
}

.detail-message {
  margin: 12px 0;
  color: #53635d;
  font-weight: 700;
}

.error {
  color: #b3261e;
}

@media (max-width: 1100px) {
  .suburb-explorer-page {
    grid-template-columns: 1fr;
  }

  .map-card {
    min-height: 650px;
  }
}

@media (max-width: 700px) {
  .suburb-explorer-page {
    padding: 16px;
  }

  .map-area {
    min-height: 560px;
  }

  .legend {
    left: 20px;
  }

  .suburb-hex {
    width: 86px;
    min-height: 48px;
    font-size: 10px;
  }

  .bottom-tabs {
    max-width: 90%;
    overflow-x: auto;
  }
}
</style>