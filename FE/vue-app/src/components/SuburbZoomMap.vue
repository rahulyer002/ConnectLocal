<template>
  <div class="zoom-root">
    <div class="zoom-header">
      <button class="back-btn" type="button" @click="$emit('back')">
        <span aria-hidden="true">←</span>
        <span>Melbourne</span>
      </button>
      <div class="zoom-title">
        <p class="zoom-name">{{ suburb?.suburb_name || 'Loading…' }}</p>
        <p class="zoom-sub">{{ totalShown }} places shown</p>
      </div>
    </div>

    <div class="layer-bar" role="group" aria-label="Map layers">
      <button
        v-for="(def, key) in LAYER_DEFS"
        :key="key"
        type="button"
        class="layer-btn"
        :class="['layer-' + key, { active: layerState[key] }]"
        @click="toggleLayer(key)"
        :aria-pressed="layerState[key]"
      >
        <span class="layer-shape" :class="['shape-' + def.shape]" :style="{ '--c': def.color }">
          <span class="shape-icon" v-html="def.iconHtml"></span>
        </span>
        <span class="layer-label">{{ def.label }}</span>
        <span v-if="layerCounts[key] != null" class="layer-count">{{ layerCounts[key] }}</span>
        <span v-else-if="layerLoading[key]" class="layer-mini-spin" aria-hidden="true"></span>
      </button>
    </div>

    <div class="zoom-map-wrap">
      <div ref="mapEl" class="zoom-map" aria-label="Suburb map with points of interest"></div>
    </div>

    <div
      v-if="selectedPoi"
      class="poi-info"
      role="status"
      aria-live="polite"
    >
      <span class="poi-marker-pill" :class="['shape-' + selectedPoi.shape]" :style="{ '--c': selectedPoi.color }">
        <span class="shape-icon" v-html="selectedPoi.iconHtml"></span>
      </span>
      <div class="poi-meta">
        <p class="poi-cat">{{ selectedPoi.category }}</p>
        <p class="poi-name">{{ selectedPoi.name }}</p>
      </div>
      <button class="poi-action" type="button" @click="planJourney(selectedPoi)">
        Plan a visit
      </button>
      <button class="poi-close" type="button" @click="selectedPoi = null" aria-label="Close">
        ×
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { jsonFetcher } from '../composables/useApi'

const props = defineProps({
  suburb:          { type: Object, default: null },
  suburbFeature:   { type: Object, default: null },
})

const emit = defineEmits(['back'])

const BASE = import.meta.env.VITE_API_BASE_URL
  || import.meta.env.VITE_ACTIVITIES_API_URL
  || 'https://connectlocal.duckdns.org'

const WELCOMING_THEMES = new Set([
  'Community Use', 'Health Services', 'Education Centre', 'Mixed Use',
])

const ICON_BUILDING = `<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M5 21V8l7-4 7 4v13M10 21v-5h4v5"/></svg>`
const ICON_COFFEE   = `<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 8h1a3 3 0 0 1 0 6h-1M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/></svg>`
const ICON_TREE     = `<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2 6 8a6 6 0 1 0 12 0Z M12 8v14"/></svg>`
const ICON_BUS      = `<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="3" width="14" height="14" rx="2"/><path d="M7 17v3M17 17v3M5 11h14M9 7h6"/></svg>`
const ICON_WC       = `<svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="2"/><path d="M12 8v6l3 7M12 14l-3 7M8 11h8"/></svg>`

const LAYER_DEFS = {
  welcoming: {
    label:    'Welcoming',
    color:    '#0F6E56',
    shape:    'pin',
    iconHtml: ICON_BUILDING,
    endpoint: (id) => `/api/suburbs/${id}/landmarks`,
    cat:      'Welcoming space',
    transform: (data) => {
      const items = data?.landmarks || data?.items || (Array.isArray(data) ? data : []) || []
      return items.filter(it => !it.theme || WELCOMING_THEMES.has(it.theme))
    },
    nameOf: (it) => it.landmark_name || it.name || it.title || 'Landmark',
  },
  cafe: {
    label:    'Cafés',
    color:    '#EE8B27',
    shape:    'circle',
    iconHtml: ICON_COFFEE,
    endpoint: (id) => `/api/suburbs/${id}/places?category=social`,
    cat:      'Café or social spot',
    transform: (data) => data?.places || data?.items || (Array.isArray(data) ? data : []) || [],
    nameOf: (it) => it.name || it.place_name || it.amenity || 'Café',
  },
  park: {
    label:    'Parks',
    color:    '#5B9420',
    shape:    'hex',
    iconHtml: ICON_TREE,
    endpoint: (id) => `/api/suburbs/${id}/green-spaces`,
    cat:      'Park or green space',
    transform: (data) => data?.green_spaces || data?.spaces || data?.items || (Array.isArray(data) ? data : []) || [],
    nameOf: (it) => it.space_name || it.name || 'Green space',
  },
  transit: {
    label:    'Transit',
    color:    '#2D7BD4',
    shape:    'pill',
    iconHtml: ICON_BUS,
    endpoint: (id) => `/api/suburbs/${id}/stops`,
    cat:      'Transit stop',
    transform: (data) => data?.stops || data?.items || (Array.isArray(data) ? data : []) || [],
    nameOf: (it) => it.stop_name || it.name || `Stop ${it.stop_id || ''}`.trim(),
  },
  toilet: {
    label:    'Toilets',
    color:    '#6B6A65',
    shape:    'square',
    iconHtml: ICON_WC,
    endpoint: (id) => `/api/suburbs/${id}/toilets`,
    cat:      'Accessible toilet',
    transform: (data) => data?.toilets || data?.items || (Array.isArray(data) ? data : []) || [],
    nameOf: (it) => it.name || it.toilet_name || 'Accessible toilet',
  },
}

const mapEl       = ref(null)
const selectedPoi = ref(null)
const layerState  = reactive({
  welcoming: true, cafe: true, park: true, transit: false, toilet: false,
})
const layerLoading = reactive({})
const layerCounts  = reactive({})

let map = null
let tileLayer = null
let polygonLayer = null
const layerGroups = {}
const poiCache = new Map()

const totalShown = computed(() => {
  let n = 0
  for (const k of Object.keys(LAYER_DEFS)) {
    if (layerState[k] && layerCounts[k] != null) n += layerCounts[k]
  }
  return n
})

function getCoords(item) {
  const lat = item.lat ?? item.latitude ?? item.centroid_lat
  const lon = item.lon ?? item.lng ?? item.longitude ?? item.centroid_lng
  if (lat == null || lon == null) return null
  const la = Number(lat), lo = Number(lon)
  if (Number.isNaN(la) || Number.isNaN(lo)) return null
  return [la, lo]
}

function makeIcon(def) {
  const sizeMap = { pin: [32, 42], circle: [28, 28], hex: [28, 28], pill: [34, 22], square: [22, 22] }
  const [w, h] = sizeMap[def.shape] || [26, 26]
  const anchor = def.shape === 'pin' ? [w / 2, h] : [w / 2, h / 2]
  return L.divIcon({
    className: 'czm-marker-wrap',
    html: `
      <div class="czm-marker shape-${def.shape}" style="--c: ${def.color}">
        <span class="shape-icon">${def.iconHtml}</span>
      </div>
    `,
    iconSize:   [w, h],
    iconAnchor: anchor,
    popupAnchor: [0, -h / 2],
  })
}

async function fetchLayer(layerKey) {
  const id = props.suburb?.suburb_id
  if (!id) return []
  const cacheKey = `${id}::${layerKey}`
  if (poiCache.has(cacheKey)) return poiCache.get(cacheKey)

  const def = LAYER_DEFS[layerKey]
  layerLoading[layerKey] = true
  try {
    const data = await jsonFetcher(`${BASE}${def.endpoint(id)}`)
    const items = def.transform(data) || []
    poiCache.set(cacheKey, items)
    return items
  } catch (e) {
    poiCache.set(cacheKey, [])
    return []
  } finally {
    layerLoading[layerKey] = false
  }
}

async function renderLayer(layerKey) {
  if (!map) return
  if (layerGroups[layerKey]) {
    layerGroups[layerKey].clearLayers()
  } else {
    layerGroups[layerKey] = L.layerGroup().addTo(map)
  }
  if (!layerState[layerKey]) {
    layerCounts[layerKey] = 0
    return
  }

  const def   = LAYER_DEFS[layerKey]
  const items = await fetchLayer(layerKey)
  const icon  = makeIcon(def)

  let plotted = 0
  for (const item of items) {
    const c = getCoords(item)
    if (!c) continue
    const marker = L.marker(c, { icon, riseOnHover: true })
    const name = def.nameOf(item)
    marker.on('click', () => {
      selectedPoi.value = {
        name,
        category: def.cat,
        color:    def.color,
        shape:    def.shape,
        iconHtml: def.iconHtml,
        lat:      c[0],
        lon:      c[1],
      }
    })
    marker.bindTooltip(name, { direction: 'top', offset: [0, -10], opacity: 0.95, className: 'czm-tip' })
    marker.addTo(layerGroups[layerKey])
    plotted++
  }
  layerCounts[layerKey] = plotted
}

async function toggleLayer(layerKey) {
  layerState[layerKey] = !layerState[layerKey]
  await renderLayer(layerKey)
}

function drawSuburbBoundary() {
  if (!map || !props.suburbFeature) return
  if (polygonLayer) { polygonLayer.remove(); polygonLayer = null }
  polygonLayer = L.geoJSON(props.suburbFeature, {
    style: {
      color:       '#04342C',
      weight:      3,
      dashArray:   '8 4',
      fillColor:   '#0F6E56',
      fillOpacity: 0.05,
    },
  }).addTo(map)
  try {
    map.fitBounds(polygonLayer.getBounds(), { padding: [28, 28], maxZoom: 16 })
  } catch {}
}

async function fullRefresh() {
  if (!map) return
  selectedPoi.value = null
  for (const k of Object.keys(LAYER_DEFS)) {
    if (layerGroups[k]) { layerGroups[k].clearLayers() }
    layerCounts[k] = layerState[k] ? null : 0
  }
  drawSuburbBoundary()
  await Promise.all(Object.keys(LAYER_DEFS).map(k => renderLayer(k)))
}

const router = useRouter()
function planJourney(poi) {
  router.push({
    path: '/journey',
    query: { to_lat: String(poi.lat), to_lon: String(poi.lon), to_name: poi.name },
  })
}

watch(() => props.suburb?.suburb_id, () => fullRefresh())
watch(() => props.suburbFeature,     () => fullRefresh())

let resizeObs = null
onMounted(() => {
  map = L.map(mapEl.value, {
    zoomControl:        true,
    scrollWheelZoom:    true,
    attributionControl: true,
    zoomSnap:           0.25,
  })
  map.setView([-37.8, 145.0], 13)

  // Real map base layer — CartoDB Voyager (free, OSM-based, Google-Maps-like look)
  tileLayer = L.tileLayer(
    'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    {
      subdomains:  'abcd',
      maxZoom:     19,
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors © <a href="https://carto.com/attributions">CARTO</a>',
    }
  ).addTo(map)

  try {
    resizeObs = new ResizeObserver(() => map.invalidateSize())
    resizeObs.observe(mapEl.value)
  } catch {}

  fullRefresh()
})

onBeforeUnmount(() => {
  if (resizeObs) try { resizeObs.disconnect() } catch {}
  if (map)       try { map.remove() } catch {}
})
</script>

<style scoped>
.zoom-root {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f2faf0;
  border-radius: 18px;
  overflow: hidden;
}

.zoom-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  background: #ffffff;
  border-bottom: 1px solid #e1f5ee;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: transparent;
  border: 1.5px solid #cfe3d5;
  border-radius: 999px;
  font-size: calc(13px * var(--font-scale));
  font-weight: 600;
  color: #0F6E56;
  cursor: pointer;
  transition: background 0.15s;
}

.back-btn:hover { background: #e1f5ee; }
.back-btn span:first-child { font-size: 16px; line-height: 1; }

.zoom-title { flex: 1; min-width: 0; }

.zoom-name {
  font-family: Georgia, serif;
  margin: 0;
  font-size: calc(18px * var(--font-scale));
  font-weight: 700;
  color: #0f1e12;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.zoom-sub {
  margin: 0;
  font-size: calc(12px * var(--font-scale));
  color: #4a6a4e;
}

.layer-bar {
  display: flex;
  gap: 8px;
  padding: 12px 14px;
  background: #ffffff;
  border-bottom: 1px solid #e1f5ee;
  overflow-x: auto;
  scrollbar-width: thin;
}

.layer-bar::-webkit-scrollbar { height: 6px; }
.layer-bar::-webkit-scrollbar-thumb { background: #cfe3d5; border-radius: 3px; }

.layer-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px 6px 8px;
  background: #f2faf0;
  border: 1px solid transparent;
  border-radius: 999px;
  cursor: pointer;
  font-size: calc(13px * var(--font-scale));
  color: #4a6a4e;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
  transition: all 0.15s;
  position: relative;
}

.layer-btn:hover { background: #e1f5ee; }

.layer-btn.active {
  background: #ffffff;
  border-color: #5DCAA5;
  color: #0f1e12;
  box-shadow: 0 1px 3px rgba(15, 110, 86, 0.1);
}

/* Layer pill shape previews (mini version of the marker) */
.layer-shape {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
}

.layer-shape .shape-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: white;
  position: relative;
  z-index: 2;
}

.layer-count {
  display: inline-block;
  min-width: 22px;
  padding: 1px 7px;
  background: #f2faf0;
  border-radius: 999px;
  font-size: calc(11px * var(--font-scale));
  font-weight: 700;
  color: #0f6e56;
  text-align: center;
}

.layer-btn.active .layer-count {
  background: #e1f5ee;
}

.layer-mini-spin {
  width: 12px;
  height: 12px;
  border: 1.5px solid rgba(15, 110, 86, 0.2);
  border-top-color: #0f6e56;
  border-radius: 50%;
  animation: zoom-spin 0.8s linear infinite;
}

@keyframes zoom-spin { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) { .layer-mini-spin { animation: none; } }

.zoom-map-wrap {
  flex: 1;
  min-height: 0;
  position: relative;
}

.zoom-map {
  width: 100%;
  height: 100%;
  background: #f2faf0;
}

.zoom-map :deep(.leaflet-container) {
  background: #f5f5f0;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}

.zoom-map :deep(.leaflet-control-zoom) {
  border: none;
  margin: 14px;
  box-shadow: 0 2px 8px rgba(15, 110, 86, 0.12);
}

.zoom-map :deep(.leaflet-control-zoom a) {
  background: #ffffff;
  color: #0f1e12;
  width: 36px;
  height: 36px;
  line-height: 34px;
  border: 1px solid #cfe3d5;
}

.zoom-map :deep(.leaflet-control-zoom a:first-child) { border-radius: 10px 10px 0 0; }
.zoom-map :deep(.leaflet-control-zoom a:last-child)  { border-radius: 0 0 10px 10px; border-top: none; }
.zoom-map :deep(.leaflet-control-zoom a:hover)       { background: #e1f5ee; }

.zoom-map :deep(.leaflet-control-attribution) {
  background: rgba(255, 255, 255, 0.85);
  padding: 2px 8px;
  font-size: 10px;
  border-radius: 6px 0 0 0;
}

.zoom-map :deep(.czm-tip) {
  background: #ffffff;
  border: 1px solid #cfe3d5;
  color: #0f1e12;
  font-size: calc(12px * var(--font-scale));
  font-weight: 500;
  border-radius: 8px;
  padding: 5px 10px;
  box-shadow: 0 4px 10px rgba(15, 110, 86, 0.15);
}

.zoom-map :deep(.czm-tip::before) {
  border-top-color: #cfe3d5;
}

/* ─── POI Marker shapes (inside divIcons) ──────────────────────── */
.zoom-map :deep(.czm-marker-wrap) {
  background: transparent;
  border: none;
}

.zoom-map :deep(.czm-marker) {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.15s ease;
  cursor: pointer;
  will-change: transform;
}

.zoom-map :deep(.czm-marker:hover) {
  transform: scale(1.15);
  z-index: 1000;
}

/* Pin (teardrop) — Welcoming */
.zoom-map :deep(.czm-marker.shape-pin) {
  width: 32px;
  height: 42px;
  background: transparent;
  position: relative;
}
.zoom-map :deep(.czm-marker.shape-pin::before) {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 32px;
  height: 32px;
  background: var(--c);
  border: 2.5px solid white;
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
  transform-origin: 50% 50%;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.28);
}
.zoom-map :deep(.czm-marker.shape-pin .shape-icon) {
  position: relative;
  z-index: 2;
  margin-top: -10px;
  color: white;
}

/* Circle with border — Cafés */
.zoom-map :deep(.czm-marker.shape-circle) {
  width: 28px;
  height: 28px;
  background: var(--c);
  border: 2.5px solid white;
  border-radius: 50%;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.22);
}
.zoom-map :deep(.czm-marker.shape-circle .shape-icon) { color: white; }

/* Hexagon — Parks */
.zoom-map :deep(.czm-marker.shape-hex) {
  width: 28px;
  height: 28px;
  background: var(--c);
  clip-path: polygon(50% 0%, 95% 25%, 95% 75%, 50% 100%, 5% 75%, 5% 25%);
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.25));
  position: relative;
}
.zoom-map :deep(.czm-marker.shape-hex::before) {
  content: '';
  position: absolute;
  inset: 2px;
  background: var(--c);
  border: 0;
  clip-path: polygon(50% 0%, 95% 25%, 95% 75%, 50% 100%, 5% 75%, 5% 25%);
}
.zoom-map :deep(.czm-marker.shape-hex .shape-icon) {
  position: relative;
  z-index: 2;
  color: white;
}

/* Pill (rounded rectangle) — Transit */
.zoom-map :deep(.czm-marker.shape-pill) {
  width: 34px;
  height: 22px;
  background: var(--c);
  border: 2px solid white;
  border-radius: 11px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.22);
}
.zoom-map :deep(.czm-marker.shape-pill .shape-icon) { color: white; }

/* Square (rounded) — Toilets */
.zoom-map :deep(.czm-marker.shape-square) {
  width: 22px;
  height: 22px;
  background: var(--c);
  border: 2px solid white;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
.zoom-map :deep(.czm-marker.shape-square .shape-icon) { color: white; }

/* Layer-bar mini shape previews — same look, smaller scale */
.shape-pin {
  width: 16px;
  height: 20px;
  position: relative;
}
.shape-pin::before {
  content: '';
  position: absolute;
  inset: 0;
  width: 16px;
  height: 16px;
  background: var(--c);
  border: 1.5px solid white;
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
  transform-origin: 50% 50%;
}
.shape-pin .shape-icon {
  position: relative;
  z-index: 2;
  margin-top: -4px;
  transform: scale(0.7);
}

.shape-circle {
  width: 16px;
  height: 16px;
  background: var(--c);
  border: 1.5px solid white;
  border-radius: 50%;
}
.shape-circle .shape-icon { transform: scale(0.7); }

.shape-hex {
  width: 16px;
  height: 16px;
  background: var(--c);
  clip-path: polygon(50% 0%, 95% 25%, 95% 75%, 50% 100%, 5% 75%, 5% 25%);
}
.shape-hex .shape-icon { transform: scale(0.7); }

.shape-pill {
  width: 22px;
  height: 14px;
  background: var(--c);
  border: 1.5px solid white;
  border-radius: 7px;
}
.shape-pill .shape-icon { transform: scale(0.6); }

.shape-square {
  width: 14px;
  height: 14px;
  background: var(--c);
  border: 1.5px solid white;
  border-radius: 3px;
}
.shape-square .shape-icon { transform: scale(0.7); }

.poi-info {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  background: #ffffff;
  border-top: 1px solid #e1f5ee;
}

.poi-marker-pill {
  flex-shrink: 0;
}

.poi-marker-pill .shape-icon {
  color: white;
  transform: scale(1.2) !important;
}

.poi-meta { flex: 1; min-width: 0; }

.poi-cat {
  margin: 0;
  font-size: calc(11px * var(--font-scale));
  color: #4a6a4e;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 600;
}

.poi-name {
  margin: 2px 0 0;
  font-size: calc(14px * var(--font-scale));
  color: #0f1e12;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.poi-action {
  padding: 9px 16px;
  background: #0F6E56;
  color: #ffffff;
  border: none;
  border-radius: 999px;
  font-size: calc(13px * var(--font-scale));
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s;
}

.poi-action:hover { background: #04342C; }

.poi-close {
  width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid #cfe3d5;
  border-radius: 50%;
  color: #4a6a4e;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.poi-close:hover { background: #e1f5ee; }

@media (max-width: 640px) {
  .poi-info { flex-wrap: wrap; }
  .poi-meta { flex-basis: 100%; order: -1; }
  .layer-btn { padding: 4px 10px 4px 6px; gap: 6px; }
  .layer-label { font-size: calc(12px * var(--font-scale)); }
}
</style>
