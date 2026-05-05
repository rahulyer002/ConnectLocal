<template>
  <div class="best-time-page">
    <div class="noise" aria-hidden="true"></div>
    <div class="orb orb-1" aria-hidden="true"></div>
    <div class="orb orb-2" aria-hidden="true"></div>

    <BestTimeLocationBar />

    <section class="hero">
      <div class="hero-bg-word" aria-hidden="true">TIMING</div>
      <div class="hero-inner">
        <p class="hero-eyebrow">
          <span class="eyebrow-line" aria-hidden="true"></span>
          Personalised timing engine
        </p>
        <h1 class="hero-headline">
          When is the<br>
          <em>best time</em> for you?
        </h1>
        <p class="hero-sub" :style="{ fontSize: scaledPx(18) }">
          Live conditions and crowd data for {{ store.locationReady ? store.locationLabel : 'your area' }}, updated every 15 minutes.
        </p>
      </div>
    </section>

    <section v-if="!store.locationReady" class="empty-band">
      <div class="empty-card">
        <svg viewBox="0 0 24 24" width="56" height="56" fill="none" stroke="#0a9b8a" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/>
          <circle cx="12" cy="10" r="2.5"/>
        </svg>
        <h3 :style="{ fontSize: scaledPx(24) }">Set your location to begin</h3>
        <p :style="{ fontSize: scaledPx(16) }">Use the location bar above - type a Melbourne suburb or postcode, or tap "Locate me".</p>
      </div>
    </section>

    <section v-else class="dashboard-band" data-reveal>
      <div class="dashboard-inner">
        <div v-if="store.loadingScore && !store.scoreResult" class="dash-loading">
          <div class="spinner-light" aria-hidden="true"></div>
          <p :style="{ fontSize: scaledPx(16) }">Loading live conditions…</p>
        </div>

        <template v-else-if="store.scoreResult">
          <div class="dash-score">
            <div class="ring-wrap">
              <svg class="ring" viewBox="0 0 180 180" aria-hidden="true">
                <circle class="ring-track" cx="90" cy="90" r="76" />
                <circle
                  class="ring-fill"
                  cx="90" cy="90" r="76"
                  :stroke="gradeColor"
                  :stroke-dasharray="`${scoreArc} ${478 - scoreArc}`"
                  stroke-dashoffset="119"
                />
              </svg>
              <div class="ring-text">
                <span class="ring-num" :style="{ fontSize: scaledPx(56) }">{{ Math.round(store.scoreResult.resonance_score) }}</span>
                <span class="ring-out" :style="{ fontSize: scaledPx(13) }">/ 100</span>
              </div>
            </div>
            <span class="grade-pill" :style="{ background: gradeColor, fontSize: scaledPx(13) }">
              {{ store.scoreResult.grade }} conditions
            </span>
          </div>

          <div class="dash-breakdown">
            <p class="dash-label">What makes up your score</p>
            <div v-for="item in breakdownItems" :key="item.label" class="bar-row">
              <span class="bar-label" :style="{ fontSize: scaledPx(14) }">{{ item.label }}</span>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: `${(item.value / item.max) * 100}%`, background: item.color }"></div>
              </div>
              <span class="bar-pts" :style="{ fontSize: scaledPx(13) }">{{ formatPts(item.value) }}<span class="bar-max">/{{ item.max }}</span></span>
            </div>
          </div>

          <div class="dash-weather" v-if="store.scoreResult.weather">
            <p class="dash-label">Right now</p>
            <div class="weather-grid">
              <div class="weather-tile">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>
                <span class="w-num" :style="{ fontSize: scaledPx(22) }">{{ store.scoreResult.weather.temperature_c }}°</span>
                <span class="w-label" :style="{ fontSize: scaledPx(11) }">Temp</span>
              </div>
              <div class="weather-tile">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9.59 4.59A2 2 0 1 1 11 8H2m10.59 11.41A2 2 0 1 0 14 16H2m15.73-8.27A2.5 2.5 0 1 1 19.5 12H2"/></svg>
                <span class="w-num" :style="{ fontSize: scaledPx(22) }">{{ store.scoreResult.weather.wind_speed_kmh }}</span>
                <span class="w-label" :style="{ fontSize: scaledPx(11) }">km/h wind</span>
              </div>
              <div class="weather-tile">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>
                <span class="w-num" :style="{ fontSize: scaledPx(22) }">{{ store.scoreResult.weather.humidity_pct }}%</span>
                <span class="w-label" :style="{ fontSize: scaledPx(11) }">Humidity</span>
              </div>
              <div class="weather-tile">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/></svg>
                <span class="w-num" :style="{ fontSize: scaledPx(22) }">{{ store.scoreResult.weather.pm25_ug_m3 }}</span>
                <span class="w-label" :style="{ fontSize: scaledPx(11) }">PM2.5</span>
              </div>
            </div>
          </div>
        </template>
      </div>
    </section>

    <div
      v-if="store.locationReady && store.safetyConditions"
      class="safety-strip"
      :class="`verdict-${(store.safetyConditions.conditions?.safety_verdict || 'unknown').toLowerCase()}`"
      role="status"
    >
      <div class="safety-inner">
        <span class="safety-dot" aria-hidden="true"></span>
        <p :style="{ fontSize: scaledPx(15) }">
          <strong>{{ store.safetyConditions.conditions?.safety_verdict || 'Conditions' }} conditions</strong>
          <span v-if="store.safetyConditions.advice"> - {{ store.safetyConditions.advice }}</span>
        </p>
      </div>
    </div>

    <section v-if="store.locationReady && store.bestTimesResult?.best_times?.length" class="quiet-band" data-reveal>
      <div class="quiet-inner">
        <div class="quiet-header">
          <p class="section-label">Historical patterns</p>
          <h2 class="section-heading" :style="{ fontSize: scaledPx(40) }">
            Quietest times<br><em>near you</em>
          </h2>
          <p class="section-sub" :style="{ fontSize: scaledPx(16) }">
            Based on 2 years of City of Melbourne pedestrian sensor data.
            <span v-if="store.bestTimesResult.tip" class="tip-inline">{{ store.bestTimesResult.tip }}</span>
          </p>
        </div>

        <div class="quiet-grid">
          <article
            v-for="(t, i) in store.bestTimesResult.best_times"
            :key="`${t.day_name}-${t.hour_label}-${i}`"
            class="quiet-tile"
            :class="{ 'quiet-tile-best': i === 0 }"
            :style="{ '--i': i }"
          >
            <div class="tile-rank">
              <span class="rank-num">{{ i + 1 }}</span>
              <span v-if="i === 0" class="best-flag" :style="{ fontSize: scaledPx(10) }">Best window</span>
            </div>
            <div class="tile-body">
              <span class="tile-day" :style="{ fontSize: scaledPx(22) }">{{ t.day_name }}</span>
              <span class="tile-time" :style="{ fontSize: scaledPx(15) }">{{ t.hour_label }}</span>
            </div>
            <div class="tile-foot">
              <span class="crowd-badge" :class="`crowd-${t.crowd_level.toLowerCase()}`" :style="{ fontSize: scaledPx(12) }">
                {{ t.crowd_level }}
              </span>
              <span class="tile-count" :style="{ fontSize: scaledPx(12) }">~{{ Math.round(t.avg_count) }} people/hr</span>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section v-if="store.locationReady" class="cta-band" data-reveal>
      <div class="cta-inner">
        <RouterLink to="/best-time/now" class="cta-card cta-primary">
          <div class="cta-icon-wrap">
            <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/>
              <circle cx="12" cy="10" r="2.5"/>
            </svg>
          </div>
          <div class="cta-text">
            <span class="cta-label" :style="{ fontSize: scaledPx(20) }">Best spots now</span>
            <span class="cta-sub" :style="{ fontSize: scaledPx(14) }">Find the quietest place near you</span>
          </div>
          <svg class="cta-arrow" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
        </RouterLink>
        <RouterLink to="/best-time/week" class="cta-card cta-secondary">
          <div class="cta-icon-wrap yellow">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>
            </svg>
          </div>
          <div class="cta-text">
            <span class="cta-label" :style="{ fontSize: scaledPx(18) }">Week forecast</span>
            <span class="cta-sub" :style="{ fontSize: scaledPx(14) }">See all 7 days</span>
          </div>
          <svg class="cta-arrow" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
        </RouterLink>
        <RouterLink to="/welcoming-spaces" class="cta-card cta-secondary">
          <div class="cta-icon-wrap purple">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
            </svg>
          </div>
          <div class="cta-text">
            <span class="cta-label" :style="{ fontSize: scaledPx(18) }">Welcoming spaces</span>
            <span class="cta-sub" :style="{ fontSize: scaledPx(14) }">Libraries &amp; community centres</span>
          </div>
          <svg class="cta-arrow" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
        </RouterLink>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { resonanceStore } from '../stores/resonanceStore'
import { uiStore } from '../stores/uiStore'
import { useResonanceApi } from '../composables/useResonanceApi'
import BestTimeLocationBar from '../components/BestTimeLocationBar.vue'

const store = resonanceStore
const { fetchScore, fetchSafety, fetchBestTimes } = useResonanceApi()
const scaledPx = (base) => `${(base * uiStore.textScale) / 100}px`

const gradeColor = computed(() => {
  const score = store.scoreResult?.resonance_score ?? 0
  if (score >= 85) return '#0a9b8a'
  if (score >= 70) return '#1d7169'
  if (score >= 50) return '#b88a00'
  return '#c44a2c'
})

const scoreArc = computed(() => {
  const s = Math.max(0, Math.min(100, store.scoreResult?.resonance_score ?? 0))
  return Math.round((s / 100) * 478)
})

const breakdownItems = computed(() => {
  const b = store.scoreResult?.breakdown
  if (!b) return []
  return [
    { label: 'Crowd level',    value: b.crowd_score,   max: 35, color: '#0a9b8a' },
    { label: 'Weather safety', value: b.weather_score, max: 35, color: '#1d7169' },
    { label: 'Comfort',        value: b.comfort_score, max: 20, color: '#5c8a3c' },
    { label: 'Toilet access',  value: b.toilet_score,  max: 5,  color: '#b88a00' },
    { label: 'Shade',          value: b.shade_score,   max: 5,  color: '#8a6a2a' },
  ]
})

function formatPts(v) {
  if (v == null) return '0'
  return Number.isInteger(v) ? v : v.toFixed(1)
}

async function loadAll() {
  if (!store.locationReady) return
  const { userLat: lat, userLon: lon } = store
  store.loadingScore = true
  try {
    const [score, safety, bestTimes] = await Promise.all([
      fetchScore(lat, lon),
      fetchSafety(lat, lon),
      fetchBestTimes(lat, lon, 6),
    ])
    store.scoreResult = score
    store.safetyConditions = safety
    store.bestTimesResult = bestTimes
  } finally {
    store.loadingScore = false
    setTimeout(setupReveal, 80)
  }
}

watch(() => store.locationReady, (ready) => { if (ready) loadAll() })
watch(() => [store.userLat, store.userLon], () => { if (store.locationReady) loadAll() })

let revealObserver = null
function setupReveal() {
  if (revealObserver) revealObserver.disconnect()
  revealObserver = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in-view') })
  }, { threshold: 0.1 })
  document.querySelectorAll('[data-reveal]').forEach(el => revealObserver.observe(el))
}

onMounted(() => {
  setupReveal()
  if (store.locationReady) loadAll()
})

onBeforeUnmount(() => {
  if (revealObserver) revealObserver.disconnect()
})
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.best-time-page {
  min-height: 100vh; background: #f2faf0; color: #1a2e1e;
  font-family: system-ui, sans-serif; position: relative; overflow-x: hidden;
}

.noise {
  position: fixed; inset: 0; z-index: 1000; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  background-size: 180px; opacity: 0.45;
}
.orb { position: fixed; border-radius: 50%; pointer-events: none; z-index: 0; filter: blur(80px); }
.orb-1 { width: 500px; height: 500px; background: rgba(90,180,110,0.18); top: -100px; left: -80px; animation: orb-drift 22s ease-in-out infinite alternate; }
.orb-2 { width: 380px; height: 380px; background: rgba(255,180,140,0.12); bottom: 10%; right: -60px; animation: orb-drift 28s ease-in-out infinite alternate-reverse; }
@keyframes orb-drift { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(40px,50px) scale(1.1)} }

.hero {
  position: relative; overflow: hidden;
  background: linear-gradient(160deg, #e4f5e0 0%, #c8edc8 100%);
  padding: 220px 52px 80px;
  border-bottom: 1px solid rgba(29,113,105,0.12);
}
.hero-bg-word { position: absolute; right: -2%; top: 50%; transform: translateY(-50%); font-family: Georgia,serif; font-size: clamp(140px, 20vw, 280px); font-weight: 700; font-style: italic; color: rgba(10,155,138,0.085); white-space: nowrap; pointer-events: none; user-select: none; letter-spacing: -0.04em; }
.hero-inner { position: relative; z-index: 2; max-width: 1500px; margin: 0 auto; }
.hero-eyebrow { display: inline-flex; align-items: center; gap: 12px; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 22px; }
.eyebrow-line { display: block; width: 32px; height: 1px; background: #0a9b8a; }
.hero-headline { font-family: Georgia,serif; font-size: clamp(46px, 6vw, 88px); font-weight: 700; line-height: 1.04; color: #0f1e12; margin-bottom: 18px; }
.hero-headline em { color: #0a9b8a; font-style: italic; }
.hero-sub { font-family: system-ui,sans-serif; font-size: 18px; color: #4a6a4e; line-height: 1.6; max-width: 720px; }

.empty-band { padding: 60px 52px 100px; }
.empty-card {
  display: flex; flex-direction: column; align-items: center; gap: 16px;
  text-align: center; max-width: 600px; margin: 0 auto;
  padding: 70px 40px; background: white;
  border: 1px solid rgba(29,113,105,0.12); border-radius: 24px;
  box-shadow: 0 8px 28px rgba(0,0,0,0.04);
}
.empty-card h3 { font-family: Georgia,serif; color: #0f1e12; font-weight: 700; }
.empty-card p { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.6; }

.dashboard-band {
  background: white;
  border-bottom: 1px solid rgba(29,113,105,0.1);
  padding: 64px 52px;
  opacity: 0; transform: translateY(40px);
  transition: all 0.9s cubic-bezier(0.22,1,0.36,1);
}
.dashboard-band.in-view { opacity: 1; transform: none; }
.dashboard-inner { max-width: 1500px; margin: 0 auto; display: grid; grid-template-columns: 280px 1fr 360px; gap: 56px; align-items: start; }
.dash-loading { grid-column: 1 / -1; display: flex; align-items: center; justify-content: center; gap: 14px; padding: 60px 0; color: #4a6a4e; font-weight: 600; }
.spinner-light { width: 32px; height: 32px; border-radius: 50%; border: 3px solid rgba(10,155,138,0.18); border-top-color: #0a9b8a; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.dash-label { font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 20px; }

.dash-score { display: flex; flex-direction: column; align-items: center; gap: 18px; }
.ring-wrap { position: relative; width: 220px; height: 220px; }
.ring { width: 220px; height: 220px; transform: rotate(-90deg); }
.ring-track { fill: none; stroke: #e8f2e8; stroke-width: 14; }
.ring-fill { fill: none; stroke-width: 14; stroke-linecap: round; transition: stroke-dasharray 0.9s cubic-bezier(0.22,1,0.36,1), stroke 0.4s; }
.ring-text { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; }
.ring-num { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1; }
.ring-out { font-family: system-ui,sans-serif; color: #6a8e6e; font-weight: 600; }
.grade-pill { padding: 8px 18px; border-radius: 999px; color: white; font-family: system-ui,sans-serif; font-weight: 800; text-transform: uppercase; letter-spacing: 0.06em; }

.dash-breakdown { min-width: 0; }
.bar-row { display: flex; align-items: center; gap: 14px; margin-bottom: 14px; }
.bar-label { width: 130px; font-family: system-ui,sans-serif; font-weight: 700; color: #1a2e1e; flex-shrink: 0; }
.bar-track { flex: 1; height: 12px; background: #eaf4ea; border-radius: 999px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 999px; transition: width 0.7s cubic-bezier(0.22,1,0.36,1); }
.bar-pts { width: 64px; font-family: system-ui,sans-serif; font-weight: 700; color: #1a2e1e; text-align: right; }
.bar-max { color: #8aaa8e; font-weight: 500; }

.dash-weather { min-width: 0; }
.weather-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.weather-tile {
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
  padding: 18px 12px; background: #f0faf0;
  border: 1px solid rgba(10,155,138,0.12); border-radius: 14px; color: #1d7169;
}
.w-num { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1; }
.w-label { font-family: system-ui,sans-serif; color: #6a8e6e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }

.safety-strip { padding: 16px 52px; border-bottom: 1px solid rgba(29,113,105,0.08); }
.safety-inner { max-width: 1500px; margin: 0 auto; display: flex; align-items: flex-start; gap: 12px; }
.safety-dot { width: 10px; height: 10px; border-radius: 50%; background: currentColor; flex-shrink: 0; margin-top: 6px; }
.safety-strip p { font-family: system-ui,sans-serif; line-height: 1.55; }
.safety-strip strong { font-weight: 800; }
.verdict-good    { background: #e8f8f5; color: #0a6e62; }
.verdict-caution { background: #fff8e0; color: #8a6000; }
.verdict-poor    { background: #ffeaea; color: #c44a2c; }
.verdict-unknown { background: #f0f0f8; color: #4a6a4e; }

.quiet-band {
  background: linear-gradient(180deg, #faf8f0 0%, #f4f8e8 100%);
  padding: 90px 52px;
  border-bottom: 1px solid rgba(29,113,105,0.1);
  opacity: 0; transform: translateY(40px);
  transition: all 0.9s cubic-bezier(0.22,1,0.36,1);
}
.quiet-band.in-view { opacity: 1; transform: none; }
.quiet-inner { max-width: 1500px; margin: 0 auto; }
.quiet-header { max-width: 720px; margin-bottom: 44px; }
.section-label { font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 14px; }
.section-heading { font-family: Georgia,serif; font-size: clamp(32px, 4.5vw, 52px); font-weight: 700; line-height: 1.06; color: #0f1e12; margin-bottom: 14px; }
.section-heading em { color: #0a9b8a; font-style: italic; }
.section-sub { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.65; }
.tip-inline { display: block; margin-top: 6px; color: #6a8e6e; font-style: italic; }

.quiet-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.quiet-tile {
  position: relative; background: white; border: 1px solid rgba(29,113,105,0.12);
  border-radius: 18px; padding: 24px 22px;
  display: flex; flex-direction: column; gap: 18px;
  transition: transform 0.3s cubic-bezier(0.22,1,0.36,1), box-shadow 0.3s;
  opacity: 0; transform: translateY(20px);
  animation: tile-in 0.6s calc(var(--i) * 80ms) forwards;
}
@keyframes tile-in { to { opacity: 1; transform: none; } }
.quiet-tile:hover { transform: translateY(-3px); box-shadow: 0 16px 40px rgba(10,155,138,0.12); }
.quiet-tile-best { border-color: #0a9b8a; background: linear-gradient(135deg, #f0faf0 0%, white 60%); box-shadow: 0 12px 32px rgba(10,155,138,0.12); }

.tile-rank { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.rank-num { width: 36px; height: 36px; border-radius: 50%; background: #e8f2e8; color: #0f1e12; font-family: Georgia,serif; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.quiet-tile-best .rank-num { background: #0a9b8a; color: white; }
.best-flag { padding: 4px 10px; border-radius: 999px; background: #0a9b8a; color: white; font-family: system-ui,sans-serif; font-weight: 800; letter-spacing: 0.05em; text-transform: uppercase; }

.tile-body { display: flex; flex-direction: column; gap: 4px; }
.tile-day { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1.1; }
.tile-time { font-family: system-ui,sans-serif; color: #4a6a4e; font-weight: 600; }

.tile-foot { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding-top: 14px; border-top: 1px solid rgba(29,113,105,0.1); flex-wrap: wrap; }
.crowd-badge { padding: 4px 12px; border-radius: 999px; font-family: system-ui,sans-serif; font-weight: 700; }
.crowd-low { background: #d6f4e7; color: #1d7169; }
.crowd-moderate { background: #fff3c2; color: #b88a00; }
.crowd-high { background: #ffded5; color: #c44a2c; }
.crowd-unknown { background: #f0f0f8; color: #6a8e6e; }
.tile-count { font-family: system-ui,sans-serif; color: #8aaa8e; font-weight: 600; }

.cta-band {
  background: linear-gradient(180deg, #e4f5e0 0%, #c8edc8 100%);
  padding: 70px 52px 90px;
  opacity: 0; transform: translateY(40px);
  transition: all 0.9s cubic-bezier(0.22,1,0.36,1);
}
.cta-band.in-view { opacity: 1; transform: none; }
.cta-inner { max-width: 1500px; margin: 0 auto; display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 16px; }
.cta-card { display: flex; align-items: center; gap: 18px; padding: 26px 28px; border-radius: 18px; text-decoration: none; transition: transform 0.3s, box-shadow 0.3s, border-color 0.3s; }
.cta-primary { background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; box-shadow: 0 14px 36px rgba(10,155,138,0.32); }
.cta-primary:hover { transform: translateY(-3px); box-shadow: 0 20px 44px rgba(10,155,138,0.42); }
.cta-primary .cta-icon-wrap { background: rgba(255,255,255,0.18); color: white; }
.cta-primary .cta-icon-wrap::before { border-color: rgba(255,255,255,0.4); }
.cta-primary .cta-sub { color: rgba(255,255,255,0.85); }
.cta-secondary { background: white; border: 1px solid rgba(29,113,105,0.14); color: #1a2e1e; box-shadow: 0 6px 18px rgba(0,0,0,0.04); }
.cta-secondary:hover { transform: translateY(-3px); border-color: #0a9b8a; box-shadow: 0 16px 36px rgba(10,155,138,0.14); }
.cta-icon-wrap { width: 54px; height: 54px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; position: relative; background: #d6f4e7; color: #1d7169; }
.cta-icon-wrap::before { content: ''; position: absolute; inset: -4px; border: 1.5px solid currentColor; border-radius: 50%; opacity: 0.2; }
.cta-icon-wrap.yellow { background: #fff3c2; color: #b88a00; }
.cta-icon-wrap.purple { background: #e6dcff; color: #5b3fb6; }
.cta-text { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 0; }
.cta-label { font-family: Georgia,serif; font-weight: 700; line-height: 1.15; }
.cta-sub { font-family: system-ui,sans-serif; color: #6a8e6e; font-weight: 500; line-height: 1.3; }
.cta-arrow { flex-shrink: 0; transition: transform 0.3s; }
.cta-card:hover .cta-arrow { transform: translateX(4px); }

@media (max-width: 1200px) {
  .dashboard-inner { grid-template-columns: 240px 1fr; }
  .dash-weather { grid-column: 1 / -1; }
  .quiet-grid { grid-template-columns: repeat(2, 1fr); }
  .cta-inner { grid-template-columns: 1fr 1fr; }
  .cta-card:first-child { grid-column: 1 / -1; }
}
@media (max-width: 980px) {
  .hero { padding: 280px 20px 60px; }
  .empty-band { padding: 40px 20px 80px; }
  .dashboard-band { padding: 48px 20px; }
  .dashboard-inner { grid-template-columns: 1fr; gap: 40px; }
  .dash-score { align-items: flex-start; }
  .safety-strip { padding: 14px 20px; }
  .quiet-band { padding: 60px 20px; }
  .quiet-grid { grid-template-columns: 1fr; }
  .cta-band { padding: 50px 20px 70px; }
  .cta-inner { grid-template-columns: 1fr; }
  .cta-card:first-child { grid-column: auto; }
  .bar-label { width: 110px; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
</style>