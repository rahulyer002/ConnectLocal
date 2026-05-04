<template>
  <div class="welcoming-page">
    <div class="noise" aria-hidden="true"></div>
    <div class="orb orb-1" aria-hidden="true"></div>
    <div class="orb orb-2" aria-hidden="true"></div>

    <BestTimeNav />

    <div class="a11y-bar">
      <div class="a11y-inner">
        <div class="text-size-control">
          <span class="a-small">A</span>
          <input type="range" class="text-slider" min="90" max="140" step="5" v-model.number="textScale" aria-label="Text size" />
          <span class="a-large">A</span>
          <span class="scale-pct">{{ textScale }}%</span>
        </div>
      </div>
    </div>

    <BestTimeLocationBar />

    <!-- ═══ HERO ═══ -->
    <section class="hero">
      <div class="hero-bg-word" aria-hidden="true">WELCOME</div>
      <div class="hero-leaves" aria-hidden="true">
        <svg viewBox="0 0 200 200" width="100%" height="100%">
          <path d="M30 120 q-10-30 0-60 q15 25 0 60z" fill="rgba(255,255,255,0.06)" />
          <path d="M170 80 q10-30 0-60 q-15 25 0 60z" fill="rgba(255,255,255,0.05)" />
          <path d="M50 180 q-10-25 0-50 q15 20 0 50z" fill="rgba(255,255,255,0.04)" />
        </svg>
      </div>
      <div class="hero-inner">
        <RouterLink to="/best-time" class="back-btn">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          Back to live score
        </RouterLink>
        <p class="hero-eyebrow"><span class="eyebrow-line"></span>Community connection</p>
        <h1 class="hero-headline">
          Welcoming spaces<br>
          <em>near you.</em>
        </h1>
        <p class="hero-sub" :style="{ fontSize: scaledPx(18) }">
          City of Melbourne designated spaces that are specifically inclusive and welcoming —
          a great first step if you'd like to connect with others.
        </p>
      </div>
    </section>

    <!-- ═══ EXPLAINER BAND ═══ -->
    <section class="explainer-band">
      <div class="explainer-inner">
        <div class="explainer-icon">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <div class="explainer-text">
          <p class="explainer-label">What is a Welcoming Space?</p>
          <p :style="{ fontSize: scaledPx(15) }">
            These are City of Melbourne designated locations — libraries, community centres, and civic spaces —
            that have committed to being inclusive, non-judgmental environments where anyone can drop in, rest, and connect.
          </p>
        </div>
      </div>
    </section>

    <!-- ═══ EMPTY / LOADING ═══ -->
    <section v-if="!store.locationReady" class="empty-band">
      <div class="empty-card">
        <svg viewBox="0 0 24 24" width="56" height="56" fill="none" stroke="#2a6a30" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>
        <h3 :style="{ fontSize: scaledPx(24) }">Set your location to find welcoming spaces</h3>
        <p :style="{ fontSize: scaledPx(16) }">Use the location bar above — autocomplete will help you set a Melbourne suburb or postcode.</p>
      </div>
    </section>

    <template v-else>
      <section v-if="loading && !allLandmarks.length" class="loading-band">
        <div class="big-spinner" aria-hidden="true"></div>
        <p :style="{ fontSize: scaledPx(18) }">Finding welcoming spaces near you…</p>
      </section>

      <template v-else>

        <!-- ═══ DESIGNATED SPACES BAND ═══ -->
        <section v-if="welcomingSpaces.length" class="spaces-band" data-reveal>
          <div class="spaces-inner">
            <div class="spaces-header">
              <p class="section-label">Officially designated</p>
              <h2 class="section-heading" :style="{ fontSize: scaledPx(40) }">
                {{ welcomingSpaces.length }}
                <em>welcoming space{{ welcomingSpaces.length !== 1 ? 's' : '' }}</em><br>
                near you
              </h2>
              <p class="section-sub" :style="{ fontSize: scaledPx(16) }">Sorted by distance from your location.</p>
            </div>

            <div class="spaces-grid">
              <article
                v-for="(space, idx) in welcomingSpaces"
                :key="space.landmark_id || space.name"
                class="space-card"
                :class="{ 'space-card-feature': idx === 0 }"
                :style="{ '--i': idx }"
              >
                <div class="space-head">
                  <div class="space-icon-wrap" :class="themeIconBg(space.theme)">
                    <component :is="'svg'" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <template v-if="themeIcon(space.sub_theme) === 'library'">
                        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                      </template>
                      <template v-else-if="themeIcon(space.sub_theme) === 'home'">
                        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                        <polyline points="9 22 9 12 15 12 15 22"/>
                      </template>
                      <template v-else-if="themeIcon(space.sub_theme) === 'landmark'">
                        <line x1="3" y1="22" x2="21" y2="22"/>
                        <line x1="6" y1="18" x2="6" y2="11"/>
                        <line x1="10" y1="18" x2="10" y2="11"/>
                        <line x1="14" y1="18" x2="14" y2="11"/>
                        <line x1="18" y1="18" x2="18" y2="11"/>
                        <polygon points="12 2 20 7 4 7"/>
                      </template>
                      <template v-else-if="themeIcon(space.sub_theme) === 'cross'">
                        <rect x="9" y="2" width="6" height="20" rx="1"/>
                        <rect x="2" y="9" width="20" height="6" rx="1"/>
                      </template>
                      <template v-else>
                        <rect x="4" y="2" width="16" height="20" rx="2"/>
                        <path d="M9 22v-4h6v4"/>
                        <path d="M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/>
                      </template>
                    </component>
                  </div>
                  <div class="space-titles">
                    <div class="space-name-row">
                      <h3 class="space-name" :style="{ fontSize: scaledPx(idx === 0 ? 28 : 22) }">{{ space.name }}</h3>
                      <span class="welcoming-badge">
                        <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>
                        Welcoming Space
                      </span>
                    </div>
                    <p class="space-sub-theme">{{ space.sub_theme || space.theme }}</p>
                    <p class="space-distance">
                      <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>
                      {{ space.distance_km?.toFixed(2) }} km away
                      <span v-if="space.suburb_name"> · {{ space.suburb_name }}</span>
                    </p>
                  </div>
                </div>

                <div class="what-to-expect">
                  <p class="expect-label">What to expect</p>
                  <p class="expect-text" :style="{ fontSize: scaledPx(14) }">{{ getExpectText(space.sub_theme, space.theme) }}</p>
                </div>

                <div class="space-tags">
                  <span class="space-tag tag-free">
                    <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>
                    Free to enter
                  </span>
                  <span class="space-tag tag-welcoming">
                    <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                    Officially welcoming
                  </span>
                  <span v-if="space.sub_theme" class="space-tag tag-type">{{ space.sub_theme }}</span>
                </div>

                <div class="space-actions">
                  <button class="action-btn primary" @click="planJourneyTo(space)">
                    Get directions
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
                  </button>
                  <button class="action-btn outline" @click="findEventsNear(space)">
                    Events nearby
                  </button>
                </div>
              </article>
            </div>
          </div>
        </section>

        <!-- ═══ NO RESULTS — fallback CTA ═══ -->
        <section v-else class="no-results-band">
          <div class="no-results-inner">
            <div class="no-results-card">
              <div class="nr-icon">
                <svg viewBox="0 0 24 24" width="56" height="56" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <rect x="4" y="2" width="16" height="20" rx="2"/>
                  <path d="M9 22v-4h6v4"/>
                  <path d="M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01"/>
                </svg>
              </div>
              <h3 :style="{ fontSize: scaledPx(26) }">No welcoming spaces found within {{ searchRadius }}km</h3>
              <p :style="{ fontSize: scaledPx(15) }">
                Welcoming Spaces are City of Melbourne designated locations, so they are concentrated in the inner suburbs.
                Try setting your location to <strong>Fitzroy, Carlton, Melbourne CBD,</strong> or <strong>Southbank</strong>.
              </p>
              <button v-if="searchRadius < 5" class="retry-btn" @click="expandSearch">
                Search within 5km instead
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
              </button>
            </div>
          </div>
        </section>

        <!-- ═══ OTHER COMMUNITY SPACES (always shown when we have any) ═══ -->
        <section v-if="communityLandmarks.length" class="community-band" data-reveal>
          <div class="community-inner">
            <div class="community-header">
              <p class="section-label">Also nearby</p>
              <h2 class="section-heading" :style="{ fontSize: scaledPx(32) }">
                Other community spaces<br><em>nearby</em>
              </h2>
              <p class="section-sub" :style="{ fontSize: scaledPx(15) }">
                Not officially designated as Welcoming Spaces, but still open, free, and community-focused.
              </p>
            </div>

            <div class="community-list">
              <button
                v-for="lm in communityLandmarks"
                :key="lm.landmark_id || lm.name"
                class="community-row"
                @click="planJourneyTo(lm)"
              >
                <div class="cr-icon">
                  <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <rect x="4" y="2" width="16" height="20" rx="2"/>
                    <path d="M9 22v-4h6v4"/>
                    <path d="M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01"/>
                  </svg>
                </div>
                <div class="cr-info">
                  <span class="cr-name" :style="{ fontSize: scaledPx(15) }">{{ lm.name }}</span>
                  <span class="cr-meta">
                    {{ lm.sub_theme || lm.theme }} · {{ lm.distance_km?.toFixed(2) }} km
                  </span>
                </div>
                <span class="cr-arrow">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
                </span>
              </button>
            </div>
          </div>
        </section>

        <!-- ═══ TIPS BAND ═══ -->
        <section class="tips-band" data-reveal>
          <div class="tips-inner">
            <div class="tips-header">
              <p class="section-label">Helpful guidance</p>
              <h2 class="section-heading" :style="{ fontSize: scaledPx(36) }">
                Tips for your<br><em>first visit</em>
              </h2>
            </div>

            <div class="tips-grid">
              <article class="tip-card">
                <div class="tip-icon mint">
                  <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M18 8h1a4 4 0 0 1 0 8h-1"/>
                    <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/>
                    <line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/>
                  </svg>
                </div>
                <h3 :style="{ fontSize: scaledPx(18) }">Go at your own pace</h3>
                <p :style="{ fontSize: scaledPx(14) }">You don't need to join anything. Just arriving and sitting quietly is enough — welcoming spaces are judgment-free zones.</p>
              </article>
              <article class="tip-card">
                <div class="tip-icon yellow">
                  <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                </div>
                <h3 :style="{ fontSize: scaledPx(18) }">Quieter in the mornings</h3>
                <p :style="{ fontSize: scaledPx(14) }">Libraries and community centres are usually less busy between 9am and 11am on weekdays.</p>
              </article>
              <article class="tip-card">
                <div class="tip-icon purple">
                  <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                  </svg>
                </div>
                <h3 :style="{ fontSize: scaledPx(18) }">Staff are there to help</h3>
                <p :style="{ fontSize: scaledPx(14) }">You can always ask staff about free programs, events, or just for a chat — that's what welcoming spaces are for.</p>
              </article>
            </div>
          </div>
        </section>

        <!-- ═══ BOTTOM NAV ═══ -->
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
            <RouterLink to="/discover" class="bnav-btn">
              Browse events
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
            </RouterLink>
          </div>
        </section>
      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { resonanceStore } from '../stores/resonanceStore'
import { useResonanceApi } from '../composables/useResonanceApi'
import BestTimeNav from '../components/BestTimeNav.vue'
import BestTimeLocationBar from '../components/BestTimeLocationBar.vue'

const store = resonanceStore
const router = useRouter()
const { fetchWelcomingSpaces } = useResonanceApi()

const textScale = ref(100)
const scaledPx = (base) => `${(base * textScale.value) / 100}px`

const loading = ref(false)
const allLandmarks = ref([])
const searchRadius = ref(2)

const welcomingSpaces = computed(() => allLandmarks.value.filter(l => l.is_welcoming_space === true))
const communityLandmarks = computed(() =>
  allLandmarks.value.filter(l => !l.is_welcoming_space).slice(0, 6)
)

function themeIcon(subTheme) {
  const s = (subTheme || '').toLowerCase()
  if (s.includes('library'))           return 'library'
  if (s.includes('community centre'))  return 'home'
  if (s.includes('civic') || s.includes('hall')) return 'landmark'
  if (s.includes('health'))            return 'cross'
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
  const lat = space.lat ?? space.latitude
  const lon = space.lng ?? space.lon ?? space.longitude
  if (lat == null || lon == null) return
  router.push({
    path: '/results',
    query: { to_lat: lat, to_lon: lon, place: space.name }
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
  const { userLat: lat, userLon: lon } = store
  try {
    const data = await fetchWelcomingSpaces(lat, lon, searchRadius.value, 25)
    const list = Array.isArray(data) ? data : (data?.landmarks || data?.results || [])
    allLandmarks.value = list
    store.welcomingSpaces = list.filter(l => l.is_welcoming_space === true)
  } catch {
    allLandmarks.value = []
  } finally {
    loading.value = false
    setTimeout(setupReveal, 80)
  }
}

watch(() => store.locationReady, (r) => { if (r) { searchRadius.value = 2; loadAll() } })
watch(() => [store.userLat, store.userLon], () => {
  if (store.locationReady) { searchRadius.value = 2; loadAll() }
})

let revealObserver = null
function setupReveal() {
  if (revealObserver) revealObserver.disconnect()
  revealObserver = new IntersectionObserver(
    es => es.forEach(e => { if (e.isIntersecting) e.target.classList.add('in-view') }),
    { threshold: 0.1 }
  )
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

.welcoming-page {
  min-height: 100vh; background: #f2faf0; color: #1a2e1e;
  font-family: system-ui, sans-serif; position: relative; overflow-x: hidden;
}

.noise {
  position: fixed; inset: 0; z-index: 1000; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  background-size: 180px; opacity: 0.45;
}
.orb { position: fixed; border-radius: 50%; pointer-events: none; z-index: 0; filter: blur(80px); }
.orb-1 { width: 500px; height: 500px; background: rgba(70,140,80,0.18); top: -100px; left: -80px; animation: orb-drift 22s ease-in-out infinite alternate; }
.orb-2 { width: 380px; height: 380px; background: rgba(245,200,18,0.10); bottom: 5%; right: -60px; animation: orb-drift 28s ease-in-out infinite alternate-reverse; }
@keyframes orb-drift { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(40px,50px) scale(1.1)} }

/* a11y bar */
.a11y-bar { position: fixed; top: 86px; right: 0; left: 0; z-index: 95; background: rgba(255,255,255,0.92); backdrop-filter: blur(14px); border-bottom: 1px solid rgba(29,113,105,0.08); }
.a11y-inner { display: flex; align-items: center; justify-content: flex-end; padding: 8px 52px; }
.text-size-control { display: inline-flex; align-items: center; gap: 12px; background: rgba(255,255,255,0.9); border: 1.5px solid rgba(29,113,105,0.18); border-radius: 999px; padding: 6px 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.06); }
.a-small { font-family: Georgia,serif; font-size: 12px; font-weight: 700; color: #2a6a30; }
.a-large { font-family: Georgia,serif; font-size: 19px; font-weight: 700; color: #2a6a30; }
.text-slider { -webkit-appearance: none; appearance: none; width: 110px; height: 4px; background: #d0e8d4; border-radius: 999px; outline: none; cursor: pointer; }
.text-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 18px; height: 18px; border-radius: 50%; background: #2a6a30; cursor: pointer; }
.scale-pct { font-size: 12px; font-weight: 700; color: #6a8e6e; min-width: 34px; }

:global(.bt-loc-bar) { top: 130px !important; }

/* ═══ HERO — forest green ═══ */
.hero {
  position: relative; overflow: hidden;
  background: linear-gradient(160deg, #2a6a30 0%, #1e5226 100%);
  padding: 220px 52px 90px;
  color: white;
}
.hero-bg-word {
  position: absolute; right: -2%; top: 50%; transform: translateY(-50%);
  font-family: Georgia,serif; font-size: clamp(140px, 20vw, 260px);
  font-weight: 700; font-style: italic; color: rgba(255,255,255,0.07);
  white-space: nowrap; pointer-events: none; user-select: none; letter-spacing: -0.04em;
}
.hero-leaves { position: absolute; inset: 0; pointer-events: none; opacity: 0.7; }
.hero-inner { position: relative; z-index: 2; max-width: 1500px; margin: 0 auto; }

.back-btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 8px 18px; background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.25); border-radius: 999px;
  color: white; font-size: 13px; font-weight: 700; text-decoration: none;
  margin-bottom: 24px; transition: background 0.2s;
}
.back-btn:hover { background: rgba(255,255,255,0.28); }

.hero-eyebrow { display: inline-flex; align-items: center; gap: 12px; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: rgba(255,255,255,0.85); margin-bottom: 22px; }
.eyebrow-line { display: block; width: 32px; height: 1px; background: rgba(255,255,255,0.85); }
.hero-headline { font-family: Georgia,serif; font-size: clamp(46px, 6vw, 88px); font-weight: 700; line-height: 1.04; color: white; margin-bottom: 18px; }
.hero-headline em { color: #f5c812; font-style: italic; }
.hero-sub { font-family: system-ui,sans-serif; color: rgba(255,255,255,0.88); line-height: 1.6; max-width: 680px; }

/* ═══ EXPLAINER BAND ═══ */
.explainer-band {
  background: #edf7ec;
  padding: 24px 52px;
  border-bottom: 1px solid rgba(42,106,48,0.18);
}
.explainer-inner {
  max-width: 1500px; margin: 0 auto;
  display: flex; align-items: flex-start; gap: 16px;
}
.explainer-icon {
  width: 40px; height: 40px; border-radius: 12px;
  background: rgba(42,106,48,0.12); color: #1e5226;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.explainer-text { flex: 1; min-width: 0; }
.explainer-label { font-family: system-ui,sans-serif; font-size: 12px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: #2a6a30; margin-bottom: 4px; }
.explainer-text p:last-child { font-family: system-ui,sans-serif; color: #1e3a26; line-height: 1.6; }

/* ═══ EMPTY / LOADING ═══ */
.empty-band, .loading-band { padding: 80px 52px; }
.empty-card {
  display: flex; flex-direction: column; align-items: center; gap: 14px;
  text-align: center; max-width: 600px; margin: 0 auto;
  padding: 60px 40px; background: white;
  border: 1px solid rgba(42,106,48,0.14); border-radius: 24px;
  box-shadow: 0 8px 28px rgba(0,0,0,0.04);
}
.empty-card h3 { font-family: Georgia,serif; color: #0f1e12; font-weight: 700; }
.empty-card p { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.6; }

.loading-band { display: flex; flex-direction: column; align-items: center; gap: 18px; }
.big-spinner { width: 44px; height: 44px; border-radius: 50%; border: 4px solid rgba(42,106,48,0.18); border-top-color: #2a6a30; animation: spin 0.8s linear infinite; }
.loading-band p { font-family: system-ui,sans-serif; color: #4a6a4e; font-weight: 600; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ═══ SPACES BAND ═══ */
.spaces-band {
  background: white;
  padding: 80px 52px;
  border-bottom: 1px solid rgba(42,106,48,0.12);
  opacity: 0; transform: translateY(40px);
  transition: all 0.9s cubic-bezier(0.22,1,0.36,1);
}
.spaces-band.in-view { opacity: 1; transform: none; }
.spaces-inner { max-width: 1500px; margin: 0 auto; }
.spaces-header { max-width: 760px; margin-bottom: 44px; }
.section-label { font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #2a6a30; margin-bottom: 14px; }
.section-heading { font-family: Georgia,serif; font-weight: 700; line-height: 1.06; color: #0f1e12; margin-bottom: 14px; }
.section-heading em { color: #2a6a30; font-style: italic; }
.section-sub { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.65; }

.spaces-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}
/* First card spans 2 columns when there's room */
.space-card-feature { grid-column: span 2; }
@media (max-width: 900px) { .space-card-feature { grid-column: auto; } }

.space-card {
  position: relative;
  background: white; border: 1px solid rgba(42,106,48,0.14);
  border-radius: 22px; padding: 30px;
  display: flex; flex-direction: column; gap: 18px;
  transition: transform 0.3s cubic-bezier(0.22,1,0.36,1), box-shadow 0.3s, border-color 0.3s;
  opacity: 0; transform: translateY(20px);
  animation: card-in 0.6s calc(var(--i) * 80ms) forwards;
}
@keyframes card-in { to { opacity: 1; transform: none; } }
.space-card:hover { transform: translateY(-3px); box-shadow: 0 18px 44px rgba(42,106,48,0.14); border-color: rgba(42,106,48,0.25); }

.space-card-feature {
  background: linear-gradient(135deg, #edf7ec 0%, white 60%);
  border-color: rgba(42,106,48,0.3);
  box-shadow: 0 16px 40px rgba(42,106,48,0.12);
}
.space-card-feature::before {
  content: ''; position: absolute; left: 0; top: 26px; bottom: 26px;
  width: 5px; border-radius: 0 4px 4px 0;
  background: linear-gradient(180deg, #2a6a30, #f5c812);
}

.space-head { display: flex; align-items: flex-start; gap: 16px; }
.space-icon-wrap {
  width: 50px; height: 50px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.bg-community { background: #edf7ec; color: #1e5226; }
.bg-health    { background: #ffe8d8; color: #a04a1a; }
.bg-leisure   { background: #d6f4e7; color: #1d7169; }
.bg-education { background: #e8e8ff; color: #2a2ab0; }
.bg-default   { background: #f0f0f8; color: #4a6a4e; }

.space-titles { flex: 1; min-width: 0; }
.space-name-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 6px; }
.space-name { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1.15; }

.welcoming-badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 12px; border-radius: 999px;
  background: #edf7ec; color: #1e5226;
  font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800;
  letter-spacing: 0.04em; text-transform: uppercase;
  white-space: nowrap;
}

.space-sub-theme { font-family: system-ui,sans-serif; font-size: 14px; color: #6a8e6e; font-weight: 700; margin-bottom: 4px; }
.space-distance { font-family: system-ui,sans-serif; font-size: 13px; color: #6a8e6e; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.space-distance svg { color: #2a6a30; }

.what-to-expect {
  padding: 16px 18px; background: #f6faf3;
  border-radius: 14px; border: 1px solid rgba(42,106,48,0.1);
}
.space-card-feature .what-to-expect { background: rgba(42,106,48,0.06); border-color: rgba(42,106,48,0.18); }
.expect-label { font-family: system-ui,sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: #2a6a30; margin-bottom: 6px; }
.expect-text { font-family: system-ui,sans-serif; color: #1e3a26; line-height: 1.6; }

.space-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.space-tag { display: inline-flex; align-items: center; gap: 5px; padding: 5px 12px; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700; }
.tag-free      { background: #f0f8e8; color: #3a6a10; }
.tag-welcoming { background: #edf7ec; color: #2a6a30; }
.tag-type      { background: #f0f0f8; color: #4a6a4e; }

.space-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 4px; }
.action-btn {
  flex: 1; min-width: 140px;
  display: inline-flex; align-items: center; justify-content: center; gap: 7px;
  padding: 13px 18px; border-radius: 12px;
  font-family: system-ui,sans-serif; font-size: 14px; font-weight: 700;
  cursor: pointer; transition: all 0.2s;
  border: none;
}
.action-btn.primary { background: linear-gradient(135deg, #2a6a30, #1e5226); color: white; box-shadow: 0 10px 24px rgba(42,106,48,0.28); }
.action-btn.primary:hover { transform: translateY(-2px); box-shadow: 0 14px 32px rgba(42,106,48,0.36); }
.action-btn.outline { background: white; color: #2a6a30; border: 1.5px solid rgba(42,106,48,0.3); }
.action-btn.outline:hover { background: #2a6a30; color: white; border-color: #2a6a30; }

/* ═══ NO RESULTS BAND ═══ */
.no-results-band {
  background: white;
  padding: 80px 52px;
  border-bottom: 1px solid rgba(42,106,48,0.12);
}
.no-results-inner { max-width: 720px; margin: 0 auto; }
.no-results-card {
  display: flex; flex-direction: column; align-items: center; gap: 16px;
  text-align: center; padding: 60px 40px;
  background: linear-gradient(135deg, #edf7ec 0%, white 60%);
  border: 1.5px solid rgba(42,106,48,0.25);
  border-radius: 24px;
}
.nr-icon { color: #2a6a30; }
.no-results-card h3 { font-family: Georgia,serif; color: #0f1e12; font-weight: 700; }
.no-results-card p { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.6; max-width: 520px; }
.no-results-card strong { color: #2a6a30; }
.retry-btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 13px 24px; background: linear-gradient(135deg, #2a6a30, #1e5226); color: white;
  border: none; border-radius: 12px;
  font-family: system-ui,sans-serif; font-size: 14px; font-weight: 700;
  cursor: pointer; transition: all 0.2s;
  box-shadow: 0 10px 24px rgba(42,106,48,0.3);
  margin-top: 8px;
}
.retry-btn:hover { transform: translateY(-2px); box-shadow: 0 14px 32px rgba(42,106,48,0.4); }

/* ═══ COMMUNITY BAND ═══ */
.community-band {
  background: linear-gradient(180deg, #faf8f0 0%, #f4f8e8 100%);
  padding: 80px 52px;
  border-bottom: 1px solid rgba(42,106,48,0.12);
  opacity: 0; transform: translateY(40px);
  transition: all 0.9s cubic-bezier(0.22,1,0.36,1);
}
.community-band.in-view { opacity: 1; transform: none; }
.community-inner { max-width: 1500px; margin: 0 auto; }
.community-header { max-width: 720px; margin-bottom: 36px; }

.community-list {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 12px;
}
.community-row {
  display: grid; grid-template-columns: 44px 1fr 32px;
  gap: 14px; align-items: center;
  padding: 16px 20px;
  background: white;
  border: 1px solid rgba(42,106,48,0.12);
  border-radius: 14px;
  font-family: system-ui,sans-serif;
  cursor: pointer;
  text-align: left;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}
.community-row:hover { transform: translateY(-2px); box-shadow: 0 12px 28px rgba(42,106,48,0.12); border-color: rgba(42,106,48,0.3); }

.cr-icon { width: 44px; height: 44px; border-radius: 12px; background: #edf7ec; color: #1e5226; display: flex; align-items: center; justify-content: center; }
.cr-info { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.cr-name { font-weight: 700; color: #0f1e12; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cr-meta { font-size: 13px; color: #6a8e6e; font-weight: 600; }
.cr-arrow { width: 32px; height: 32px; border-radius: 50%; background: #f6faf3; color: #2a6a30; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }
.community-row:hover .cr-arrow { background: #2a6a30; color: white; }

/* ═══ TIPS BAND ═══ */
.tips-band {
  background: linear-gradient(180deg, #edf7ec 0%, #d6e8d8 100%);
  padding: 90px 52px;
  border-bottom: 1px solid rgba(42,106,48,0.14);
  opacity: 0; transform: translateY(40px);
  transition: all 0.9s cubic-bezier(0.22,1,0.36,1);
}
.tips-band.in-view { opacity: 1; transform: none; }
.tips-inner { max-width: 1500px; margin: 0 auto; }
.tips-header { max-width: 600px; margin-bottom: 40px; }

.tips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 18px;
}
.tip-card {
  background: white; border: 1px solid rgba(42,106,48,0.12);
  border-radius: 18px; padding: 28px;
  display: flex; flex-direction: column; gap: 14px;
  transition: transform 0.3s, box-shadow 0.3s;
}
.tip-card:hover { transform: translateY(-3px); box-shadow: 0 14px 36px rgba(42,106,48,0.12); }

.tip-icon {
  width: 52px; height: 52px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  position: relative;
}
.tip-icon::before { content: ''; position: absolute; inset: -4px; border: 1.5px solid currentColor; border-radius: 14px; opacity: 0.18; }
.tip-icon.mint   { background: #d6f4e7; color: #1d7169; }
.tip-icon.yellow { background: #fff3c2; color: #b88a00; }
.tip-icon.purple { background: #e6dcff; color: #5b3fb6; }

.tip-card h3 { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; line-height: 1.2; }
.tip-card p { font-family: system-ui,sans-serif; color: #4a6a4e; line-height: 1.55; }

/* ═══ BOTTOM NAV ═══ */
.bottom-nav-band { padding: 50px 52px 80px; background: #f2faf0; }
.bottom-nav-inner { max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }
.bnav-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 10px;
  padding: 18px 24px; border-radius: 14px;
  background: white; border: 1.5px solid rgba(42,106,48,0.2);
  color: #1a2e1e; font-family: system-ui,sans-serif; font-weight: 700;
  text-decoration: none; transition: all 0.25s;
}
.bnav-btn:hover { border-color: #2a6a30; color: #2a6a30; }
.bnav-btn.primary {
  background: linear-gradient(135deg, #2a6a30, #1e5226); color: white;
  border-color: transparent;
  box-shadow: 0 12px 28px rgba(42,106,48,0.3);
}
.bnav-btn.primary:hover { color: white; transform: translateY(-2px); box-shadow: 0 16px 36px rgba(42,106,48,0.38); }

@media (max-width: 980px) {
  .hero { padding: 280px 20px 70px; }
  .a11y-inner { padding: 8px 20px; }
  .explainer-band, .spaces-band, .no-results-band, .community-band, .tips-band { padding-left: 20px; padding-right: 20px; }
  .empty-band, .loading-band { padding: 60px 20px; }
  .spaces-band { padding: 60px 20px; }
  .community-band, .tips-band { padding: 60px 20px; }
  .bottom-nav-band { padding: 40px 20px 70px; }
  .bottom-nav-inner { grid-template-columns: 1fr; }
  .space-card { padding: 24px 22px; }
  .no-results-card { padding: 40px 24px; }
  .explainer-inner { padding: 0; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
</style>