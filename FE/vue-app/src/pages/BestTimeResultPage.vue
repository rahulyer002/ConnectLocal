<!-- src/pages/BestTimeResultPage.vue — Page 2: Go Now (Top 3 Spots) -->
<template>
  <MainLayout>
    <div class="page">
      <LocationBar @locationChanged="loadAll" />

      <!-- Hero -->
      <div class="result-hero">
        <button class="back-btn" @click="$router.back()">‹ Back</button>
        <p class="hero-eyebrow">YOUR BEST SPOTS RIGHT NOW</p>
        <h1>Find the best place<br /><em>near you today</em></h1>
        <div class="hero-circle c1"></div>
        <div class="hero-circle c2"></div>
      </div>

      <!-- No location -->
      <div v-if="!store.locationReady" class="empty-state">
        <div class="empty-icon">📍</div>
        <h3>Set your location first</h3>
        <p>Use the bar above to enter your suburb or tap "Locate me".</p>
      </div>

      <template v-else>
        <!-- Safety banner -->
        <div
          v-if="store.safetyConditions"
          class="safety-banner"
          :class="`verdict-${store.safetyConditions.conditions?.safety_verdict?.toLowerCase()}`"
        >
          <span class="safety-dot"></span>
          <span>
            <strong>{{ store.safetyConditions.conditions?.safety_verdict }}</strong>
            conditions · {{ store.safetyConditions.conditions?.temperature_c }}°C ·
            {{ store.safetyConditions.advice }}
          </span>
        </div>

        <!-- Loading -->
        <div v-if="store.loadingGoNow" class="loading-state">
          <div class="spinner"></div>
          <p>Finding the best spots near you…</p>
        </div>

        <div v-else class="content-area">
          <!-- Generated at timestamp -->
          <p v-if="store.goNowResult?.generated_at" class="generated-at">
            Updated {{ store.goNowResult.generated_at }} ·
            {{ store.goNowResult.total_spaces_checked }} spaces checked
          </p>

          <!-- ── 3 Recommendation Cards ─────────────────────────────── -->
          <div
            v-for="(rec, idx) in recommendations"
            :key="rec.space_name"
            class="rec-card"
            :class="{ 'rec-best': idx === 0 }"
          >
            <!-- Card header -->
            <div class="rec-header">
              <div class="rec-rank-wrap">
                <span class="rec-rank">{{ idx + 1 }}</span>
              </div>
              <div class="rec-title-group">
                <div class="rec-name-row">
                  <h2 class="rec-name">{{ rec.space_name }}</h2>
                  <span class="grade-badge" :class="`grade-${rec.grade?.toLowerCase()}`">
                    {{ rec.grade }}
                  </span>
                </div>
                <p class="rec-distance">{{ rec.distance_km?.toFixed(1) }} km away</p>
              </div>
              <div class="rec-score-wrap">
                <span class="rec-score">{{ Math.round(rec.resonance_score) }}</span>
                <span class="rec-score-label">score</span>
              </div>
            </div>

            <!-- Why recommended -->
            <p class="why-rec">{{ rec.why_recommended }}</p>

            <!-- Detail chips -->
            <div class="chip-row">
              <span class="info-chip" :class="`crowd-${rec.crowd_level?.toLowerCase()}`">
                👥 {{ rec.crowd_level }}
                <span v-if="rec.is_quiet_now"> · Quiet now</span>
              </span>
              <span v-if="rec.has_toilet_nearby" class="info-chip chip-toilet">
                🚻 Toilet nearby
              </span>
              <span v-else class="info-chip chip-no-toilet">
                ⚠ No toilet within 200m
              </span>
            </div>

            <!-- Nearest toilet detail -->
            <div
              v-if="rec.has_toilet_nearby && nearestToilet"
              class="toilet-detail"
            >
              <span class="toilet-icon">🚻</span>
              <div class="toilet-info">
                <span class="toilet-name">{{ nearestToilet.name }}</span>
                <span class="toilet-dist">{{ (nearestToilet.distance_km * 1000).toFixed(0) }}m away</span>
                <span v-if="nearestToilet.has_wheelchair" class="wheelchair-badge">♿ Accessible</span>
              </div>
            </div>

            <!-- Nearby transport — only on first card -->
            <div v-if="idx === 0 && nearbyStops.length" class="transport-section">
              <p class="transport-label">NEARBY TRANSPORT</p>
              <div class="stops-list">
                <div v-for="stop in nearbyStops.slice(0, 3)" :key="stop.stop_id" class="stop-row">
                  <span class="stop-mode-badge" :class="`mode-${stop.mode}`">
                    {{ modeIcon(stop.mode) }} {{ stop.mode }}
                  </span>
                  <span class="stop-name">{{ stop.stop_name }}</span>
                  <span class="stop-dist">{{ (stop.distance_km * 1000).toFixed(0) }}m</span>
                  <span v-if="stop.is_wheelchair_accessible" class="stop-access">♿</span>
                </div>
              </div>
            </div>

            <!-- Get directions CTA -->
            <button class="get-there-btn" @click="planJourney(rec)">
              Get me there →
            </button>
          </div>

          <!-- No results -->
          <div v-if="!recommendations.length" class="no-result">
            <p>No spots found near you. Try increasing the search radius.</p>
          </div>

          <!-- Bottom nav -->
          <div class="bottom-nav">
            <button class="nav-btn" @click="$router.push('/best-time')">
              ← Back to live score
            </button>
            <button class="nav-btn nav-btn-primary" @click="$router.push('/best-time/week')">
              See full week forecast →
            </button>
          </div>
        </div>
      </template>
    </div>
  </MainLayout>
</template>

<script setup>
import { computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import LocationBar from '../components/LocationBar.vue'
import { resonanceStore as store } from '../stores/resonanceStore'
import { useResonanceApi } from '../composables/useResonanceApi'

const router = useRouter()
const { fetchGoNow, fetchSafety, fetchToilets, fetchNearbyStops } = useResonanceApi()

const recommendations = computed(() => store.goNowResult?.recommendations ?? [])
const nearbyStops     = computed(() => store.nearbyStops ?? [])
const nearestToilet   = computed(() => store.nearbyToilets?.[0] ?? null)

function modeIcon(mode) {
  if (mode === 'tram')  return '🚋'
  if (mode === 'train') return '🚆'
  return '🚌'
}

async function loadAll() {
  if (!store.locationReady) return
  const { userLat: lat, userLon: lon } = store
  store.loadingGoNow = true

  const [goNow, safety, toilets, stops] = await Promise.all([
    fetchGoNow(lat, lon, 2),
    fetchSafety(lat, lon),
    fetchToilets(lat, lon, 0.5),
    fetchNearbyStops(lat, lon, 0.5),
  ])

  store.goNowResult      = goNow
  store.safetyConditions = safety
  store.nearbyToilets    = toilets
  store.nearbyStops      = stops
  store.loadingGoNow     = false
}

function planJourney(rec) {
  if (!rec.lat || !rec.lon) return
  router.push({
    path: '/results',
    query: { to_lat: rec.lat, to_lon: rec.lon, place: rec.space_name }
  })
}

watch(() => store.locationReady, (ready) => { if (ready) loadAll() })
watch(() => [store.userLat, store.userLon], () => { if (store.locationReady) loadAll() })
onMounted(() => { if (store.locationReady) loadAll() })
</script>

<style scoped>
.page { min-height: 100vh; background: #f5f5fa; }

.result-hero {
  position: relative; overflow: hidden;
  padding: 40px 48px 44px;
  background: linear-gradient(135deg, #0c8b7d, #0a6e62);
  color: #fff;
}
.back-btn {
  display: inline-flex; align-items: center; gap: 6px;
  margin-bottom: 20px; padding: 8px 16px;
  border-radius: 999px; border: none;
  background: rgba(255,255,255,0.18); color: #fff;
  font-size: calc(14px * var(--font-scale)); font-weight: 700;
  cursor: pointer; transition: background 0.15s;
}
.back-btn:hover { background: rgba(255,255,255,0.28); }
.hero-eyebrow {
  margin: 0 0 10px;
  font-size: calc(12px * var(--font-scale)); font-weight: 800;
  letter-spacing: 0.1em; opacity: 0.8;
}
.result-hero h1 {
  margin: 0; font-family: 'Fraunces', serif;
  font-size: calc(42px * var(--font-scale)); font-weight: 700; line-height: 1.15;
}
.result-hero em { color: #f5c812; font-style: italic; }
.hero-circle { position: absolute; border-radius: 50%; background: rgba(255,255,255,0.09); }
.c1 { width: 220px; height: 220px; right: -40px; top: -40px; }
.c2 { width: 140px; height: 140px; right: 150px; bottom: -60px; }

.empty-state { text-align: center; padding: 72px 40px; color: #6b6d88; }
.empty-icon { font-size: 48px; margin-bottom: 16px; }
.empty-state h3 { margin: 0 0 10px; font-size: calc(22px * var(--font-scale)); color: #2f3152; }
.empty-state p { margin: 0; font-size: calc(16px * var(--font-scale)); }

.loading-state {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; min-height: 40vh; gap: 16px;
  color: #6b6d88; font-size: calc(16px * var(--font-scale)); font-weight: 600;
}
.spinner {
  width: 40px; height: 40px;
  border: 4px solid #e0e1ed; border-top-color: #0c8b7d;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.safety-banner {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 13px 40px; font-size: calc(14px * var(--font-scale)); font-weight: 600;
}
.verdict-good    { background: #e8f8f5; color: #0a6e62; }
.verdict-caution { background: #fff8e0; color: #8a6000; }
.verdict-poor    { background: #ffeaea; color: #c84848; }
.verdict-unknown { background: #f0f0f8; color: #6b6d88; }
.safety-dot {
  width: 9px; height: 9px; border-radius: 50%;
  background: currentColor; flex-shrink: 0; margin-top: 3px;
}

.content-area {
  padding: 24px 40px 48px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  /* removed max-width: 860px — now full width */
}
.generated-at { margin: 0; font-size: calc(13px * var(--font-scale)); color: #9b9db8; font-weight: 600; }

.rec-card {
  background: #fff; border: 1.5px solid #e0e1ed;
  border-radius: 20px; padding: 24px 28px;
  display: flex; flex-direction: column; gap: 16px;
  transition: box-shadow 0.2s;
}
.rec-card:hover { box-shadow: 0 6px 24px rgba(0,0,0,0.08); }
.rec-best { border-color: #0c8b7d; background: linear-gradient(135deg, #f0faf8 0%, #fff 60%); }

.rec-header { display: flex; align-items: flex-start; gap: 14px; }
.rec-rank {
  width: 36px; height: 36px; border-radius: 50%;
  background: #e8e9f3; color: #3c3c58;
  font-size: calc(16px * var(--font-scale)); font-weight: 800;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.rec-best .rec-rank { background: #0c8b7d; color: #fff; }
.rec-title-group { flex: 1; }
.rec-name-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 4px; }
.rec-name {
  margin: 0; font-family: 'Fraunces', serif;
  font-size: calc(22px * var(--font-scale)); font-weight: 700; color: #2f3152;
}
.grade-badge { padding: 3px 12px; border-radius: 999px; font-size: calc(12px * var(--font-scale)); font-weight: 800; }
.grade-excellent { background: #e8f8f5; color: #0a6e62; }
.grade-good      { background: #e8f5f0; color: #0c8b7d; }
.grade-fair      { background: #fff8e0; color: #8a6000; }
.grade-poor      { background: #ffeaea; color: #c84848; }
.rec-distance { margin: 0; font-size: calc(14px * var(--font-scale)); color: #6b6d88; font-weight: 600; }
.rec-score-wrap { display: flex; flex-direction: column; align-items: center; gap: 2px; flex-shrink: 0; }
.rec-score { font-size: calc(36px * var(--font-scale)); font-weight: 800; color: #0c8b7d; line-height: 1; }
.rec-score-label { font-size: calc(11px * var(--font-scale)); color: #9b9db8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }

.why-rec {
  margin: 0; padding: 12px 16px; background: #f8f8fc;
  border-radius: 12px; font-size: calc(15px * var(--font-scale));
  color: #3c3c58; line-height: 1.5; font-weight: 600;
}
.rec-best .why-rec { background: #e8f8f5; }

.chip-row { display: flex; flex-wrap: wrap; gap: 8px; }
.info-chip { padding: 6px 14px; border-radius: 999px; font-size: calc(13px * var(--font-scale)); font-weight: 700; }
.crowd-low      { background: #e8f8f5; color: #0a6e62; }
.crowd-moderate { background: #fff8e0; color: #8a6000; }
.crowd-high     { background: #ffeaea; color: #c84848; }
.crowd-unknown  { background: #f0f0f8; color: #6b6d88; }
.chip-toilet    { background: #e8f0ff; color: #2a4ab0; }
.chip-no-toilet { background: #fff3e8; color: #8a4000; }

.toilet-detail {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 12px 16px; background: #f0f8ff;
  border: 1px solid #c8e0ff; border-radius: 12px;
}
.toilet-icon { font-size: 20px; flex-shrink: 0; }
.toilet-info { display: flex; flex-direction: column; gap: 3px; }
.toilet-name { font-size: calc(13px * var(--font-scale)); font-weight: 700; color: #2f3152; }
.toilet-dist { font-size: calc(12px * var(--font-scale)); color: #6b6d88; }
.wheelchair-badge {
  display: inline-block; padding: 2px 8px; border-radius: 999px;
  background: #e8f8f5; color: #0a6e62;
  font-size: calc(11px * var(--font-scale)); font-weight: 800;
}

.transport-section { border-top: 1.5px solid #e8e9f3; padding-top: 16px; }
.transport-label { margin: 0 0 10px; font-size: calc(11px * var(--font-scale)); font-weight: 800; letter-spacing: 0.08em; color: #6b6d88; }
.stops-list { display: flex; flex-direction: column; gap: 8px; }
.stop-row {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 12px; background: #f8f8fc; border-radius: 10px; flex-wrap: wrap;
}
.stop-mode-badge { padding: 3px 10px; border-radius: 999px; font-size: calc(12px * var(--font-scale)); font-weight: 700; white-space: nowrap; }
.mode-tram  { background: #e8f8f5; color: #0a6e62; }
.mode-train { background: #e8e8ff; color: #2a2ab0; }
.mode-bus   { background: #fff3e8; color: #8a4000; }
.stop-name { flex: 1; font-size: calc(13px * var(--font-scale)); font-weight: 600; color: #2f3152; }
.stop-dist { font-size: calc(12px * var(--font-scale)); color: #9b9db8; font-weight: 600; }
.stop-access { font-size: 14px; }

.get-there-btn {
  width: 100%; padding: 16px 24px; border: none; border-radius: 14px;
  background: #f5c812; color: #1a1200;
  font-family: 'Manrope', sans-serif;
  font-size: calc(16px * var(--font-scale)); font-weight: 800;
  cursor: pointer; transition: all 0.18s ease;
}
.get-there-btn:hover { background: #e6b800; transform: translateY(-2px); }

.no-result { text-align: center; padding: 48px 20px; color: #6b6d88; font-size: calc(16px * var(--font-scale)); }

.bottom-nav {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.nav-btn {
  flex: 1; min-width: 180px; padding: 15px 20px;
  border: 2px solid #d8d9e8; border-radius: 14px;
  background: #fff; color: #3c3c58;
  font-family: 'Manrope', sans-serif;
  font-size: calc(15px * var(--font-scale)); font-weight: 700;
  cursor: pointer; transition: all 0.15s ease;
}
.nav-btn:hover { border-color: #0c8b7d; color: #0c8b7d; }
.nav-btn-primary { background: #0c8b7d; color: #fff; border-color: #0c8b7d; }
.nav-btn-primary:hover { background: #0a756a; color: #fff; }

@media (max-width: 900px) {
  .result-hero { padding: 32px 20px; }
  .result-hero h1 { font-size: calc(30px * var(--font-scale)); }
  .content-area { padding: 20px 16px 40px; }
  .safety-banner { padding: 12px 16px; }
  .rec-card { padding: 18px 16px; }
  .rec-name { font-size: calc(18px * var(--font-scale)); }
  .rec-score { font-size: calc(28px * var(--font-scale)); }
}
</style>