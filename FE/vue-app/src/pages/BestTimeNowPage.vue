<template>
  <div class="now-page">
    <div class="noise" aria-hidden="true"></div>
    <div class="orb orb-1" aria-hidden="true"></div>
    <div class="orb orb-2" aria-hidden="true"></div>

    <BestTimeLocationBar />

    <section class="hero">
      <div class="hero-bg-word" aria-hidden="true">SPOTS</div>
      <div class="hero-inner">
        <div class="hero-text">
          <RouterLink to="/best-time" class="back-btn">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
            Back to live score
          </RouterLink>
          <p class="hero-eyebrow"><span class="eyebrow-line"></span>Your best spots right now</p>
          <h1 class="hero-headline">
            The best places<br>
            <em>near you, today.</em>
          </h1>
          <p class="hero-sub" :style="{ fontSize: scaledPx(18) }">
            Top 3 spots ranked by crowd, comfort, and toilet access — refreshed for {{ store.locationReady ? store.locationLabel : 'your area' }} every 15 minutes.
          </p>
        </div>

        <div v-if="store.locationReady && store.safetyConditions" class="snapshot-card">
          <p class="snapshot-label">Conditions right now</p>
          <div class="snapshot-verdict" :class="`verdict-${(store.safetyConditions.conditions?.safety_verdict || 'unknown').toLowerCase()}`">
            <span class="verdict-dot" aria-hidden="true"></span>
            <span class="verdict-text">{{ store.safetyConditions.conditions?.safety_verdict || 'Unknown' }}</span>
          </div>
          <p class="snapshot-advice" :style="{ fontSize: scaledPx(14) }">
            {{ store.safetyConditions.advice || 'Live conditions for outdoor activity.' }}
          </p>
          <div class="snapshot-row" v-if="store.safetyConditions.conditions">
            <div class="snap-stat">
              <span class="snap-num">{{ store.safetyConditions.conditions.temperature_c ?? '—' }}°</span>
              <span class="snap-lbl">Temp</span>
            </div>
            <div class="snap-divider"></div>
            <div class="snap-stat">
              <span class="snap-num">{{ store.goNowResult?.total_spaces_checked ?? 0 }}</span>
              <span class="snap-lbl">Spaces checked</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section v-if="!store.locationReady" class="empty-band">
      <div class="empty-card">
        <svg viewBox="0 0 24 24" width="56" height="56" fill="none" stroke="#0a9b8a" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>
        <h3 :style="{ fontSize: scaledPx(24) }">Set your location to see the best spots</h3>
        <p :style="{ fontSize: scaledPx(16) }">Use the location bar above — autocomplete will help you find the right Melbourne suburb.</p>
      </div>
    </section>

    <template v-else>
      <section v-if="store.loadingGoNow && !store.goNowResult" class="loading-band">
        <div class="loading-inner">
          <div class="big-spinner" aria-hidden="true"></div>
          <p :style="{ fontSize: scaledPx(18) }">Finding the best spots near you…</p>
        </div>
      </section>

      <template v-else-if="recommendations.length">
        <div class="meta-strip">
          <div class="meta-inner">
            <span class="meta-pill" v-if="store.goNowResult?.generated_at">
              <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              Updated {{ store.goNowResult.generated_at }}
            </span>
            <span class="meta-pill" v-if="store.goNowResult?.total_spaces_checked">
              {{ store.goNowResult.total_spaces_checked }} spaces evaluated
            </span>
          </div>
        </div>

        <section class="featured-band" data-reveal>
          <div class="featured-inner">
            <div class="featured-rank-badge">
              <span class="rank-trophy">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/>
                  <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/>
                  <path d="M4 22h16"/>
                  <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/>
                  <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/>
                  <path d="M18 2H6v7a6 6 0 0 0 12 0V2z"/>
                </svg>
              </span>
              <span class="rank-text">Top pick</span>
            </div>

            <article class="featured-card" :data-grade="(recommendations[0].grade || '').toLowerCase()">
              <div class="featured-head">
                <div class="featured-title-block">
                  <h2 class="featured-name" :style="{ fontSize: scaledPx(40) }">{{ recommendations[0].space_name }}</h2>
                  <p class="featured-meta">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>
                    {{ recommendations[0].distance_km?.toFixed(1) }} km away
                    <span class="grade-chip" :class="`grade-${(recommendations[0].grade || '').toLowerCase()}`">{{ recommendations[0].grade }}</span>
                  </p>
                </div>
                <div class="featured-score">
                  <span class="score-num" :style="{ fontSize: scaledPx(64) }">{{ Math.round(recommendations[0].resonance_score) }}</span>
                  <span class="score-out">/ 100</span>
                </div>
              </div>

              <p class="featured-why" :style="{ fontSize: scaledPx(17) }">{{ recommendations[0].why_recommended }}</p>

              <div class="featured-tags">
                <span class="info-tag" :class="`crowd-${(recommendations[0].crowd_level || 'unknown').toLowerCase()}`">
                  <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
                  {{ recommendations[0].crowd_level }}
                  <span v-if="recommendations[0].is_quiet_now"> · Quiet now</span>
                </span>
                <span v-if="recommendations[0].has_toilet_nearby" class="info-tag tag-toilet">
                  <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>
                  Toilet nearby
                </span>
                <span v-else class="info-tag tag-no-toilet">
                  <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                  No toilet within 200m
                </span>
              </div>

              <div v-if="recommendations[0].has_toilet_nearby && nearestToilet" class="detail-row toilet-detail">
                <div class="detail-icon mint">
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <rect x="9" y="2" width="6" height="20" rx="1"/>
                    <rect x="2" y="9" width="20" height="6" rx="1"/>
                  </svg>
                </div>
                <div class="detail-text">
                  <span class="detail-name" :style="{ fontSize: scaledPx(15) }">{{ nearestToilet.name }}</span>
                  <span class="detail-sub">
                    {{ (nearestToilet.distance_km * 1000).toFixed(0) }}m away
                    <span v-if="nearestToilet.has_wheelchair" class="wheelchair-tag">
                      <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="4" r="2"/><path d="M12 6v5l4 4"/><path d="M10 11H6.5a2.5 2.5 0 0 0 0 5H10"/><path d="M16 17.5A4.5 4.5 0 1 1 10 14"/></svg>
                      Accessible
                    </span>
                  </span>
                </div>
              </div>

              <div v-if="nearbyStops.length" class="transport-block">
                <p class="transport-label">Nearby transport</p>
                <div class="transport-list">
                  <div v-for="stop in nearbyStops.slice(0, 3)" :key="stop.stop_id" class="stop-row">
                    <span class="stop-mode-chip" :class="`mode-${stop.mode}`">{{ stop.mode }}</span>
                    <span class="stop-name" :style="{ fontSize: scaledPx(14) }">{{ stop.stop_name }}</span>
                    <span v-if="stop.is_wheelchair_accessible" class="stop-access" aria-label="Wheelchair accessible">
                      <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="4" r="2"/><path d="M12 6v5l4 4"/><path d="M10 11H6.5a2.5 2.5 0 0 0 0 5H10"/><path d="M16 17.5A4.5 4.5 0 1 1 10 14"/></svg>
                    </span>
                    <span class="stop-dist">{{ (stop.distance_km * 1000).toFixed(0) }}m</span>
                  </div>
                </div>
              </div>

              <button class="get-there-btn primary" @click="planJourney(recommendations[0])">
                <span>Get me there</span>
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
              </button>
            </article>
          </div>
        </section>

        <section v-if="recommendations.length > 1" class="runners-band" data-reveal>
          <div class="runners-inner">
            <h2 class="runners-heading" :style="{ fontSize: scaledPx(28) }">Other great options</h2>
            <div class="runners-grid">
              <article
                v-for="(rec, idx) in recommendations.slice(1, 3)"
                :key="rec.space_name"
                class="runner-card"
                :data-grade="(rec.grade || '').toLowerCase()"
              >
                <div class="runner-head">
                  <span class="runner-rank">{{ idx + 2 }}</span>
                  <span class="grade-chip" :class="`grade-${(rec.grade || '').toLowerCase()}`">{{ rec.grade }}</span>
                </div>
                <h3 class="runner-name" :style="{ fontSize: scaledPx(22) }">{{ rec.space_name }}</h3>
                <p class="runner-meta">
                  <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>
                  {{ rec.distance_km?.toFixed(1) }} km away
                </p>
                <div class="runner-score-strip">
                  <span class="runner-score-num">{{ Math.round(rec.resonance_score) }}</span>
                  <span class="runner-score-bar"><span class="bar-inner" :style="{ width: `${Math.min(100, rec.resonance_score)}%` }"></span></span>
                </div>
                <p class="runner-why" :style="{ fontSize: scaledPx(14) }">{{ rec.why_recommended }}</p>
                <div class="runner-tags">
                  <span class="info-tag-sm" :class="`crowd-${(rec.crowd_level || 'unknown').toLowerCase()}`">{{ rec.crowd_level }}</span>
                  <span v-if="rec.has_toilet_nearby" class="info-tag-sm tag-toilet">Toilet nearby</span>
                  <span v-else class="info-tag-sm tag-no-toilet">No toilet</span>
                </div>
                <button class="get-there-btn outline" @click="planJourney(rec)">
                  Get me there
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
                </button>
              </article>
            </div>
          </div>
        </section>
      </template>

      <section v-else class="empty-band">
        <div class="empty-card">
          <h3 :style="{ fontSize: scaledPx(24) }">No spots found nearby</h3>
          <p :style="{ fontSize: scaledPx(16) }">Try a location closer to Melbourne CBD or one of the inner suburbs.</p>
        </div>
      </section>

      <section class="bottom-nav-band">
        <div class="bottom-nav-inner">
          <RouterLink to="/best-time" class="bnav-btn">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
            Back to live score
          </RouterLink>
          <RouterLink to="/best-time/week" class="bnav-btn primary">
            See full week forecast
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
          </RouterLink>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { resonanceStore } from '../stores/resonanceStore'
import { uiStore } from '../stores/uiStore'
import { useResonanceApi } from '../composables/useResonanceApi'
import BestTimeLocationBar from '../components/BestTimeLocationBar.vue'

const store = resonanceStore
const router = useRouter()
const { fetchGoNow, fetchSafety, fetchToilets, fetchNearbyStops } = useResonanceApi()
const scaledPx = (base) => `${(base * uiStore.textScale) / 100}px`

const recommendations = computed(() => store.goNowResult?.recommendations ?? [])
const nearbyStops     = computed(() => store.nearbyStops ?? [])
const nearestToilet   = computed(() => store.nearbyToilets?.[0] ?? null)

async function loadAll() {
  if (!store.locationReady) return
  const { userLat: lat, userLon: lon } = store
  store.loadingGoNow = true
  try {
    const [goNow, safety, toilets, stops] = await Promise.all([
      fetchGoNow(lat, lon, 2),
      fetchSafety(lat, lon),
      fetchToilets(lat, lon, 0.5),
      fetchNearbyStops(lat, lon, 0.5),
    ])
    store.goNowResult      = goNow
    store.safetyConditions = safety
    store.nearbyToilets    = toilets || []
    store.nearbyStops      = stops || []
  } finally {
    store.loadingGoNow = false
    setTimeout(setupReveal, 80)
  }
}

function planJourney(rec) {
  if (!rec.lat || !rec.lon) return
  router.push({
    path: '/results',
    query: { to_lat: rec.lat, to_lon: rec.lon, place: rec.space_name }
  })
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

.now-page { min-height: 100vh; background: #f2faf0; color: #1a2e1e; font-family: system-ui, sans-serif; position: relative; overflow-x: hidden; }

.noise { position: fixed; inset: 0; z-index: 1000; pointer-events: none; background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E"); background-size: 180px; opacity: 0.45; }
.orb { position: fixed; border-radius: 50%; pointer-events: none; z-index: 0; filter: blur(80px); }
.orb-1 { width: 500px; height: 500px; background: rgba(90,180,110,0.18); top: -100px; left: -80px; animation: orb-drift 22s ease-in-out infinite alternate; }
.orb-2 { width: 380px; height: 380px; background: rgba(255,180,140,0.12); bottom: 5%; right: -60px; animation: orb-drift 28s ease-in-out infinite alternate-reverse; }
@keyframes orb-drift { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(40px,50px) scale(1.1)} }

.hero {
  position: relative; overflow: hidden;
  background: linear-gradient(160deg, #e4f5e0 0%, #c8edc8 100%);
  padding: 220px 52px 80px;
  border-bottom: 1px solid rgba(29,113,105,0.12);
}
.hero-bg-word { position: absolute; right: -2%; top: 50%; transform: translateY(-50%); font-family: Georgia,serif; font-size: clamp(140px, 20vw, 280px); font-weight: 700; font-style: italic; color: rgba(10,155,138,0.085); white-space: nowrap; pointer-events: none; user-select: none; letter-spacing: -0.04em; }
.hero-inner { position: relative; z-index: 2; max-width: 1500px; margin: 0 auto; display: grid; grid-template-columns: 1fr 360px; gap: 60px; align-items: end; }
.hero-text { max-width: 720px; }

.back-btn { display: inline-flex; align-items: center; gap: 8px; padding: 8px 18px; background: rgba(255,255,255,0.7); backdrop-filter: blur(8px); border: 1px solid rgba(29,113,105,0.18); border-radius: 999px; color: #0a9b8a; font-size: 13px; font-weight: 700; text-decoration: none; margin-bottom: 24px; transition: background 0.2s; }
.back-btn:hover { background: white; }

.hero-eyebrow { display: inline-flex; align-items: center; gap: 12px; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 22px; }
.eyebrow-line { display: block; width: 32px; height: 1px; background: #0a9b8a; }
.hero-headline { font-family: Georgia,serif; font-size: clamp(42px, 5.5vw, 80px); font-weight: 700; line-height: 1.05; color: #0f1e12; margin-bottom: 18px; }
.hero-headline em { color: #0a9b8a; font-style: italic; }
.hero-sub { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.6; max-width: 580px; }

.snapshot-card {
  background: white; border: 1px solid rgba(29,113,105,0.16);
  border-radius: 22px; padding: 26px;
  box-shadow: 0 20px 50px rgba(10,155,138,0.12);
}
.snapshot-label { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 12px; }
.snapshot-verdict { display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 999px; margin-bottom: 14px; font-family: Georgia,serif; font-weight: 700; font-size: 18px; }
.verdict-dot { width: 9px; height: 9px; border-radius: 50%; background: currentColor; }
.verdict-good    { background: #e8f8f5; color: #0a6e62; }
.verdict-caution { background: #fff8e0; color: #8a6000; }
.verdict-poor    { background: #ffeaea; color: #c44a2c; }
.verdict-unknown { background: #f0f0f8; color: #4a6a4e; }
.snapshot-advice { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.55; margin-bottom: 16px; }
.snapshot-row { display: flex; align-items: center; gap: 16px; padding-top: 16px; border-top: 1px solid rgba(29,113,105,0.1); }
.snap-stat { display: flex; flex-direction: column; gap: 2px; }
.snap-num { font-family: Georgia,serif; font-size: 28px; font-weight: 700; color: #0a9b8a; line-height: 1; }
.snap-lbl { font-family: system-ui,sans-serif; font-size: 11px; color: #6a8e6e; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
.snap-divider { width: 1px; height: 36px; background: rgba(29,113,105,0.18); }

.empty-band { padding: 60px 52px 100px; }
.empty-card { display: flex; flex-direction: column; align-items: center; gap: 14px; text-align: center; max-width: 600px; margin: 0 auto; padding: 70px 40px; background: white; border: 1px solid rgba(29,113,105,0.12); border-radius: 24px; box-shadow: 0 8px 28px rgba(0,0,0,0.04); }
.empty-card h3 { font-family: Georgia,serif; color: #0f1e12; font-weight: 700; }
.empty-card p { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.6; }

.loading-band { padding: 80px 52px; }
.loading-inner { display: flex; flex-direction: column; align-items: center; gap: 18px; }
.big-spinner { width: 44px; height: 44px; border-radius: 50%; border: 4px solid rgba(10,155,138,0.18); border-top-color: #0a9b8a; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-inner p { font-family: system-ui,sans-serif; color: #4a6a4e; font-weight: 600; }

.meta-strip { background: white; border-bottom: 1px solid rgba(29,113,105,0.08); padding: 14px 52px; }
.meta-inner { max-width: 1500px; margin: 0 auto; display: flex; flex-wrap: wrap; gap: 10px; }
.meta-pill { display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; background: #f0faf0; border: 1px solid rgba(10,155,138,0.18); border-radius: 999px; color: #1d7169; font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; }

.featured-band {
  background: white;
  padding: 64px 52px;
  border-bottom: 1px solid rgba(29,113,105,0.1);
  opacity: 0; transform: translateY(40px);
  transition: all 0.9s cubic-bezier(0.22,1,0.36,1);
}
.featured-band.in-view { opacity: 1; transform: none; }
.featured-inner { max-width: 1100px; margin: 0 auto; }

.featured-rank-badge { display: inline-flex; align-items: center; gap: 10px; padding: 8px 18px; background: linear-gradient(135deg, #fff3c2, #ffe18a); border: 1px solid rgba(184,138,0,0.3); border-radius: 999px; margin-bottom: 20px; }
.rank-trophy { color: #b88a00; display: inline-flex; }
.rank-text { font-family: system-ui,sans-serif; font-size: 13px; font-weight: 800; color: #8a6000; letter-spacing: 0.05em; text-transform: uppercase; }

.featured-card {
  position: relative;
  background: linear-gradient(135deg, #f0faf0 0%, white 60%);
  border: 1.5px solid rgba(10,155,138,0.25);
  border-radius: 24px; padding: 40px;
  box-shadow: 0 24px 60px rgba(10,155,138,0.14);
  display: flex; flex-direction: column; gap: 24px;
}
.featured-card::before { content: ''; position: absolute; left: 0; top: 24px; bottom: 24px; width: 5px; border-radius: 0 4px 4px 0; background: linear-gradient(180deg, #b88a00, #f5c812); }

.featured-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 20px; flex-wrap: wrap; }
.featured-name { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1.05; margin-bottom: 10px; }
.featured-meta { display: inline-flex; align-items: center; gap: 10px; font-family: system-ui,sans-serif; font-size: 14px; color: #4a6a4e; font-weight: 600; flex-wrap: wrap; }
.featured-meta svg { color: #0a9b8a; }
.grade-chip { padding: 3px 10px; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.05em; text-transform: uppercase; }
.grade-excellent { background: #d6f4e7; color: #0a6e62; }
.grade-good      { background: #e8f5f0; color: #1d7169; }
.grade-fair      { background: #fff8e0; color: #8a6000; }
.grade-poor      { background: #ffeaea; color: #c44a2c; }

.featured-score { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; }
.score-num { font-family: Georgia,serif; font-weight: 700; color: #0a9b8a; line-height: 1; }
.score-out { font-family: system-ui,sans-serif; font-size: 13px; color: #6a8e6e; font-weight: 600; }

.featured-why { padding: 18px 22px; background: rgba(10,155,138,0.06); border-radius: 14px; color: #1a2e1e; line-height: 1.6; font-family: system-ui,sans-serif; }

.featured-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.info-tag { display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 13px; font-weight: 700; }
.crowd-low      { background: #d6f4e7; color: #1d7169; }
.crowd-moderate { background: #fff3c2; color: #b88a00; }
.crowd-high     { background: #ffded5; color: #c44a2c; }
.crowd-unknown  { background: #f0f0f8; color: #6a8e6e; }
.tag-toilet    { background: #e6dcff; color: #5b3fb6; }
.tag-no-toilet { background: #ffe8d8; color: #a04a1a; }

.detail-row { display: flex; align-items: flex-start; gap: 14px; padding: 14px 18px; background: white; border: 1px solid rgba(10,155,138,0.16); border-radius: 14px; }
.detail-icon { width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.detail-icon.mint { background: #d6f4e7; color: #1d7169; }
.detail-text { display: flex; flex-direction: column; gap: 4px; }
.detail-name { font-family: system-ui,sans-serif; font-weight: 700; color: #0f1e12; }
.detail-sub { font-family: system-ui,sans-serif; font-size: 13px; color: #6a8e6e; font-weight: 600; display: inline-flex; align-items: center; gap: 8px; }
.wheelchair-tag { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; background: #d6f4e7; color: #0a6e62; border-radius: 999px; font-size: 11px; font-weight: 800; }

.transport-block { padding-top: 4px; }
.transport-label { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; color: #6a8e6e; margin-bottom: 10px; text-transform: uppercase; }
.transport-list { display: flex; flex-direction: column; gap: 6px; }
.stop-row { display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: white; border: 1px solid rgba(10,155,138,0.1); border-radius: 10px; }
.stop-mode-chip { padding: 3px 10px; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; }
.mode-tram  { background: #d6f4e7; color: #0a6e62; }
.mode-train { background: #e8e8ff; color: #2a2ab0; }
.mode-bus   { background: #ffe8d8; color: #a04a1a; }
.stop-name { flex: 1; font-family: system-ui,sans-serif; font-weight: 600; color: #0f1e12; }
.stop-access { color: #0a9b8a; display: inline-flex; }
.stop-dist { font-family: system-ui,sans-serif; font-size: 12px; color: #8aaa8e; font-weight: 700; }

.get-there-btn { display: inline-flex; align-items: center; justify-content: center; gap: 10px; padding: 16px 28px; border-radius: 14px; font-family: system-ui,sans-serif; font-weight: 700; cursor: pointer; transition: all 0.25s; border: none; }
.get-there-btn.primary { background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; box-shadow: 0 12px 32px rgba(10,155,138,0.32); font-size: 16px; }
.get-there-btn.primary:hover { transform: translateY(-2px); box-shadow: 0 18px 40px rgba(10,155,138,0.42); }
.get-there-btn.outline { background: white; color: #0a9b8a; border: 1.5px solid rgba(10,155,138,0.3); font-size: 14px; padding: 12px 22px; }
.get-there-btn.outline:hover { background: #0a9b8a; color: white; border-color: #0a9b8a; }

.runners-band {
  background: linear-gradient(180deg, #faf8f0 0%, #f4f8e8 100%);
  padding: 80px 52px;
  border-bottom: 1px solid rgba(29,113,105,0.1);
  opacity: 0; transform: translateY(40px);
  transition: all 0.9s cubic-bezier(0.22,1,0.36,1);
}
.runners-band.in-view { opacity: 1; transform: none; }
.runners-inner { max-width: 1100px; margin: 0 auto; }
.runners-heading { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; margin-bottom: 28px; }
.runners-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

.runner-card {
  position: relative;
  background: white; border: 1px solid rgba(29,113,105,0.12);
  border-radius: 18px; padding: 28px;
  display: flex; flex-direction: column; gap: 12px;
  transition: transform 0.3s, box-shadow 0.3s;
}
.runner-card:hover { transform: translateY(-3px); box-shadow: 0 16px 40px rgba(10,155,138,0.12); }
.runner-card::before { content: ''; position: absolute; left: 0; top: 22px; bottom: 22px; width: 4px; border-radius: 0 4px 4px 0; background: rgba(10,155,138,0.4); }

.runner-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.runner-rank { width: 32px; height: 32px; border-radius: 50%; background: #e8f2e8; color: #0f1e12; font-family: Georgia,serif; font-weight: 700; font-size: 14px; display: inline-flex; align-items: center; justify-content: center; }
.runner-name { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1.2; }
.runner-meta { display: inline-flex; align-items: center; gap: 6px; font-family: system-ui,sans-serif; font-size: 13px; color: #6a8e6e; font-weight: 600; }
.runner-meta svg { color: #0a9b8a; }

.runner-score-strip { display: flex; align-items: center; gap: 12px; padding: 12px 0; }
.runner-score-num { font-family: Georgia,serif; font-size: 32px; font-weight: 700; color: #0a9b8a; line-height: 1; min-width: 50px; }
.runner-score-bar { flex: 1; height: 8px; background: #eaf4ea; border-radius: 999px; overflow: hidden; }
.bar-inner { display: block; height: 100%; background: linear-gradient(90deg, #0a9b8a, #1d7169); border-radius: 999px; transition: width 0.6s; }

.runner-why { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.55; }
.runner-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.info-tag-sm { padding: 4px 10px; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 11px; font-weight: 700; }

.bottom-nav-band { padding: 50px 52px 80px; }
.bottom-nav-inner { max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.bnav-btn { display: inline-flex; align-items: center; justify-content: center; gap: 10px; padding: 18px 24px; border-radius: 14px; background: white; border: 1.5px solid rgba(29,113,105,0.2); color: #1a2e1e; font-family: system-ui,sans-serif; font-weight: 700; text-decoration: none; transition: all 0.25s; }
.bnav-btn:hover { border-color: #0a9b8a; color: #0a9b8a; }
.bnav-btn.primary { background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; border-color: transparent; box-shadow: 0 12px 28px rgba(10,155,138,0.3); }
.bnav-btn.primary:hover { color: white; transform: translateY(-2px); box-shadow: 0 16px 36px rgba(10,155,138,0.38); }

@media (max-width: 1100px) {
  .hero-inner { grid-template-columns: 1fr; gap: 32px; }
  .runners-grid { grid-template-columns: 1fr; }
  .featured-card { padding: 28px; }
}
@media (max-width: 980px) {
  .hero { padding: 280px 20px 60px; }
  .meta-strip { padding: 12px 20px; }
  .featured-band, .runners-band { padding: 50px 20px; }
  .empty-band, .loading-band { padding: 40px 20px 80px; }
  .featured-name { font-size: 30px !important; }
  .bottom-nav-band { padding: 40px 20px 70px; }
  .bottom-nav-inner { grid-template-columns: 1fr; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
</style>