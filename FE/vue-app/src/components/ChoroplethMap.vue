<template>
  <div class="choro-root">
    <div
      v-if="initialLoad"
      class="choro-loading"
      role="status"
      aria-live="polite"
    >
      <div class="choro-loader" aria-hidden="true"></div>
      <p>Loading Melbourne…</p>
    </div>

    <div
      v-if="loadError"
      class="choro-error"
      role="alert"
    >
      <span aria-hidden="true">⚠</span>
      <div>
        <p class="err-title">Couldn't load the map</p>
        <p class="err-msg">{{ loadError }}</p>
        <button class="err-retry" type="button" @click="reload">Try again</button>
      </div>
    </div>

    <div ref="mapEl" class="choro-map" aria-label="Melbourne suburbs map"></div>

    <div v-if="!initialLoad && !loadError" class="choro-legend" aria-hidden="false">
      <span class="leg-lo">{{ legendLow }}</span>
      <span
        v-for="(c, i) in TEAL_STOPS"
        :key="i"
        class="leg-swatch"
        :style="{ background: c }"
      ></span>
      <span class="leg-hi">{{ legendHigh }}</span>
      <span class="leg-nodata">
        <span class="leg-swatch leg-nodata-swatch"></span>
        No data
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useSuburbRankings } from '../composables/useSuburbInference'

const props = defineProps({
  selectedMetric:   { type: String, default: 'outing_score' },
  selectedSuburbId: { type: [Number, null], default: null },
})

const emit = defineEmits(['select', 'hover', 'geojson-loaded'])

const TEAL_STOPS = ['#E1F5EE', '#9FE1CB', '#5DCAA5', '#1D9E75', '#0F6E56', '#085041']
const NO_DATA = '#E5E7EB'

const DOMAINS = {
  outing_score:    { range: [0, 100], unit: ''  },
  score_amenities: { range: [0, 100], unit: ''  },
  score_transit:   { range: [0, 100], unit: ''  },
  score_social:    { range: [0, 100], unit: ''  },
  elderly_pct:     { range: [0, 30],  unit: '%' },
}

// Per-metric plain-English labels. Each value is what the corresponding end
// of the legend gradient *means*, not a raw number. First-time users
// shouldn't have to know that "100" means "fully connected".
const LEGEND_LABELS = {
  outing_score:    { low: 'Less connected',  high: 'More connected' },
  score_amenities: { low: 'Few amenities',   high: 'Lots of amenities' },
  score_transit:   { low: 'Light transit',   high: 'Strong transit' },
  score_social:    { low: 'Fewer locals 65+', high: 'Many locals 65+' },
  elderly_pct:     { low: 'Lower share 65+', high: 'Higher share 65+' },
}

const mapEl       = ref(null)
const initialLoad = ref(true)
const loadError   = ref(null)

let map = null
let geoLayer = null
let geojson  = null
const scoreById = new Map()

const legendLow  = computed(() => LEGEND_LABELS[props.selectedMetric]?.low  ?? 'Low')
const legendHigh = computed(() => LEGEND_LABELS[props.selectedMetric]?.high ?? 'High')

function metricValue(rec, metric = props.selectedMetric) {
  if (!rec) return null
  if (metric === 'outing_score') return rec.outing_score
  if (metric === 'elderly_pct')  return rec.elderly_pct
  if (metric.startsWith('score_')) {
    const key = metric.slice(6)
    return rec.scores?.[key]
  }
  return null
}

function colorFor(value, metric) {
  if (value == null || Number.isNaN(value)) return NO_DATA
  const d = DOMAINS[metric] || DOMAINS.outing_score
  const [lo, hi] = d.range
  const z = Math.max(0, Math.min(1, (value - lo) / (hi - lo)))
  if (z >= 0.83) return TEAL_STOPS[5]
  if (z >= 0.67) return TEAL_STOPS[4]
  if (z >= 0.50) return TEAL_STOPS[3]
  if (z >= 0.33) return TEAL_STOPS[2]
  if (z >= 0.17) return TEAL_STOPS[1]
  return TEAL_STOPS[0]
}

function styleForFeature(feature) {
  const id    = Number(feature.properties.suburb_id)
  const rec   = scoreById.get(id)
  const v     = metricValue(rec)
  const isSel = id === props.selectedSuburbId
  return {
    fillColor:   colorFor(v, props.selectedMetric),
    fillOpacity: rec ? 0.85 : 0.4,
    color:       isSel ? '#04342C' : '#FFFFFF',
    weight:      isSel ? 3 : 0.7,
    opacity:     1,
  }
}

function onEachFeature(feature, layer) {
  layer.on({
    mouseover: (e) => {
      const id = Number(feature.properties.suburb_id)
      const rec = scoreById.get(id)
      e.target.setStyle({ weight: 2.5, color: '#04342C' })
      e.target.bringToFront()
      emit('hover', {
        suburb_id:   id,
        suburb_name: feature.properties.suburb_name,
        value:       metricValue(rec),
        elderly_pct: rec?.elderly_pct ?? null,
        persona:     rec?.persona ?? null,
      })
    },
    mouseout: (e) => {
      if (geoLayer) geoLayer.resetStyle(e.target)
      const id = Number(feature.properties.suburb_id)
      if (id === props.selectedSuburbId) {
        e.target.setStyle({ weight: 3, color: '#04342C' })
        e.target.bringToFront()
      }
      emit('hover', null)
    },
    click: () => {
      emit('select', {
        suburb_id:   Number(feature.properties.suburb_id),
        suburb_name: feature.properties.suburb_name,
      })
    },
  })
}

const { data: rankingsData, error: rankingsError, run: runRankings } =
  useSuburbRankings(() => ({ metric: 'outing_score', top: 1000 }))

async function loadGeo() {
  const res = await fetch('/melbourne-suburbs.geojson')
  if (!res.ok) throw new Error(`Couldn't load suburb boundaries (HTTP ${res.status}). Make sure the file is at /melbourne-suburbs.geojson.`)
  const data = await res.json()
  data.features = data.features.filter(f => f.geometry && f.properties?.suburb_id)
  return data
}

async function reload() {
  loadError.value = null
  initialLoad.value = true
  try {
    await Promise.all([loadGeo().then(d => (geojson = d)), runRankings()])
    rebuildScoreMap()
    drawGeoLayer()
    emit('geojson-loaded', geojson)
  } catch (e) {
    loadError.value = e?.message || 'Something went wrong loading the map.'
  } finally {
    initialLoad.value = false
  }
}

function rebuildScoreMap() {
  scoreById.clear()
  const arr = rankingsData.value?.suburbs || []
  for (const s of arr) scoreById.set(Number(s.suburb_id), s)
}

function drawGeoLayer() {
  if (!map || !geojson) return
  if (geoLayer) { geoLayer.remove(); geoLayer = null }
  geoLayer = L.geoJSON(geojson, {
    style: styleForFeature,
    onEachFeature,
  }).addTo(map)
  try {
    const b = geoLayer.getBounds()
    if (b.isValid()) map.fitBounds(b, { padding: [16, 16], maxZoom: 11 })
  } catch {}
}

function restyleAll() {
  if (!geoLayer) return
  geoLayer.setStyle(styleForFeature)
  geoLayer.eachLayer((layer) => {
    const id = Number(layer.feature?.properties?.suburb_id)
    if (id === props.selectedSuburbId) layer.bringToFront()
  })
}

watch(() => props.selectedMetric,   restyleAll)
watch(() => props.selectedSuburbId, restyleAll)
watch(rankingsData, () => {
  rebuildScoreMap()
  restyleAll()
})
watch(rankingsError, (err) => {
  if (err) loadError.value = err.message
})

let resizeObs = null

onMounted(async () => {
  map = L.map(mapEl.value, {
    zoomControl:           true,
    // scrollWheelZoom stays false — we handle pinch via our own wheel
    // listener below so that regular page-scroll still works.
    scrollWheelZoom:       false,
    doubleClickZoom:       true,
    boxZoom:               false,
    attributionControl:    false,
    zoomSnap:              0.25,
    preferCanvas:          true,
    // Enable Leaflet's built-in keyboard: arrows pan, +/- zoom (when map has focus)
    keyboard:              true,
    keyboardPanDelta:      80,
    // Touch pinch zoom on mobile/tablet
    touchZoom:             true,
    bounceAtZoomLimits:    false,
  })
  // Tighter initial view focused on metro Melbourne where most suburbs sit.
  // This matches the "default zoom" the user requested — covers from Sunbury
  // in the north down to Frankston in the south, and Werribee to Lilydale
  // east–west — without showing the wide regional Greater Melbourne extent.
  map.fitBounds([[-38.10, 144.75], [-37.65, 145.40]], { padding: [12, 12] })

  map.on('click', () => emit('select', null))

  // ─── Pinch-to-zoom on trackpads ───────────────────────────────────────
  // Browsers deliver trackpad pinch gestures as wheel events with
  // `ctrlKey: true` (this is a long-standing convention; the OS sets it,
  // not the user's keyboard). We listen for those specifically so that:
  //   • Trackpad pinch → zoom the map
  //   • Cmd/Ctrl + scroll wheel → zoom the map
  //   • Regular scroll wheel alone → page scrolls normally
  mapEl.value.addEventListener('wheel', onWheelPinch, { passive: false })

  // Window-level +/- and arrow-key zoom so the user doesn't have to click the
  // map first to give it focus. Ignored when the user is typing in an input.
  window.addEventListener('keydown', onWindowKey)

  try {
    resizeObs = new ResizeObserver(() => map.invalidateSize())
    resizeObs.observe(mapEl.value)
  } catch {}

  await reload()
})

function onWheelPinch(e) {
  if (!map) return
  // Trackpad pinch comes through as wheel + ctrlKey. Plain scroll won't have it.
  if (!e.ctrlKey && !e.metaKey) return
  e.preventDefault()
  // deltaY is negative on pinch-out (zoom in), positive on pinch-in (zoom out).
  // Scale the step by deltaY so a fast pinch zooms more than a gentle one.
  const delta = -e.deltaY / 120        // wheel "ticks" → roughly 1 zoom step per tick
  const stepped = Math.max(-2, Math.min(2, delta))
  // Zoom toward the cursor, not the map center, so the gesture feels natural.
  const rect = mapEl.value.getBoundingClientRect()
  const point = L.point(e.clientX - rect.left, e.clientY - rect.top)
  const latlng = map.containerPointToLatLng(point)
  map.setZoomAround(latlng, map.getZoom() + stepped, { animate: false })
}

function onWindowKey(e) {
  if (!map) return
  // Don't hijack typing
  const t = e.target
  if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return

  switch (e.key) {
    case '+':
    case '=':       // unshifted + on US keyboards
      map.zoomIn()
      e.preventDefault()
      break
    case '-':
    case '_':       // shift+- still works
      map.zoomOut()
      e.preventDefault()
      break
    case 'ArrowUp':
      map.panBy([0, -80])
      e.preventDefault()
      break
    case 'ArrowDown':
      map.panBy([0, 80])
      e.preventDefault()
      break
    case 'ArrowLeft':
      map.panBy([-80, 0])
      e.preventDefault()
      break
    case 'ArrowRight':
      map.panBy([80, 0])
      e.preventDefault()
      break
  }
}

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onWindowKey)
  if (mapEl.value) {
    try { mapEl.value.removeEventListener('wheel', onWheelPinch) } catch {}
  }
  if (resizeObs) { try { resizeObs.disconnect() } catch {} }
  if (map)       { try { map.remove() } catch {} }
})
</script>

<style scoped>
.choro-root {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 400px;
  background: #f2faf0;
  border-radius: 18px;
  overflow: hidden;
}

.choro-map {
  width: 100%;
  height: 100%;
  background: #f2faf0;
}

.choro-map :deep(.leaflet-container) {
  background: #f2faf0;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  outline: none;
}

.choro-map :deep(.leaflet-control-zoom) {
  border: none;
  margin: 14px;
  box-shadow: 0 2px 8px rgba(15, 110, 86, 0.08);
}

.choro-map :deep(.leaflet-control-zoom a) {
  background: #ffffff;
  color: #0f1e12;
  border: 1px solid #cfe3d5;
  font-weight: 600;
  width: 36px;
  height: 36px;
  line-height: 34px;
}

.choro-map :deep(.leaflet-control-zoom a:first-child) {
  border-radius: 10px 10px 0 0;
}
.choro-map :deep(.leaflet-control-zoom a:last-child) {
  border-radius: 0 0 10px 10px;
  border-top: none;
}

.choro-map :deep(.leaflet-control-zoom a:hover) {
  background: #e1f5ee;
}

.choro-loading,
.choro-error {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: rgba(242, 250, 240, 0.92);
  z-index: 500;
  text-align: center;
  padding: 24px;
}

.choro-loading p {
  font-family: Georgia, serif;
  color: #0f6e56;
  margin: 0;
  font-size: calc(16px * var(--font-scale));
}

.choro-loader {
  width: 44px;
  height: 44px;
  border: 3px solid #cfe3d5;
  border-top-color: #0a9b8a;
  border-radius: 50%;
  animation: choro-spin 1s linear infinite;
}

@keyframes choro-spin {
  to { transform: rotate(360deg); }
}

@media (prefers-reduced-motion: reduce) {
  .choro-loader { animation: none; }
}

.choro-error {
  flex-direction: row;
  align-items: flex-start;
  gap: 14px;
  background: #FEF5E7;
  text-align: left;
}

.choro-error span[aria-hidden] {
  font-size: 32px;
  color: #B07919;
  line-height: 1;
}

.err-title {
  font-family: Georgia, serif;
  margin: 0 0 4px;
  font-size: calc(17px * var(--font-scale));
  font-weight: 700;
  color: #4A2E10;
}

.err-msg {
  margin: 0 0 12px;
  font-size: calc(14px * var(--font-scale));
  line-height: 1.6;
  color: #4A2E10;
  max-width: 380px;
}

.err-retry {
  padding: 8px 16px;
  background: transparent;
  border: 1.5px solid #B07919;
  border-radius: 999px;
  color: #4A2E10;
  font-size: calc(13px * var(--font-scale));
  font-weight: 700;
  cursor: pointer;
}

.err-retry:hover { background: #B07919; color: white; }

.choro-legend {
  position: absolute;
  bottom: 14px;
  left: 14px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid #cfe3d5;
  border-radius: 999px;
  font-size: calc(12px * var(--font-scale));
  color: #0f1e12;
  box-shadow: 0 2px 8px rgba(15, 110, 86, 0.08);
  z-index: 400;
}

.leg-swatch {
  display: inline-block;
  width: 18px;
  height: 10px;
  border-radius: 2px;
}

.leg-nodata-swatch {
  background: #E5E7EB;
  border: 1px solid #cfe3d5;
}

.leg-nodata {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-left: 8px;
  padding-left: 10px;
  border-left: 1px solid #cfe3d5;
}

.leg-lo, .leg-hi {
  font-weight: 600;
  color: #4a6a4e;
}

@media (max-width: 640px) {
  .choro-legend {
    font-size: calc(11px * var(--font-scale));
    padding: 6px 10px;
  }
  .leg-swatch { width: 12px; height: 8px; }
}
</style>