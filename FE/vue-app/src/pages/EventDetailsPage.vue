<template>
  <div class="details-page">
    <div class="noise" aria-hidden="true"></div>
    <div class="orb orb-1" aria-hidden="true"></div>
    <div class="orb orb-2" aria-hidden="true"></div>

    <nav class="nav" :class="{ scrolled: scrollY > 60 }">
      <div class="nav-brand">
        <div class="nav-logo">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/>
            <circle cx="12" cy="10" r="2.5"/>
          </svg>
        </div>
        <span class="nav-wordmark"><em>Connect</em>Local</span>
      </div>
      <div class="nav-links" role="navigation" aria-label="Main navigation">
        <RouterLink to="/home">Home</RouterLink>
        <RouterLink to="/discover">Events</RouterLink>

        <RouterLink to="/best-time">Best Time</RouterLink>
      </div>
      <RouterLink to="/checkin" class="nav-cta" aria-label="Start your wellbeing check-in">
        Start Check-in
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M5 12h14M13 5l7 7-7 7"/>
        </svg>
      </RouterLink>
    </nav>



    <div v-if="isLoading" class="state-wrap">
      <div class="state-card" role="status" aria-live="polite">
        <div class="spinner" aria-hidden="true"></div>
        <p :style="{ fontSize: scaledPx(18) }">Loading event details…</p>
      </div>
    </div>

    <div v-else-if="loadError" class="state-wrap">
      <div class="state-card state-error" role="alert">
        <svg viewBox="0 0 24 24" width="36" height="36" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 8v4M12 16h.01"/>
        </svg>
        <p :style="{ fontSize: scaledPx(18) }">{{ loadError }}</p>
      </div>
    </div>

    <template v-else-if="event">
      <header class="hero">
        <div class="hero-bg-word" aria-hidden="true">EVENT</div>
        <div class="hero-inner">
          <RouterLink class="back-btn" to="/discover" aria-label="Back to activities list">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M15 18l-6-6 6-6"/>
            </svg>
            Back to activities
          </RouterLink>
          <div class="tags" role="list">
            <span class="tag tag-price" role="listitem" :style="{ fontSize: scaledPx(13) }">{{ priceText }}</span>
            <span v-if="event.category" class="tag tag-category" role="listitem" :style="{ fontSize: scaledPx(13) }">{{ event.category }}</span>
          </div>
          <h1 class="hero-title" :style="{ fontSize: scaledPx(64) }">{{ event.name }}</h1>
          <p v-if="event.source" class="hero-organiser" :style="{ fontSize: scaledPx(17) }">by {{ event.source }}</p>
        </div>
      </header>

      <main class="content" id="main-content">
        <div class="info-card" data-reveal>
          <div class="info-row">
            <div class="info-icon mint" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2"/>
                <path d="M16 2v4M8 2v4M3 10h18"/>
              </svg>
            </div>
            <div>
              <p class="info-label" :style="{ fontSize: scaledPx(12) }">Date and Time</p>
              <p class="info-value" :style="{ fontSize: scaledPx(18) }">{{ dateTimeText }}</p>
            </div>
          </div>
          <div class="info-divider" aria-hidden="true"></div>
          <div class="info-row">
            <div class="info-icon yellow" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/>
                <circle cx="12" cy="10" r="2.5"/>
              </svg>
            </div>
            <div>
              <p class="info-label" :style="{ fontSize: scaledPx(12) }">Venue</p>
              <p class="info-value" :style="{ fontSize: scaledPx(18) }">{{ venueText }}</p>
            </div>
          </div>
          <div class="info-divider" aria-hidden="true"></div>
          <div class="info-row">
            <div class="info-icon purple" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3"/>
                <path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>
              </svg>
            </div>
            <div>
              <p class="info-label" :style="{ fontSize: scaledPx(12) }">Distance from you</p>
              <p class="info-value" :style="{ fontSize: scaledPx(18) }">{{ distanceText }}</p>
            </div>
          </div>
          <div class="info-divider" aria-hidden="true"></div>
          <div class="info-row">
            <div class="info-icon pink" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
            </div>
            <div>
              <p class="info-label" :style="{ fontSize: scaledPx(12) }">Restrictions</p>
              <p class="info-value" :style="{ fontSize: scaledPx(18) }">{{ restrictionsText }}</p>
            </div>
          </div>
        </div>

        <div v-if="event.image_url" class="image-card" data-reveal>
          <img :src="event.image_url" :alt="event.name" />
        </div>

        <div class="about-card" data-reveal>
          <p class="section-label" :style="{ fontSize: scaledPx(12) }">About this activity</p>
          <p class="about-text" :style="{ fontSize: scaledPx(17) }">{{ event.description || 'Activity details are not available yet.' }}</p>
        </div>

        <div class="actions" data-reveal>
          <button class="btn-primary" type="button" @click="goToJourney" :style="{ fontSize: scaledPx(16) }">
            I would like to go — show me how to get there
          </button>
          <a v-if="event.url" class="btn-primary" :href="event.url" target="_blank" rel="noopener noreferrer" :style="{ fontSize: scaledPx(16) }">Open original event page</a>
          <RouterLink to="/discover" class="btn-secondary" :style="{ fontSize: scaledPx(16) }">Back to activities</RouterLink>
        </div>
      </main>
    </template>

  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const BASE_URL = import.meta.env.VITE_ACTIVITIES_API_URL || 'https://connectlocal.duckdns.org'

const event = ref(null)
const isLoading = ref(false)
const loadError = ref('')
const scrollY = ref(0)
import { uiStore } from '../stores/uiStore'
const scaledPx = (base) => `${(base * uiStore.textScale) / 100}px`
const handleScroll = () => { scrollY.value = window.scrollY }

let observer = null
function setupReveal() {
  observer = new IntersectionObserver(
    entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in-view') }),
    { threshold: 0.1 }
  )
  document.querySelectorAll('[data-reveal]').forEach(el => observer.observe(el))
}

const n = (value) => (Number.isFinite(+value) ? +value : null)

const buildEventDetailUrl = () => {
  const url = new URL(`${BASE_URL}/api/events/${route.params.id}`)
  if (route.query.lat && route.query.lon) {
    url.searchParams.set('lat', route.query.lat)
    url.searchParams.set('lon', route.query.lon)
  }
  return url
}

const fetchEventDetail = async () => {
  isLoading.value = true
  loadError.value = ''
  try {
    const response = await fetch(buildEventDetailUrl().toString())
    if (!response.ok) throw new Error(`Failed (${response.status})`)
    event.value = await response.json()
    setTimeout(() => setupReveal(), 100)
  } catch {
    loadError.value = 'Unable to load this event right now. Please try again later.'
    event.value = null
  } finally {
    isLoading.value = false
  }
}

const priceText = computed(() => {
  if (!event.value) return ''
  if (event.value.is_free) return 'Free'
  const price = n(event.value.min_price)
  return price == null ? 'Paid' : `From $${price}`
})
const dateTimeText = computed(() => {
  if (!event.value) return 'Date and time TBC'
  return event.value.session_datetime_summary || event.value.datetime_summary || 'Date and time TBC'
})
const venueText = computed(() => {
  if (!event.value) return 'Venue TBC'
  const venue = event.value.venue || 'Venue TBC'
  const suburb = event.value.suburb || ''
  return suburb ? `${venue}, ${suburb}` : venue
})
const distanceText = computed(() => {
  if (!event.value) return 'Distance unavailable'
  const distance = n(event.value.distance_km)
  return distance == null ? 'Distance unavailable' : `${distance.toFixed(1)} km`
})
const restrictionsText = computed(() => {
  if (!event.value) return 'No restrictions listed'
  return event.value.restrictions || 'No restrictions listed'
})

const goToJourney = () => {
  if (!event.value) return

  const destination =
    event.value.location_summary ||
    event.value.address ||
    venueText.value

  router.push({
    path: '/journey',
    query: destination ? { destination } : {}
  })
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  fetchEventDetail()
})
onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
  if (observer) observer.disconnect()
})
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.details-page {
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
.orb-2 { width: 380px; height: 380px; background: rgba(255,180,140,0.12); bottom: 5%; right: -60px; animation: orb-drift 28s ease-in-out infinite alternate-reverse; }
@keyframes orb-drift { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(40px,50px) scale(1.1)} }

.nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 24px 52px; transition: background 0.4s, padding 0.4s, box-shadow 0.4s;
}
.nav.scrolled { background: rgba(242,250,240,0.9); backdrop-filter: blur(18px); padding: 16px 52px; box-shadow: 0 1px 0 rgba(29,113,105,0.12); }
.nav-brand { display: flex; align-items: center; gap: 12px; }
.nav-logo { width: 38px; height: 38px; border-radius: 50%; background: linear-gradient(135deg,#0a9b8a,#056b5e); color: white; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 16px rgba(7,141,127,0.3); }
.nav-wordmark { font-family: Georgia,serif; font-size: 20px; color: #1a2e1e; }
.nav-wordmark em { color: #0a9b8a; font-style: italic; }
.nav-links { display: flex; gap: 32px; align-items: center; }
.nav-links a { font-size: 15px; font-weight: 600; color: #3a5a3e; text-decoration: none; transition: color 0.2s; }
.nav-links a:hover { color: #0a9b8a; }
.nav-links .router-link-active { color: #0a9b8a; }
.nav-links a:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 3px; border-radius: 3px; }
.nav-link-coming { color: #3a5a3e; font-size: 15px; font-weight: 600; cursor: default; font-family: system-ui,sans-serif; }
.nav-cta { display: inline-flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 700; color: #0a9b8a; text-decoration: none; padding: 10px 22px; border: 1.5px solid #0a9b8a; border-radius: 999px; transition: all 0.3s; }
.nav-cta:hover { background: #0a9b8a; color: white; }
.nav-cta:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 3px; }

.state-wrap { display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 20px; }
.state-card { display: flex; flex-direction: column; align-items: center; gap: 16px; text-align: center; background: white; border: 1px solid rgba(29,113,105,0.12); border-radius: 20px; padding: 60px 40px; max-width: 480px; width: 100%; color: #4a6a4e; font-size: 18px; font-weight: 500; }
.state-error { border-color: rgba(180,50,50,0.2); color: #8b2020; }
.spinner { width: 36px; height: 36px; border-radius: 50%; border: 3px solid rgba(10,155,138,0.2); border-top-color: #0a9b8a; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.hero {
  position: relative; overflow: hidden;
  background: linear-gradient(160deg, #e4f5e0 0%, #c8edc8 100%);
  padding: 60px 52px 80px; border-bottom: 1px solid rgba(29,113,105,0.12); margin-top: 160px;
}
.hero-bg-word { position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%); font-family: Georgia,serif; font-size: clamp(100px,16vw,200px); font-weight: 700; font-style: italic; color: rgba(10,155,138,0.055); white-space: nowrap; pointer-events: none; user-select: none; letter-spacing: -0.04em; }
.hero-inner { position: relative; z-index: 2; max-width: 900px; }
.back-btn { display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px; border-radius: 999px; background: rgba(255,255,255,0.7); backdrop-filter: blur(8px); border: 1px solid rgba(29,113,105,0.18); color: #0a9b8a; font-size: 14px; font-weight: 700; text-decoration: none; margin-bottom: 32px; transition: all 0.25s; }
.back-btn:hover { background: white; }
.back-btn:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 3px; }
.tags { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
.tag { display: inline-flex; align-items: center; padding: 6px 16px; border-radius: 999px; font-size: 13px; font-weight: 700; }
.tag-price { background: #0a9b8a; color: white; }
.tag-category { background: rgba(255,255,255,0.7); border: 1px solid rgba(29,113,105,0.2); color: #1a2e1e; }
.hero-title { font-family: Georgia,serif; font-size: clamp(32px,5vw,64px); font-weight: 700; line-height: 1.1; color: #0f1e12; margin-bottom: 12px; }
.hero-organiser { font-size: 17px; color: #4a6a4e; font-weight: 500; }

.content { position: relative; z-index: 2; max-width: 860px; margin: 0 auto; padding: 48px 52px 100px; display: flex; flex-direction: column; gap: 24px; }

.info-card { background: white; border: 1px solid rgba(29,113,105,0.12); border-radius: 20px; padding: 36px; box-shadow: 0 8px 28px rgba(0,0,0,0.05); opacity: 0; transform: translateY(24px); transition: opacity 0.7s cubic-bezier(0.22,1,0.36,1), transform 0.7s cubic-bezier(0.22,1,0.36,1); }
.info-card.in-view { opacity: 1; transform: none; }
.info-row { display: flex; align-items: flex-start; gap: 20px; }
.info-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.mint   { background: #d6f4e7; color: #0a6b55; }
.yellow { background: #fff3c2; color: #8a6600; }
.purple { background: #ede8ff; color: #4a3db6; }
.pink   { background: #ffded5; color: #c44a2c; }
.info-label { font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #6a8e6e; margin-bottom: 6px; }
.info-value { font-size: 17px; font-weight: 600; color: #0f1e12; line-height: 1.4; }
.info-divider { height: 1px; background: rgba(29,113,105,0.1); margin: 20px 0; }

.image-card { border-radius: 20px; overflow: hidden; border: 1px solid rgba(29,113,105,0.1); box-shadow: 0 8px 28px rgba(0,0,0,0.05); opacity: 0; transform: translateY(24px); transition: opacity 0.7s 0.1s cubic-bezier(0.22,1,0.36,1), transform 0.7s 0.1s cubic-bezier(0.22,1,0.36,1); }
.image-card.in-view { opacity: 1; transform: none; }
.image-card img { display: block; width: 100%; max-height: 440px; object-fit: cover; }

.about-card { background: white; border: 1px solid rgba(29,113,105,0.12); border-radius: 20px; padding: 36px; box-shadow: 0 8px 28px rgba(0,0,0,0.05); opacity: 0; transform: translateY(24px); transition: opacity 0.7s 0.15s cubic-bezier(0.22,1,0.36,1), transform 0.7s 0.15s cubic-bezier(0.22,1,0.36,1); }
.about-card.in-view { opacity: 1; transform: none; }
.section-label { font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 14px; }
.about-text { font-size: 17px; line-height: 1.75; color: #2a4a2e; }

.actions { display: flex; gap: 14px; flex-wrap: wrap; opacity: 0; transform: translateY(24px); transition: opacity 0.7s 0.2s cubic-bezier(0.22,1,0.36,1), transform 0.7s 0.2s cubic-bezier(0.22,1,0.36,1); }
.actions.in-view { opacity: 1; transform: none; }

.btn-primary { display: inline-flex; align-items: center; gap: 10px; padding: 16px 28px; border-radius: 12px; background: linear-gradient(135deg,#0a9b8a,#056b5e); color: white; font-size: 16px; font-weight: 700; text-decoration: none; font-family: system-ui,sans-serif; box-shadow: 0 10px 28px rgba(10,155,138,0.28); transition: all 0.3s cubic-bezier(0.22,1,0.36,1); }
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 18px 36px rgba(10,155,138,0.38); }
.btn-primary:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 3px; }

.btn-secondary { display: inline-flex; align-items: center; gap: 8px; padding: 16px 24px; border-radius: 12px; background: white; border: 1.5px solid rgba(29,113,105,0.2); color: #3a5a3e; font-size: 16px; font-weight: 700; text-decoration: none; font-family: system-ui,sans-serif; transition: all 0.25s; }
.btn-secondary:hover { border-color: #0a9b8a; color: #0a9b8a; }
.btn-secondary:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 3px; }

@media (max-width: 900px) {
  .nav { padding: 18px 20px; }
  .nav.scrolled { padding: 14px 20px; }
  .nav-links { display: none; }
  .hero { padding: 40px 20px 60px; margin-top: 160px; }
  .content { padding: 32px 20px 80px; }
  .info-card, .about-card { padding: 24px 20px; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
</style>
