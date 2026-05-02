<!-- src/pages/BestTimePage.vue — Page 1: Live Score Dashboard -->
<template>
  <MainLayout>
    <div class="page">
      <LocationBar @locationChanged="loadAll" />

      <!-- Hero -->
      <div class="hero">
        <div class="hero-badge">☆ Personalised Timing Engine</div>
        <h1>When is the <em>best time</em> for you?</h1>
        <p class="hero-sub">Live conditions and crowd data for your area, updated every 15 minutes.</p>
        <div class="hero-circle c1"></div>
        <div class="hero-circle c2"></div>
      </div>

      <!-- No location prompt -->
      <div v-if="!store.locationReady" class="empty-state">
        <div class="empty-icon">📍</div>
        <h3>Set your location to get started</h3>
        <p>Use the bar above to enter your suburb or tap "Locate me".</p>
      </div>

      <template v-else>
        <!-- ── Live Score Ring ──────────────────────────────────────── -->
        <section class="section">
          <div v-if="store.loadingScore" class="loading-row">
            <div class="spinner"></div> Loading live conditions…
          </div>

          <div v-else-if="store.scoreResult" class="score-panel">
            <!-- Score ring -->
            <div class="score-ring-wrap">
              <svg class="score-ring" viewBox="0 0 120 120">
                <circle class="ring-bg" cx="60" cy="60" r="50" />
                <circle
                  class="ring-fill"
                  cx="60" cy="60" r="50"
                  :stroke="gradeColor"
                  :stroke-dasharray="`${scoreArc} ${314 - scoreArc}`"
                  stroke-dashoffset="78"
                />
              </svg>
              <div class="score-label-wrap">
                <span class="score-num">{{ Math.round(store.scoreResult.resonance_score) }}</span>
                <span class="score-grade" :style="{ color: gradeColor }">{{ store.scoreResult.grade }}</span>
              </div>
            </div>

            <!-- Breakdown bars -->
            <div class="breakdown">
              <p class="breakdown-title">What makes up your score right now</p>
              <div v-for="item in breakdownItems" :key="item.label" class="bar-row">
                <span class="bar-label">{{ item.label }}</span>
                <div class="bar-track">
                  <div class="bar-fill" :style="{ width: `${(item.value / item.max) * 100}%`, background: item.color }"></div>
                </div>
                <span class="bar-pts">{{ item.value }}/{{ item.max }}</span>
              </div>

              <!-- Weather detail -->
              <div v-if="store.scoreResult.weather" class="weather-strip">
                <div class="weather-chip">🌡 {{ store.scoreResult.weather.temperature_c }}°C</div>
                <div class="weather-chip">💨 {{ store.scoreResult.weather.wind_speed_kmh }} km/h</div>
                <div class="weather-chip">💧 {{ store.scoreResult.weather.humidity_pct }}%</div>
                <div class="weather-chip">🌫 PM2.5 {{ store.scoreResult.weather.pm25_ug_m3 }}</div>
              </div>
            </div>
          </div>
        </section>

        <!-- Safety advice banner -->
        <div
          v-if="store.safetyConditions"
          class="advice-banner"
          :class="`verdict-${store.safetyConditions.conditions?.safety_verdict?.toLowerCase()}`"
        >
          <span class="advice-dot"></span>
          <div>
            <strong>{{ store.safetyConditions.conditions?.safety_verdict }} conditions</strong>
            — {{ store.safetyConditions.advice }}
          </div>
        </div>

        <!-- ── Quietest Times ─────────────────────────────────────── -->
        <section class="section" v-if="store.bestTimesResult?.best_times?.length">
          <h2 class="section-title">🕐 Quietest times near you</h2>
          <p class="section-sub">Based on 2 years of City of Melbourne pedestrian sensor data.</p>

          <div class="quiet-list">
            <div
              v-for="(t, i) in store.bestTimesResult.best_times"
              :key="i"
              class="quiet-item"
              :class="{ 'quiet-best': i === 0 }"
            >
              <div class="quiet-rank">{{ i + 1 }}</div>
              <div class="quiet-info">
                <span class="quiet-day">{{ t.day_name }}</span>
                <span class="quiet-time">{{ t.hour_label }}</span>
              </div>
              <div class="quiet-right">
                <span class="crowd-badge" :class="`crowd-${t.crowd_level.toLowerCase()}`">
                  {{ t.crowd_level }}
                </span>
                <span class="quiet-count">{{ Math.round(t.avg_count) }} people/hr avg</span>
              </div>
              <span v-if="i === 0" class="best-tag">Best window</span>
            </div>
          </div>

          <p class="tip-text">{{ store.bestTimesResult.tip }}</p>
        </section>

       <!-- ── CTA buttons ───────────────────────────────────────── -->
      <div class="cta-group">
        <button class="cta-primary" @click="$router.push('/best-time/result')">
          <span class="cta-icon">📍</span>
          <span class="cta-text">
            <span class="cta-label">Best spot now</span>
            <span class="cta-sub">Find the quietest place near me</span>
          </span>
        </button>
        <button class="cta-secondary" @click="$router.push('/best-time/week')">
          <span class="cta-icon">📅</span>
          <span class="cta-text">
            <span class="cta-label">Week forecast</span>
            <span class="cta-sub">See all 7 days</span>
          </span>
        </button>
        <button class="cta-secondary" @click="$router.push('/best-time/welcoming')">
          <span class="cta-icon">🤝</span>
          <span class="cta-text">
            <span class="cta-label">Welcoming spaces</span>
            <span class="cta-sub">Libraries & community centres</span>
          </span>
        </button>
      </div>

      </template>
    </div>
  </MainLayout>
</template>

<script setup>
import { computed, watch, onMounted } from 'vue'
import MainLayout from '../layouts/MainLayout.vue'
import LocationBar from '../components/LocationBar.vue'
import { resonanceStore as store } from '../stores/resonanceStore'
import { useResonanceApi } from '../composables/useResonanceApi'

const { fetchScore, fetchSafety, fetchBestTimes } = useResonanceApi()

const gradeColor = computed(() => {
  const g = store.scoreResult?.grade
  if (g === 'Excellent') return '#0a9e6e'
  if (g === 'Good')      return '#0c8b7d'
  if (g === 'Fair')      return '#e6a800'
  return '#c84848'
})

const scoreArc = computed(() => {
  const s = store.scoreResult?.resonance_score ?? 0
  return Math.round((s / 100) * 314)
})

const breakdownItems = computed(() => {
  const b = store.scoreResult?.breakdown
  if (!b) return []
  return [
    { label: 'Crowd level',    value: b.crowd_score,   max: 35, color: '#0c8b7d' },
    { label: 'Weather safety', value: b.weather_score, max: 35, color: '#2196a6' },
    { label: 'Comfort',        value: b.comfort_score, max: 20, color: '#5c8a3c' },
    { label: 'Toilet access',  value: b.toilet_score,  max: 5,  color: '#8b7d0c' },
    { label: 'Shade',          value: b.shade_score,   max: 5,  color: '#6a5c2a' },
  ]
})

async function loadAll() {
  if (!store.locationReady) return
  const { userLat: lat, userLon: lon } = store
  store.loadingScore = true

  const [score, safety, bestTimes] = await Promise.all([
    fetchScore(lat, lon),
    fetchSafety(lat, lon),
    fetchBestTimes(lat, lon, 5),
  ])

  store.scoreResult      = score
  store.safetyConditions = safety
  store.bestTimesResult  = bestTimes
  store.loadingScore     = false
}

watch(() => store.locationReady, (ready) => { if (ready) loadAll() })
watch(() => [store.userLat, store.userLon], () => { if (store.locationReady) loadAll() })
onMounted(() => { if (store.locationReady) loadAll() })
</script>

<style scoped>
.page { min-height: 100vh; background: #f5f5fa; }

.hero {
  position: relative; overflow: hidden;
  padding: 52px 48px 48px;
  background: linear-gradient(135deg, #0c8b7d, #0a6e62);
  color: #fff;
}
.hero-badge {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 18px; border-radius: 999px;
  background: rgba(255,255,255,0.18);
  font-size: calc(14px * var(--font-scale)); font-weight: 700;
  margin-bottom: 20px;
}
.hero h1 {
  margin: 0 0 14px;
  font-family: 'Fraunces', serif;
  font-size: calc(46px * var(--font-scale));
  font-weight: 700; line-height: 1.1;
}
.hero em { color: #f5c812; font-style: italic; }
.hero-sub { margin: 0; font-size: calc(16px * var(--font-scale)); opacity: 0.88; max-width: 520px; }
.hero-circle { position: absolute; border-radius: 50%; background: rgba(255,255,255,0.09); }
.c1 { width: 240px; height: 240px; right: -50px; top: -50px; }
.c2 { width: 160px; height: 160px; right: 160px; bottom: -70px; }

.empty-state {
  text-align: center; padding: 72px 40px; color: #6b6d88;
}
.empty-icon { font-size: 48px; margin-bottom: 16px; }
.empty-state h3 { margin: 0 0 10px; font-size: calc(22px * var(--font-scale)); color: #2f3152; }
.empty-state p { margin: 0; font-size: calc(16px * var(--font-scale)); }

.section { padding: 32px 40px; border-bottom: 1.5px solid #e8e9f3; }
.section-title { margin: 0 0 6px; font-family: 'Fraunces', serif; font-size: calc(24px * var(--font-scale)); color: #2f3152; }
.section-sub { margin: 0 0 20px; font-size: calc(14px * var(--font-scale)); color: #6b6d88; }

.loading-row {
  display: flex; align-items: center; gap: 12px;
  color: #6b6d88; font-size: calc(16px * var(--font-scale)); font-weight: 600;
}
.spinner {
  width: 28px; height: 28px;
  border: 3px solid #e0e1ed; border-top-color: #0c8b7d;
  border-radius: 50%; animation: spin 0.8s linear infinite; flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

.score-panel { display: flex; gap: 40px; align-items: flex-start; flex-wrap: wrap; }

.score-ring-wrap { position: relative; width: 140px; height: 140px; flex-shrink: 0; }
.score-ring { width: 140px; height: 140px; transform: rotate(-90deg); }
.ring-bg { fill: none; stroke: #e8e9f3; stroke-width: 12; }
.ring-fill { fill: none; stroke-width: 12; stroke-linecap: round; transition: stroke-dasharray 0.6s ease; }
.score-label-wrap {
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 2px;
}
.score-num { font-size: calc(32px * var(--font-scale)); font-weight: 800; color: #2f3152; line-height: 1; }
.score-grade { font-size: calc(13px * var(--font-scale)); font-weight: 800; }

.breakdown { flex: 1; min-width: 260px; }
.breakdown-title { margin: 0 0 16px; font-size: calc(14px * var(--font-scale)); font-weight: 700; color: #6b6d88; }

.bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.bar-label { width: 120px; font-size: calc(13px * var(--font-scale)); font-weight: 700; color: #3c3c58; flex-shrink: 0; }
.bar-track { flex: 1; height: 10px; background: #e8e9f3; border-radius: 999px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 999px; transition: width 0.5s ease; }
.bar-pts { width: 44px; font-size: calc(12px * var(--font-scale)); font-weight: 700; color: #6b6d88; text-align: right; }

.weather-strip { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
.weather-chip {
  padding: 5px 12px; border-radius: 999px;
  background: #f0f0f8; color: #3c3c58;
  font-size: calc(13px * var(--font-scale)); font-weight: 700;
}

.advice-banner {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 16px 40px; font-size: calc(15px * var(--font-scale));
}
.verdict-good    { background: #e8f8f5; color: #0a6e62; }
.verdict-caution { background: #fff8e0; color: #8a6000; }
.verdict-poor    { background: #ffeaea; color: #c84848; }
.verdict-unknown { background: #f0f0f8; color: #6b6d88; }
.advice-dot { width: 10px; height: 10px; border-radius: 50%; background: currentColor; flex-shrink: 0; margin-top: 4px; }

.quiet-list { display: flex; flex-direction: column; gap: 10px; }
.quiet-item {
  display: flex; align-items: center; gap: 14px;
  padding: 16px 20px; background: #fff;
  border: 1.5px solid #e0e1ed; border-radius: 14px;
  position: relative;
}
.quiet-best { border-color: #0c8b7d; background: #f0faf8; }
.quiet-rank {
  width: 32px; height: 32px; border-radius: 50%;
  background: #e8e9f3; color: #3c3c58;
  font-weight: 800; font-size: calc(15px * var(--font-scale));
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.quiet-best .quiet-rank { background: #0c8b7d; color: #fff; }
.quiet-info { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.quiet-day { font-size: calc(16px * var(--font-scale)); font-weight: 800; color: #2f3152; }
.quiet-time { font-size: calc(14px * var(--font-scale)); color: #6b6d88; font-weight: 600; }
.quiet-right { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.quiet-count { font-size: calc(12px * var(--font-scale)); color: #9b9db8; font-weight: 600; }
.crowd-badge {
  padding: 3px 10px; border-radius: 999px;
  font-size: calc(12px * var(--font-scale)); font-weight: 700;
}
.crowd-low      { background: #e8f8f5; color: #0a6e62; }
.crowd-moderate { background: #fff8e0; color: #8a6000; }
.crowd-high     { background: #ffeaea; color: #c84848; }
.best-tag {
  position: absolute; top: -10px; left: 20px;
  padding: 2px 10px; border-radius: 999px;
  background: #0c8b7d; color: #fff;
  font-size: calc(11px * var(--font-scale)); font-weight: 800;
}
.tip-text { margin: 16px 0 0; font-size: calc(13px * var(--font-scale)); color: #9b9db8; font-style: italic; }

/* CTAs — 3 in a row */
.cta-group {
  padding: 28px 40px 40px;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 12px;
}

.cta-primary, .cta-secondary {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px 20px;
  border-radius: 18px;
  font-family: 'Manrope', sans-serif;
  cursor: pointer;
  transition: all 0.18s ease;
  text-align: left;
  width: 100%;
}

.cta-primary {
  border: none;
  background: #0c8b7d;
  color: #fff;
  box-shadow: 0 6px 20px rgba(12,139,125,0.25);
}
.cta-primary:hover { background: #0a756a; transform: translateY(-2px); }

.cta-secondary {
  border: 2px solid #d8d9e8;
  background: #fff;
  color: #3c3c58;
}
.cta-secondary:hover { border-color: #0c8b7d; color: #0c8b7d; }

.cta-icon { font-size: 24px; flex-shrink: 0; }

.cta-text {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.cta-label {
  font-size: calc(15px * var(--font-scale));
  font-weight: 800;
  line-height: 1;
}

.cta-sub {
  font-size: calc(12px * var(--font-scale));
  font-weight: 600;
  opacity: 0.7;
  line-height: 1.3;
}


@media (max-width: 900px) {
  .hero { padding: 40px 20px; }
  .hero h1 { font-size: calc(32px * var(--font-scale)); }
  .section { padding: 24px 20px; }
  .score-panel { flex-direction: column; align-items: center; }
  .cta-group {
    grid-template-columns: 1fr;
    padding: 20px 16px 32px;
  }
  .advice-banner { padding: 14px 20px; }
}
</style>