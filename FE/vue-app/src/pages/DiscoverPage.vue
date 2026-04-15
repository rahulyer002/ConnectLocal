<template>
  <MainLayout>
    <section class="hero">
      <h2>Find your next <em>warm moment</em></h2>
      <p>Free and low-cost activities near {{ nearbyLabel }}</p>

      <form class="location-picker" @submit.prevent="applyManualLocation">
        <input
          class="location-input"
          v-model="locationInput"
          type="text"
          aria-label="Location"
          placeholder="Enter suburb or postcode"
        />
        <button type="button" class="change-btn" :disabled="isLocating" @click="getLocation">
          {{ isLocating ? 'Locating...' : 'Locate' }}
        </button>
        <button type="submit" class="apply-btn" :disabled="isApplying || !locationInput.trim()">
          {{ isApplying ? 'Updating...' : 'Change' }}
        </button>
      </form>

      <div class="chips">
        <button
          v-for="chip in chips"
          :key="chip.key"
          class="chip"
          :class="{ solid: activeFilters[chip.key] }"
          @click="toggleFilter(chip.key)"
        >
          {{ chip.label }}
        </button>
      </div>
    </section>

    <section class="results-header">
      <h3>{{ filteredActivities.length }} activities</h3>
      <button class="print-btn" type="button" @click="printList">Print list</button>
    </section>

    <section class="activity-list" v-if="!isLoading && !loadError && filteredActivities.length">
      <article class="event-card" v-for="activity in filteredActivities" :key="activity.id">
        <div class="tags">
          <span class="tag green" v-if="activity.isFree">Free / Low-cost</span>
          <span class="tag lilac" v-if="activity.indoor">Indoor</span>
          <span class="tag lilac" v-if="activity.easyAccess">Easy Access</span>
          <span class="distance" v-if="activity.distanceKm !== null">{{ activity.distanceKm.toFixed(1) }} km</span>
        </div>
        <h4>{{ activity.title }}</h4>
        <p class="meta">{{ formatMeta(activity) }}</p>
        <p class="desc">{{ activity.description }}</p>
        <div class="event-foot">
          <span>{{ activity.spotsLeftText }}</span>
          <a v-if="activity.link" :href="activity.link" target="_blank" rel="noreferrer">View details →</a>
          <span v-else>Details coming soon</span>
        </div>
      </article>
    </section>

    <section class="activity-list" v-else>
      <article class="event-card state-card" v-if="isLoading">Loading activities...</article>
      <article class="event-card state-card" v-else-if="loadError">{{ loadError }}</article>
      <article class="event-card state-card" v-else>
        No activities match current filters. Try removing one or two filters.
      </article>
    </section>
  </MainLayout>
</template>

<script setup>
import MainLayout from '../layouts/MainLayout.vue'
import { computed, onMounted, reactive, ref } from 'vue'
import { useLocationState } from '../composables/useLocationState'

const { setDetectedLocation, setDetectedUnavailable } = useLocationState()

const ACTIVITIES_API_URL = import.meta.env.VITE_ACTIVITIES_API_URL || '/api/activities'
const LOW_COST_THRESHOLD = 10
const CLOSE_HOME_KM = 5

const locationInput = ref('')
const nearbyLabel = ref('your area')
const isLocating = ref(false)
const isApplying = ref(false)

const activities = ref([])
const isLoading = ref(false)
const loadError = ref('')

const activeFilters = reactive({
  free: true,
  thisWeek: true,
  closeHome: true,
  indoor: false,
  easyAccess: false,
})

const chips = [
  { key: 'free', label: 'Free' },
  { key: 'thisWeek', label: 'This Week' },
  { key: 'closeHome', label: 'Close to Home' },
  { key: 'indoor', label: 'Indoor' },
  { key: 'easyAccess', label: 'Easy Access' },
]

const AU_STATE_MAP = {
  Victoria: 'VIC',
  Queensland: 'QLD',
  'New South Wales': 'NSW',
  Tasmania: 'TAS',
  'South Australia': 'SA',
  'Western Australia': 'WA',
  'Northern Territory': 'NT',
  'Australian Capital Territory': 'ACT',
}

const parseBoolean = (value) => {
  if (typeof value === 'boolean') return value
  if (typeof value === 'number') return value > 0
  if (typeof value === 'string') {
    const normalized = value.trim().toLowerCase()
    return ['true', 'yes', 'y', '1'].includes(normalized)
  }
  return false
}

const parseNumber = (value) => {
  if (value === null || value === undefined || value === '') return null
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

const parseDate = (value) => {
  if (!value) return null
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

const toArray = (value) => {
  if (Array.isArray(value)) return value
  if (typeof value === 'string') {
    return value
      .split(',')
      .map((part) => part.trim())
      .filter(Boolean)
  }
  return []
}

const normalizeActivity = (raw, idx) => {
  const title = raw.title || raw.name || raw.eventName || `Activity ${idx + 1}`
  const description =
    raw.description || raw.summary || raw.details || 'Community activity details available soon.'

  const venue = raw.venue || raw.location || raw.address || raw.place || 'Location TBC'
  const suburb = raw.suburb || raw.city || raw.area || ''

  const dateRaw = raw.startDate || raw.date || raw.start_time || raw.datetime || raw.start
  const date = parseDate(dateRaw)
  const dateText = date ? date.toLocaleDateString('en-AU', { weekday: 'short', day: 'numeric', month: 'short' }) : 'Date TBC'
  const timeText = raw.time || (date ? date.toLocaleTimeString('en-AU', { hour: 'numeric', minute: '2-digit' }) : 'Time TBC')

  const tags = toArray(raw.tags).map((tag) => tag.toLowerCase())
  const cost = parseNumber(raw.cost ?? raw.price ?? raw.fee)
  const isFreeFlag = parseBoolean(raw.isFree ?? raw.free)
  const isLowCost = cost !== null ? cost <= LOW_COST_THRESHOLD : false
  const hasFreeTag = tags.includes('free') || tags.includes('low-cost')
  const isFree = isFreeFlag || isLowCost || hasFreeTag

  const indoor =
    parseBoolean(raw.indoor ?? raw.isIndoor) ||
    tags.includes('indoor') ||
    String(raw.venueType || '').toLowerCase() === 'indoor'

  const easyAccess =
    parseBoolean(raw.easyAccess ?? raw.accessible ?? raw.wheelchairAccessible) ||
    tags.includes('easy access') ||
    tags.includes('accessible')

  const distanceKm = parseNumber(raw.distanceKm ?? raw.distance_km ?? raw.distance)

  const spotsLeft = parseNumber(raw.spotsLeft ?? raw.remainingSpots ?? raw.capacityRemaining)
  const spotsLeftText = spotsLeft === null ? 'Spots info unavailable' : `${Math.max(0, Math.floor(spotsLeft))} spots left`

  return {
    id: raw.id || raw._id || `${title}-${idx}`,
    title,
    description,
    venue,
    suburb,
    date,
    dateText,
    timeText,
    isFree,
    indoor,
    easyAccess,
    distanceKm,
    spotsLeftText,
    link: raw.link || raw.url || raw.detailsUrl || '',
  }
}

const fetchActivities = async () => {
  isLoading.value = true
  loadError.value = ''

  try {
    const response = await fetch(ACTIVITIES_API_URL)
    if (!response.ok) {
      throw new Error(`Failed to load activities (${response.status})`)
    }

    const payload = await response.json()
    const source = Array.isArray(payload)
      ? payload
      : Array.isArray(payload?.activities)
        ? payload.activities
        : Array.isArray(payload?.data)
          ? payload.data
          : []

    activities.value = source.map(normalizeActivity)
  } catch (error) {
    console.warn('Load activities failed', error)
    loadError.value = 'Unable to load activities from API right now.'
    activities.value = []
  } finally {
    isLoading.value = false
  }
}

const formatFromNominatim = (address = {}) => {
  const suburb =
    address.suburb ||
    address.neighbourhood ||
    address.city_district ||
    address.town ||
    address.village ||
    address.city ||
    ''

  const stateCodeFromIso =
    address['ISO3166-2-lvl4']?.split('-')?.[1] || ''
  const state =
    stateCodeFromIso || AU_STATE_MAP[address.state] || address.state || ''
  const postcode = address.postcode || ''

  const region = [suburb, state].filter(Boolean).join(', ')
  return {
    text: [region, postcode].filter(Boolean).join(' '),
    suburb,
  }
}

const setLocationText = (text, suburbFallback = '') => {
  locationInput.value = text
  nearbyLabel.value = suburbFallback || text.split(',')[0] || 'your area'
}

const getLocation = () => {
  if (!navigator.geolocation) {
    locationInput.value = 'Geolocation not supported'
    setDetectedUnavailable()
    return
  }

  isLocating.value = true
  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      const lat = pos.coords.latitude
      const lon = pos.coords.longitude
      try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&accept-language=en`,
          { headers: { 'User-Agent': 'ConnectLocal App' } }
        )
        const data = await response.json()
        const formatted = formatFromNominatim(data.address)
        if (formatted.text) {
          setLocationText(formatted.text, formatted.suburb)
          setDetectedLocation(formatted.text)
        } else {
          const latLonText = `${lat.toFixed(5)}, ${lon.toFixed(5)}`
          setLocationText(latLonText, '')
          setDetectedLocation(latLonText)
        }
      } catch (error) {
        console.warn('Reverse geocode failed', error)
        const latLonText = `${lat.toFixed(5)}, ${lon.toFixed(5)}`
        setLocationText(latLonText, '')
        setDetectedLocation(latLonText)
      } finally {
        isLocating.value = false
      }
    },
    (error) => {
      console.warn('Geolocation failed', error)
      locationInput.value = 'Unable to get location'
      setDetectedUnavailable()
      isLocating.value = false
    }
  )
}

const applyManualLocation = async () => {
  const query = locationInput.value.trim()
  if (!query) return

  isApplying.value = true
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=jsonv2&q=${encodeURIComponent(query)}&addressdetails=1&limit=1&accept-language=en`,
      { headers: { 'User-Agent': 'ConnectLocal App' } }
    )
    const data = await response.json()
    const top = data?.[0]
    if (!top) {
      locationInput.value = 'Address not found'
      return
    }

    const formatted = formatFromNominatim(top.address || {})
    if (formatted.text) {
      setLocationText(formatted.text, formatted.suburb)
      setDetectedLocation(formatted.text)
    } else {
      const fallbackText = top.display_name || query
      setLocationText(fallbackText, query)
      setDetectedLocation(fallbackText)
    }
  } catch (error) {
    console.warn('Manual geocode failed', error)
    locationInput.value = 'Unable to update location'
  } finally {
    isApplying.value = false
  }
}

const homeSuburb = computed(() => nearbyLabel.value.trim().toLowerCase())

const isThisWeek = (activity) => {
  if (!activity.date) return false
  const now = new Date()
  const nextWeek = new Date(now)
  nextWeek.setDate(now.getDate() + 7)
  return activity.date >= now && activity.date <= nextWeek
}

const isCloseToHome = (activity) => {
  if (activity.distanceKm !== null) {
    return activity.distanceKm <= CLOSE_HOME_KM
  }

  if (homeSuburb.value && homeSuburb.value !== 'your area') {
    const suburbText = String(activity.suburb || activity.venue).toLowerCase()
    return suburbText.includes(homeSuburb.value) || homeSuburb.value.includes(suburbText)
  }

  return true
}

const filteredActivities = computed(() => {
  return activities.value.filter((activity) => {
    if (activeFilters.free && !activity.isFree) return false
    if (activeFilters.thisWeek && !isThisWeek(activity)) return false
    if (activeFilters.closeHome && !isCloseToHome(activity)) return false
    if (activeFilters.indoor && !activity.indoor) return false
    if (activeFilters.easyAccess && !activity.easyAccess) return false
    return true
  })
})

const formatMeta = (activity) => `${activity.dateText} · ${activity.timeText} · ${activity.venue}`

const toggleFilter = (key) => {
  activeFilters[key] = !activeFilters[key]
}

const printList = () => {
  window.print()
}

onMounted(() => {
  fetchActivities()
  getLocation()
})
</script>

<style scoped>
.hero {
  background: linear-gradient(135deg, var(--orange) 0%, var(--orange-deep) 100%);
  color: #fff;
  padding: 30px 28px;
}

.hero h2 {
  margin: 0;
  font-family: 'Fraunces', serif;
  font-size: clamp(36px, 4vw, 56px);
  line-height: 1;
}

.hero h2 em {
  color: #ffd24d;
  font-style: italic;
}

.hero p {
  margin: 10px 0 20px;
  font-size: clamp(18px, 2.2vw, 34px);
  font-weight: 600;
}

.location-picker {
  width: 100%;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
}

.location-input {
  flex: 1;
  border: none;
  background: transparent;
  color: #fff;
  font-size: clamp(18px, 2vw, 28px);
  font-weight: 800;
  outline: none;
  min-width: 0;
}

.location-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.change-btn,
.apply-btn {
  border: 2px solid rgba(255, 255, 255, 0.65);
  border-radius: 999px;
  color: #fff;
  padding: 10px 18px;
  font-size: 16px;
  font-weight: 800;
  cursor: pointer;
}

.change-btn {
  background: transparent;
}

.change-btn:hover {
  background: rgba(255, 255, 255, 0.12);
}

.apply-btn {
  background: rgba(255, 255, 255, 0.16);
}

.apply-btn:hover {
  background: rgba(255, 255, 255, 0.24);
}

.change-btn:disabled,
.apply-btn:disabled {
  opacity: 0.75;
  cursor: wait;
}

.chips {
  margin-top: 18px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chip {
  border-radius: 999px;
  border: 2px solid rgba(255, 255, 255, 0.65);
  background: transparent;
  color: #fff;
  padding: 10px 16px;
  font-size: 20px;
  font-weight: 800;
  cursor: pointer;
}

.chip.solid {
  border-color: #b08b0a;
  background: var(--yellow);
  color: #1f1d1a;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 22px 24px 12px;
}

.results-header h3 {
  margin: 0;
  font-size: clamp(24px, 2.5vw, 36px);
}

.print-btn {
  border: 2px solid #c7c8dc;
  border-radius: 999px;
  background: transparent;
  color: #616580;
  font-size: 16px;
  padding: 8px 14px;
  font-weight: 700;
  cursor: pointer;
}

.activity-list {
  padding: 0 18px 24px;
  display: grid;
  gap: 14px;
}

.event-card {
  background: var(--panel-2);
  border: 2px solid #cbccdf;
  border-radius: var(--radius-xl);
  padding: 20px;
}

.state-card {
  font-size: 20px;
  font-weight: 700;
  color: #565973;
}

.tags {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.tag {
  border-radius: 999px;
  padding: 7px 13px;
  font-size: 16px;
  font-weight: 800;
}

.tag.green {
  background: #088f7e;
  color: #fff;
}

.tag.lilac {
  background: #d9d0f5;
  color: #4a42a8;
}

.distance {
  margin-left: auto;
  background: #caece7;
  border: 2px solid #a2d8d1;
  color: #0c7f72;
  border-radius: 14px;
  padding: 7px 11px;
  font-size: 16px;
  font-weight: 800;
}

.event-card h4 {
  margin: 16px 0 8px;
  font-family: 'Fraunces', serif;
  font-size: clamp(30px, 3vw, 46px);
  line-height: 1.08;
}

.meta {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #565973;
}

.desc {
  margin: 14px 0 18px;
  font-size: 20px;
  line-height: 1.35;
  color: #41445b;
}

.event-foot {
  border-top: 2px solid #d7d7e5;
  padding-top: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 800;
}

.event-foot a {
  color: #06786f;
}

@media (max-width: 980px) {
  .results-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .event-foot {
    font-size: 17px;
    flex-direction: column;
    align-items: flex-start;
  }

  .chip {
    font-size: 16px;
  }
}
</style>
