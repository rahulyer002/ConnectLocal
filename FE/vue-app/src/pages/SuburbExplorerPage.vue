<template>
  <MainLayout>
    <div class="se-page">
      <!-- Toolbar: just search -->
      <div class="se-toolbar">
        <div class="se-search" :class="{ open: searchOpen }">
          <span class="se-search-ic" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
          </span>
          <input
            v-model="search.query.value"
            class="se-search-input"
            type="search"
            placeholder="Find a suburb in Melbourne…"
            aria-label="Search Melbourne suburbs"
            @focus="searchOpen = true"
            @blur="onSearchBlur"
          />
          <button
            v-if="search.query.value"
            class="se-search-clear"
            type="button"
            aria-label="Clear search"
            @mousedown.prevent="search.clear()"
          >×</button>

          <ul
            v-if="searchOpen && search.query.value.trim().length >= 1"
            class="se-search-results"
            role="listbox"
          >
            <li v-if="search.isLoading.value" class="se-result-msg">Searching…</li>
            <li v-else-if="search.error.value" class="se-result-msg err">{{ search.error.value }}</li>
            <li v-else-if="!search.results.value.length" class="se-result-msg">
              No Melbourne suburbs match "{{ search.query.value }}". Try a different name.
            </li>
            <template v-else>
              <li
                v-for="r in search.results.value"
                :key="r.suburb_id"
                role="option"
                tabindex="0"
                class="se-result"
                @mousedown.prevent="onPickResult(r)"
                @keydown.enter="onPickResult(r)"
              >
                <span class="se-result-name">{{ r.suburb_name }}</span>
                <span class="se-result-go" aria-hidden="true">↵</span>
              </li>
            </template>
          </ul>
        </div>
      </div>

      <!-- Main split -->
      <div class="se-body">
        <div class="se-map-area">
          <ChoroplethMap
            v-if="viewMode === 'overview'"
            :selected-metric="selectedMetric"
            :selected-suburb-id="selectedSuburbId"
            @select="onMapSelect"
            @hover="onMapHover"
            @geojson-loaded="onGeojsonLoaded"
          />
          <SuburbZoomMap
            v-else
            :suburb="selectedSuburbForZoom"
            :suburb-feature="selectedFeature"
            @back="exitZoom"
          />

          <!-- ── PROMINENT "Showing X" control (top-left) ── -->
          <div
            v-if="viewMode === 'overview'"
            class="map-view-ctrl"
            ref="fabRef"
          >
            <button
              type="button"
              class="mvc-btn"
              :aria-expanded="fabOpen"
              @click="fabOpen = !fabOpen"
            >
              <span class="mvc-swatch" :style="{ background: currentMetric.color }" aria-hidden="true"></span>
              <span class="mvc-text">
                <span class="mvc-prefix">Showing</span>
                <span class="mvc-metric">{{ currentMetric.label }}</span>
              </span>
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" :class="{ flipped: fabOpen }" class="mvc-chev" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>
            </button>

            <transition name="mvc-menu">
              <div v-if="fabOpen" class="mvc-menu" role="menu">
                <p class="mvc-menu-title">Map view</p>
                <button
                  v-for="m in METRICS"
                  :key="m.key"
                  type="button"
                  role="menuitem"
                  class="mvc-item"
                  :class="{ active: selectedMetric === m.key }"
                  @click="onMetricChange(m.key)"
                >
                  <span class="mvc-item-swatch" :style="{ background: m.color }"></span>
                  <span class="mvc-item-label">{{ m.label }}</span>
                  <svg v-if="selectedMetric === m.key" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>
                </button>
              </div>
            </transition>
          </div>

          <!-- Hover card -->
          <transition name="hover-fade">
            <div v-if="hoveredInfo && viewMode === 'overview'" class="hover-card">
              <p class="hover-name">{{ hoveredInfo.suburb_name }}</p>
              <p class="hover-stats">
                <span v-if="hoveredInfo.elderly_pct != null" class="hover-stat">
                  <span class="hover-stat-num">{{ hoveredInfo.elderly_pct.toFixed(1) }}%</span>
                  aged 65+
                </span>
                <span v-if="hoveredInfo.value != null && hoveredInfo.elderly_pct != null" class="hover-divider" aria-hidden="true">·</span>
                <span v-if="hoveredInfo.value != null" class="hover-stat">
                  <span class="hover-stat-num">{{ formatHoverValue(hoveredInfo.value) }}</span>
                  {{ currentMetric.hoverLabel }}
                </span>
                <span v-else-if="hoveredInfo.elderly_pct == null" class="hover-stat hover-nodata">no data available</span>
              </p>
              <p v-if="hoveredInfo.persona" class="hover-persona">{{ hoveredInfo.persona }}</p>
            </div>
          </transition>
        </div>

        <!-- Side panel -->
        <aside class="se-panel-area">
          <SuburbDetailPanel
            :suburb-id="selectedSuburbId"
            :display-name="selectedDisplayName"
            :top-suburbs="topSuburbs"
            @close="clearSelection"
            @select-suburb="onPanelSelectPeer"
            @find-events="goToEvents"
            @plan-journey="goToJourney"
            @view-on-map="zoomIntoSelected"
          />
        </aside>
      </div>

      <!-- Mobile bottom sheet -->
      <transition name="mobile-sheet">
        <div v-if="isMobile && selectedSuburbId && mobileSheetOpen" class="mobile-sheet">
          <div class="mobile-sheet-grabber" aria-hidden="true"></div>
          <SuburbDetailPanel
            :suburb-id="selectedSuburbId"
            :display-name="selectedDisplayName"
            :top-suburbs="topSuburbs"
            @close="mobileSheetOpen = false"
            @select-suburb="onPanelSelectPeer"
            @find-events="goToEvents"
            @plan-journey="goToJourney"
            @view-on-map="zoomIntoSelected"
          />
        </div>
      </transition>

      <transition name="hover-fade">
        <div
          v-if="isMobile && mobileSheetOpen"
          class="mobile-backdrop"
          @click="mobileSheetOpen = false"
        ></div>
      </transition>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MainLayout         from '../layouts/MainLayout.vue'
import ChoroplethMap      from '../components/ChoroplethMap.vue'
import SuburbZoomMap      from '../components/SuburbZoomMap.vue'
import SuburbDetailPanel  from '../components/SuburbDetailPanel.vue'
import { useSuburbSearch }    from '../composables/useSuburbSearch'
import { useSuburbRankings }  from '../composables/useSuburbInference'

const METRICS = [
  { key: 'outing_score',    label: 'Connection',        hoverLabel: 'connection',    color: '#0F6E56' },
  { key: 'score_amenities', label: 'Amenities',         hoverLabel: 'amenities',     color: '#1D9E75' },
  { key: 'score_transit',   label: 'Transit',           hoverLabel: 'transit',       color: '#2D7BD4' },
  { key: 'score_social',    label: 'Welcoming places',  hoverLabel: 'welcoming',     color: '#EE8B27' },
  { key: 'elderly_pct',     label: 'Aged 65 and over',  hoverLabel: 'aged 65+',      color: '#7C3AED' },
]

const route  = useRoute()
const router = useRouter()

const selectedMetric      = ref('outing_score')
const selectedSuburbId    = ref(null)
const selectedDisplayName = ref('')
const viewMode            = ref('overview')
const hoveredInfo         = ref(null)
const allFeatures         = ref([])
const isMobile            = ref(false)
const mobileSheetOpen     = ref(false)
const searchOpen          = ref(false)
const fabOpen             = ref(false)
const fabRef              = ref(null)

const search = useSuburbSearch()

const { data: rankingsData, run: runRankings } =
  useSuburbRankings(() => ({ metric: 'outing_score', top: 10 }))

const currentMetric = computed(() =>
  METRICS.find(m => m.key === selectedMetric.value) || METRICS[0]
)

const topSuburbs = computed(() => (rankingsData.value?.suburbs || []).slice(0, 4))

onMounted(async () => {
  checkViewport()
  window.addEventListener('resize', checkViewport)
  window.addEventListener('keydown', onKeydown)
  window.addEventListener('click', onDocClick)

  const id = route.query.id ? Number(route.query.id) : null
  const m  = route.query.metric
  if (m && METRICS.some(x => x.key === m)) selectedMetric.value = m
  if (id) selectSuburb(id)

  await runRankings()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkViewport)
  window.removeEventListener('keydown', onKeydown)
  window.removeEventListener('click', onDocClick)
})

function checkViewport() {
  isMobile.value = window.innerWidth < 900
}

function onKeydown(e) {
  if (e.key === 'Escape') {
    if (fabOpen.value) fabOpen.value = false
    else if (mobileSheetOpen.value) mobileSheetOpen.value = false
    else if (selectedSuburbId.value) clearSelection()
  }
}

function onDocClick(e) {
  if (fabOpen.value && fabRef.value && !fabRef.value.contains(e.target)) {
    fabOpen.value = false
  }
}

function onMetricChange(key) {
  selectedMetric.value = key
  fabOpen.value = false
  syncUrl()
}

function selectSuburb(id, name = '') {
  selectedSuburbId.value = id
  if (name) selectedDisplayName.value = name
  if (isMobile.value) mobileSheetOpen.value = true
  syncUrl()
}

function clearSelection() {
  selectedSuburbId.value = null
  selectedDisplayName.value = ''
  viewMode.value = 'overview'
  mobileSheetOpen.value = false
  syncUrl()
}

function syncUrl() {
  const next = { ...route.query }
  if (selectedSuburbId.value) next.id = String(selectedSuburbId.value)
  else delete next.id
  next.metric = selectedMetric.value
  router.replace({ query: next }).catch(() => {})
}

function onMapSelect(payload) {
  if (!payload) return
  selectSuburb(payload.suburb_id, payload.suburb_name)
}

function onMapHover(info) {
  if (isMobile.value) return
  hoveredInfo.value = info
}

function onGeojsonLoaded(geo) {
  allFeatures.value = geo?.features || []
}

const selectedFeature = computed(() => {
  if (!selectedSuburbId.value) return null
  return allFeatures.value.find(
    f => Number(f.properties?.suburb_id) === selectedSuburbId.value,
  ) || null
})

const selectedSuburbForZoom = computed(() => ({
  suburb_id:   selectedSuburbId.value,
  suburb_name: selectedFeature.value?.properties?.suburb_name || selectedDisplayName.value,
}))

function zoomIntoSelected() {
  if (!selectedSuburbId.value || !selectedFeature.value) return
  viewMode.value = 'detail'
  if (isMobile.value) mobileSheetOpen.value = false
}

function exitZoom() {
  viewMode.value = 'overview'
}

function onPanelSelectPeer(id) {
  if (!id) return
  const feat = allFeatures.value.find(f => Number(f.properties?.suburb_id) === Number(id))
  selectSuburb(Number(id), feat?.properties?.suburb_name || '')
}

function onSearchBlur() {
  setTimeout(() => { searchOpen.value = false }, 120)
}

function onPickResult(r) {
  selectSuburb(Number(r.suburb_id), r.suburb_name)
  search.clear()
  searchOpen.value = false
}

function formatHoverValue(v) {
  if (v == null || isNaN(v)) return '—'
  if (selectedMetric.value === 'elderly_pct') return `${Number(v).toFixed(1)}%`
  return `${Math.round(v)}/100`
}

function goToEvents() {
  if (!selectedSuburbId.value) return
  router.push({ path: '/discover', query: { suburb_id: String(selectedSuburbId.value) } })
}

function goToJourney() {
  const feat = selectedFeature.value
  if (!feat) { router.push('/journey'); return }
  let lat = null, lon = null
  try {
    const coords = feat.geometry?.coordinates
    if (feat.geometry?.type === 'MultiPolygon') {
      const ring = coords[0][0]
      lat = ring.reduce((a, c) => a + c[1], 0) / ring.length
      lon = ring.reduce((a, c) => a + c[0], 0) / ring.length
    } else if (feat.geometry?.type === 'Polygon') {
      const ring = coords[0]
      lat = ring.reduce((a, c) => a + c[1], 0) / ring.length
      lon = ring.reduce((a, c) => a + c[0], 0) / ring.length
    }
  } catch {}
  if (lat != null && lon != null) {
    router.push({ path: '/journey', query: { from_lat: lat.toFixed(5), from_lon: lon.toFixed(5) } })
  } else {
    router.push('/journey')
  }
}
</script>

<style scoped>
.se-page {
  --teal:        #0F6E56;
  --teal-deep:   #04342C;
  --teal-soft:   #E1F5EE;
  --mint:        #F2FAF0;
  --ink:         #0f1e12;
  --muted:       #6a7e6d;
  --line:        #ECF3EC;

  min-height: calc(100vh - 80px);
  background: linear-gradient(180deg, #f8fcf6 0%, #ebf6e8 100%);
  padding: 20px 24px 24px;
}

/* Toolbar */
.se-toolbar {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 16px;
}
.se-search {
  position: relative;
  display: flex;
  align-items: center;
  background: #ffffff;
  border: 1.5px solid var(--line);
  border-radius: 999px;
  padding: 6px 14px;
  flex: 1;
  min-width: 220px;
  max-width: 480px;
  transition: border-color 0.15s, box-shadow 0.15s;
  /* Sit above Leaflet panes (max 700) and the "Showing X" pill (800) */
  z-index: 1500;
}
.se-search.open {
  border-color: var(--teal);
  box-shadow: 0 0 0 3px rgba(15, 110, 86, 0.12);
}
.se-search-ic { color: var(--muted); display: inline-flex; margin-right: 6px; }
.se-search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: calc(15px * var(--font-scale));
  color: var(--ink);
  font-family: inherit;
  outline: none;
  padding: 6px 0;
}
.se-search-input::placeholder { color: var(--muted); }
.se-search-clear {
  border: none;
  background: transparent;
  font-size: 18px;
  line-height: 1;
  color: var(--muted);
  cursor: pointer;
  padding: 4px 6px;
}
.se-search-results {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 6px;
  list-style: none;
  margin: 0;
  max-height: 320px;
  overflow-y: auto;
  /* Above the search input's own stacking context — above Leaflet, above pills */
  z-index: 1600;
  box-shadow: 0 8px 24px rgba(15, 110, 86, 0.18);
}
.se-result {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-radius: 10px;
  cursor: pointer;
  font-size: calc(14px * var(--font-scale));
  transition: background 0.1s;
}
.se-result:hover, .se-result:focus { background: var(--teal-soft); outline: none; }
.se-result-name { color: var(--ink); font-weight: 500; }
.se-result-go { color: var(--muted); font-size: 12px; opacity: 0; transition: opacity 0.15s; }
.se-result:hover .se-result-go, .se-result:focus .se-result-go { opacity: 1; }
.se-result-msg {
  padding: 12px 14px;
  font-size: calc(13px * var(--font-scale));
  color: var(--muted);
  text-align: center;
}
.se-result-msg.err { color: #B07919; }

/* Main split */
.se-body {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 440px;
  gap: 20px;
  height: calc(100vh - 200px);
  min-height: 540px;
}
.se-map-area {
  height: 100%;
  min-height: 480px;
  position: relative;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(15, 110, 86, 0.08);
}
.se-panel-area {
  height: 100%;
  min-height: 480px;
}

/* ──────────────────────────────────────────────────────────────── */
/*  "Showing X" map view control — top-RIGHT so it doesn't overlap   */
/*  with Leaflet's top-left +/- zoom controls                        */
/* ──────────────────────────────────────────────────────────────── */
.map-view-ctrl {
  position: absolute;
  top: 18px;
  right: 18px;
  z-index: 800;
}
.mvc-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px 10px 12px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 14px;
  cursor: pointer;
  font-family: inherit;
  font-size: calc(13px * var(--font-scale));
  font-weight: 600;
  color: var(--ink);
  box-shadow: 0 4px 14px rgba(15, 110, 86, 0.14);
  transition: all 0.15s;
}
.mvc-btn:hover { border-color: #5DCAA5; transform: translateY(-1px); }
.mvc-swatch {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.6);
}
.mvc-text { display: inline-flex; align-items: baseline; gap: 6px; }
.mvc-prefix {
  font-size: calc(11px * var(--font-scale));
  color: var(--muted);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.mvc-metric { color: var(--ink); }
.mvc-chev { color: var(--muted); transition: transform 0.2s; }
.mvc-chev.flipped { transform: rotate(180deg); }

.mvc-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 6px;
  min-width: 240px;
  box-shadow: 0 8px 28px rgba(15, 110, 86, 0.2);
  display: flex;
  flex-direction: column;
}
.mvc-menu-title {
  margin: 0;
  padding: 8px 12px 6px;
  font-size: calc(11px * var(--font-scale));
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
  font-weight: 600;
}
.mvc-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-family: inherit;
  font-size: calc(13px * var(--font-scale));
  color: var(--ink);
  text-align: left;
  width: 100%;
  transition: background 0.1s;
}
.mvc-item:hover { background: var(--mint); }
.mvc-item.active { background: var(--teal-soft); }
.mvc-item.active .mvc-item-label { color: var(--teal-deep); font-weight: 600; }
.mvc-item svg { color: var(--teal); margin-left: auto; }
.mvc-item-swatch {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.mvc-item-label { flex: 1; }

.mvc-menu-enter-active, .mvc-menu-leave-active {
  transition: opacity 0.18s, transform 0.18s cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: top left;
}
.mvc-menu-enter-from, .mvc-menu-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.96);
}

/* ──────────────────────────────────────────────────────────────── */
/*  Hover card — z-index above Leaflet panes (max 700)              */
/* ──────────────────────────────────────────────────────────────── */
.hover-card {
  position: absolute;
  top: 18px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 20px;
  background: rgba(15, 30, 18, 0.96);
  color: #ffffff;
  border-radius: 14px;
  z-index: 999;
  pointer-events: none;
  text-align: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.22);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  max-width: 360px;
}
.hover-name {
  margin: 0 0 4px;
  font-family: Georgia, serif;
  font-size: calc(15px * var(--font-scale));
  font-weight: 700;
  letter-spacing: -0.01em;
}
.hover-stats {
  margin: 0;
  font-size: calc(12px * var(--font-scale));
  opacity: 0.92;
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: center;
  flex-wrap: wrap;
}
.hover-stat-num {
  font-family: Georgia, serif;
  font-weight: 700;
  color: #9FE1CB;
  margin-right: 4px;
}
.hover-divider { opacity: 0.5; }
.hover-nodata { opacity: 0.7; font-style: italic; }
.hover-persona {
  display: inline-block;
  margin: 4px 0 0;
  padding: 2px 10px;
  background: rgba(93, 202, 165, 0.18);
  border-radius: 999px;
  font-size: calc(11px * var(--font-scale));
  color: #9FE1CB;
  font-weight: 600;
}

.hover-fade-enter-active, .hover-fade-leave-active {
  transition: opacity 0.18s, transform 0.18s;
}
.hover-fade-enter-from, .hover-fade-leave-to { opacity: 0; }

@media (prefers-reduced-motion: reduce) {
  .mvc-menu-enter-active, .mvc-menu-leave-active,
  .hover-fade-enter-active, .hover-fade-leave-active { transition: none; }
}

/* Mobile */
@media (max-width: 900px) {
  .se-page { padding: 14px 16px 16px; }
  .se-body {
    grid-template-columns: 1fr;
    height: calc(100vh - 160px);
  }
  .se-panel-area { display: none; }
  .hover-card {
    top: 76px;
    max-width: 280px;
    padding: 10px 16px;
  }
  .map-view-ctrl {
    top: 14px;
    left: 14px;
    right: 14px;
  }
  .mvc-btn { width: 100%; justify-content: space-between; }
  .mvc-menu { left: 0; right: 0; min-width: 0; }
}

/* Mobile bottom sheet */
.mobile-sheet {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 90vh;
  background: #ffffff;
  border-radius: 24px 24px 0 0;
  z-index: 1100;
  display: flex;
  flex-direction: column;
  box-shadow: 0 -4px 24px rgba(15, 110, 86, 0.18);
  overflow: hidden;
}
.mobile-sheet-grabber {
  width: 40px;
  height: 4px;
  background: var(--line);
  border-radius: 2px;
  margin: 10px auto 0;
  flex-shrink: 0;
}
.mobile-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 30, 18, 0.4);
  z-index: 1099;
}

.mobile-sheet-enter-active, .mobile-sheet-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.mobile-sheet-enter-from, .mobile-sheet-leave-to { transform: translateY(100%); }
</style>