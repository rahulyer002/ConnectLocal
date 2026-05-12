<template>
  <MainLayout>
    <div class="discover-page">

    <!-- Noise overlay -->
    <div class="noise" aria-hidden="true"></div>

    <!-- Ambient orbs -->
    <div class="orb orb-1" aria-hidden="true"></div>
    <div class="orb orb-2" aria-hidden="true"></div>

    <!-- ═══ HERO ═══ -->
    <section class="hero">
      <div class="hero-bg-word" aria-hidden="true">DISCOVER</div>
      <div class="hero-inner">
        <p class="hero-eyebrow">
          <span class="eyebrow-line"></span>
          Free &amp; low-cost activities
        </p>
        <h1 class="hero-headline">
          Find your next<br>
          <em>warm moment.</em>
        </h1>
        <p class="hero-sub">Near {{ nearbyLabel }}</p>

        <!-- Location bar -->
        <form class="location-bar" @submit.prevent="applyManualLocation" role="search" aria-label="Search by location">
          <div class="location-input-wrap">
            <svg class="location-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/>
              <circle cx="12" cy="10" r="2.5"/>
            </svg>
            <input
              class="location-input"
              v-model="locationInput"
              type="text"
              aria-label="Enter suburb or postcode in Melbourne"
              placeholder="Enter suburb or postcode in Melbourne"
              @focus="handleLocationInputFocus"
              :style="{ fontSize: scaledPx(17) }"
            />
          </div>
          <div class="location-btns">
            <button
              type="button"
              class="loc-btn locate-btn"
              :disabled="isLocating"
              @click="getLocation"
              :aria-label="isLocating ? 'Locating your position' : 'Use my current location'"
              :style="{ fontSize: scaledPx(15) }"
            >
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <circle cx="12" cy="12" r="3"/>
                <path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>
              </svg>
              {{ isLocating ? 'Locating…' : 'Locate me' }}
            </button>
            <button
              type="submit"
              class="loc-btn change-btn"
              :disabled="isApplying || !locationInput.trim()"
              :aria-label="isApplying ? 'Updating location' : 'Apply location'"
              :style="{ fontSize: scaledPx(15) }"
            >
              {{ isApplying ? 'Updating…' : 'Search' }}
            </button>
          </div>
        </form>

        <p class="location-note" role="note" :style="{ fontSize: scaledPx(14) }">
          Using search (not Locate) may return a representative point of the suburb or postcode, not your exact position.
        </p>

        <!-- Filter chips -->
        <div class="chips" role="group" aria-label="Filter activities">
          <button
            v-for="chip in chips"
            :key="chip.key"
            class="chip"
            :class="{ active: activeFilters[chip.key] }"
            :aria-pressed="activeFilters[chip.key]"
            @click="toggleFilter(chip.key)"
            :style="{ fontSize: scaledPx(15) }"
          >
            <svg v-if="chip.key === 'free'" viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2zM9 9h6M9 12h6M9 15h4"/>
            </svg>
            <svg v-else-if="chip.key === 'thisWeek'" viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <rect x="3" y="4" width="18" height="18" rx="2"/>
              <path d="M16 2v4M8 2v4M3 10h18"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/>
              <circle cx="12" cy="10" r="2.5"/>
            </svg>
            {{ chip.label }}
          </button>
        </div>
      </div>
    </section>

    <!-- ═══ ACTIVITY LIST ═══ -->
    <main class="activity-list" id="main-content">

      <!-- Loading -->
      <div v-if="isLoading" class="state-card" role="status" aria-live="polite">
        <div class="state-spinner" aria-hidden="true"></div>
        <p :style="{ fontSize: scaledPx(18) }">Loading activities…</p>
      </div>

      <!-- Error -->
      <div v-else-if="loadError" class="state-card state-error" role="alert">
        <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 8v4M12 16h.01"/>
        </svg>
        <p :style="{ fontSize: scaledPx(18) }">{{ loadError }}</p>
      </div>

      <!-- No location / no results -->
      <div v-else-if="!activities.length" class="state-card" role="status">
        <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#0a9b8a" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/>
          <circle cx="12" cy="10" r="2.5"/>
        </svg>
        <p :style="{ fontSize: scaledPx(18) }">
          <template v-if="!hasLocationConfirmed">
            Enter a Melbourne suburb or postcode above, then tap Search.
          </template>
          <template v-else>
            No activities found for the current filters.
          </template>
        </p>
      </div>

      <!-- Cards -->
      <template v-else>
        <article
          v-for="activity in activities"
          :key="activity.id"
          class="event-card"
          :aria-labelledby="`title-${activity.id}`"
        >
          <div class="card-tags">
            <span
              v-for="tag in activity.displayTags"
              :key="`${activity.id}-${tag.text}`"
              class="tag"
              :class="tag.tone"
              :style="{ fontSize: scaledPx(13) }"
            >{{ tag.text }}</span>
            <span
              class="distance-badge"
              v-if="activity.distanceKm !== null"
              :style="{ fontSize: scaledPx(13) }"
            >
              <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
                <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/>
              </svg>
              {{ activity.distanceKm.toFixed(1) }} km
            </span>
          </div>

          <h2
            :id="`title-${activity.id}`"
            class="card-title"
            :style="{ fontSize: scaledPx(26) }"
          >{{ activity.title }}</h2>

          <p class="card-meta" :style="{ fontSize: scaledPx(15) }">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
              <rect x="3" y="4" width="18" height="18" rx="2"/>
              <path d="M16 2v4M8 2v4M3 10h18"/>
            </svg>
            {{ formatMeta(activity) }}
          </p>

          <p class="card-desc" :style="{ fontSize: scaledPx(16) }">{{ activity.description }}</p>

          <div class="card-foot">
            <span class="spots" :style="{ fontSize: scaledPx(15) }">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
                <circle cx="12" cy="8" r="4"/>
                <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
              </svg>
              {{ activity.spotsLeftText }}
            </span>
            <RouterLink
              :to="detailsTo(activity.id)"
              class="details-link"
              :style="{ fontSize: scaledPx(15) }"
              :aria-label="`View details for ${activity.title}`"
            >
              View details
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M5 12h14M13 5l7 7-7 7"/>
              </svg>
            </RouterLink>
          </div>
        </article>

        <!-- Pagination -->
        <nav class="pagination" v-if="totalPages > 1" aria-label="Activity pages">
          <button
            class="page-btn"
            type="button"
            :disabled="currentPage === 1"
            @click="goToPage(currentPage - 1)"
            aria-label="Previous page"
            :style="{ fontSize: scaledPx(14) }"
          >
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M15 18l-6-6 6-6"/>
            </svg>
            Prev
          </button>

          <button
            v-for="page in visiblePages"
            :key="page"
            class="page-btn"
            type="button"
            :class="{ active: page === currentPage }"
            :aria-label="`Page ${page}`"
            :aria-current="page === currentPage ? 'page' : undefined"
            @click="goToPage(page)"
            :style="{ fontSize: scaledPx(14) }"
          >{{ page }}</button>

          <button
            class="page-btn"
            type="button"
            :disabled="currentPage === totalPages || isLoading"
            @click="goToPage(currentPage + 1)"
            aria-label="Next page"
            :style="{ fontSize: scaledPx(14) }"
          >
            Next
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </button>
        </nav>
      </template>
    </main>
    </div>
  </MainLayout>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, reactive, ref, watch } from 'vue'
import MainLayout from '../layouts/MainLayout.vue'
import { useLocationState } from '../composables/useLocationState'

const { setDetectedLocation, setDetectedUnavailable } = useLocationState()
const BASE_URL = import.meta.env.VITE_ACTIVITIES_API_URL || 'https://connectlocal.duckdns.org'
const API = `${BASE_URL}/api/events/search`
const CLOSE_KM = 5
const UI_PAGE_SIZE = 3
const FETCH_LIMIT = UI_PAGE_SIZE
const MELBOURNE_NOT_FOUND = 'The location you specified was not found in Melbourne.'

const locationInput = ref('')
const nearbyLabel = ref('your area')
const isLocating = ref(false)
const isApplying = ref(false)
const activities = ref([])
const isLoading = ref(false)
const loadError = ref('')
const currentPage = ref(1)
const hasLocationConfirmed = ref(false)
const locationLat = ref(null)
const locationLon = ref(null)
const locationQueryMode = ref('suburb')
const totalHint = ref(null)
import { uiStore } from '../stores/uiStore'
const scaledPx = (base) => `${(base * uiStore.textScale) / 100}px`

const activeFilters = reactive({ free: false, thisWeek: false, closeHome: false })
const chips = [
  { key: 'free', label: 'Free' },
  { key: 'thisWeek', label: 'This Week' },
  { key: 'closeHome', label: 'Close to Home' }
]

const n = (v) => (Number.isFinite(+v) ? +v : null)
const b = (v) => v === true || v === 1 || /^true|yes|y|1$/i.test(String(v || ''))
const isExplicitFalse = (v) => v === false || v === 0 || /^false|no|n|0$/i.test(String(v || ''))
const d = (v) => { const x = v ? new Date(String(v).replace(' ', 'T')) : null; return x && !Number.isNaN(x.getTime()) ? x : null }
const arr = (p) => (Array.isArray(p?.events) ? p.events : [])
const total = (p) => n(p?.total_filtered ?? p?.total)
const isPostcodeInput = (q) => /^\d{4}$/.test(q)
const isSuburbInput = (q) => /^[A-Za-z][A-Za-z\s'-]{1,59}$/.test(q)
const isValidLocationInput = (q) => isPostcodeInput(q) || isSuburbInput(q)
const isVictoriaPostcodeRange = (q) => { const code = Number(q); return Number.isInteger(code) && code >= 3000 && code <= 3999 }
const normalizePlace = (s) => String(s || '').trim().toLowerCase().replace(/\s+/g, ' ')
const normalizePostcode = (s) => (String(s || '').match(/\b\d{4}\b/) || [''])[0]
const isInMelbourne = (a = {}, displayName = '') => { const state = String(a.state || '').toLowerCase(); const text = String(displayName || '').toLowerCase(); return state.includes('victoria') && text.includes('melbourne') }

const normalize = (r, i) => {
  const date = d(r.datetime_start)
  const km = n(r.distance_km)
  const cost = n(r.min_price)
  const isFree = isExplicitFalse(r.is_free) ? false : b(r.is_free) || (cost != null && cost <= 10)
  const venue = r.venue || 'Location TBC'
  const address = String(r.address || r.location_summary || '').trim()
  const suburb = r.suburb || ''
  const spots = n(r.spots_left)
  const category = String(r?.category || '').trim()
  const source = String(r?.source || '').trim()
  const cancelled = b(r.is_cancelled)
  return {
    id: r.id ?? `event-${i}`,
    title: r.name || `Activity ${i + 1}`,
    description: r.description || 'Community activity details available soon.',
    venue, suburb, date,
    dateText: date ? date.toLocaleDateString('en-AU', { weekday: 'short', day: 'numeric', month: 'short' }) : r.datetime_summary || 'Date TBC',
    timeText: date ? date.toLocaleTimeString('en-AU', { hour: 'numeric', minute: '2-digit' }) : 'Time TBC',
    isFree,
    distanceKm: km,
    spotsLeftText: spots == null ? (address ? `Address: ${address}` : 'Spots info unavailable') : `${Math.max(0, Math.floor(spots))} spots left`,
    displayTags: [
      isFree && { text: 'Free / Low-cost', tone: 'green' },
      km != null && km <= CLOSE_KM && { text: 'Near You', tone: 'lilac' },
      category && { text: category, tone: 'soft' },
      source && { text: source, tone: 'soft' },
      cancelled && { text: 'Cancelled', tone: 'warn' }
    ].filter(Boolean)
  }
}

const buildSearchUrl = (page = currentPage.value) => {
  const u = new URL(API)
  const offset = (Math.max(1, page) - 1) * FETCH_LIMIT
  u.searchParams.set('offset', String(offset))
  u.searchParams.set('rows', String(FETCH_LIMIT))
  u.searchParams.set('is_free', activeFilters.free ? 'true' : 'false')
  if (activeFilters.thisWeek) {
    const today = new Date()
    const end = new Date(Date.now() + 7 * 86400000)
    u.searchParams.set('date_from', today.toISOString().slice(0, 10))
    u.searchParams.set('date_to', end.toISOString().slice(0, 10))
  }
  if (activeFilters.closeHome) u.searchParams.set('radius_km', String(CLOSE_KM))
  if (locationQueryMode.value === 'latlon' && locationLat.value != null && locationLon.value != null) {
    u.searchParams.set('lat', String(locationLat.value))
    u.searchParams.set('lon', String(locationLon.value))
  } else if (locationInput.value.trim()) {
    const suburbQuery = nearbyLabel.value && nearbyLabel.value !== 'your area' ? nearbyLabel.value : locationInput.value.trim()
    u.searchParams.set('suburb', suburbQuery.toLowerCase())
  }
  return u
}

const fetchActivities = async (page = currentPage.value) => {
  if (!hasLocationConfirmed.value) return
  isLoading.value = true
  loadError.value = ''
  try {
    const u = buildSearchUrl(page)
    const r = await fetch(u.toString())
    if (!r.ok) throw new Error(`Failed (${r.status})`)
    const p = await r.json()
    totalHint.value = total(p) ?? totalHint.value
    activities.value = arr(p).map(normalize)
    currentPage.value = page
  } catch {
    loadError.value = 'Unable to load activities right now. Please try again later.'
    activities.value = []
  } finally {
    isLoading.value = false
  }
}

const setLocation = (text, suburb = '', lat = null, lon = null) => {
  locationInput.value = text
  nearbyLabel.value = suburb || text.split(',')[0] || 'your area'
  locationLat.value = lat
  locationLon.value = lon
  hasLocationConfirmed.value = true
  setDetectedLocation(text)
}
const handleLocationInputFocus = () => { if (locationInput.value === MELBOURNE_NOT_FOUND) locationInput.value = '' }
const parseAddress = (a = {}) => ({ suburb: a.suburb || a.neighbourhood || a.city_district || a.town || a.village || a.city || '', postcode: a.postcode || '' })
const formatSuburbPostcode = ({ suburb, postcode }) => [suburb, postcode].filter(Boolean).join(' , ').trim()

const getLocation = () => {
  if (!navigator.geolocation) { locationInput.value = MELBOURNE_NOT_FOUND; setDetectedUnavailable(); return }
  isLocating.value = true
  navigator.geolocation.getCurrentPosition(
    async ({ coords }) => {
      try {
        const r = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${coords.latitude}&lon=${coords.longitude}&accept-language=en`)
        const top = await r.json()
        if (!isInMelbourne(top?.address || {}, top?.display_name || '')) {
          locationInput.value = MELBOURNE_NOT_FOUND; locationLat.value = null; locationLon.value = null; hasLocationConfirmed.value = false; setDetectedUnavailable()
        } else {
          const f = parseAddress(top.address || {})
          const value = formatSuburbPostcode(f)
          if (!value) { locationInput.value = MELBOURNE_NOT_FOUND; locationLat.value = null; locationLon.value = null; hasLocationConfirmed.value = false; setDetectedUnavailable() }
          else { setLocation(value, f.suburb || value, coords.latitude, coords.longitude); locationQueryMode.value = 'latlon'; await fetchActivities() }
        }
      } catch { locationInput.value = MELBOURNE_NOT_FOUND; locationLat.value = null; locationLon.value = null; hasLocationConfirmed.value = false; setDetectedUnavailable() }
      isLocating.value = false
    },
    () => { locationInput.value = MELBOURNE_NOT_FOUND; locationLat.value = null; locationLon.value = null; hasLocationConfirmed.value = false; setDetectedUnavailable(); isLocating.value = false }
  )
}

const applyManualLocation = async () => {
  const q = locationInput.value.trim()
  if (!q) return
  const fail = () => { hasLocationConfirmed.value = false; locationLat.value = null; locationLon.value = null; locationInput.value = MELBOURNE_NOT_FOUND; setDetectedUnavailable() }
  if (!isValidLocationInput(q)) { fail(); return }
  if (isPostcodeInput(q) && !isVictoriaPostcodeRange(q)) { fail(); return }
  isApplying.value = true
  try {
    const queryText = isPostcodeInput(q) ? `${q}, Victoria, Australia` : `${q}, Melbourne, Victoria, Australia`
    const r = await fetch(`https://nominatim.openstreetmap.org/search?format=jsonv2&q=${encodeURIComponent(queryText)}&addressdetails=1&limit=20&accept-language=en&countrycodes=au`)
    const list = (await r.json()) || []
    const top = list.find((item) => {
      const state = String(item?.address?.state || '').toLowerCase()
      const f = parseAddress(item?.address || {})
      const isoState = String(item?.address?.['ISO3166-2-lvl4'] || '').toUpperCase()
      const display = String(item?.display_name || '').toLowerCase()
      const inVictoria = state.includes('victoria') || isoState === 'AU-VIC' || display.includes('victoria')
      if (isPostcodeInput(q)) { const postcodeMatched = normalizePostcode(f.postcode) === normalizePostcode(q) || normalizePostcode(item?.display_name) === normalizePostcode(q); return inVictoria && postcodeMatched }
      if (!isInMelbourne(item?.address || {}, item?.display_name || '')) return false
      return normalizePlace(f.suburb) === normalizePlace(q)
    })
    if (!top) { fail() } else {
      const f = parseAddress(top.address || {})
      const value = formatSuburbPostcode(f)
      if (!value) { fail() } else { setLocation(value, f.suburb || value, n(top.lat), n(top.lon)); locationQueryMode.value = 'suburb'; await fetchActivities() }
    }
  } catch { fail() }
  isApplying.value = false
}

const totalPages = computed(() => Math.max(1, Math.ceil((totalHint.value ?? 0) / UI_PAGE_SIZE)))
const totalCount = computed(() => totalHint.value ?? 0)
const visiblePages = computed(() => {
  const t = totalPages.value
  if (t <= 7) return Array.from({ length: t }, (_, i) => i + 1)
  return Array.from({ length: t }, (_, i) => i + 1).slice(Math.max(0, currentPage.value - 3), Math.min(t, currentPage.value + 3))
})
const formatMeta = (a) => `${a.dateText} · ${a.timeText} · ${a.venue}`
const detailsTo = (id) => {
  const q = {}
  if (locationLat.value != null && locationLon.value != null) { q.lat = String(locationLat.value); q.lon = String(locationLon.value) }
  return { path: `/events/${id}`, query: q }
}
const toggleFilter = async (k) => { activeFilters[k] = !activeFilters[k]; if (!hasLocationConfirmed.value) return; totalHint.value = null; await fetchActivities(1) }
const goToPage = async (p) => { await fetchActivities(Math.min(totalPages.value, Math.max(1, p))) }
const printList = () => window.print()

watch(activities, () => { if (currentPage.value > totalPages.value) currentPage.value = totalPages.value })
onMounted(() => {
  getLocation()
})

onBeforeUnmount(() => {})
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.discover-page {
  min-height: 100vh;
  background: #f2faf0;
  color: #1a2e1e;
  font-family: system-ui, sans-serif;
  position: relative;
  overflow-x: hidden;
}

/* Noise */
.noise {
  position: fixed; inset: 0; z-index: 1000; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  background-size: 180px; opacity: 0.45;
}

/* Orbs */
.orb { position: fixed; border-radius: 50%; pointer-events: none; z-index: 0; filter: blur(80px); }
.orb-1 { width: 500px; height: 500px; background: rgba(90,180,110,0.18); top: -100px; left: -80px; animation: orb-drift 22s ease-in-out infinite alternate; }
.orb-2 { width: 380px; height: 380px; background: rgba(255,180,140,0.12); bottom: 5%; right: -60px; animation: orb-drift 28s ease-in-out infinite alternate-reverse; }
@keyframes orb-drift { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(40px,50px) scale(1.1)} }

/* Hero */
.hero {
  padding: 80px 52px 80px;
}
.hero-bg-word {
  position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%);
  font-family: Georgia,serif; font-size: clamp(100px,16vw,200px);
  font-weight: 700; font-style: italic;
  color: rgba(10,155,138,0.055);
  white-space: nowrap; pointer-events: none; user-select: none; letter-spacing: -0.04em;
}
.hero-inner { position: relative; z-index: 2; max-width: 900px; }

.hero-eyebrow {
  display: inline-flex; align-items: center; gap: 12px;
  font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
  color: #0a9b8a; margin-bottom: 20px;
}
.eyebrow-line { display: block; width: 32px; height: 1px; background: #0a9b8a; }

.hero-headline {
  font-family: Georgia,serif;
  font-size: clamp(42px,6vw,84px);
  font-weight: 700; line-height: 1.05; color: #0f1e12; margin-bottom: 10px;
}
.hero-headline em { color: #0a9b8a; font-style: italic; }

.hero-sub { font-size: 18px; color: #4a6a4e; margin-bottom: 32px; font-weight: 500; }

/* Location bar */
.location-bar {
  display: flex; flex-wrap: wrap; gap: 12px; align-items: center;
  background: white; border: 1.5px solid rgba(29,113,105,0.2);
  border-radius: 16px; padding: 10px 16px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
  margin-bottom: 14px;
  max-width: 760px;
}
.location-input-wrap { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 200px; }
.location-icon { color: #0a9b8a; flex-shrink: 0; }
.location-input {
  border: none; outline: none; background: transparent;
  font-size: 17px; font-weight: 600; color: #1a2e1e;
  width: 100%; font-family: system-ui,sans-serif;
}
.location-input::placeholder { color: #8aaa8e; font-weight: 400; }
.location-btns { display: flex; gap: 8px; }
.loc-btn {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 10px 20px; border-radius: 10px;
  font-size: 15px; font-weight: 700; cursor: pointer;
  transition: all 0.25s; border: 1.5px solid transparent;
  font-family: system-ui,sans-serif;
}
.locate-btn { background: #f0faf0; border-color: rgba(29,113,105,0.2); color: #0a9b8a; }
.locate-btn:hover { background: #0a9b8a; color: white; }
.change-btn { background: #0a9b8a; color: white; }
.change-btn:hover { background: #056b5e; }
.loc-btn:disabled { opacity: 0.55; cursor: wait; }

.location-note { font-size: 13px; color: #8aaa8e; margin-bottom: 28px; max-width: 620px; line-height: 1.5; }

/* Chips */
.chips { display: flex; flex-wrap: wrap; gap: 10px; }
.chip {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 11px 20px; border-radius: 999px;
  border: 1.5px solid rgba(29,113,105,0.25);
  background: rgba(255,255,255,0.7); backdrop-filter: blur(8px);
  color: #3a5a3e; font-size: 15px; font-weight: 700;
  cursor: pointer; transition: all 0.25s; font-family: system-ui,sans-serif;
}
.chip:hover { border-color: #0a9b8a; color: #0a9b8a; background: white; }
.chip.active { background: #0a9b8a; border-color: #0a9b8a; color: white; }
.chip:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 2px; }

.a11y-left { display: flex; align-items: baseline; gap: 8px; }
.results-count { display: flex; align-items: baseline; gap: 8px; }
.results-count strong { font-family: Georgia,serif; font-size: 28px; color: #0a9b8a; line-height: 1; }
.results-count span { font-size: 15px; color: #6a8e6e; font-weight: 500; }

.a11y-right { display: flex; align-items: center; gap: 20px; }

.text-scale-label { font-size: 13px; color: #6a8e6e; font-weight: 700; min-width: 36px; }

.print-btn {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 9px 18px; border-radius: 10px;
  border: 1.5px solid rgba(29,113,105,0.2);
  background: white; color: #3a5a3e;
  font-size: 14px; font-weight: 700;
  cursor: pointer; transition: all 0.25s; font-family: system-ui,sans-serif;
}
.print-btn:hover { border-color: #0a9b8a; color: #0a9b8a; }

/* Activity list */
.activity-list { padding: 40px 52px 80px; display: grid; gap: 20px; max-width: 1100px; margin: 0 auto; }

/* State cards */
.state-card {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 16px; text-align: center;
  background: white; border: 1px solid rgba(29,113,105,0.12);
  border-radius: 16px; padding: 60px 40px;
  color: #4a6a4e; font-size: 18px; font-weight: 500;
}
.state-error { border-color: rgba(180,50,50,0.2); color: #8b2020; }
.state-spinner {
  width: 36px; height: 36px; border-radius: 50%;
  border: 3px solid rgba(10,155,138,0.2);
  border-top-color: #0a9b8a;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Event cards */
.event-card {
  background: white;
  border: 1px solid rgba(29,113,105,0.12);
  border-radius: 16px; padding: 28px 32px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.04);
  transition: transform 0.3s cubic-bezier(0.22,1,0.36,1), box-shadow 0.3s;
}
.event-card:hover { transform: translateY(-3px); box-shadow: 0 16px 40px rgba(10,155,138,0.12); }

.card-tags { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }
.tag { border-radius: 999px; padding: 5px 12px; font-size: 13px; font-weight: 700; }
.tag.green { background: #d6f4e7; color: #0a6b55; }
.tag.lilac { background: #ede8ff; color: #4a42a8; }
.tag.soft  { background: #e8f2e8; color: #2a5a3e; }
.tag.warn  { background: #ffe8e8; color: #a22b2b; }
.distance-badge {
  display: inline-flex; align-items: center; gap: 4px;
  margin-left: auto; background: #e4f5e0;
  border: 1px solid rgba(10,155,138,0.2);
  color: #0a6b55; border-radius: 8px; padding: 5px 10px;
  font-size: 13px; font-weight: 700;
}

.card-title { font-family: Georgia,serif; font-size: 26px; font-weight: 700; color: #0f1e12; line-height: 1.2; margin-bottom: 10px; }
.card-meta { display: flex; align-items: center; gap: 7px; font-size: 14px; color: #6a8e6e; font-weight: 600; margin-bottom: 14px; }
.card-desc { font-size: 16px; line-height: 1.65; color: #3a5a3e; margin-bottom: 20px; }

.card-foot {
  border-top: 1px solid rgba(29,113,105,0.1);
  padding-top: 16px; display: flex; justify-content: space-between; align-items: center; gap: 12px;
}
.spots { display: flex; align-items: center; gap: 6px; font-size: 14px; font-weight: 600; color: #6a8e6e; }
.details-link {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 15px; font-weight: 700; color: #0a9b8a; text-decoration: none;
  transition: gap 0.2s;
}
.details-link:hover { gap: 10px; }
.details-link:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 2px; border-radius: 4px; }

/* Pagination */
.pagination { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin-top: 16px; }
.page-btn {
  display: inline-flex; align-items: center; gap: 6px;
  border: 1.5px solid rgba(29,113,105,0.2); border-radius: 10px;
  background: white; color: #3a5a3e;
  min-width: 44px; padding: 10px 14px;
  font-size: 14px; font-weight: 700; cursor: pointer;
  transition: all 0.2s; font-family: system-ui,sans-serif;
}
.page-btn:hover { border-color: #0a9b8a; color: #0a9b8a; }
.page-btn.active { background: #0a9b8a; border-color: #0a9b8a; color: white; }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.page-btn:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 2px; }

/* Responsive */
@media (max-width: 900px) {
  .hero { padding: 70px 20px 60px; }
  .activity-list { padding: 28px 20px 60px; }
  .event-card { padding: 20px; }
  .card-foot { flex-direction: column; align-items: flex-start; }
  .text-slider { width: 70px; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}

@media print {
  .nav, .hero, .pagination, .noise, .orb { display: none !important; }
  .activity-list { padding: 0; }
  .event-card { box-shadow: none; border: 1px solid #ccc; break-inside: avoid; }
}
</style>