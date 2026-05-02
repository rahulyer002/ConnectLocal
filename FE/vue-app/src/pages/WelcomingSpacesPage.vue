<!-- src/pages/WelcomingSpacesPage.vue — Welcoming Community Spaces -->
<template>
  <MainLayout>
    <div class="page">
      <LocationBar @locationChanged="loadAll" />

      <!-- Hero -->
      <div class="welcoming-hero">
        <button class="back-btn" @click="$router.back()">‹ Back</button>
        <p class="hero-eyebrow">COMMUNITY CONNECTION</p>
        <h1>Welcoming spaces<br /><em>near you</em></h1>
        <p class="hero-sub">
          City of Melbourne designated spaces that are specifically inclusive
          and welcoming — a great first step if you'd like to connect with others.
        </p>
        <div class="hero-circle c1"></div>
        <div class="hero-circle c2"></div>
      </div>

      <!-- No location -->
      <div v-if="!store.locationReady" class="empty-state">
        <div class="empty-icon"><AppIcon name="heart" :size="48" color="#9b9db8" /></div>
        <h3>Set your location to find welcoming spaces</h3>
        <p>Use the bar above to enter your suburb or tap "Locate me".</p>
      </div>

      <template v-else>
        <!-- What is a welcoming space -->
        <div class="explainer-banner">
          <AppIcon name="info" :size="20" color="#2a6a30" />
          <p>
            <strong>What is a Welcoming Space?</strong>
            These are City of Melbourne designated locations — libraries, community centres,
            and civic spaces — that have committed to being inclusive, non-judgmental
            environments where anyone can drop in, rest, and connect.
          </p>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Finding welcoming spaces near you…</p>
        </div>

        <div v-else class="content-area">

          <!-- Welcoming spaces list -->
          <section class="section" v-if="store.welcomingSpaces.length">
            <h2 class="section-title">
              <AppIcon name="heart" :size="20" color="#2f3152" class="title-icon" /> {{ store.welcomingSpaces.length }} welcoming space{{ store.welcomingSpaces.length !== 1 ? 's' : '' }} found
            </h2>
            <p class="section-sub">Sorted by distance from your location.</p>

            <div class="spaces-list">
              <div
                v-for="(space, idx) in store.welcomingSpaces"
                :key="space.landmark_id"
                class="space-card"
                :class="{ 'space-card-first': idx === 0 }"
              >
                <!-- Icon + header -->
                <div class="space-header">
                  <div class="space-icon-wrap" :class="themeIconBg(space.theme)">
                    <AppIcon :name="themeIcon(space.sub_theme)" :size="24" color="#2a6a30" />
                  </div>
                  <div class="space-title-group">
                    <div class="space-name-row">
                      <h2 class="space-name">{{ space.name }}</h2>
                      <span class="welcoming-badge"><AppIcon name="check" :size="12" color="#2a6a30" /> Welcoming Space</span>
                    </div>
                    <p class="space-sub-theme">{{ space.sub_theme || space.theme }}</p>
                    <p class="space-distance">
                      {{ space.distance_km?.toFixed(2) }} km away
                      <span v-if="space.suburb_name"> · {{ space.suburb_name }}</span>
                    </p>
                  </div>
                </div>

                <!-- What to expect -->
                <div class="what-to-expect">
                  <p class="expect-label">WHAT TO EXPECT</p>
                  <p class="expect-text">{{ getExpectText(space.sub_theme, space.theme) }}</p>
                </div>

                <!-- Tags -->
                <div class="space-tags">
                  <span class="space-tag tag-free"><AppIcon name="check" :size="12" color="#3a6a10" /> Free to enter</span>
                  <span class="space-tag tag-welcoming"><AppIcon name="heart" :size="12" color="#2a6a30" /> Officially welcoming</span>
                  <span v-if="space.sub_theme" class="space-tag tag-type">
                    {{ space.sub_theme }}
                  </span>
                </div>

                <!-- Action buttons -->
                <div class="space-actions">
                  <button class="action-btn action-primary" @click="planJourneyTo(space)">
                    Get directions →
                  </button>
                  <button class="action-btn action-secondary" @click="findEventsNear(space)">
                    Events nearby
                  </button>
                </div>
              </div>
            </div>
          </section>

          <!-- No welcoming spaces found -->
          <section class="section" v-else>
            <div class="no-result">
              <div class="empty-icon"><AppIcon name="building" :size="48" color="#9b9db8" /></div>
              <h3>No welcoming spaces found within 2km</h3>
              <p>
                Welcoming Spaces are City of Melbourne designated locations, so they are
                concentrated in the inner suburbs. Try setting your location to Fitzroy,
                Carlton, Melbourne CBD, or Southbank.
              </p>
              <button class="retry-btn" @click="expandSearch">
                Search within 5km instead
              </button>
            </div>
          </section>

          <!-- Also useful: all community landmarks even if not officially designated -->
          <section class="section" v-if="communityLandmarks.length">
            <h2 class="section-title"><AppIcon name="landmark" :size="22" color="#2f3152" class="title-icon" /> Other community spaces nearby</h2>
            <p class="section-sub">
              Not officially designated as Welcoming Spaces, but still open, free,
              and community-focused.
            </p>
            <div class="community-list">
              <div
                v-for="lm in communityLandmarks"
                :key="lm.landmark_id"
                class="community-item"
              >
                <AppIcon :name="themeIcon(lm.sub_theme)" :size="22" color="#3c3c58" />
                <div class="community-info">
                  <span class="community-name">{{ lm.name }}</span>
                  <span class="community-meta">
                    {{ lm.sub_theme || lm.theme }} · {{ lm.distance_km?.toFixed(2) }} km
                  </span>
                </div>
                <button class="dir-btn" @click="planJourneyTo(lm)">→</button>
              </div>
            </div>
          </section>

          <!-- Tips for elderly users -->
          <section class="section tips-section">
            <h2 class="section-title"><AppIcon name="zap" :size="22" color="#2f3152" class="title-icon" /> Tips for your first visit</h2>
            <div class="tips-grid">
              <div class="tip-card">
                <span class="tip-icon-wrap"><AppIcon name="coffee" :size="28" color="#2f3152" /></span>
                <h3>Go at your own pace</h3>
                <p>You don't need to join anything. Just arriving and sitting quietly is enough — welcoming spaces are judgment-free zones.</p>
              </div>
              <div class="tip-card">
                <span class="tip-icon-wrap"><AppIcon name="clock" :size="28" color="#2f3152" /></span>
                <h3>Quieter in the mornings</h3>
                <p>Libraries and community centres are usually less busy between 9am and 11am on weekdays.</p>
              </div>
              <div class="tip-card">
                <span class="tip-icon-wrap"><AppIcon name="message-circle" :size="28" color="#2f3152" /></span>
                <h3>Staff are there to help</h3>
                <p>You can always ask staff about free programs, events, or just for a chat — that's what welcoming spaces are for.</p>
              </div>
            </div>
          </section>

          <!-- Bottom nav -->
          <div class="bottom-nav">
            <button class="nav-btn" @click="$router.push('/best-time')">← Live score</button>
            <button class="nav-btn nav-btn-primary" @click="$router.push('/best-time/result')">Best spots now →</button>
            <button class="nav-btn" @click="$router.push('/discover')">Browse events</button>
          </div>
        </div>
      </template>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import LocationBar from '../components/LocationBar.vue'
import AppIcon from '../components/AppIcon.vue'
import { resonanceStore as store } from '../stores/resonanceStore'
import { useResonanceApi } from '../composables/useResonanceApi'

const router  = useRouter()
const { fetchWelcomingSpaces, fetchJourneyPlan } = useResonanceApi()

const loading    = ref(false)
const allLandmarks = ref([])   // full unfiltered response
const searchRadius = ref(2)

// Community landmarks that are NOT welcoming spaces (fallback list)
const communityLandmarks = computed(() =>
  allLandmarks.value
    .filter(l => !l.is_welcoming_space)
    .slice(0, 5)
)

function themeIcon(subTheme) {
  const s = (subTheme || '').toLowerCase()
  if (s.includes('library'))          return 'library'
  if (s.includes('community centre')) return 'home'
  if (s.includes('civic') || s.includes('hall')) return 'landmark'
  if (s.includes('health'))           return 'cross'
  if (s.includes('park'))             return 'leaf'
  if (s.includes('museum') || s.includes('gallery')) return 'image'
  if (s.includes('church') || s.includes('chapel'))  return 'building'
  return 'building'
}

function themeIconBg(theme) {
  const t = (theme || '').toLowerCase()
  if (t.includes('community')) return 'bg-community'
  if (t.includes('health'))    return 'bg-health'
  if (t.includes('leisure'))   return 'bg-leisure'
  if (t.includes('education')) return 'bg-education'
  return 'bg-default'
}

function getExpectText(subTheme, theme) {
  const s = (subTheme || theme || '').toLowerCase()
  if (s.includes('library'))
    return 'A calm, quiet space with free Wi-Fi, books, newspapers, and friendly staff. No purchase needed — you can simply sit and rest.'
  if (s.includes('community centre'))
    return 'A hub for local programs, social groups, and activities. Drop in anytime or ask about upcoming free events.'
  if (s.includes('civic') || s.includes('hall'))
    return 'A public civic space open to all. Often hosts free exhibitions, public events, and community gatherings.'
  if (s.includes('health'))
    return 'A health and wellbeing service. Friendly staff can connect you with community programs and support services.'
  return 'A welcoming community space — open to all, free to enter, with friendly staff on hand.'
}

function planJourneyTo(space) {
  if (!space.lat && !space.lng) return
  router.push({
    path: '/results',
    query: {
      to_lat: space.lat,
      to_lon: space.lng,
      place: space.name,
    }
  })
}

function findEventsNear(space) {
  router.push({
    path: '/discover',
    query: { suburb: space.suburb_name || '' }
  })
}

async function expandSearch() {
  searchRadius.value = 5
  await loadAll()
}

async function loadAll() {
  if (!store.locationReady) return
  loading.value = true

  const BASE = 'https://connectlocal.duckdns.org'
  const { userLat: lat, userLon: lon } = store

  try {
    // Fetch all Community Use landmarks (welcoming + non-welcoming)
    const url = new URL(`${BASE}/api/landmarks/nearby`)
    url.searchParams.set('lat', lat)
    url.searchParams.set('lon', lon)
    url.searchParams.set('radius_km', searchRadius.value)
    url.searchParams.set('theme', 'Community Use')
    url.searchParams.set('limit', 20)

    const res  = await fetch(url.toString())
    const data = await res.json()
    const list = Array.isArray(data) ? data : data.landmarks || []

    allLandmarks.value       = list
    store.welcomingSpaces    = list.filter(l => l.is_welcoming_space === true)
  } catch {
    // Mock fallback
    store.welcomingSpaces = [
      { landmark_id: 1, name: 'Fitzroy Library', theme: 'Community Use', sub_theme: 'Library', distance_km: 0.2, is_welcoming_space: true, suburb_name: 'Fitzroy', lat: -37.7990, lng: 144.9780 },
      { landmark_id: 2, name: 'Carlton Neighbourhood Learning Centre', theme: 'Community Use', sub_theme: 'Community Centre', distance_km: 0.6, is_welcoming_space: true, suburb_name: 'Carlton', lat: -37.8020, lng: 144.9670 },
      { landmark_id: 3, name: 'Melbourne Town Hall', theme: 'Community Use', sub_theme: 'Civic Hall', distance_km: 1.1, is_welcoming_space: true, suburb_name: 'Melbourne', lat: -37.8136, lng: 144.9631 },
    ]
    allLandmarks.value = store.welcomingSpaces
  }

  loading.value = false
}

watch(() => store.locationReady, (ready) => { if (ready) loadAll() })
watch(() => [store.userLat, store.userLon], () => { if (store.locationReady) loadAll() })
onMounted(() => { if (store.locationReady) loadAll() })
</script>

<style scoped>
.page { min-height: 100vh; background: #f5f5fa; }

/* ── Hero ── */
.welcoming-hero {
  position: relative; overflow: hidden;
  padding: 40px 48px 44px;
  background: linear-gradient(135deg, #2a6a30, #1e5226);
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
.hero-eyebrow { margin: 0 0 10px; font-size: calc(12px * var(--font-scale)); font-weight: 800; letter-spacing: 0.1em; opacity: 0.8; }
.welcoming-hero h1 {
  margin: 0 0 14px; font-family: 'Fraunces', serif;
  font-size: calc(42px * var(--font-scale)); font-weight: 700; line-height: 1.15;
}
.welcoming-hero em { color: #f5c812; font-style: italic; }
.hero-sub { margin: 0; font-size: calc(15px * var(--font-scale)); opacity: 0.88; max-width: 560px; line-height: 1.6; }
.hero-circle { position: absolute; border-radius: 50%; background: rgba(255,255,255,0.09); }
.c1 { width: 220px; height: 220px; right: -40px; top: -40px; }
.c2 { width: 140px; height: 140px; right: 150px; bottom: -60px; }

/* ── Explainer banner ── */
.explainer-banner {
  display: flex; align-items: flex-start; gap: 14px;
  padding: 16px 40px; background: #edf7ec;
  border-bottom: 1.5px solid #b0d9b3;
}
.explainer-icon { font-size: 20px; flex-shrink: 0; margin-top: 2px; }
.explainer-banner p { margin: 0; font-size: calc(14px * var(--font-scale)); color: #2a6a30; line-height: 1.6; }

/* ── States ── */
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
  width: 36px; height: 36px;
  border: 4px solid #e0e1ed; border-top-color: #2a6a30;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Content ── */
.content-area { display: flex; flex-direction: column; }
.section { padding: 28px 40px; border-bottom: 1.5px solid #e8e9f3; }
.section-title { margin: 0 0 6px; font-family: 'Fraunces', serif; font-size: calc(22px * var(--font-scale)); color: #2f3152; }
.section-sub { margin: 0 0 20px; font-size: calc(13px * var(--font-scale)); color: #6b6d88; }

/* ── Space cards ── */
.spaces-list { display: flex; flex-direction: column; gap: 16px; }

.space-card {
  background: #fff; border: 1.5px solid #e0e1ed;
  border-radius: 20px; padding: 24px 28px;
  display: flex; flex-direction: column; gap: 16px;
  transition: box-shadow 0.2s;
}
.space-card:hover { box-shadow: 0 6px 24px rgba(0,0,0,0.07); }
.space-card-first { border-color: #2a6a30; background: linear-gradient(135deg, #edf7ec 0%, #fff 60%); }

.space-header { display: flex; align-items: flex-start; gap: 16px; }
.space-icon-wrap {
  width: 52px; height: 52px; border-radius: 14px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; font-size: 24px;
}
.bg-community { background: #edf7ec; }
.bg-health    { background: #ffeaea; }
.bg-leisure   { background: #e8f8f5; }
.bg-education { background: #e8f0ff; }
.bg-default   { background: #f0f0f8; }

.space-title-group { flex: 1; }
.space-name-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 4px; }
.space-name {
  margin: 0; font-family: 'Fraunces', serif;
  font-size: calc(20px * var(--font-scale)); font-weight: 700; color: #2f3152;
}
.welcoming-badge {
  padding: 3px 12px; border-radius: 999px;
  background: #edf7ec; color: #2a6a30;
  font-size: calc(12px * var(--font-scale)); font-weight: 800;
  white-space: nowrap;
}
.space-sub-theme { margin: 0 0 3px; font-size: calc(14px * var(--font-scale)); color: #6b6d88; font-weight: 700; }
.space-distance { margin: 0; font-size: calc(13px * var(--font-scale)); color: #9b9db8; font-weight: 600; }

.what-to-expect {
  padding: 14px 16px; background: #f8f8fc;
  border-radius: 12px;
}
.space-card-first .what-to-expect { background: #edf7ec; }
.expect-label { margin: 0 0 6px; font-size: calc(11px * var(--font-scale)); font-weight: 800; letter-spacing: 0.08em; color: #6b6d88; }
.expect-text { margin: 0; font-size: calc(14px * var(--font-scale)); color: #3c3c58; line-height: 1.6; }

.space-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.space-tag { padding: 4px 12px; border-radius: 999px; font-size: calc(12px * var(--font-scale)); font-weight: 700; }
.tag-free      { background: #f0f8e8; color: #3a6a10; }
.tag-welcoming { background: #edf7ec; color: #2a6a30; }
.tag-type      { background: #f0f0f8; color: #3c3c58; }

.space-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.action-btn {
  flex: 1; min-width: 140px; padding: 13px 18px;
  border-radius: 12px; font-family: 'Manrope', sans-serif;
  font-size: calc(14px * var(--font-scale)); font-weight: 700;
  cursor: pointer; transition: all 0.15s ease;
}
.action-primary { border: none; background: #2a6a30; color: #fff; }
.action-primary:hover { background: #1e5226; transform: translateY(-1px); }
.action-secondary { border: 2px solid #d8d9e8; background: #fff; color: #3c3c58; }
.action-secondary:hover { border-color: #2a6a30; color: #2a6a30; }

/* ── No result ── */
.no-result {
  text-align: center; padding: 48px 20px;
  color: #6b6d88;
}
.no-result-icon { font-size: 48px; margin-bottom: 16px; }
.no-result h3 { margin: 0 0 12px; font-size: calc(20px * var(--font-scale)); color: #2f3152; }
.no-result p { margin: 0 0 20px; font-size: calc(15px * var(--font-scale)); max-width: 480px; margin-inline: auto; line-height: 1.6; }
.retry-btn {
  padding: 13px 24px; border: none; border-radius: 12px;
  background: #2a6a30; color: #fff;
  font-family: 'Manrope', sans-serif;
  font-size: calc(15px * var(--font-scale)); font-weight: 700;
  cursor: pointer; transition: background 0.15s;
}
.retry-btn:hover { background: #1e5226; }

/* ── Community list (non-welcoming fallback) ── */
.community-list { display: flex; flex-direction: column; gap: 10px; }
.community-item {
  display: flex; align-items: center; gap: 14px;
  padding: 14px 18px; background: #fff;
  border: 1.5px solid #e0e1ed; border-radius: 12px;
}
.community-icon { font-size: 22px; flex-shrink: 0; }
.community-info { display: flex; flex-direction: column; gap: 3px; flex: 1; }
.community-name { font-size: calc(15px * var(--font-scale)); font-weight: 700; color: #2f3152; }
.community-meta { font-size: calc(13px * var(--font-scale)); color: #6b6d88; font-weight: 600; }
.dir-btn {
  width: 36px; height: 36px; border-radius: 50%;
  border: 2px solid #d8d9e8; background: #fff; color: #3c3c58;
  font-size: 18px; font-weight: 700; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s; flex-shrink: 0;
}
.dir-btn:hover { border-color: #2a6a30; color: #2a6a30; }

/* ── Tips ── */
.tips-section { background: #f0f8e8; }
.tips-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
.tip-card {
  background: #fff; border-radius: 16px; padding: 20px;
  display: flex; flex-direction: column; gap: 8px;
}
.tip-icon { font-size: 28px; }
.tip-card h3 { margin: 0; font-size: calc(16px * var(--font-scale)); font-weight: 800; color: #2f3152; }
.tip-card p { margin: 0; font-size: calc(13px * var(--font-scale)); color: #6b6d88; line-height: 1.6; }

/* ── Bottom nav ── */
.bottom-nav { display: flex; gap: 10px; flex-wrap: wrap; padding: 24px 40px 40px; }
.nav-btn {
  flex: 1; min-width: 130px; padding: 14px 16px;
  border: 2px solid #d8d9e8; border-radius: 14px;
  background: #fff; color: #3c3c58;
  font-family: 'Manrope', sans-serif;
  font-size: calc(14px * var(--font-scale)); font-weight: 700;
  cursor: pointer; transition: all 0.15s ease; text-align: center;
}
.nav-btn:hover { border-color: #2a6a30; color: #2a6a30; }
.nav-btn-primary { background: #2a6a30; color: #fff; border-color: #2a6a30; }
.nav-btn-primary:hover { background: #1e5226; color: #fff; }

@media (max-width: 900px) {
  .welcoming-hero { padding: 32px 20px; }
  .welcoming-hero h1 { font-size: calc(30px * var(--font-scale)); }
  .section { padding: 22px 16px; }
  .explainer-banner { padding: 14px 16px; }
  .space-card { padding: 18px 16px; }
  .bottom-nav { padding: 20px 16px 36px; }
  .tips-grid { grid-template-columns: 1fr; }
}
</style>