<template>
  <div class="checkin-landing">
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
        <span class="nav-link-coming" aria-disabled="true" role="link">Places</span>
        <RouterLink to="/about">About</RouterLink>
        <RouterLink to="/resources">Resources</RouterLink>
        <RouterLink to="/best-time">Best Time</RouterLink>
      </div>
    </nav>

    <div class="a11y-bar" role="region" aria-label="Accessibility options">
      <div class="a11y-inner">
        <div class="text-size-control" role="group" aria-label="Adjust text size">
          <span class="a-small" aria-hidden="true">A</span>
          <input
            type="range"
            class="text-slider"
            min="90"
            max="140"
            step="5"
            v-model.number="textScale"
            aria-label="Text size"
            aria-valuemin="90"
            aria-valuemax="140"
            :aria-valuenow="textScale"
            :aria-valuetext="`Text size ${textScale}%`"
          />
          <span class="a-large" aria-hidden="true">A</span>
          <span class="scale-pct" aria-hidden="true">{{ textScale }}%</span>
        </div>
      </div>
    </div>

    <header class="hero">
      <div class="hero-bg-word" aria-hidden="true">CHECKIN</div>
      <div class="hero-inner">
        <div class="hero-badge">
          <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
          Your weekly wellbeing check-in
        </div>
        <h1 class="hero-headline" :style="{ fontSize: scaledPx(76) }">
          How are you feeling<br>
          <em>about your connections?</em>
        </h1>
        <p class="hero-sub" :style="{ fontSize: scaledPx(19) }">
          This gentle 5-minute check-in helps you understand how connected you
          feel to the people around you, and points you toward warm, welcoming
          activities in your neighbourhood.
        </p>
      </div>
    </header>

    <main class="content" id="main-content">
      <div class="info-grid">
        <div class="info-card" data-reveal>
          <div class="info-num" aria-hidden="true">01</div>
          <div class="info-icon mint" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="8" r="4"/>
              <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
            </svg>
          </div>
          <div class="info-text">
            <h2 :style="{ fontSize: scaledPx(22) }">20 simple questions</h2>
            <p :style="{ fontSize: scaledPx(16) }">Easy to answer, no right or wrong. Just how you honestly feel right now.</p>
          </div>
        </div>

        <div class="info-card" data-reveal>
          <div class="info-num" aria-hidden="true">02</div>
          <div class="info-icon yellow" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2"/>
              <path d="M3 9h18M9 21V9"/>
            </svg>
          </div>
          <div class="info-text">
            <h2 :style="{ fontSize: scaledPx(22) }">A clear picture of your wellbeing</h2>
            <p :style="{ fontSize: scaledPx(16) }">See which areas of connection are going well and which need a little attention.</p>
          </div>
        </div>

        <div class="info-card" data-reveal>
          <div class="info-num" aria-hidden="true">03</div>
          <div class="info-icon purple" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/>
              <circle cx="12" cy="10" r="2.5"/>
            </svg>
          </div>
          <div class="info-text">
            <h2 :style="{ fontSize: scaledPx(22) }">Activities matched to you</h2>
            <p :style="{ fontSize: scaledPx(16) }">Discover free, nearby events chosen to suit your situation and interests.</p>
          </div>
        </div>
      </div>

      <div class="cta-wrap" data-reveal>
        <button
          class="start-btn"
          @click="startCheckin"
          aria-label="Start your wellbeing check-in, takes about 5 minutes"
          :style="{ fontSize: scaledPx(20) }"
        >
          <span>Start My Check-in</span>
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M5 12h14M13 5l7 7-7 7"/>
          </svg>
        </button>
        <p class="note" :style="{ fontSize: scaledPx(14) }">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="3" y="11" width="18" height="11" rx="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          Anonymous · Nothing is stored · Takes about 5 minutes
        </p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'

const router = useRouter()
const scrollY = ref(0)
const textScale = ref(100)
const scaledPx = (base) => `${(base * textScale.value) / 100}px`

function startCheckin() { router.push('/checkin/form') }
const handleScroll = () => { scrollY.value = window.scrollY }

let observer = null
function setupReveal() {
  observer = new IntersectionObserver(
    entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in-view') }),
    { threshold: 0.12 }
  )
  document.querySelectorAll('[data-reveal]').forEach(el => observer.observe(el))
}

onMounted(() => { window.addEventListener('scroll', handleScroll, { passive: true }); setupReveal() })
onBeforeUnmount(() => { window.removeEventListener('scroll', handleScroll); if (observer) observer.disconnect() })
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.checkin-landing {
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
  padding: 24px 52px;
  transition: background 0.4s, padding 0.4s, box-shadow 0.4s;
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

.a11y-bar {
  position: fixed; top: 86px; right: 0; left: 0; z-index: 90;
  background: rgba(255,255,255,0.92); backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(29,113,105,0.1);
  box-shadow: 0 4px 16px rgba(0,0,0,0.04);
}
.a11y-inner { display: flex; align-items: center; justify-content: flex-end; padding: 10px 52px; }
.text-size-control {
  display: inline-flex; align-items: center; gap: 12px;
  background: rgba(255,255,255,0.9); backdrop-filter: blur(10px);
  border: 1.5px solid rgba(29,113,105,0.18);
  border-radius: 999px; padding: 8px 18px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.06);
}
.a-small { font-family: Georgia,serif; font-size: 13px; font-weight: 700; color: #0a9b8a; line-height: 1; }
.a-large { font-family: Georgia,serif; font-size: 22px; font-weight: 700; color: #0a9b8a; line-height: 1; }
.text-slider {
  -webkit-appearance: none; appearance: none;
  width: 120px; height: 4px;
  background: #d1e8d4; border-radius: 999px; outline: none; cursor: pointer;
}
.text-slider::-webkit-slider-thumb {
  -webkit-appearance: none; width: 22px; height: 22px; border-radius: 50%;
  background: #0a9b8a; box-shadow: 0 2px 8px rgba(10,155,138,0.4);
  cursor: pointer; transition: transform 0.2s;
}
.text-slider::-webkit-slider-thumb:hover { transform: scale(1.15); }
.text-slider:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 3px; }
.scale-pct { font-size: 13px; font-weight: 700; color: #6a8e6e; min-width: 38px; }

.hero {
  position: relative; overflow: hidden;
  background: linear-gradient(160deg, #e4f5e0 0%, #c8edc8 100%);
  padding: 60px 52px 88px;
  border-bottom: 1px solid rgba(29,113,105,0.12);
  margin-top: 160px;
}
.hero-bg-word {
  position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%);
  font-family: Georgia,serif; font-size: clamp(90px,14vw,180px);
  font-weight: 700; font-style: italic; color: rgba(10,155,138,0.055);
  white-space: nowrap; pointer-events: none; user-select: none; letter-spacing: -0.04em;
}
.hero-inner { position: relative; z-index: 2; max-width: 820px; }

.hero-badge {
  display: inline-flex; align-items: center; gap: 10px;
  padding: 10px 20px; border-radius: 999px;
  background: rgba(255,255,255,0.7); backdrop-filter: blur(8px);
  border: 1px solid rgba(29,113,105,0.18);
  font-size: 13px; font-weight: 700; color: #0a9b8a;
  letter-spacing: 0.04em; margin-bottom: 28px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}
.hero-headline { font-family: Georgia,serif; font-size: clamp(38px,6vw,76px); font-weight: 700; line-height: 1.08; color: #0f1e12; margin-bottom: 24px; }
.hero-headline em { color: #0a9b8a; font-style: italic; }
.hero-sub { font-size: 19px; line-height: 1.75; color: #4a6a4e; max-width: 640px; }

.content { position: relative; z-index: 2; max-width: 900px; margin: 0 auto; padding: 72px 52px 100px; }
.info-grid { display: grid; gap: 20px; margin-bottom: 52px; }

.info-card {
  display: flex; align-items: center; gap: 24px;
  background: white; border: 1px solid rgba(29,113,105,0.12);
  border-radius: 18px; padding: 32px 36px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.04);
  position: relative; overflow: hidden;
  opacity: 0; transform: translateY(28px);
  transition: opacity 0.7s cubic-bezier(0.22,1,0.36,1), transform 0.7s cubic-bezier(0.22,1,0.36,1), box-shadow 0.3s;
}
.info-card.in-view { opacity: 1; transform: none; }
.info-card:nth-child(2) { transition-delay: 0.1s; }
.info-card:nth-child(3) { transition-delay: 0.2s; }
.info-card:hover { transform: translateY(-3px); box-shadow: 0 18px 44px rgba(10,155,138,0.1); }

.info-num { position: absolute; top: 16px; right: 20px; font-family: Georgia,serif; font-size: 13px; font-weight: 700; color: rgba(10,155,138,0.25); letter-spacing: 0.06em; }
.info-icon { width: 64px; height: 64px; flex-shrink: 0; border-radius: 16px; display: flex; align-items: center; justify-content: center; }
.mint   { background: #d6f4e7; color: #0a6b55; }
.yellow { background: #fff3c2; color: #8a6600; }
.purple { background: #ede8ff; color: #4a3db6; }
.info-text h2 { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; margin-bottom: 8px; line-height: 1.2; }
.info-text p { line-height: 1.65; color: #4a6a4e; }

.cta-wrap {
  display: flex; flex-direction: column; align-items: center; gap: 20px;
  opacity: 0; transform: translateY(28px);
  transition: opacity 0.7s 0.25s cubic-bezier(0.22,1,0.36,1), transform 0.7s 0.25s cubic-bezier(0.22,1,0.36,1);
}
.cta-wrap.in-view { opacity: 1; transform: none; }

.start-btn {
  display: inline-flex; align-items: center; gap: 14px;
  padding: 22px 52px; border-radius: 14px; border: none;
  background: linear-gradient(135deg,#0a9b8a,#056b5e); color: white;
  font-weight: 700; cursor: pointer; font-family: system-ui,sans-serif;
  box-shadow: 0 16px 40px rgba(10,155,138,0.32);
  transition: all 0.3s cubic-bezier(0.22,1,0.36,1);
  width: 100%; justify-content: center; max-width: 480px;
}
.start-btn:hover { transform: translateY(-3px); box-shadow: 0 24px 52px rgba(10,155,138,0.42); }
.start-btn:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 3px; }
.start-btn svg { transition: transform 0.3s; }
.start-btn:hover svg { transform: translateX(5px); }

.note { display: flex; align-items: center; gap: 8px; color: #8aaa8e; font-weight: 500; }

@media (max-width: 900px) {
  .nav { padding: 18px 20px; }
  .nav.scrolled { padding: 14px 20px; }
  .nav-links { display: none; }
  .a11y-inner { padding: 10px 20px; }
  .hero { padding: 40px 20px 64px; margin-top: 140px; }
  .content { padding: 48px 20px 80px; }
  .info-card { flex-direction: column; align-items: flex-start; padding: 24px; gap: 16px; }
  .start-btn { padding: 20px 32px; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
</style>