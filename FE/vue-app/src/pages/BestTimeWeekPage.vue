<template>
  <div class="week-page">
    <div class="noise" aria-hidden="true"></div>
    <div class="orb orb-1" aria-hidden="true"></div>
    <div class="orb orb-2" aria-hidden="true"></div>

    <BestTimeLocationBar />

    <section class="hero">
      <div class="hero-bg-word" aria-hidden="true">FORECAST</div>
      <div class="hero-inner">
        <RouterLink to="/best-time" class="back-btn">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          Back to live score
        </RouterLink>
        <p class="hero-eyebrow"><span class="eyebrow-line"></span>Your 7-day resonance forecast</p>
        <h1 class="hero-headline">
          Your best windows<br>
          <em>this week.</em>
        </h1>
        <p class="hero-sub" :style="{ fontSize: scaledPx(18) }">
          Built from 2 years of City of Melbourne pedestrian sensor data. Find quieter windows for outings.
        </p>
      </div>

      <div v-if="store.locationReady && quietestDay" class="best-window-callout">
        <div class="bw-icon">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        </div>
        <div class="bw-text">
          <p class="bw-label">Best window this week</p>
          <p class="bw-main"><strong>{{ quietestDay.day }} at {{ formatHour(quietestDay.hour) }}</strong> — your quietest moment.</p>
        </div>
        <RouterLink to="/best-time/now" class="bw-btn">
          Find best spots
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
        </RouterLink>
      </div>
    </section>

    <section v-if="!store.locationReady" class="empty-band">
      <div class="empty-card">
        <h3 :style="{ fontSize: scaledPx(24) }">Set your location to see your forecast</h3>
        <p :style="{ fontSize: scaledPx(16) }">Use the location bar above to set your suburb, then your 7-day heatmap will appear here.</p>
      </div>
    </section>

    <template v-else>
      <section v-if="store.loadingForecast && !store.forecastResult" class="loading-band">
        <div class="big-spinner" aria-hidden="true"></div>
        <p :style="{ fontSize: scaledPx(18) }">Building your week forecast…</p>
      </section>

      <template v-else-if="store.forecastResult">
        <section class="heatmap-band" data-reveal>
          <div class="heatmap-inner">
            <div class="heatmap-header">
              <p class="section-label">Crowd heatmap</p>
              <h2 class="section-heading" :style="{ fontSize: scaledPx(40) }">
                Crowd heatmap<br><em>this week.</em>
              </h2>
              <p class="section-sub" :style="{ fontSize: scaledPx(15) }">
                Each cell is one hour, 8am – 8pm. Darker teal means quieter; warmer tones mean busier. Tap a cell for detail.
              </p>
            </div>

            <div class="heatmap-wrap">
              <div class="heat-grid axis-row">
                <div class="day-spacer"></div>
                <span v-for="h in displayHours" :key="`hh-${h}`" class="hour-label">{{ formatHour(h) }}</span>
              </div>

              <div v-for="day in forecastDays" :key="day" class="heat-grid day-row">
                <div class="day-label">{{ day.slice(0, 3) }}</div>
                <button
                  v-for="h in displayHours"
                  :key="`${day}-${h}`"
                  class="heat-cell"
                  :style="cellStyle(day, h)"
                  :class="{ 'cell-selected': isSelected(day, h), 'cell-best': isBestCell(day, h) }"
                  :aria-label="`${day} ${formatHour(h)} ${getHourData(day, h)?.crowd_level || 'unknown'}`"
                  @click="selectCell(day, h)"
                >
                  <span v-if="isBestCell(day, h)" class="best-star" aria-hidden="true">
                    <svg viewBox="0 0 24 24" width="11" height="11" fill="white" stroke="white" stroke-width="0.5" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                  </span>
                </button>
              </div>

              <div class="legend-row">
                <div class="day-spacer"></div>
                <div class="legend-content">
                  <span class="legend-label">Quietest</span>
                  <div class="legend-bar"></div>
                  <span class="legend-label">Busiest</span>
                </div>
              </div>
            </div>

            <div v-if="selectedCell" class="cell-detail">
              <div class="cd-icon">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              </div>
              <div class="cd-text">
                <span class="cd-when">{{ selectedCell.day }}, {{ formatHour(selectedCell.hour) }}</span>
                <span class="cd-meta">
                  <span class="crowd-badge" :class="`crowd-${selectedCell.level.toLowerCase()}`">{{ selectedCell.level }}</span>
                  <span class="cd-count">~{{ selectedCell.avg_count }} people/hr</span>
                </span>
              </div>
              <RouterLink to="/best-time/now" class="cd-plan-btn">
                Plan this visit
                <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
              </RouterLink>
              <button class="cd-close" @click="selectedCell = null" aria-label="Close detail">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>
            <p v-if="store.forecastResult.data_note" class="data-note">{{ store.forecastResult.data_note }}</p>
          </div>
        </section>

        <section class="cream-band" data-reveal>
          <div class="cream-inner">
            <div class="cream-grid">
              <div class="quietest-card" v-if="quietestDay">
                <p class="card-label">Quietest day this week</p>
                <h3 class="qd-day" :style="{ fontSize: scaledPx(48) }">{{ quietestDay.day }}</h3>
                <p class="qd-best">Best from {{ formatHour(quietestDay.hour) }}</p>
                <div class="qd-stats">
                  <span class="crowd-badge crowd-low">Low crowd</span>
                  <span class="qd-count">~{{ quietestDay.avg_count }} people/hr</span>
                </div>
                <RouterLink to="/best-time/now" class="qd-cta">
                  Find quiet spots near me
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
                </RouterLink>
              </div>

              <div class="spaces-section">
                <p class="card-label">Comfortable parks near you</p>
                <h3 class="spaces-heading" :style="{ fontSize: scaledPx(28) }">Green spaces ranked by comfort</h3>
                <p class="spaces-sub" :style="{ fontSize: scaledPx(14) }">Comfort score combines walkability, shade, and toilet access.</p>

                <div v-if="store.loadingSpaces && !store.greenSpaces.length" class="mini-loading">
                  <div class="mini-spin" aria-hidden="true"></div> Loading nearby parks…
                </div>
                <div v-else-if="store.greenSpaces.length" class="spaces-list">
                  <article v-for="space in store.greenSpaces.slice(0, 5)" :key="space.space_id || space.space_name" class="space-row">
                    <div class="space-icon">
                      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 22c1.25-1.25 2.5-2.5 3.5-4C7 16 8 13.5 8 11c0-5.5 4.5-9 9-9 0 4.5-1 8-3.5 10.5S8.5 16 6 18c-1 1-2.5 2.5-4 4z"/></svg>
                    </div>
                    <div class="space-info">
                      <span class="space-name" :style="{ fontSize: scaledPx(15) }">{{ space.space_name }}</span>
                      <span class="space-meta">
                        {{ space.distance_km?.toFixed(1) }} km
                        <span v-if="space.has_toilet_nearby" class="micro-tag toilet">Toilet</span>
                        <span v-if="space.walkability_score > 70" class="micro-tag walk">Walkable</span>
                      </span>
                    </div>
                    <div class="space-comfort">
                      <span class="comfort-num" :style="{ fontSize: scaledPx(20) }">{{ Math.round(space.comfort_score) }}</span>
                      <div class="comfort-bar"><div class="comfort-fill" :class="comfortBarClass(space.comfort_score)" :style="{ width: `${space.comfort_score}%` }"></div></div>
                    </div>
                  </article>
                </div>
                <p v-else class="no-spaces">No parks found nearby. Try a different location.</p>
              </div>
            </div>
          </div>
        </section>
      </template>

      <section v-else class="empty-band">
        <div class="empty-card">
          <h3 :style="{ fontSize: scaledPx(24) }">No forecast data available</h3>
          <p :style="{ fontSize: scaledPx(16) }">No pedestrian sensors found near this location. Try a suburb closer to Melbourne CBD.</p>
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
          <RouterLink to="/welcoming-spaces" class="bnav-btn">
            Welcoming spaces
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
          </RouterLink>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { resonanceStore } from '../stores/resonanceStore'
import { uiStore } from '../stores/uiStore'
import { useResonanceApi } from '../composables/useResonanceApi'
import BestTimeLocationBar from '../components/BestTimeLocationBar.vue'

const store = resonanceStore
const { fetchForecast, fetchGreenSpaces } = useResonanceApi()
const scaledPx = (base) => `${(base * uiStore.textScale) / 100}px`

const selectedCell = ref(null)
const displayHours = Array.from({ length: 13 }, (_, i) => i + 8)

const forecastDays = computed(() => store.forecastResult?.forecast_days ?? [])

function formatHour(h) {
  const ampm = h < 12 ? 'am' : 'pm'
  const h12  = h % 12 === 0 ? 12 : h % 12
  return `${h12}${ampm}`
}
function getHourData(day, hour) { return store.forecastResult?.forecast?.[day]?.[hour] ?? null }
function isSelected(day, hour) { return selectedCell.value?.day === day && selectedCell.value?.hour === hour }
function selectCell(day, hour) {
  const d = getHourData(day, hour)
  if (!d) return
  if (isSelected(day, hour)) { selectedCell.value = null; return }
  selectedCell.value = { day, hour, level: d.crowd_level, avg_count: Math.round(d.avg_count) }
}
function isBestCell(day, hour) { return quietestDay.value?.day === day && quietestDay.value?.hour === hour }

const maxCount = computed(() => {
  let m = 1
  for (const day of forecastDays.value) {
    for (const h of displayHours) {
      const d = getHourData(day, h)
      if (d && d.avg_count > m) m = d.avg_count
    }
  }
  return m
})

function countToColor(count) {
  const t = Math.min(count / maxCount.value, 1)
  const stops = [
    [10, 110, 98],
    [86, 154, 102],
    [212, 168, 84],
    [196, 110, 76],
    [156, 60, 50],
  ]
  const seg = t * (stops.length - 1)
  const lo  = Math.floor(seg)
  const hi  = Math.min(lo + 1, stops.length - 1)
  const f   = seg - lo
  const [r1,g1,b1] = stops[lo]
  const [r2,g2,b2] = stops[hi]
  return {
    r: Math.round(r1 + (r2 - r1) * f),
    g: Math.round(g1 + (g2 - g1) * f),
    b: Math.round(b1 + (b2 - b1) * f),
  }
}

function cellStyle(day, hour) {
  const d = getHourData(day, hour)
  if (!d) return { background: '#eaf4ea' }
  const { r, g, b } = countToColor(d.avg_count)
  return { background: `rgb(${r},${g},${b})` }
}

const quietestDay = computed(() => {
  const f = store.forecastResult?.forecast
  if (!f) return null
  let best = null
  for (const day of forecastDays.value) {
    for (const h of displayHours) {
      const d = f[day]?.[h]
      if (!d || d.crowd_level !== 'Low') continue
      if (!best || d.avg_count < best.avg_count) {
        best = { day, hour: h, avg_count: Math.round(d.avg_count) }
      }
    }
  }
  return best
})

function comfortBarClass(s) {
  if (s >= 70) return 'high'
  if (s >= 45) return 'mid'
  return 'low'
}

async function loadAll() {
  if (!store.locationReady) return
  const { userLat: lat, userLon: lon } = store
  store.loadingForecast = true
  store.loadingSpaces = true
  selectedCell.value = null
  try {
    const [forecast, spaces] = await Promise.all([
      fetchForecast(lat, lon, 2),
      fetchGreenSpaces(lat, lon, 2, null, 6),
    ])
    store.forecastResult = forecast
    store.greenSpaces = spaces || []
  } finally {
    store.loadingForecast = false
    store.loadingSpaces = false
    setTimeout(setupReveal, 80)
  }
}

watch(() => store.locationReady, (r) => { if (r) loadAll() })
watch(() => [store.userLat, store.userLon], () => { if (store.locationReady) loadAll() })

let revealObserver = null
function setupReveal() {
  if (revealObserver) revealObserver.disconnect()
  revealObserver = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) e.target.classList.add('in-view') }), { threshold: 0.1 })
  document.querySelectorAll('[data-reveal]').forEach(el => revealObserver.observe(el))
}

onMounted(() => {
  setupReveal()
  if (store.locationReady) loadAll()
})
onBeforeUnmount(() => { if (revealObserver) revealObserver.disconnect() })
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
.week-page { min-height: 100vh; background: #f2faf0; color: #1a2e1e; font-family: system-ui, sans-serif; position: relative; overflow-x: hidden; }
.noise { position: fixed; inset: 0; z-index: 1000; pointer-events: none; background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E"); background-size: 180px; opacity: 0.45; }
.orb { position: fixed; border-radius: 50%; pointer-events: none; z-index: 0; filter: blur(80px); }
.orb-1 { width: 500px; height: 500px; background: rgba(90,180,110,0.18); top: -100px; left: -80px; animation: orb-drift 22s ease-in-out infinite alternate; }
.orb-2 { width: 380px; height: 380px; background: rgba(255,180,140,0.12); bottom: 5%; right: -60px; animation: orb-drift 28s ease-in-out infinite alternate-reverse; }
@keyframes orb-drift { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(40px,50px) scale(1.1)} }

.hero {
  position: relative; overflow: hidden;
  background: linear-gradient(160deg, #0a9b8a 0%, #056b5e 100%);
  padding: 220px 52px 140px;
  color: white;
}
.hero-bg-word { position: absolute; right: -2%; top: 50%; transform: translateY(-50%); font-family: Georgia,serif; font-size: clamp(140px, 20vw, 280px); font-weight: 700; font-style: italic; color: rgba(255,255,255,0.08); white-space: nowrap; pointer-events: none; user-select: none; letter-spacing: -0.04em; }
.hero-inner { position: relative; z-index: 2; max-width: 1500px; margin: 0 auto; }

.back-btn { display: inline-flex; align-items: center; gap: 8px; padding: 8px 18px; background: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.25); border-radius: 999px; color: white; font-size: 13px; font-weight: 700; text-decoration: none; margin-bottom: 24px; transition: background 0.2s; }
.back-btn:hover { background: rgba(255,255,255,0.28); }

.hero-eyebrow { display: inline-flex; align-items: center; gap: 12px; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: rgba(255,255,255,0.85); margin-bottom: 22px; }
.eyebrow-line { display: block; width: 32px; height: 1px; background: rgba(255,255,255,0.85); }
.hero-headline { font-family: Georgia,serif; font-size: clamp(46px, 6vw, 88px); font-weight: 700; line-height: 1.04; color: white; margin-bottom: 16px; }
.hero-headline em { color: #f5c812; font-style: italic; }
.hero-sub { font-family: system-ui,sans-serif; color: rgba(255,255,255,0.88); line-height: 1.6; max-width: 640px; }

.best-window-callout {
  position: absolute; bottom: -40px; right: 52px; z-index: 5;
  display: flex; align-items: center; gap: 16px;
  background: white; border-radius: 18px;
  padding: 18px 22px;
  box-shadow: 0 24px 60px rgba(0,0,0,0.18);
  max-width: 620px;
}
.bw-icon { width: 44px; height: 44px; border-radius: 12px; background: #fff3c2; color: #b88a00; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; }
.bw-text { flex: 1; min-width: 0; }
.bw-label { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: #b88a00; margin-bottom: 4px; }
.bw-main { font-family: system-ui,sans-serif; font-size: 14px; color: #1a2e1e; line-height: 1.45; }
.bw-main strong { font-family: Georgia,serif; font-size: 16px; color: #0a9b8a; font-weight: 700; }
.bw-btn { display: inline-flex; align-items: center; gap: 7px; padding: 11px 18px; background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; border-radius: 12px; font-family: system-ui,sans-serif; font-size: 13px; font-weight: 700; text-decoration: none; flex-shrink: 0; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 8px 20px rgba(10,155,138,0.32); }
.bw-btn:hover { transform: translateY(-2px); box-shadow: 0 12px 28px rgba(10,155,138,0.42); }

.empty-band, .loading-band { padding: 100px 52px 80px; }
.empty-card { display: flex; flex-direction: column; align-items: center; gap: 12px; text-align: center; max-width: 600px; margin: 0 auto; padding: 60px 40px; background: white; border: 1px solid rgba(29,113,105,0.12); border-radius: 24px; box-shadow: 0 8px 28px rgba(0,0,0,0.04); }
.empty-card h3 { font-family: Georgia,serif; color: #0f1e12; font-weight: 700; }
.empty-card p { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.6; }
.loading-band { display: flex; flex-direction: column; align-items: center; gap: 18px; }
.big-spinner { width: 44px; height: 44px; border-radius: 50%; border: 4px solid rgba(10,155,138,0.18); border-top-color: #0a9b8a; animation: spin 0.8s linear infinite; }
.loading-band p { font-family: system-ui,sans-serif; color: #4a6a4e; font-weight: 600; }
@keyframes spin { to { transform: rotate(360deg); } }

.heatmap-band {
  background: white;
  padding: 90px 52px;
  border-bottom: 1px solid rgba(29,113,105,0.1);
  opacity: 0; transform: translateY(40px);
  transition: all 0.9s cubic-bezier(0.22,1,0.36,1);
}
.heatmap-band.in-view { opacity: 1; transform: none; }
.heatmap-inner { max-width: 1500px; margin: 0 auto; }
.heatmap-header { max-width: 720px; margin-bottom: 36px; }
.section-label { font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 14px; }
.section-heading { font-family: Georgia,serif; font-size: clamp(32px, 4vw, 48px); font-weight: 700; line-height: 1.06; color: #0f1e12; margin-bottom: 14px; }
.section-heading em { color: #0a9b8a; font-style: italic; }
.section-sub { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.65; }

.heatmap-wrap { overflow-x: auto; padding-bottom: 6px; }
.heat-grid { display: grid; grid-template-columns: 56px repeat(13, 1fr); gap: 5px; min-width: 720px; align-items: center; }
.axis-row { margin-bottom: 6px; }
.day-spacer { width: 56px; }
.hour-label { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 700; color: #6a8e6e; text-align: center; }
.day-row { margin-bottom: 5px; }
.day-label { font-family: system-ui,sans-serif; font-size: 13px; font-weight: 800; color: #0f1e12; text-align: right; padding-right: 10px; }
.heat-cell {
  height: 36px; border: none; border-radius: 6px;
  cursor: pointer; padding: 0; position: relative;
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.12s ease, box-shadow 0.12s;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.18), inset 0 -1px 0 rgba(0,0,0,0.06);
}
.heat-cell:hover { transform: scale(1.1); z-index: 2; box-shadow: 0 4px 12px rgba(0,0,0,0.22); }
.heat-cell:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 2px; }
.cell-selected { outline: 3px solid white; outline-offset: -3px; transform: scale(1.1); z-index: 3; box-shadow: 0 4px 16px rgba(0,0,0,0.28); }
.cell-best { outline: 2.5px solid white; outline-offset: -2px; z-index: 4; }
.best-star { display: inline-flex; }

.legend-row { display: grid; grid-template-columns: 56px 1fr; align-items: center; margin-top: 14px; }
.legend-content { display: flex; align-items: center; gap: 12px; }
.legend-label { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 700; color: #6a8e6e; }
.legend-bar { flex: 1; height: 10px; border-radius: 999px; background: linear-gradient(90deg, rgb(10,110,98) 0%, rgb(86,154,102) 25%, rgb(212,168,84) 50%, rgb(196,110,76) 75%, rgb(156,60,50) 100%); }

.cell-detail { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; margin-top: 24px; padding: 16px 20px; background: white; border: 2px solid #0a9b8a; border-radius: 14px; box-shadow: 0 12px 28px rgba(10,155,138,0.18); animation: fade-in 0.18s ease; }
@keyframes fade-in { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: none; } }
.cd-icon { width: 38px; height: 38px; border-radius: 10px; background: #d6f4e7; color: #1d7169; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.cd-text { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 180px; }
.cd-when { font-family: Georgia,serif; font-size: 16px; font-weight: 700; color: #0f1e12; }
.cd-meta { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.cd-count { font-family: system-ui,sans-serif; font-size: 13px; color: #6a8e6e; font-weight: 600; }
.crowd-badge { padding: 4px 12px; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; }
.crowd-low      { background: #d6f4e7; color: #1d7169; }
.crowd-moderate { background: #fff3c2; color: #b88a00; }
.crowd-high     { background: #ffded5; color: #c44a2c; }
.cd-plan-btn { display: inline-flex; align-items: center; gap: 7px; padding: 9px 16px; background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; border-radius: 10px; font-family: system-ui,sans-serif; font-size: 13px; font-weight: 700; text-decoration: none; flex-shrink: 0; }
.cd-plan-btn:hover { background: #056b5e; }
.cd-close { width: 28px; height: 28px; border-radius: 50%; border: 1px solid rgba(29,113,105,0.2); background: white; color: #6a8e6e; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.15s; flex-shrink: 0; }
.cd-close:hover { color: #c44a2c; border-color: #c44a2c; }

.data-note { margin-top: 18px; font-family: system-ui,sans-serif; font-size: 12px; color: #8aaa8e; font-style: italic; }

.cream-band {
  background: linear-gradient(180deg, #faf8f0 0%, #f4f8e8 100%);
  padding: 90px 52px;
  border-bottom: 1px solid rgba(29,113,105,0.1);
  opacity: 0; transform: translateY(40px);
  transition: all 0.9s cubic-bezier(0.22,1,0.36,1);
}
.cream-band.in-view { opacity: 1; transform: none; }
.cream-inner { max-width: 1500px; margin: 0 auto; }
.cream-grid { display: grid; grid-template-columns: 380px 1fr; gap: 40px; align-items: start; }
.card-label { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 14px; }

.quietest-card {
  background: linear-gradient(135deg, #f0faf0 0%, white 60%);
  border: 1.5px solid rgba(10,155,138,0.25);
  border-radius: 24px; padding: 32px;
  box-shadow: 0 16px 40px rgba(10,155,138,0.12);
}
.qd-day { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1; margin-bottom: 8px; }
.qd-best { font-family: system-ui,sans-serif; color: #4a6a4e; font-weight: 600; margin-bottom: 16px; font-size: 15px; }
.qd-stats { display: flex; align-items: center; gap: 12px; padding: 14px 0; border-top: 1px solid rgba(29,113,105,0.12); border-bottom: 1px solid rgba(29,113,105,0.12); margin-bottom: 18px; }
.qd-count { font-family: system-ui,sans-serif; font-size: 13px; color: #6a8e6e; font-weight: 600; }
.qd-cta { display: inline-flex; align-items: center; gap: 8px; padding: 12px 20px; background: #0a9b8a; color: white; border-radius: 12px; font-family: system-ui,sans-serif; font-size: 14px; font-weight: 700; text-decoration: none; transition: all 0.25s; }
.qd-cta:hover { background: #056b5e; transform: translateY(-1px); }

.spaces-section { min-width: 0; }
.spaces-heading { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; margin-bottom: 6px; }
.spaces-sub { font-family: system-ui,sans-serif; color: #6a8e6e; margin-bottom: 22px; }
.mini-loading { display: flex; align-items: center; gap: 10px; color: #6a8e6e; font-family: system-ui,sans-serif; font-weight: 600; padding: 20px 0; }
.mini-spin { width: 18px; height: 18px; border-radius: 50%; border: 2px solid rgba(10,155,138,0.2); border-top-color: #0a9b8a; animation: spin 0.7s linear infinite; }
.no-spaces { font-family: system-ui,sans-serif; color: #8aaa8e; font-style: italic; }

.spaces-list { display: flex; flex-direction: column; gap: 10px; }
.space-row {
  display: grid; grid-template-columns: 44px 1fr 130px; gap: 14px; align-items: center;
  padding: 14px 18px; background: white;
  border: 1px solid rgba(29,113,105,0.12); border-radius: 14px;
  transition: transform 0.2s, box-shadow 0.2s;
}
.space-row:hover { transform: translateY(-1px); box-shadow: 0 8px 22px rgba(10,155,138,0.1); }
.space-icon { width: 44px; height: 44px; border-radius: 12px; background: #d6f4e7; color: #1d7169; display: flex; align-items: center; justify-content: center; }
.space-info { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.space-name { font-family: system-ui,sans-serif; font-weight: 700; color: #0f1e12; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.space-meta { display: flex; align-items: center; gap: 6px; font-family: system-ui,sans-serif; font-size: 12px; color: #6a8e6e; font-weight: 600; flex-wrap: wrap; }
.micro-tag { padding: 2px 8px; border-radius: 999px; font-size: 10px; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; }
.micro-tag.toilet { background: #e6dcff; color: #5b3fb6; }
.micro-tag.walk { background: #d6f4e7; color: #0a6e62; }

.space-comfort { display: flex; flex-direction: column; gap: 6px; }
.comfort-num { font-family: Georgia,serif; font-weight: 700; color: #0a9b8a; line-height: 1; text-align: right; }
.comfort-bar { height: 6px; background: #eaf4ea; border-radius: 999px; overflow: hidden; }
.comfort-fill { height: 100%; border-radius: 999px; transition: width 0.6s; }
.comfort-fill.high { background: linear-gradient(90deg, #0a9b8a, #1d7169); }
.comfort-fill.mid  { background: linear-gradient(90deg, #d4a854, #b88a00); }
.comfort-fill.low  { background: #c44a2c; }

.bottom-nav-band { padding: 50px 52px 80px; }
.bottom-nav-inner { max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }
.bnav-btn { display: inline-flex; align-items: center; justify-content: center; gap: 10px; padding: 18px 24px; border-radius: 14px; background: white; border: 1.5px solid rgba(29,113,105,0.2); color: #1a2e1e; font-family: system-ui,sans-serif; font-weight: 700; text-decoration: none; transition: all 0.25s; }
.bnav-btn:hover { border-color: #0a9b8a; color: #0a9b8a; }
.bnav-btn.primary { background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; border-color: transparent; box-shadow: 0 12px 28px rgba(10,155,138,0.3); }
.bnav-btn.primary:hover { color: white; transform: translateY(-2px); box-shadow: 0 16px 36px rgba(10,155,138,0.38); }

@media (max-width: 1100px) {
  .cream-grid { grid-template-columns: 1fr; }
  .best-window-callout { right: 20px; left: 20px; bottom: -50px; }
}
@media (max-width: 980px) {
  .hero { padding: 280px 20px 140px; }
  .heatmap-band, .cream-band { padding: 60px 20px; }
  .empty-band, .loading-band { padding: 80px 20px 60px; }
  .space-row { grid-template-columns: 36px 1fr 90px; gap: 10px; padding: 12px; }
  .bottom-nav-band { padding: 40px 20px 70px; }
  .bottom-nav-inner { grid-template-columns: 1fr; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
</style>