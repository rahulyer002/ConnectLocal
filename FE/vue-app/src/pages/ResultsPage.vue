<template>
  <div class="results-page">
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

    <header class="hero-band">
      <div class="hero-bg-word" aria-hidden="true">RESULTS</div>
      <div class="hero-inner">
        <p class="hero-eyebrow">
          <span class="eyebrow-line" aria-hidden="true"></span>
          Wellbeing Check
        </p>
        <h1 class="hero-headline" :style="{ fontSize: scaledPx(72) }">
          Your results<br>
          <em>are ready.</em>
        </h1>
        <p class="hero-sub" :style="{ fontSize: scaledPx(18) }">
          This result is based only on your current visit. It is not saved
          when you refresh or reopen the website.
        </p>
      </div>
    </header>

    <main class="content" id="main-content">

      <!-- HAS RESULT -->
      <template v-if="wellbeingStore.hasResult">

        <!-- Score card -->
        <div class="score-card" :class="resultBandClass" data-reveal>
          <div class="score-left">
            <p class="score-label" :style="{ fontSize: scaledPx(12) }">Wellbeing score</p>
            <div class="score-number" :style="{ fontSize: scaledPx(96) }">
              {{ wellbeingStore.totalScore }}
            </div>
            <p class="score-out" :style="{ fontSize: scaledPx(18) }">out of 80</p>
            <span class="score-band-pill" :style="{ fontSize: scaledPx(14) }">
              {{ wellbeingStore.resultBand }}
            </span>
          </div>
          <div class="score-right">
            <h2 :style="{ fontSize: scaledPx(22) }">What this means</h2>
            <p :style="{ fontSize: scaledPx(16) }">{{ wellbeingStore.resultExplanation }}</p>
            <p class="small-note" :style="{ fontSize: scaledPx(13) }">
              Some items are reverse scored to reflect positive social connection.
            </p>
          </div>
        </div>

        <!-- Dimension cards -->
        <div class="dimension-section" data-reveal>
          <p class="section-label" :style="{ fontSize: scaledPx(12) }">Your scores by area</p>
          <div class="dimension-grid">
            <div class="dimension-card">
              <div class="dim-icon mint" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="8" r="4"/>
                  <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
                </svg>
              </div>
              <p class="dim-title" :style="{ fontSize: scaledPx(13) }">Companionship</p>
              <p class="dim-score" :style="{ fontSize: scaledPx(48) }">{{ wellbeingStore.dimensionScores.companionship }}</p>
              <p class="dim-desc" :style="{ fontSize: scaledPx(14) }">Feelings of company, support, and not being alone.</p>
            </div>

            <div class="dimension-card">
              <div class="dim-icon yellow" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
              </div>
              <p class="dim-title" :style="{ fontSize: scaledPx(13) }">Social Connection</p>
              <p class="dim-score" :style="{ fontSize: scaledPx(48) }">{{ wellbeingStore.dimensionScores.socialConnection }}</p>
              <p class="dim-desc" :style="{ fontSize: scaledPx(14) }">Belonging, shared interests, and connection with people around you.</p>
            </div>

            <div class="dimension-card">
              <div class="dim-icon purple" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 21s-7-4.5-7-11a5 5 0 0 1 9-3 5 5 0 0 1 9 3c0 6.5-7 11-7 11z"/>
                </svg>
              </div>
              <p class="dim-title" :style="{ fontSize: scaledPx(13) }">Intimacy</p>
              <p class="dim-score" :style="{ fontSize: scaledPx(48) }">{{ wellbeingStore.dimensionScores.intimacy }}</p>
              <p class="dim-desc" :style="{ fontSize: scaledPx(14) }">Emotional closeness, trust, and having people you can turn to.</p>
            </div>
          </div>
        </div>

        <!-- Next steps -->
        <div class="next-block" data-reveal>
          <div class="next-inner">
            <p class="section-label" :style="{ fontSize: scaledPx(12) }">Suggested next step</p>
            <p class="next-text" :style="{ fontSize: scaledPx(18) }">{{ nextStepText }}</p>
          </div>
        </div>

        <!-- Retake -->
        <div class="retake-block" data-reveal>
          <div class="retake-inner">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#0a9b8a" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
            <div>
              <p class="retake-title" :style="{ fontSize: scaledPx(16) }">Retake reminder</p>
              <p class="retake-text" :style="{ fontSize: scaledPx(15) }">
                You may wish to retake this check-in in around 90 days to reflect on any changes over time.
              </p>
              <p class="small-note" :style="{ fontSize: scaledPx(13) }">
                This is shown as a privacy-safe suggestion only. The website does not save your answers or send reminders.
              </p>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="page-actions" data-reveal>
          <RouterLink to="/discover" class="btn-primary" aria-label="Check out events near you">
            Check out events near you
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M5 12h14M13 5l7 7-7 7"/>
            </svg>
          </RouterLink>
          <RouterLink to="/checkin" class="btn-secondary" aria-label="Back to check-in">
            Back to Check-in
          </RouterLink>
        </div>

      </template>

      <!-- NO RESULT -->
      <template v-else>
        <div class="empty-state" data-reveal>
          <svg viewBox="0 0 24 24" width="52" height="52" fill="none" stroke="#0a9b8a" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/>
            <circle cx="12" cy="10" r="2.5"/>
          </svg>
          <h2 :style="{ fontSize: scaledPx(32) }">No results yet</h2>
          <p :style="{ fontSize: scaledPx(17) }">
            No check-in result is available yet. Please complete the check-in first
            to see your score summary and explanation.
          </p>
          <RouterLink to="/checkin" class="btn-primary" aria-label="Go to wellbeing check-in">
            Go to Check-in
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M5 12h14M13 5l7 7-7 7"/>
            </svg>
          </RouterLink>
        </div>
      </template>

    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { wellbeingStore } from '../stores/wellbeingStore'

const scrollY = ref(0)
const textScale = ref(100)
const scaledPx = (base) => `${(base * textScale.value) / 100}px`
const handleScroll = () => { scrollY.value = window.scrollY }

let observer = null
function setupReveal() {
  observer = new IntersectionObserver(
    entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in-view') }),
    { threshold: 0.1 }
  )
  document.querySelectorAll('[data-reveal]').forEach(el => observer.observe(el))
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  setupReveal()
})
onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
  if (observer) observer.disconnect()
})

const resultBandClass = computed(() => {
  const score = wellbeingStore.totalScore
  if (score <= 34) return 'band-low'
  if (score <= 49) return 'band-mild'
  if (score <= 64) return 'band-moderate'
  return 'band-high'
})

const nextStepText = computed(() => {
  const score = wellbeingStore.totalScore
  if (score <= 34) return 'Your score suggests a lower level of loneliness at the moment. You may still benefit from maintaining regular social contact and familiar routines.'
  if (score <= 49) return 'Your score suggests some distance from others. A small and manageable step, such as revisiting a familiar place or talking to someone you trust, may help.'
  if (score <= 64) return 'Your score suggests a moderate level of loneliness. Gentle social opportunities, familiar community spaces, or simple local activities may be helpful next steps.'
  return 'Your score suggests a higher level of loneliness. It may help to start with low-pressure social options and reach out to trusted people or nearby support services when comfortable.'
})
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.results-page {
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
.nav-cta { display: inline-flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 700; color: #0a9b8a; text-decoration: none; padding: 10px 22px; border: 1.5px solid #0a9b8a; border-radius: 999px; transition: all 0.3s; }
.nav-cta:hover { background: #0a9b8a; color: white; }
.nav-cta:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 3px; }

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

.hero-band {
  position: relative; overflow: hidden;
  background: linear-gradient(160deg, #e4f5e0 0%, #c8edc8 100%);
  padding: 60px 52px 72px;
  border-bottom: 1px solid rgba(29,113,105,0.12);
  margin-top: 160px;
}
.hero-bg-word {
  position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%);
  font-family: Georgia,serif; font-size: clamp(80px,14vw,180px);
  font-weight: 700; font-style: italic; color: rgba(10,155,138,0.055);
  white-space: nowrap; pointer-events: none; user-select: none; letter-spacing: -0.04em;
}
.hero-inner { position: relative; z-index: 2; max-width: 820px; }
.hero-eyebrow { display: inline-flex; align-items: center; gap: 12px; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 20px; }
.eyebrow-line { display: block; width: 32px; height: 1px; background: #0a9b8a; }
.hero-headline { font-family: Georgia,serif; font-size: clamp(36px,5vw,72px); font-weight: 700; line-height: 1.08; color: #0f1e12; margin-bottom: 16px; }
.hero-headline em { color: #0a9b8a; font-style: italic; }
.hero-sub { font-size: 17px; line-height: 1.7; color: #4a6a4e; max-width: 600px; }

.content { position: relative; z-index: 2; max-width: 960px; margin: 0 auto; padding: 52px 52px 100px; display: flex; flex-direction: column; gap: 28px; }

/* Score card */
.score-card {
  display: grid; grid-template-columns: 220px 1fr; gap: 40px;
  border-radius: 20px; padding: 40px;
  border: 1px solid rgba(29,113,105,0.12);
  box-shadow: 0 16px 48px rgba(0,0,0,0.05);
  opacity: 0; transform: translateY(28px);
  transition: opacity 0.7s cubic-bezier(0.22,1,0.36,1), transform 0.7s cubic-bezier(0.22,1,0.36,1);
}
.score-card.in-view { opacity: 1; transform: none; }

.band-low      { background: linear-gradient(135deg, #e8f8ed, #d4f0dc); }
.band-mild     { background: linear-gradient(135deg, #fef8e6, #fdefc4); }
.band-moderate { background: linear-gradient(135deg, #fef0e6, #fde0c4); }
.band-high     { background: linear-gradient(135deg, #fee8e8, #fdd4d4); }

.score-left { display: flex; flex-direction: column; align-items: flex-start; gap: 4px; }
.score-label { font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #6a8e6e; }
.score-number { font-family: Georgia,serif; font-size: 96px; font-weight: 700; line-height: 1; color: #0a9b8a; }
.score-out { font-size: 16px; color: #6a8e6e; font-weight: 500; margin-bottom: 8px; }
.score-band-pill {
  display: inline-block; padding: 7px 16px; border-radius: 999px;
  font-size: 13px; font-weight: 700;
  background: rgba(255,255,255,0.65); color: #1a2e1e;
  border: 1px solid rgba(29,113,105,0.15);
}

.score-right { display: flex; flex-direction: column; gap: 12px; justify-content: center; }
.score-right h2 { font-family: Georgia,serif; font-size: 22px; font-weight: 700; color: #0f1e12; }
.score-right p { font-size: 16px; line-height: 1.7; color: #3a5a3e; }
.small-note { font-size: 13px !important; color: #8aaa8e !important; margin-top: 4px; }

/* Dimension section */
.dimension-section {
  opacity: 0; transform: translateY(28px);
  transition: opacity 0.7s 0.1s cubic-bezier(0.22,1,0.36,1), transform 0.7s 0.1s cubic-bezier(0.22,1,0.36,1);
}
.dimension-section.in-view { opacity: 1; transform: none; }
.section-label { font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 16px; }
.dimension-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; }

.dimension-card {
  background: white; border: 1px solid rgba(29,113,105,0.1);
  border-radius: 18px; padding: 28px 24px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.04);
  transition: transform 0.3s, box-shadow 0.3s;
}
.dimension-card:hover { transform: translateY(-3px); box-shadow: 0 14px 36px rgba(10,155,138,0.1); }

.dim-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 14px; }
.mint   { background: #d6f4e7; color: #0a6b55; }
.yellow { background: #fff3c2; color: #8a6600; }
.purple { background: #ede8ff; color: #4a3db6; }

.dim-title { font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #6a8e6e; margin-bottom: 8px; }
.dim-score { font-family: Georgia,serif; font-size: 48px; font-weight: 700; color: #0a9b8a; line-height: 1; margin-bottom: 10px; }
.dim-desc { font-size: 14px; line-height: 1.6; color: #4a6a4e; }

/* Next step */
.next-block {
  background: white; border: 1px solid rgba(29,113,105,0.1);
  border-radius: 18px; padding: 36px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.04);
  opacity: 0; transform: translateY(28px);
  transition: opacity 0.7s 0.15s cubic-bezier(0.22,1,0.36,1), transform 0.7s 0.15s cubic-bezier(0.22,1,0.36,1);
}
.next-block.in-view { opacity: 1; transform: none; }
.next-text { font-size: 18px; line-height: 1.75; color: #2a4a2e; margin-top: 10px; }

/* Retake */
.retake-block {
  background: linear-gradient(135deg, #e4f5e0, #d0eed0);
  border: 1px solid rgba(29,113,105,0.12);
  border-radius: 18px; padding: 28px 36px;
  opacity: 0; transform: translateY(28px);
  transition: opacity 0.7s 0.2s cubic-bezier(0.22,1,0.36,1), transform 0.7s 0.2s cubic-bezier(0.22,1,0.36,1);
}
.retake-block.in-view { opacity: 1; transform: none; }
.retake-inner { display: flex; align-items: flex-start; gap: 18px; }
.retake-title { font-size: 16px; font-weight: 700; color: #0f1e12; margin-bottom: 6px; }
.retake-text { font-size: 15px; line-height: 1.65; color: #3a5a3e; margin-bottom: 6px; }

/* Actions */
.page-actions {
  display: flex; gap: 16px; flex-wrap: wrap;
  opacity: 0; transform: translateY(28px);
  transition: opacity 0.7s 0.25s cubic-bezier(0.22,1,0.36,1), transform 0.7s 0.25s cubic-bezier(0.22,1,0.36,1);
}
.page-actions.in-view { opacity: 1; transform: none; }

.btn-primary {
  display: inline-flex; align-items: center; gap: 10px;
  padding: 18px 32px; border-radius: 12px; border: none;
  background: linear-gradient(135deg,#0a9b8a,#056b5e); color: white;
  font-size: 16px; font-weight: 700; text-decoration: none;
  font-family: system-ui,sans-serif;
  box-shadow: 0 12px 32px rgba(10,155,138,0.28);
  transition: all 0.3s cubic-bezier(0.22,1,0.36,1);
}
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 20px 40px rgba(10,155,138,0.38); }
.btn-primary:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 3px; }
.btn-primary svg { transition: transform 0.3s; }
.btn-primary:hover svg { transform: translateX(4px); }

.btn-secondary {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 18px 28px; border-radius: 12px;
  background: white; border: 1.5px solid rgba(29,113,105,0.2);
  color: #3a5a3e; font-size: 16px; font-weight: 700;
  text-decoration: none; font-family: system-ui,sans-serif;
  transition: all 0.25s;
}
.btn-secondary:hover { border-color: #0a9b8a; color: #0a9b8a; }
.btn-secondary:focus-visible { outline: 3px solid #0a9b8a; outline-offset: 3px; }

/* Empty state */
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  text-align: center; gap: 20px;
  background: white; border: 1px solid rgba(29,113,105,0.1);
  border-radius: 20px; padding: 72px 40px;
  opacity: 0; transform: translateY(28px);
  transition: opacity 0.7s cubic-bezier(0.22,1,0.36,1), transform 0.7s cubic-bezier(0.22,1,0.36,1);
}
.empty-state.in-view { opacity: 1; transform: none; }
.empty-state h2 { font-family: Georgia,serif; font-size: 32px; font-weight: 700; color: #0f1e12; }
.empty-state p { font-size: 17px; line-height: 1.7; color: #4a6a4e; max-width: 480px; }

@media (max-width: 900px) {
  .nav { padding: 18px 20px; }
  .nav.scrolled { padding: 14px 20px; }
  .nav-links { display: none; }
  .a11y-inner { padding: 10px 20px; }
  .hero-band { padding: 40px 20px 56px; margin-top: 140px; }
  .content { padding: 32px 20px 80px; }
  .score-card { grid-template-columns: 1fr; gap: 24px; padding: 28px 20px; }
  .dimension-grid { grid-template-columns: 1fr; }
  .next-block, .retake-block { padding: 24px 20px; }
  .retake-inner { flex-direction: column; gap: 12px; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
</style>