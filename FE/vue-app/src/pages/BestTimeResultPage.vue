<!-- src/pages/BestTimeResultPage.vue — Page 2: Go Now (Top 3 Spots + Nature Spaces) -->
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

          <!-- Top recommendation cards from resonance/gonow API -->
          <div
            v-for="(rec, idx) in recommendations"
            :key="rec.space_name"
            class="rec-card"
            :class="{ 'rec-best': idx === 0 }"
          >
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

            <p class="why-rec">{{ rec.why_recommended }}</p>

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

            <!-- Toilet detail for this specific place -->
            <div
              v-if="rec.has_toilet_nearby && getNearestToiletForPlace(rec)"
              class="toilet-detail"
            >
              <span class="toilet-icon">🚻</span>
              <div class="toilet-info">
                <span class="toilet-name">
                  {{ getNearestToiletForPlace(rec).name }}
                </span>

                <span class="toilet-dist">
                  {{ (getNearestToiletForPlace(rec).distance_km * 1000).toFixed(0) }}m away
                </span>

                <span
                  v-if="getNearestToiletForPlace(rec).has_wheelchair"
                  class="wheelchair-badge"
                >
                  ♿ Accessible
                </span>
              </div>
            </div>

            <!-- Nearby transport for this specific place -->
            <div v-if="getNearbyStopsForPlace(rec).length" class="transport-section">
              <p class="transport-label">NEARBY TRANSPORT</p>

              <div class="stops-list">
                <div
                  v-for="stop in getNearbyStopsForPlace(rec).slice(0, 3)"
                  :key="stop.stop_id"
                  class="stop-row"
                >
                  <span class="stop-mode-badge" :class="`mode-${stop.mode}`">
                    {{ modeIcon(stop.mode) }} {{ stop.mode }}
                  </span>
                  <span class="stop-name">{{ stop.stop_name }}</span>
                  <span class="stop-dist">{{ (stop.distance_km * 1000).toFixed(0) }}m</span>
                  <span v-if="stop.is_wheelchair_accessible" class="stop-access">♿</span>
                </div>
              </div>
            </div>

            <button class="get-there-btn" @click="planJourney(rec)">
              Get me there →
            </button>
          </div>

          <!-- Nature Spaces section from greenspace/nearby API -->
          <section v-if="natureSpaces.length" class="nature-section">
            <div class="nature-header">
              <p class="nature-eyebrow">Nature Spaces</p>
              <h2>Nearby outdoor places with accessibility details</h2>
              <p>
                These places are loaded from the green space API and may suit a
                gentle outing, fresh air break, or short walk.
              </p>
            </div>

            <div class="nature-grid">
              <article
                v-for="space in natureSpaces"
                :key="space.id"
                class="nature-card"
              >
                <div class="nature-card-top">
                  <div>
                    <span class="nature-type">{{ space.type }}</span>
                    <h3>{{ space.name }}</h3>
                    <p class="nature-distance">{{ space.walkingDistance }}</p>
                  </div>

                  <span class="quiet-pill">{{ space.quietness }}</span>
                </div>

                <p class="nature-reason">{{ space.reason }}</p>

                <div class="accessibility-grid">
                  <div class="access-item">
                    <span class="access-label">Walking distance</span>
                    <strong>{{ space.walkingDistance }}</strong>
                  </div>

                  <div class="access-item">
                    <span class="access-label">Shade</span>
                    <strong>{{ space.shade }}</strong>
                  </div>

                  <div class="access-item">
                    <span class="access-label">Seating</span>
                    <strong>{{ space.seating }}</strong>
                  </div>

                  <div class="access-item">
                    <span class="access-label">Toilet</span>
                    <strong>{{ space.toilet }}</strong>
                  </div>
                </div>

                <div class="nature-extra-row">
                  <span class="nature-chip">
                    Comfort {{ space.comfortScore }}
                  </span>

                  <span class="nature-chip">
                    Walkability {{ space.walkabilityScore }}
                  </span>

                  <span v-if="space.publicAccess" class="nature-chip chip-public">
                    Free public access
                  </span>
                </div>

                <button class="nature-route-btn" @click="planJourney(space.raw)">
                  Plan a gentle visit →
                </button>
              </article>
            </div>
          </section>

          <div v-else-if="store.loadingSpaces" class="loading-state small-loading">
            <div class="spinner"></div>
            <p>Loading nearby nature spaces…</p>
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
import { computed, watch, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import LocationBar from '../components/LocationBar.vue'
import { resonanceStore as store } from '../stores/resonanceStore'
import { useResonanceApi } from '../composables/useResonanceApi'

const router = useRouter()

const {
  fetchGoNow,
  fetchSafety,
  fetchToilets,
  fetchNearbyStops,
  fetchGreenSpaces,
} = useResonanceApi()

const recommendations = computed(() => store.goNowResult?.recommendations ?? [])

const toiletsByPlace = ref({})
const stopsByPlace = ref({})

const natureSpaces = computed(() => {
  const spaces = store.greenSpaces ?? []

  return spaces.map((space, index) => {
    const matchedRecommendation = findMatchingRecommendation(space)

    return {
      raw: space,
      id: space.space_id || space.space_name || index,
      name: space.space_name || 'Unnamed outdoor space',
      type: getNatureType(space.space_name, space.category, index),
      walkingDistance: `${Number(space.distance_km ?? 0).toFixed(1)} km away`,
      shade: getShadeAvailability(space),
      seating: getSeatingAvailability(space),
      toilet: getToiletAvailability(space),
      quietness: getQuietnessIndicator(matchedRecommendation),
      reason: getNatureReason(space, matchedRecommendation),
      comfortScore: Math.round(space.comfort_score ?? 0),
      walkabilityScore: Math.round(space.walkability_score ?? 0),
      publicAccess: space.public_access !== false,
    }
  })
})

function modeIcon(mode) {
  if (mode === 'tram') return '🚋'
  if (mode === 'train') return '🚆'
  return '🚌'
}

function getLat(item) {
  return item.lat ?? item.latitude ?? item.centroid_lat ?? item.y
}

function getLon(item) {
  return item.lon ?? item.lng ?? item.longitude ?? item.centroid_lon ?? item.x
}

function placeKey(place) {
  const lat = getLat(place)
  const lon = getLon(place)

  return place.space_name || place.name || `${lat}-${lon}`
}

function getNearestToiletForPlace(place) {
  const toilets = toiletsByPlace.value[placeKey(place)] ?? []
  return toilets[0] ?? null
}

function getNearbyStopsForPlace(place) {
  return stopsByPlace.value[placeKey(place)] ?? []
}

async function loadFacilitiesForRecommendations(recs) {
  const topRecs = recs.slice(0, 3)

  const facilityResults = await Promise.all(
    topRecs.map(async (rec) => {
      const lat = getLat(rec)
      const lon = getLon(rec)

      if (!lat || !lon) {
        return {
          key: placeKey(rec),
          toilets: [],
          stops: [],
        }
      }

      const [toilets, stops] = await Promise.all([
        fetchToilets(lat, lon, 0.5),
        fetchNearbyStops(lat, lon, 0.5),
      ])

      return {
        key: placeKey(rec),
        toilets,
        stops,
      }
    })
  )

  const toiletMap = {}
  const stopMap = {}

  facilityResults.forEach((item) => {
    toiletMap[item.key] = item.toilets
    stopMap[item.key] = item.stops
  })

  toiletsByPlace.value = toiletMap
  stopsByPlace.value = stopMap
}

function findMatchingRecommendation(space) {
  return recommendations.value.find((rec) => {
    const recName = rec.space_name?.toLowerCase() ?? ''
    const spaceName = space.space_name?.toLowerCase() ?? ''

    return recName && spaceName && recName === spaceName
  })
}

function getNatureType(name, category, index) {
  const lowerName = name?.toLowerCase() ?? ''
  const lowerCategory = category?.toLowerCase() ?? ''

  if (lowerName.includes('garden') || lowerCategory.includes('garden')) return 'Garden'
  if (lowerName.includes('park') || lowerCategory.includes('park')) return 'Park'
  if (lowerName.includes('walk') || lowerName.includes('trail')) return 'Walkway'

  const fallbackTypes = ['Park', 'Garden', 'Walkway']
  return fallbackTypes[index % fallbackTypes.length]
}

function getShadeAvailability(space) {
  const comfortScore = Number(space.comfort_score ?? 0)
  const walkabilityScore = Number(space.walkability_score ?? 0)

  if (comfortScore >= 75 || walkabilityScore >= 80) return 'Good shade likely'
  if (comfortScore >= 55 || walkabilityScore >= 60) return 'Some shade available'

  return 'Limited shade information'
}

function getSeatingAvailability(space) {
  const category = space.category?.toLowerCase() ?? ''
  const name = space.space_name?.toLowerCase() ?? ''

  if (category.includes('garden') || category.includes('park')) {
    return 'Seating likely available'
  }

  if (name.includes('garden') || name.includes('park')) {
    return 'Seating likely available'
  }

  return 'Limited seating information'
}

function getToiletAvailability(space) {
  if (space.has_toilet_nearby) {
    return 'Toilet nearby'
  }

  return 'No toilet nearby'
}

function getQuietnessIndicator(matchedRecommendation) {
  if (!matchedRecommendation) {
    return 'Usually quiet mornings'
  }

  if (matchedRecommendation.is_quiet_now) {
    return 'Quiet now'
  }

  if (matchedRecommendation.crowd_level === 'Low') {
    return 'Usually quiet mornings'
  }

  if (matchedRecommendation.crowd_level === 'Moderate') {
    return 'Usually calmer earlier in the day'
  }

  return 'May be busier during peak times'
}

function getNatureReason(space, matchedRecommendation) {
  if (matchedRecommendation?.why_recommended) {
    return matchedRecommendation.why_recommended
  }

  const comfortScore = Math.round(space.comfort_score ?? 0)

  if (comfortScore >= 70) {
    return 'Recommended because it has a strong comfort score for a gentle outdoor visit.'
  }

  return 'Recommended as a nearby outdoor place for a short walk or fresh air break.'
}

async function loadAll() {
  if (!store.locationReady) return

  const { userLat: lat, userLon: lon } = store

  store.loadingGoNow = true
  store.loadingSpaces = true
  toiletsByPlace.value = {}
  stopsByPlace.value = {}

  try {
    const [goNow, safety, greenSpaces] = await Promise.all([
      fetchGoNow(lat, lon, 5),          
      fetchSafety(lat, lon),
      fetchGreenSpaces(lat, lon, 5, null, 6),  
    ])

    store.goNowResult = goNow
    store.safetyConditions = safety
    store.greenSpaces = greenSpaces

    if (goNow?.recommendations?.length) {
      await loadFacilitiesForRecommendations(goNow.recommendations)
    }

  } catch (error) {
    console.error('Go now page failed:', error)
    store.goNowResult = null
    store.safetyConditions = null
    store.greenSpaces = []
  } finally {
    store.loadingGoNow = false
    store.loadingSpaces = false
  }
}

function planJourney(place) {
  const lat = getLat(place)
  const lon = getLon(place)
  const placeName = place.space_name || place.name || 'Selected place'

  if (!lat || !lon) return

  router.push({
    path: '/results',
    query: {
      to_lat: lat,
      to_lon: lon,
      place: placeName,
    },
  })
}

watch(() => store.locationReady, (ready) => {
  if (ready) loadAll()
})

watch(() => [store.userLat, store.userLon], () => {
  if (store.locationReady) loadAll()
})

onMounted(() => {
  if (store.locationReady) loadAll()
})
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
.small-loading { min-height: 140px; }
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
.verdict-good { background: #e8f8f5; color: #0a6e62; }
.verdict-caution { background: #fff8e0; color: #8a6000; }
.verdict-poor { background: #ffeaea; color: #c84848; }
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
.grade-good { background: #e8f5f0; color: #0c8b7d; }
.grade-fair { background: #fff8e0; color: #8a6000; }
.grade-poor { background: #ffeaea; color: #c84848; }
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
.crowd-low { background: #e8f8f5; color: #0a6e62; }
.crowd-moderate { background: #fff8e0; color: #8a6000; }
.crowd-high { background: #ffeaea; color: #c84848; }
.crowd-unknown { background: #f0f0f8; color: #6b6d88; }
.chip-toilet { background: #e8f0ff; color: #2a4ab0; }
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
.mode-tram { background: #e8f8f5; color: #0a6e62; }
.mode-train { background: #e8e8ff; color: #2a2ab0; }
.mode-bus { background: #fff3e8; color: #8a4000; }
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

/* Nature Spaces section */
.nature-section {
  margin-top: 8px;
  padding: 28px;
  background: #ffffff;
  border: 1.5px solid #c9ebe7;
  border-radius: 24px;
}

.nature-header {
  margin-bottom: 22px;
}

.nature-eyebrow {
  margin: 0 0 8px;
  color: #0c8b7d;
  font-size: calc(12px * var(--font-scale));
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.nature-header h2 {
  margin: 0 0 8px;
  font-family: 'Fraunces', serif;
  font-size: calc(28px * var(--font-scale));
  color: #2f3152;
}

.nature-header p {
  margin: 0;
  color: #6b6d88;
  font-size: calc(15px * var(--font-scale));
  line-height: 1.5;
}

.nature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.nature-card {
  padding: 20px;
  border: 1.5px solid #e0e1ed;
  border-radius: 18px;
  background: linear-gradient(135deg, #f8fffd, #ffffff);
}

.nature-card-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 12px;
}

.nature-type {
  display: inline-block;
  margin-bottom: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  background: #e8f8f5;
  color: #0a6e62;
  font-size: calc(11px * var(--font-scale));
  font-weight: 900;
  text-transform: uppercase;
}

.nature-card h3 {
  margin: 0;
  font-family: 'Fraunces', serif;
  color: #2f3152;
  font-size: calc(20px * var(--font-scale));
  line-height: 1.2;
}

.nature-distance {
  margin: 6px 0 0;
  color: #6b6d88;
  font-size: calc(13px * var(--font-scale));
  font-weight: 700;
}

.quiet-pill {
  flex-shrink: 0;
  padding: 6px 10px;
  border-radius: 999px;
  background: #fff8e0;
  color: #8a6000;
  font-size: calc(11px * var(--font-scale));
  font-weight: 900;
}

.nature-reason {
  margin: 0 0 16px;
  color: #3c3c58;
  font-size: calc(14px * var(--font-scale));
  line-height: 1.5;
  font-weight: 600;
}

.accessibility-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  margin-bottom: 16px;
}

.access-item {
  padding: 12px;
  border-radius: 12px;
  background: #f5f5fa;
}

.access-label {
  display: block;
  margin-bottom: 4px;
  color: #6b6d88;
  font-size: calc(11px * var(--font-scale));
  font-weight: 900;
  text-transform: uppercase;
}

.access-item strong {
  color: #2f3152;
  font-size: calc(13px * var(--font-scale));
  line-height: 1.35;
}

.nature-extra-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.nature-chip {
  padding: 5px 10px;
  border-radius: 999px;
  background: #f0f0f8;
  color: #3c3c58;
  font-size: calc(11px * var(--font-scale));
  font-weight: 800;
}

.chip-public {
  background: #e8f8f5;
  color: #0a6e62;
}

.nature-route-btn {
  width: 100%;
  padding: 13px 16px;
  border: none;
  border-radius: 14px;
  background: #0c8b7d;
  color: #ffffff;
  font-size: calc(14px * var(--font-scale));
  font-weight: 800;
  cursor: pointer;
}

.nature-route-btn:hover {
  background: #0a756a;
}

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

@media (max-width: 1100px) {
  .nature-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .result-hero { padding: 32px 20px; }
  .result-hero h1 { font-size: calc(30px * var(--font-scale)); }
  .content-area { padding: 20px 16px 40px; }
  .safety-banner { padding: 12px 16px; }
  .rec-card { padding: 18px 16px; }
  .rec-name { font-size: calc(18px * var(--font-scale)); }
  .rec-score { font-size: calc(28px * var(--font-scale)); }
  .nature-section { padding: 22px 16px; }
  .bottom-nav { grid-template-columns: 1fr; }
}
</style>