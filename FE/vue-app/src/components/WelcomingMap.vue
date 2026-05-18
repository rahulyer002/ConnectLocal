<template>
  <div class="welcoming-map-wrap" :class="{ loading: !mapReady }">
    <div ref="mapEl" class="welcoming-map" aria-label="Map of welcoming spaces"></div>
    <div v-if="!mapReady" class="map-loading-overlay">
      <div class="map-spinner" aria-hidden="true"></div>
      <p>Loading map…</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  landmarks: { type: Array, default: () => [] },
  userLat:   { type: Number, default: null },
  userLon:   { type: Number, default: null },
  selectedId:{ type: [String, Number, null], default: null },
})
const emit = defineEmits(['select'])

const mapEl = ref(null)
const mapReady = ref(false)
let map = null
let landmarkMarkers = []
let userMarker = null

// Category → color mapping (matches the legend in BestTimePage)
function categoryColor(subTheme) {
  const s = (subTheme || '').toLowerCase()
  if (s.includes('library'))   return { bg: '#e6dcff', fg: '#5b3fb6' }
  if (s.includes('police'))    return { bg: '#dde6f8', fg: '#2a4ab0' }
  if (s.includes('fire'))      return { bg: '#ffe2d8', fg: '#c44a2c' }
  if (s.includes('visitor'))   return { bg: '#fff3c2', fg: '#b88a00' }
  if (s.includes('court'))     return { bg: '#f0e0d0', fg: '#6a3a1a' }
  if (s.includes('public') || s.includes('hall')) return { bg: '#d6f4e7', fg: '#1d7169' }
  if (s.includes('health'))    return { bg: '#fce4ec', fg: '#c44a8a' }
  return { bg: '#e0eedc', fg: '#4a6a4e' }
}

function buildLandmarkIcon(landmark, isSelected) {
  const c = categoryColor(landmark.sub_theme)
  return L.divIcon({
    className: 'cl-pin-wrap',
    html: `
      <div class="cl-pin ${isSelected ? 'is-selected' : ''}" style="background:${c.bg};border-color:${c.fg};">
        <span class="cl-pin-dot" style="background:${c.fg}"></span>
      </div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  })
}

function buildUserIcon() {
  return L.divIcon({
    className: 'cl-user-wrap',
    html: `<div class="cl-user-pulse"></div><div class="cl-user-dot"></div><span class="cl-user-tag">YOU</span>`,
    iconSize: [40, 40],
    iconAnchor: [20, 20],
  })
}

function renderLandmarks() {
  if (!map) return
  for (const m of landmarkMarkers) map.removeLayer(m)
  landmarkMarkers = []
  for (const l of props.landmarks) {
    if (l.lat == null || (l.lng == null && l.lon == null)) continue
    const lng = l.lng ?? l.lon
    const isSelected = props.selectedId && (props.selectedId === l.landmark_id)
    const marker = L.marker([l.lat, lng], {
      icon: buildLandmarkIcon(l, isSelected),
      keyboard: true,
      title: l.name || 'Welcoming space',
    })
    marker.on('click', () => emit('select', l.landmark_id))
    marker.addTo(map)
    landmarkMarkers.push(marker)
  }
}

function renderUser() {
  if (!map) return
  if (userMarker) { map.removeLayer(userMarker); userMarker = null }
  if (props.userLat == null || props.userLon == null) return
  userMarker = L.marker([props.userLat, props.userLon], {
    icon: buildUserIcon(),
    interactive: false,
    zIndexOffset: 1000,
  }).addTo(map)
}

function fitBounds() {
  if (!map) return
  const pts = []
  if (props.userLat != null && props.userLon != null) pts.push([props.userLat, props.userLon])
  for (const l of props.landmarks) {
    if (l.lat != null) pts.push([l.lat, l.lng ?? l.lon])
  }
  if (!pts.length) return
  if (pts.length === 1) map.setView(pts[0], 15)
  else map.fitBounds(L.latLngBounds(pts), { padding: [40, 40], maxZoom: 15 })
}

onMounted(async () => {
  await nextTick()
  map = L.map(mapEl.value, {
    zoomControl: true,
    scrollWheelZoom: false,
    attributionControl: true,
  }).setView([props.userLat || -37.8136, props.userLon || 144.9631], 14)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors',
  }).addTo(map)

  renderUser()
  renderLandmarks()
  fitBounds()

  setTimeout(() => {
    if (map) map.invalidateSize()
    mapReady.value = true
  }, 200)
})

onBeforeUnmount(() => {
  if (map) { map.remove(); map = null }
  landmarkMarkers = []
  userMarker = null
})

watch(() => props.landmarks, () => { renderLandmarks(); fitBounds() }, { deep: true })
watch(() => [props.userLat, props.userLon], () => { renderUser(); fitBounds() })
watch(() => props.selectedId, (newId, oldId) => {
  // Re-render with new selection highlight
  renderLandmarks()
  // Pan to selected
  if (newId) {
    const l = props.landmarks.find(x => x.landmark_id === newId)
    if (l && map) map.panTo([l.lat, l.lng ?? l.lon])
  }
})
</script>

<style scoped>
.welcoming-map-wrap {
  position: relative;
  width: 100%; height: 520px;
  border-radius: 18px; overflow: hidden;
  border: 1px solid rgba(29,113,105,0.16);
  box-shadow: 0 12px 32px rgba(10,155,138,0.1);
  background: #f0f5ee;
}
.welcoming-map { width: 100%; height: 100%; }

.map-loading-overlay {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px;
  background: rgba(247,251,244,0.92); backdrop-filter: blur(4px);
  font-family: system-ui,sans-serif; color: #4a6a4e; font-size: 14px;
  z-index: 400;
}
.map-spinner { width: 28px; height: 28px; border-radius: 50%; border: 3px solid rgba(10,155,138,0.18); border-top-color: #0a9b8a; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 760px) {
  .welcoming-map-wrap { height: 420px; }
}
</style>

<!-- Leaflet injects pin DOM directly into the body; selectors must be unscoped -->
<style>
.cl-pin {
  width: 28px; height: 28px; border-radius: 50%;
  border: 2px solid;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 10px rgba(0,0,0,0.18);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}
.cl-pin:hover { transform: scale(1.18); box-shadow: 0 6px 14px rgba(0,0,0,0.28); }
.cl-pin.is-selected { transform: scale(1.32); box-shadow: 0 0 0 4px rgba(10,155,138,0.32), 0 8px 18px rgba(0,0,0,0.3); }
.cl-pin-dot { width: 10px; height: 10px; border-radius: 50%; }

.cl-user-wrap { position: relative; }
.cl-user-pulse {
  position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%);
  width: 32px; height: 32px; border-radius: 50%;
  background: rgba(10,155,138,0.35);
  animation: cl-user-pulse 2.2s ease-out infinite;
}
.cl-user-dot {
  position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%);
  width: 14px; height: 14px; border-radius: 50%;
  background: #0a9b8a; border: 2.5px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.32);
}
.cl-user-tag {
  position: absolute; left: 50%; top: -16px; transform: translateX(-50%);
  padding: 1px 7px; background: #0a9b8a; color: white;
  font-family: system-ui,sans-serif; font-size: 9px; font-weight: 800;
  letter-spacing: 0.06em; border-radius: 999px; text-transform: uppercase;
  white-space: nowrap;
}
@keyframes cl-user-pulse {
  0% { transform: translate(-50%,-50%) scale(0.6); opacity: 0.8; }
  100% { transform: translate(-50%,-50%) scale(2.2); opacity: 0; }
}
</style>
