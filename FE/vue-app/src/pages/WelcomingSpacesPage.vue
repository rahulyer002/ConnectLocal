<template>
  <div class="welcoming-page">
    <div class="noise" aria-hidden="true"></div>
    <div class="orb orb-1" aria-hidden="true"></div>
    <div class="orb orb-2" aria-hidden="true"></div>

    <BestTimeLocationBar />

    <section class="hero">
      <div class="hero-bg-word" aria-hidden="true">WELCOME</div>
      <div class="hero-leaves" aria-hidden="true">
        <svg viewBox="0 0 200 200" width="100%" height="100%">
          <path d="M30 120 q-10-30 0-60 q15 25 0 60z" fill="rgba(255,255,255,0.06)" />
          <path d="M170 80 q10-30 0-60 q-15 25 0 60z" fill="rgba(255,255,255,0.05)" />
          <path d="M50 180 q-10-25 0-50 q15 20 0 50z" fill="rgba(255,255,255,0.04)" />
        </svg>
      </div>
      <div class="hero-inner">
        <RouterLink to="/best-time" class="back-btn">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          Back to live score
        </RouterLink>
        <p class="hero-eyebrow"><span class="eyebrow-line"></span>Community connection</p>
        <h1 class="hero-headline">
          Welcoming spaces<br>
          <em>near you.</em>
        </h1>
        <p class="hero-sub" :style="{ fontSize: scaledPx(18) }">
          Community spaces around you - libraries, civic buildings, visitor centres, and more.
          All open, free, and great places to drop in, rest, and connect.
        </p>
      </div>
    </section>

    <section class="explainer-band">
      <div class="explainer-inner">
        <div class="explainer-icon">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <div class="explainer-text">
          <p class="explainer-label">Click any pin to learn more</p>
          <p :style="{ fontSize: scaledPx(15) }">
            Your location is the green pin. Each coloured pin is a community space - colour shows the type. The yellow star marks
            spaces officially designated by the City of Melbourne as Welcoming Spaces. Click a pin to see what to expect there
            and get directions.
          </p>
        </div>
      </div>
    </section>

    <section v-if="!store.locationReady" class="empty-band">
      <div class="empty-card">
        <svg viewBox="0 0 24 24" width="56" height="56" fill="none" stroke="#2a6a30" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>
        <h3 :style="{ fontSize: scaledPx(24) }">Set your location to see community spaces</h3>
        <p :style="{ fontSize: scaledPx(16) }">Use the location bar above - autocomplete will help you set a Melbourne suburb or postcode.</p>
      </div>
    </section>

    <template v-else>
      <section v-if="loading && !allLandmarks.length" class="loading-band">
        <div class="big-spinner" aria-hidden="true"></div>
        <p :style="{ fontSize: scaledPx(18) }">Finding community spaces near you…</p>
      </section>

      <template v-else>
        <!-- ═══ INTERACTIVE MAP ═══ -->
        <section v-if="allLandmarks.length" class="map-band" data-reveal>
          <div class="map-inner">
            <div class="map-header">
              <p class="section-label">Interactive map</p>
              <h2 class="section-heading" :style="{ fontSize: scaledPx(40) }">
                {{ allLandmarks.length }}
                <em>community space{{ allLandmarks.length !== 1 ? 's' : '' }}</em><br>
                within 2km
              </h2>
              <p class="section-sub" :style="{ fontSize: scaledPx(16) }">
                Pan and zoom the map freely. Click any pin to see details and get directions.
              </p>
            </div>

            <!-- Legend -->
            <div class="map-legend" role="list" aria-label="Map legend">
              <span
                v-for="cat in legendCategories"
                :key="cat.name"
                class="legend-chip"
                :style="{ background: cat.bg, color: cat.fg, borderColor: cat.fg }"
                role="listitem"
              >
                <span class="legend-dot" :style="{ background: cat.fg }"></span>
                {{ cat.name }}
                <span class="legend-count">{{ cat.count }}</span>
              </span>
              <span v-if="hasWelcoming" class="legend-chip welcoming-chip" role="listitem">
                <span class="legend-star">★</span>
                Designated welcoming
              </span>
            </div>

            <!-- The actual map -->
            <div class="map-container">
              <div ref="mapEl" class="leaflet-map" role="application" aria-label="Interactive map of community spaces"></div>

              <!-- Recenter / zoom-to-fit button overlay -->
              <button class="map-recenter-btn" @click="recenterMap" aria-label="Recentre map on your location">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <circle cx="12" cy="12" r="3"/>
                  <path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>
                </svg>
                Recentre
              </button>
            </div>

            <!-- Detail card / hint card -->
            <transition name="detail" mode="out-in">
              <article v-if="selectedLandmark" :key="selectedLandmark.landmark_id" class="map-detail-card">
                <button class="detail-close" @click="selectedId = null" aria-label="Close detail">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>

                <div class="detail-head">
                  <div class="detail-icon-wrap" :style="{ background: selectedLandmark._color.bg, color: selectedLandmark._color.fg }">
                    <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <rect x="4" y="2" width="16" height="20" rx="2"/>
                      <path d="M9 22v-4h6v4"/>
                      <path d="M8 6h.01M12 6h.01M16 6h.01M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01"/>
                    </svg>
                  </div>
                  <div class="detail-title-block">
                    <div class="detail-name-row">
                      <h3 class="detail-name" :style="{ fontSize: scaledPx(28) }">{{ selectedLandmark.name }}</h3>
                      <span v-if="selectedLandmark.is_welcoming_space" class="detail-welcoming-badge">
                        <span class="badge-star">★</span>
                        Designated welcoming
                      </span>
                    </div>
                    <p class="detail-meta">
                      <span class="detail-category" :style="{ background: selectedLandmark._color.bg, color: selectedLandmark._color.fg }">
                        {{ selectedLandmark.sub_theme || selectedLandmark.theme }}
                      </span>
                      <span class="detail-distance">
                        <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>
                        {{ selectedLandmark.distance_km?.toFixed(2) }} km away
                      </span>
                      <span v-if="selectedLandmark.suburb_name" class="detail-suburb">
                        {{ selectedLandmark.suburb_name }}
                      </span>
                    </p>
                  </div>
                </div>

                <div class="detail-expect">
                  <p class="expect-label">What to expect</p>
                  <p :style="{ fontSize: scaledPx(15) }">{{ getExpectText(selectedLandmark.sub_theme, selectedLandmark.theme) }}</p>
                </div>

                <div class="detail-actions">
                <button class="detail-action-btn primary" @click="planJourneyTo(selectedLandmark)">
                  <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>
                  Get directions
                </button>
                
                <!-- <a :href="googleMapsLink(selectedLandmark)"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="detail-action-btn outline"
                >
  Open in Google Maps
  <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
</a> -->
                <button class="detail-action-btn outline" @click="findEventsNear(selectedLandmark)">
                  Events nearby
                </button>
              </div>
              </article>

              <div v-else key="hint" class="map-hint">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                <span>Click any pin on the map to see what to expect there and get directions.</span>
              </div>
            </transition>
          </div>
        </section>

        <!-- Generic empty (rare) -->
        <section v-else class="generic-empty-band">
          <div class="generic-empty-card">
            <svg viewBox="0 0 24 24" width="56" height="56" fill="none" stroke="#2a6a30" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <rect x="4" y="2" width="16" height="20" rx="2"/>
              <path d="M9 22v-4h6v4"/>
            </svg>
            <h3 :style="{ fontSize: scaledPx(26) }">No community spaces found within 2km</h3>
            <p :style="{ fontSize: scaledPx(15) }">
              Try setting your location to a Melbourne suburb closer to the CBD -
              <strong>Fitzroy</strong>, <strong>Carlton</strong>, <strong>Melbourne CBD</strong>, or <strong>Southbank</strong> usually have plenty.
            </p>
          </div>
        </section>

        <!-- Tips -->
        <section class="tips-band" data-reveal>
          <div class="tips-inner">
            <div class="tips-header">
              <p class="section-label">Helpful guidance</p>
              <h2 class="section-heading" :style="{ fontSize: scaledPx(36) }">
                Tips for your<br><em>first visit</em>
              </h2>
            </div>

            <div class="tips-grid">
              <article class="tip-card">
                <div class="tip-icon mint">
                  <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M18 8h1a4 4 0 0 1 0 8h-1"/>
                    <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/>
                    <line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/>
                  </svg>
                </div>
                <h3 :style="{ fontSize: scaledPx(18) }">Go at your own pace</h3>
                <p :style="{ fontSize: scaledPx(14) }">You don't need to join anything. Just arriving and sitting quietly is enough - these are judgment-free spaces.</p>
              </article>
              <article class="tip-card">
                <div class="tip-icon yellow">
                  <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                </div>
                <h3 :style="{ fontSize: scaledPx(18) }">Quieter in the mornings</h3>
                <p :style="{ fontSize: scaledPx(14) }">Libraries and community centres are usually less busy between 9am and 11am on weekdays.</p>
              </article>
              <article class="tip-card">
                <div class="tip-icon purple">
                  <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                  </svg>
                </div>
                <h3 :style="{ fontSize: scaledPx(18) }">Staff are there to help</h3>
                <p :style="{ fontSize: scaledPx(14) }">You can always ask staff about free programs, events, or just for a chat - that's what these spaces are for.</p>
              </article>
            </div>
          </div>
        </section>

        <section class="bottom-nav-band">
          <div class="bottom-nav-inner">
            <RouterLink to="/best-time" class="bnav-btn">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
              Live score
            </RouterLink>
            <RouterLink to="/best-time/now" class="bnav-btn primary">
              Best spots now
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
            </RouterLink>
            <RouterLink to="/discover" class="bnav-btn">
              Browse events
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
            </RouterLink>
          </div>
        </section>
      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { resonanceStore } from '../stores/resonanceStore'
import { uiStore } from '../stores/uiStore'
import { useResonanceApi } from '../composables/useResonanceApi'
import BestTimeLocationBar from '../components/BestTimeLocationBar.vue'
 
const store = resonanceStore
const router = useRouter()
const { fetchWelcomingSpaces } = useResonanceApi()
const scaledPx = (base) => `${(base * uiStore.textScale) / 100}px`

const loading = ref(false)
const allLandmarks = ref([])
const selectedId = ref(null)
const mapEl = ref(null)

let mapInstance = null
let userMarker = null
const markersById = new Map()  // landmark_id → L.Marker

// ── Categories ───────────────────────────────────────
function categoryColor(subTheme) {
  const s = (subTheme || '').toLowerCase()
  if (s.includes('library'))   return { bg: '#e6dcff', fg: '#5b3fb6', name: 'Library' }
  if (s.includes('police'))    return { bg: '#dde6f8', fg: '#2a4ab0', name: 'Police' }
  if (s.includes('fire'))      return { bg: '#ffe2d8', fg: '#c44a2c', name: 'Fire station' }
  if (s.includes('visitor'))   return { bg: '#fff3c2', fg: '#b88a00', name: 'Visitor centre' }
  if (s.includes('court'))     return { bg: '#f0e0d0', fg: '#6a3a1a', name: 'Court' }
  if (s.includes('public') || s.includes('hall')) return { bg: '#edf7ec', fg: '#2a6a30', name: 'Public building' }
  if (s.includes('health'))    return { bg: '#fce4ec', fg: '#c44a8a', name: 'Health' }
  return { bg: '#e0eedc', fg: '#4a6a4e', name: 'Community' }
}

function categoryIconSvg(subTheme) {
  const s = (subTheme || '').toLowerCase()
  const base = `width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"`
  if (s.includes('library'))
    return `<svg ${base}><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>`
  if (s.includes('police'))
    return `<svg ${base}><path d="M12 2l8 4v6c0 5-3.5 9-8 10-4.5-1-8-5-8-10V6z"/></svg>`
  if (s.includes('fire'))
    return `<svg ${base}><path d="M8 14s-2-2-2-5c0-2 2-4 2-4s4 4 4 9a4 4 0 0 1-8 0c0-2 2-3 2-3"/></svg>`
  if (s.includes('visitor'))
    return `<svg ${base}><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`
  if (s.includes('court'))
    return `<svg ${base}><line x1="12" y1="3" x2="12" y2="21"/><line x1="3" y1="21" x2="21" y2="21"/><path d="M3 8l4-5 4 5M13 8l4-5 4 5"/></svg>`
  if (s.includes('health'))
    return `<svg ${base}><rect x="9" y="3" width="6" height="18" rx="1"/><rect x="3" y="9" width="18" height="6" rx="1"/></svg>`
  return `<svg ${base}><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4"/><circle cx="9" cy="7" r="0.5" fill="currentColor"/><circle cx="12" cy="7" r="0.5" fill="currentColor"/><circle cx="15" cy="7" r="0.5" fill="currentColor"/><circle cx="9" cy="11" r="0.5" fill="currentColor"/><circle cx="12" cy="11" r="0.5" fill="currentColor"/><circle cx="15" cy="11" r="0.5" fill="currentColor"/></svg>`
}

const enrichedLandmarks = computed(() =>
  allLandmarks.value.map(l => ({ ...l, _color: categoryColor(l.sub_theme) }))
)

const selectedLandmark = computed(() =>
  selectedId.value
    ? enrichedLandmarks.value.find(l => l.landmark_id === selectedId.value)
    : null
)

const legendCategories = computed(() => {
  const seen = new Map()
  for (const l of enrichedLandmarks.value) {
    const key = l._color.name
    if (!seen.has(key)) seen.set(key, { ...l._color, count: 1 })
    else seen.get(key).count++
  }
  return Array.from(seen.values()).sort((a, b) => b.count - a.count)
})

const hasWelcoming = computed(() => allLandmarks.value.some(l => l.is_welcoming_space))

// ── Map setup ───────────────────────────────────────
function buildLandmarkIcon(landmark) {
  const color = categoryColor(landmark.sub_theme)
  const svg = categoryIconSvg(landmark.sub_theme)
  const star = landmark.is_welcoming_space
    ? `<div class="cl-pin-star" aria-hidden="true">★</div>`
    : ''

  return L.divIcon({
    className: 'cl-landmark-marker',
    html: `
      <div class="cl-pin" style="--bg:${color.bg};--fg:${color.fg};">
        <div class="cl-pin-circle">${svg}</div>
        ${star}
      </div>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 20],
    popupAnchor: [0, -20],
  })
}

function buildUserIcon() {
  return L.divIcon({
    className: 'cl-user-marker',
    html: `
      <div class="cl-user-pulse"></div>
      <div class="cl-user-dot"></div>
      <div class="cl-user-tag">YOU</div>
    `,
    iconSize: [44, 44],
    iconAnchor: [22, 22],
  })
}

async function initMap() {
  if (!mapEl.value || !store.locationReady) return

  // Tear down any existing instance
  if (mapInstance) {
    mapInstance.remove()
    mapInstance = null
    markersById.clear()
    userMarker = null
  }

  mapInstance = L.map(mapEl.value, {
    center: [store.userLat, store.userLon],
    zoom: 14,
    scrollWheelZoom: true,
    zoomControl: true,
    attributionControl: true,
  })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
    maxZoom: 19,
  }).addTo(mapInstance)

  // User marker
  userMarker = L.marker([store.userLat, store.userLon], {
    icon: buildUserIcon(),
    zIndexOffset: 2000,
    interactive: false,
    keyboard: false,
  }).addTo(mapInstance)

  refreshLandmarkMarkers()
}

function refreshLandmarkMarkers() {
  if (!mapInstance) return

  // Clear existing
  markersById.forEach(m => mapInstance.removeLayer(m))
  markersById.clear()

  for (const l of allLandmarks.value) {
    const lat = l.lat ?? l.latitude
    const lng = l.lng ?? l.lon ?? l.longitude
    if (lat == null || lng == null) continue

    const marker = L.marker([lat, lng], {
      icon: buildLandmarkIcon(l),
      title: l.name,
      alt: `${l.name}, ${l.sub_theme || 'community space'}, ${l.distance_km?.toFixed(2)} km`,
      riseOnHover: true,
    })
    marker.on('click', () => { selectedId.value = l.landmark_id })
    marker.addTo(mapInstance)
    markersById.set(l.landmark_id, marker)
  }

  // Fit bounds to include user + all landmarks
  if (allLandmarks.value.length) {
    const points = []
    for (const l of allLandmarks.value) {
      const lat = l.lat ?? l.latitude
      const lng = l.lng ?? l.lon ?? l.longitude
      if (lat != null && lng != null) points.push([lat, lng])
    }
    points.push([store.userLat, store.userLon])
    const bounds = L.latLngBounds(points)
    mapInstance.fitBounds(bounds, { padding: [60, 60], maxZoom: 16 })
  }
}

function recenterMap() {
  if (!mapInstance) return
  selectedId.value = null
  if (allLandmarks.value.length) {
    const points = []
    for (const l of allLandmarks.value) {
      const lat = l.lat ?? l.latitude
      const lng = l.lng ?? l.lon ?? l.longitude
      if (lat != null && lng != null) points.push([lat, lng])
    }
    points.push([store.userLat, store.userLon])
    mapInstance.flyToBounds(L.latLngBounds(points), { padding: [60, 60], maxZoom: 16, duration: 0.6 })
  } else {
    mapInstance.flyTo([store.userLat, store.userLon], 14, { duration: 0.6 })
  }
}

// ── Selection visual sync ───────────────────────────
watch(selectedId, (newId, oldId) => {
  // Remove .selected from old marker
  if (oldId && markersById.has(oldId)) {
    const el = markersById.get(oldId).getElement()
    if (el) el.classList.remove('cl-selected')
  }
  // Add .selected to new and pan to it
  if (newId && markersById.has(newId)) {
    const m = markersById.get(newId)
    const el = m.getElement()
    if (el) el.classList.add('cl-selected')
    const ll = m.getLatLng()
    mapInstance?.flyTo(ll, Math.max(mapInstance.getZoom(), 16), { duration: 0.5 })
  }
})

// ── Detail copy ─────────────────────────────────────
function getExpectText(subTheme, theme) {
  const s = (subTheme || theme || '').toLowerCase()
  if (s.includes('library'))
    return 'A calm, quiet space with free Wi-Fi, books, newspapers, and friendly staff. No purchase needed - you can simply sit, read, or use the computers.'
  if (s.includes('community centre'))
    return 'A hub for local programs, social groups, and activities. Drop in anytime or ask about upcoming free events.'
  if (s.includes('visitor'))
    return 'Free maps, brochures, and friendly staff who can help with directions, transit info, and recommendations for what to do nearby.'
  if (s.includes('public') || s.includes('hall'))
    return 'A public civic space open to all. Often hosts free exhibitions, public events, and community gatherings.'
  if (s.includes('police'))
    return 'A staffed station for safety concerns, lost property, and general assistance during business hours.'
  if (s.includes('fire'))
    return 'A staffed fire station. The public can drop in for safety advice or in genuine emergencies.'
  if (s.includes('court'))
    return 'A public court building. Public galleries are usually open during sessions for anyone to observe proceedings.'
  if (s.includes('health'))
    return 'A health and wellbeing service. Friendly staff can connect you with community programs and support services.'
  return 'A welcoming community space - open to all, free to enter, with friendly staff on hand.'
}

// ── Actions ────────────────────────────────────────
function planJourneyTo(space) {
  const lat = space.lat ?? space.latitude
  const lon = space.lng ?? space.lon ?? space.longitude
  if (lat == null || lon == null) return
  router.push({
    path: '/journey',
    query: {
      dest_lat: lat,
      dest_lon: lon,
      dest_name: space.name,
      auto: '1'
    }
  })
}

function findEventsNear(space) {
  router.push({
    path: '/discover',
    query: { suburb: space.suburb_name || '' }
  })
}

function googleMapsLink(space) {
  const lat = space.lat ?? space.latitude
  const lon = space.lng ?? space.lon ?? space.longitude
  const q = encodeURIComponent(space.name || `${lat},${lon}`)
  return `https://www.google.com/maps/search/?api=1&query=${lat},${lon}&query_place_id=${q}`
}

// ── Data loading ────────────────────────────────────
async function loadAll() {
  if (!store.locationReady) return
  loading.value = true
  selectedId.value = null
  const { userLat: lat, userLon: lon } = store
  try {
    const data = await fetchWelcomingSpaces(lat, lon, 5, 30)
    const list = Array.isArray(data) ? data : (data?.landmarks || data?.results || [])
    allLandmarks.value = list
    store.welcomingSpaces = list.filter(l => l.is_welcoming_space === true)
  } catch {
    allLandmarks.value = []
  } finally {
    loading.value = false
    await nextTick()
    setupReveal()
    if (allLandmarks.value.length) {
      await nextTick()
      initMap()
    }
  }
}

watch(() => store.locationReady, (r) => { if (r) loadAll() })
watch(() => [store.userLat, store.userLon], async () => {
  if (!store.locationReady) return
  await loadAll()
})

let revealObserver = null
function setupReveal() {
  if (revealObserver) revealObserver.disconnect()
  revealObserver = new IntersectionObserver(
    es => es.forEach(e => { if (e.isIntersecting) e.target.classList.add('in-view') }),
    { threshold: 0.1 }
  )
  document.querySelectorAll('[data-reveal]').forEach(el => revealObserver.observe(el))
}

// Chatbot integration — if the URL has lat/lon (e.g. from the chatbot pushing
// us here), make sure the store reflects that even on direct URL access.
const route = useRoute()
function applyChatbotQuery() {
  const q = route.query || {}
  if (!q.lat || !q.lon) return
  const lat = parseFloat(q.lat), lon = parseFloat(q.lon)
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return
  if (store.userLat === lat && store.userLon === lon) return
  store.setLocation(lat, lon, q.suburb || store.locationLabel || null)
}

onMounted(() => {
  setupReveal()
  applyChatbotQuery()
  if (store.locationReady) loadAll()
})

onBeforeUnmount(() => {
  if (revealObserver) revealObserver.disconnect()
  if (mapInstance) {
    mapInstance.remove()
    mapInstance = null
    markersById.clear()
    userMarker = null
  }
})
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
.welcoming-page { min-height: 100vh; background: #f2faf0; color: #1a2e1e; font-family: system-ui, sans-serif; position: relative; overflow-x: hidden; }
.noise { position: fixed; inset: 0; z-index: 1000; pointer-events: none; background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E"); background-size: 180px; opacity: 0.45; }
.orb { position: fixed; border-radius: 50%; pointer-events: none; z-index: 0; filter: blur(80px); }
.orb-1 { width: 500px; height: 500px; background: rgba(70,140,80,0.18); top: -100px; left: -80px; animation: orb-drift 22s ease-in-out infinite alternate; }
.orb-2 { width: 380px; height: 380px; background: rgba(245,200,18,0.10); bottom: 5%; right: -60px; animation: orb-drift 28s ease-in-out infinite alternate-reverse; }
@keyframes orb-drift { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(40px,50px) scale(1.1)} }

/* ─── Hero ─── */
.hero { position: relative; overflow: hidden; background: linear-gradient(160deg, #2a6a30 0%, #1e5226 100%); padding: 220px 52px 90px; color: white; }
.hero-bg-word { position: absolute; right: -2%; top: 50%; transform: translateY(-50%); font-family: Georgia,serif; font-size: clamp(140px, 20vw, 260px); font-weight: 700; font-style: italic; color: rgba(255,255,255,0.07); white-space: nowrap; pointer-events: none; user-select: none; letter-spacing: -0.04em; }
.hero-leaves { position: absolute; inset: 0; pointer-events: none; opacity: 0.7; }
.hero-inner { position: relative; z-index: 2; max-width: 1500px; margin: 0 auto; }
.back-btn { display: inline-flex; align-items: center; gap: 8px; padding: 8px 18px; background: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.25); border-radius: 999px; color: white; font-size: 13px; font-weight: 700; text-decoration: none; margin-bottom: 24px; transition: background 0.2s; }
.back-btn:hover { background: rgba(255,255,255,0.28); }
.hero-eyebrow { display: inline-flex; align-items: center; gap: 12px; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: rgba(255,255,255,0.85); margin-bottom: 22px; }
.eyebrow-line { display: block; width: 32px; height: 1px; background: rgba(255,255,255,0.85); }
.hero-headline { font-family: Georgia,serif; font-size: clamp(46px, 6vw, 88px); font-weight: 700; line-height: 1.04; color: white; margin-bottom: 18px; }
.hero-headline em { color: #f5c812; font-style: italic; }
.hero-sub { font-family: system-ui,sans-serif; color: rgba(255,255,255,0.88); line-height: 1.6; max-width: 680px; }

.explainer-band { background: #edf7ec; padding: 24px 52px; border-bottom: 1px solid rgba(42,106,48,0.18); }
.explainer-inner { max-width: 1500px; margin: 0 auto; display: flex; align-items: flex-start; gap: 16px; }
.explainer-icon { width: 40px; height: 40px; border-radius: 12px; background: rgba(42,106,48,0.12); color: #1e5226; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.explainer-text { flex: 1; min-width: 0; }
.explainer-label { font-family: system-ui,sans-serif; font-size: 12px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: #2a6a30; margin-bottom: 4px; }
.explainer-text p:last-child { font-family: system-ui,sans-serif; color: #1e3a26; line-height: 1.6; }

/* ─── Empty / loading ─── */
.empty-band, .loading-band { padding: 80px 52px; }
.empty-card { display: flex; flex-direction: column; align-items: center; gap: 14px; text-align: center; max-width: 600px; margin: 0 auto; padding: 60px 40px; background: white; border: 1px solid rgba(42,106,48,0.14); border-radius: 24px; box-shadow: 0 8px 28px rgba(0,0,0,0.04); }
.empty-card h3 { font-family: Georgia,serif; color: #0f1e12; font-weight: 700; }
.empty-card p { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.6; }
.loading-band { display: flex; flex-direction: column; align-items: center; gap: 18px; }
.big-spinner { width: 44px; height: 44px; border-radius: 50%; border: 4px solid rgba(42,106,48,0.18); border-top-color: #2a6a30; animation: spin 0.8s linear infinite; }
.loading-band p { font-family: system-ui,sans-serif; color: #4a6a4e; font-weight: 600; }
@keyframes spin { to { transform: rotate(360deg); } }

.generic-empty-band { background: white; padding: 80px 52px; border-bottom: 1px solid rgba(42,106,48,0.12); }
.generic-empty-card { display: flex; flex-direction: column; align-items: center; gap: 16px; text-align: center; max-width: 720px; margin: 0 auto; padding: 60px 40px; background: linear-gradient(135deg, #edf7ec 0%, white 60%); border: 1.5px solid rgba(42,106,48,0.25); border-radius: 24px; }
.generic-empty-card h3 { font-family: Georgia,serif; color: #0f1e12; font-weight: 700; }
.generic-empty-card p { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.6; max-width: 520px; }
.generic-empty-card strong { color: #2a6a30; }

/* ═══ MAP BAND ═══ */
.map-band { background: white; padding: 80px 52px; border-bottom: 1px solid rgba(42,106,48,0.12); opacity: 0; transform: translateY(40px); transition: all 0.9s cubic-bezier(0.22,1,0.36,1); }
.map-band.in-view { opacity: 1; transform: none; }
.map-inner { max-width: 1500px; margin: 0 auto; }
.map-header { max-width: 760px; margin-bottom: 28px; }
.section-label { font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #2a6a30; margin-bottom: 14px; }
.section-heading { font-family: Georgia,serif; font-weight: 700; line-height: 1.06; color: #0f1e12; margin-bottom: 14px; }
.section-heading em { color: #2a6a30; font-style: italic; }
.section-sub { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.65; }

.map-legend { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 22px; padding: 14px 18px; background: #f6faf3; border: 1px solid rgba(42,106,48,0.12); border-radius: 14px; }
.legend-chip { display: inline-flex; align-items: center; gap: 7px; padding: 6px 12px; background: white; border: 1.5px solid; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.legend-count { background: rgba(0,0,0,0.08); padding: 1px 8px; border-radius: 999px; font-size: 11px; font-weight: 800; margin-left: 2px; }
.welcoming-chip { background: #fff8e0; border-color: #b88a00; color: #8a6000; }
.legend-star { color: #b88a00; font-size: 14px; line-height: 1; }

.map-container { position: relative; width: 100%; height: 600px; border-radius: 22px; overflow: hidden; border: 1.5px solid rgba(42,106,48,0.18); box-shadow: 0 16px 44px rgba(42,106,48,0.12); margin-bottom: 22px; }
.leaflet-map { width: 100%; height: 100%; background: #e8f3e4; }

.map-recenter-btn {
  position: absolute; top: 16px; right: 16px; z-index: 500;
  display: inline-flex; align-items: center; gap: 7px;
  padding: 10px 16px;
  background: white; border: 1.5px solid rgba(42,106,48,0.3);
  border-radius: 12px;
  font-family: system-ui,sans-serif; font-size: 13px; font-weight: 700;
  color: #2a6a30; cursor: pointer;
  box-shadow: 0 4px 14px rgba(0,0,0,0.12);
  transition: all 0.2s;
}
.map-recenter-btn:hover { background: #2a6a30; color: white; border-color: #2a6a30; }

/* Detail card */
.map-detail-card { position: relative; background: linear-gradient(135deg, #f6faf3 0%, white 60%); border: 1.5px solid rgba(42,106,48,0.25); border-radius: 20px; padding: 28px 32px; box-shadow: 0 18px 44px rgba(42,106,48,0.16); display: flex; flex-direction: column; gap: 20px; }
.map-detail-card::before { content: ''; position: absolute; left: 0; top: 24px; bottom: 24px; width: 5px; border-radius: 0 4px 4px 0; background: linear-gradient(180deg, #2a6a30, #f5c812); }

.detail-close { position: absolute; top: 16px; right: 16px; width: 30px; height: 30px; border-radius: 50%; border: 1px solid rgba(42,106,48,0.2); background: white; color: #6a8e6e; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.detail-close:hover { color: #c44a2c; border-color: #c44a2c; }

.detail-head { display: flex; align-items: flex-start; gap: 18px; }
.detail-icon-wrap { width: 56px; height: 56px; border-radius: 16px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.detail-title-block { flex: 1; min-width: 0; padding-right: 30px; }
.detail-name-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 8px; }
.detail-name { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1.15; }
.detail-welcoming-badge { display: inline-flex; align-items: center; gap: 5px; padding: 4px 12px; border-radius: 999px; background: #fff3c2; color: #8a6000; font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; white-space: nowrap; }
.badge-star { font-size: 12px; line-height: 1; }

.detail-meta { display: inline-flex; align-items: center; gap: 12px; flex-wrap: wrap; font-family: system-ui,sans-serif; font-size: 13px; color: #4a6a4e; font-weight: 600; }
.detail-category { padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 800; letter-spacing: 0.03em; }
.detail-distance { display: inline-flex; align-items: center; gap: 5px; }
.detail-distance svg { color: #2a6a30; }
.detail-suburb { color: #6a8e6e; }
.detail-suburb::before { content: '· '; color: #c5d6c7; }

.detail-expect { padding: 18px 22px; background: rgba(42,106,48,0.06); border-radius: 14px; border: 1px solid rgba(42,106,48,0.12); }
.expect-label { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: #2a6a30; margin-bottom: 6px; }
.detail-expect p:last-child { font-family: system-ui,sans-serif; color: #1e3a26; line-height: 1.6; }

.detail-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.detail-action-btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 13px 22px; border-radius: 12px; font-family: system-ui,sans-serif; font-size: 14px; font-weight: 700; cursor: pointer; transition: all 0.25s; border: none; text-decoration: none; }
.detail-action-btn.primary { background: linear-gradient(135deg, #2a6a30, #1e5226); color: white; box-shadow: 0 12px 28px rgba(42,106,48,0.32); flex: 1; min-width: 180px; }
.detail-action-btn.primary:hover { transform: translateY(-2px); box-shadow: 0 16px 36px rgba(42,106,48,0.42); }
.detail-action-btn.outline { background: white; color: #2a6a30; border: 1.5px solid rgba(42,106,48,0.3); }
.detail-action-btn.outline:hover { background: #2a6a30; color: white; border-color: #2a6a30; }

.map-hint { display: flex; align-items: center; justify-content: center; gap: 10px; padding: 22px 26px; background: #f6faf3; border: 1px dashed rgba(42,106,48,0.3); border-radius: 16px; font-family: system-ui,sans-serif; font-size: 14px; color: #4a6a4e; font-weight: 600; }
.map-hint svg { color: #2a6a30; }

.detail-enter-active, .detail-leave-active { transition: opacity 0.3s, transform 0.3s; }
.detail-enter-from, .detail-leave-to { opacity: 0; transform: translateY(8px); }

/* ─── Tips ─── */
.tips-band { background: linear-gradient(180deg, #edf7ec 0%, #d6e8d8 100%); padding: 90px 52px; border-bottom: 1px solid rgba(42,106,48,0.14); opacity: 0; transform: translateY(40px); transition: all 0.9s cubic-bezier(0.22,1,0.36,1); }
.tips-band.in-view { opacity: 1; transform: none; }
.tips-inner { max-width: 1500px; margin: 0 auto; }
.tips-header { max-width: 600px; margin-bottom: 40px; }

.tips-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 18px; }
.tip-card { background: white; border: 1px solid rgba(42,106,48,0.12); border-radius: 18px; padding: 28px; display: flex; flex-direction: column; gap: 14px; transition: transform 0.3s, box-shadow 0.3s; }
.tip-card:hover { transform: translateY(-3px); box-shadow: 0 14px 36px rgba(42,106,48,0.12); }

.tip-icon { width: 52px; height: 52px; border-radius: 14px; display: flex; align-items: center; justify-content: center; position: relative; }
.tip-icon::before { content: ''; position: absolute; inset: -4px; border: 1.5px solid currentColor; border-radius: 14px; opacity: 0.18; }
.tip-icon.mint   { background: #d6f4e7; color: #1d7169; }
.tip-icon.yellow { background: #fff3c2; color: #b88a00; }
.tip-icon.purple { background: #e6dcff; color: #5b3fb6; }

.tip-card h3 { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1.2; }
.tip-card p { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.55; }

.bottom-nav-band { padding: 50px 52px 80px; background: #f2faf0; }
.bottom-nav-inner { max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }
.bnav-btn { display: inline-flex; align-items: center; justify-content: center; gap: 10px; padding: 18px 24px; border-radius: 14px; background: white; border: 1.5px solid rgba(42,106,48,0.2); color: #1a2e1e; font-family: system-ui,sans-serif; font-weight: 700; text-decoration: none; transition: all 0.25s; }
.bnav-btn:hover { border-color: #2a6a30; color: #2a6a30; }
.bnav-btn.primary { background: linear-gradient(135deg, #2a6a30, #1e5226); color: white; border-color: transparent; box-shadow: 0 12px 28px rgba(42,106,48,0.3); }
.bnav-btn.primary:hover { color: white; transform: translateY(-2px); box-shadow: 0 16px 36px rgba(42,106,48,0.38); }

@media (max-width: 980px) {
  .hero { padding: 280px 20px 70px; }
  .explainer-band, .map-band, .generic-empty-band, .tips-band { padding-left: 20px; padding-right: 20px; }
  .empty-band, .loading-band { padding: 60px 20px; }
  .map-band, .tips-band { padding-top: 60px; padding-bottom: 60px; }
  .map-container { height: 440px; }
  .map-detail-card { padding: 22px 24px; }
  .detail-action-btn.primary { min-width: 0; width: 100%; }
  .bottom-nav-band { padding: 40px 20px 70px; }
  .bottom-nav-inner { grid-template-columns: 1fr; }
  .map-legend { padding: 12px; }
  .legend-chip { font-size: 11px; padding: 5px 10px; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
</style>

<!-- ═══ UNSCOPED: Leaflet marker styles (must be global) ═══ -->
<style>
.leaflet-container {
  font-family: system-ui, sans-serif;
  background: #e8f3e4;
}
.leaflet-control-attribution {
  font-size: 10px !important;
  background: rgba(255,255,255,0.85) !important;
  padding: 2px 8px !important;
}
.leaflet-control-zoom a {
  background: white !important;
  color: #2a6a30 !important;
  border: 1px solid rgba(42,106,48,0.2) !important;
  font-weight: 700 !important;
}
.leaflet-control-zoom a:hover {
  background: #edf7ec !important;
}

/* User marker */
.cl-user-marker {
  position: relative;
  width: 44px !important;
  height: 44px !important;
  pointer-events: none;
}
.cl-user-pulse {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 18px; height: 18px;
  background: rgba(42,106,48,0.4);
  border-radius: 50%;
  animation: cl-user-pulse 2.4s ease-out infinite;
}
@keyframes cl-user-pulse {
  0%   { transform: translate(-50%, -50%) scale(0.6); opacity: 0.7; }
  100% { transform: translate(-50%, -50%) scale(3.4); opacity: 0; }
}
.cl-user-dot {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 18px; height: 18px;
  background: #2a6a30;
  border: 4px solid white;
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(42,106,48,0.5);
}
.cl-user-tag {
  position: absolute;
  top: -8px; left: 50%;
  transform: translateX(-50%);
  background: #2a6a30;
  color: white;
  font-family: system-ui, sans-serif;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.1em;
  padding: 2px 8px;
  border-radius: 999px;
  border: 2px solid white;
  white-space: nowrap;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}

/* Landmark marker */
.cl-landmark-marker {
  background: transparent !important;
  border: none !important;
}
.cl-pin {
  position: relative;
  width: 40px;
  height: 40px;
  cursor: pointer;
  transition: transform 0.2s cubic-bezier(0.22,1,0.36,1);
}
.cl-pin:hover {
  transform: scale(1.18);
  z-index: 1000;
}
.cl-pin-circle {
  width: 40px;
  height: 40px;
  background: var(--bg, #edf7ec);
  border: 3px solid var(--fg, #2a6a30);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--fg, #2a6a30);
  box-shadow: 0 4px 12px rgba(0,0,0,0.22);
  transition: box-shadow 0.2s, transform 0.2s;
}
.cl-pin:hover .cl-pin-circle {
  box-shadow: 0 8px 20px rgba(0,0,0,0.32);
}
.cl-pin-circle svg {
  display: block;
}
.cl-pin-star {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 18px;
  height: 18px;
  background: #f5c812;
  color: white;
  border: 2px solid white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 800;
  line-height: 1;
  box-shadow: 0 2px 5px rgba(0,0,0,0.3);
}

/* Selected pin */
.cl-landmark-marker.cl-selected .cl-pin {
  transform: scale(1.32);
  z-index: 1500;
}
.cl-landmark-marker.cl-selected .cl-pin::before {
  content: '';
  position: absolute;
  inset: -8px;
  border: 3px solid var(--fg, #2a6a30);
  border-radius: 50%;
  opacity: 0.4;
  animation: cl-selected-ring 1.4s ease-in-out infinite;
}
@keyframes cl-selected-ring {
  0%, 100% { transform: scale(1); opacity: 0.4; }
  50%      { transform: scale(1.15); opacity: 0.15; }
}
.cl-landmark-marker.cl-selected .cl-pin-circle {
  box-shadow: 0 10px 28px rgba(0,0,0,0.4);
}
</style>