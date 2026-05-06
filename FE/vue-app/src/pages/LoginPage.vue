<template>
  <div class="page" @mousemove="handleMouse">
    <div class="noise" aria-hidden="true"></div>
    <div class="orb orb-1" aria-hidden="true"></div>
    <div class="orb orb-2" aria-hidden="true"></div>

    <!-- Floating ambient tags (same as HomePage) -->
    <div class="hero-tag tag-1" :style="{ transform: `translate(${mouse.x * -0.016}px, ${mouse.y * -0.012}px)` }">
      <span class="tag-dot"></span> Melbourne, VIC
    </div>
    <div class="hero-tag tag-2" :style="{ transform: `translate(${mouse.x * 0.02}px, ${mouse.y * 0.014}px)` }">
      <span class="tag-dot"></span> Real connections
    </div>
    <div class="hero-tag tag-3" :style="{ transform: `translate(${mouse.x * -0.011}px, ${mouse.y * 0.018}px)` }">
      <span class="tag-dot"></span> Free & open
    </div>

    <div class="layout">

      <!-- ══ LEFT — journey map ══════════════════════════════ -->
      <div class="map-col" aria-hidden="true">
        <div class="bg-word">LOCAL</div>

        <!-- Animated Melbourne suburb journey map -->
        <svg
          class="map-svg"
          viewBox="0 0 420 560"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <defs>
            <!-- Tram line gradient -->
            <linearGradient id="tram-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#0a9b8a"/>
              <stop offset="100%" stop-color="#056b5e"/>
            </linearGradient>
            <!-- Train line gradient -->
            <linearGradient id="train-grad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#c8940a"/>
              <stop offset="100%" stop-color="#a87008"/>
            </linearGradient>
            <!-- Bus gradient -->
            <linearGradient id="bus-grad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#5a8a3c"/>
              <stop offset="100%" stop-color="#3a6a20"/>
            </linearGradient>
          </defs>

          <!-- Subtle street grid -->
          <g stroke="rgba(29,113,105,0.08)" stroke-width="1" fill="none">
            <line x1="70"  y1="0"   x2="70"  y2="560"/>
            <line x1="140" y1="0"   x2="140" y2="560"/>
            <line x1="210" y1="0"   x2="210" y2="560"/>
            <line x1="280" y1="0"   x2="280" y2="560"/>
            <line x1="350" y1="0"   x2="350" y2="560"/>
            <line x1="0"   y1="70"  x2="420" y2="70"/>
            <line x1="0"   y1="140" x2="420" y2="140"/>
            <line x1="0"   y1="210" x2="420" y2="210"/>
            <line x1="0"   y1="280" x2="420" y2="280"/>
            <line x1="0"   y1="350" x2="420" y2="350"/>
            <line x1="0"   y1="420" x2="420" y2="420"/>
            <line x1="0"   y1="490" x2="420" y2="490"/>
          </g>

          <!-- ═══ ROUTE LINES ═══ -->

          <!-- Tram line 1 — vertical teal (Swanston St) -->
          <path
            class="route tram-line"
            d="M 140 20 L 140 140 Q 140 210 210 210 L 210 420 Q 210 490 140 490 L 140 540"
            fill="none" stroke="#0a9b8a" stroke-width="3.5"
            stroke-linecap="round" stroke-linejoin="round"
          />

          <!-- Train line — diagonal amber (Sandringham line style) -->
          <path
            class="route train-line"
            d="M 20 100 L 140 140 L 280 140 L 380 80"
            fill="none" stroke="#c8940a" stroke-width="3"
            stroke-linecap="round" stroke-linejoin="round"
          />

          <!-- Bus line — dashed green -->
          <path
            class="route bus-line"
            d="M 20 280 L 140 280 L 210 210 L 280 280 L 380 300"
            fill="none" stroke="#5a8a3c" stroke-width="2.5"
            stroke-dasharray="8 5"
            stroke-linecap="round" stroke-linejoin="round"
          />

          <!-- Second tram — blue diagonal -->
          <path
            class="route tram2-line"
            d="M 280 20 L 280 140 L 210 210 L 280 280 L 280 540"
            fill="none" stroke="rgba(29,113,105,0.35)" stroke-width="2.5"
            stroke-linecap="round" stroke-linejoin="round"
          />

          <!-- Walk connector (thin dashed) -->
          <path
            class="route walk-line"
            d="M 140 210 L 210 210"
            fill="none" stroke="rgba(10,155,138,0.4)" stroke-width="1.5"
            stroke-dasharray="4 4"
            stroke-linecap="round"
          />

          <!-- ═══ STATIONS ═══ -->

          <!-- Melbourne CBD — main hub -->
          <g class="station" style="--delay:2.2s">
            <circle cx="140" cy="210" r="14" fill="white" stroke="#0a9b8a" stroke-width="2.5"/>
            <circle cx="140" cy="210" r="7" fill="#0a9b8a"/>
            <!-- Pulse ring -->
            <circle cx="140" cy="210" r="7" fill="none" stroke="#0a9b8a" stroke-width="1.5" class="pulse"/>
            <text x="158" y="206" font-family="system-ui,sans-serif" font-size="10" font-weight="700" fill="#0f1e12" class="stn-label">Melbourne CBD</text>
            <text x="158" y="219" font-family="system-ui,sans-serif" font-size="9" fill="#6a8e6e" class="stn-label">Hub · 4 routes</text>
          </g>

          <!-- Fitzroy -->
          <g class="station" style="--delay:2.5s">
            <circle cx="140" cy="70" r="9" fill="white" stroke="#0a9b8a" stroke-width="2"/>
            <circle cx="140" cy="70" r="4.5" fill="#0a9b8a"/>
            <text x="154" y="67" font-family="system-ui,sans-serif" font-size="9.5" font-weight="600" fill="#1a2e1e" class="stn-label">Fitzroy</text>
            <text x="154" y="78" font-family="system-ui,sans-serif" font-size="8.5" fill="#6a8e6e" class="stn-label">Arts &amp; culture</text>
          </g>

          <!-- Flinders St -->
          <g class="station" style="--delay:2.7s">
            <circle cx="280" cy="140" r="10" fill="white" stroke="#c8940a" stroke-width="2"/>
            <circle cx="280" cy="140" r="5" fill="#c8940a"/>
            <circle cx="280" cy="140" r="5" fill="none" stroke="#c8940a" stroke-width="1.5" class="pulse" style="animation-delay:3.2s"/>
            <text x="294" y="137" font-family="system-ui,sans-serif" font-size="9.5" font-weight="600" fill="#1a2e1e" class="stn-label">Flinders St</text>
            <text x="294" y="148" font-family="system-ui,sans-serif" font-size="8.5" fill="#6a8e6e" class="stn-label">Train interchange</text>
          </g>

          <!-- South Yarra -->
          <g class="station" style="--delay:3.0s">
            <circle cx="140" cy="350" r="9" fill="white" stroke="#0a9b8a" stroke-width="2"/>
            <circle cx="140" cy="350" r="4.5" fill="#0a9b8a"/>
            <circle cx="140" cy="350" r="4.5" fill="none" stroke="#0a9b8a" stroke-width="1.5" class="pulse" style="animation-delay:3.8s"/>
            <text x="154" y="347" font-family="system-ui,sans-serif" font-size="9.5" font-weight="600" fill="#1a2e1e" class="stn-label">South Yarra</text>
            <text x="154" y="358" font-family="system-ui,sans-serif" font-size="8.5" fill="#6a8e6e" class="stn-label">Tram &amp; train</text>
          </g>

          <!-- Richmond -->
          <g class="station" style="--delay:3.2s">
            <circle cx="280" cy="280" r="8" fill="white" stroke="#5a8a3c" stroke-width="2"/>
            <circle cx="280" cy="280" r="4" fill="#5a8a3c"/>
            <text x="293" y="277" font-family="system-ui,sans-serif" font-size="9.5" font-weight="600" fill="#1a2e1e" class="stn-label">Richmond</text>
            <text x="293" y="288" font-family="system-ui,sans-serif" font-size="8.5" fill="#6a8e6e" class="stn-label">Gardens nearby</text>
          </g>

          <!-- Carlton -->
          <g class="station" style="--delay:2.9s">
            <circle cx="70" cy="140" r="8" fill="white" stroke="#0a9b8a" stroke-width="1.8"/>
            <circle cx="70" cy="140" r="4" fill="#0a9b8a"/>
            <text x="82" y="137" font-family="system-ui,sans-serif" font-size="9.5" font-weight="600" fill="#1a2e1e" class="stn-label">Carlton</text>
            <text x="82" y="148" font-family="system-ui,sans-serif" font-size="8.5" fill="#6a8e6e" class="stn-label">Uni &amp; gardens</text>
          </g>

          <!-- Collingwood -->
          <g class="station" style="--delay:3.1s">
            <circle cx="350" cy="210" r="8" fill="white" stroke="#c8940a" stroke-width="1.8"/>
            <circle cx="350" cy="210" r="4" fill="#c8940a"/>
            <text x="276" y="222" font-family="system-ui,sans-serif" font-size="9.5" font-weight="600" fill="#1a2e1e" class="stn-label" text-anchor="end">Collingwood</text>
          </g>

          <!-- Southbank -->
          <g class="station" style="--delay:3.3s">
            <circle cx="210" cy="420" r="8" fill="white" stroke="#0a9b8a" stroke-width="1.8"/>
            <circle cx="210" cy="420" r="4" fill="#0a9b8a"/>
            <text x="224" y="417" font-family="system-ui,sans-serif" font-size="9.5" font-weight="600" fill="#1a2e1e" class="stn-label">Southbank</text>
            <text x="224" y="428" font-family="system-ui,sans-serif" font-size="8.5" fill="#6a8e6e" class="stn-label">Arts precinct</text>
          </g>

          <!-- St Kilda -->
          <g class="station" style="--delay:3.5s">
            <circle cx="140" cy="490" r="8" fill="white" stroke="#0a9b8a" stroke-width="1.8"/>
            <circle cx="140" cy="490" r="4" fill="#0a9b8a"/>
            <text x="154" y="487" font-family="system-ui,sans-serif" font-size="9.5" font-weight="600" fill="#1a2e1e" class="stn-label">St Kilda</text>
            <text x="154" y="498" font-family="system-ui,sans-serif" font-size="8.5" fill="#6a8e6e" class="stn-label">Beach &amp; cafes</text>
          </g>

          <!-- ═══ MOVING VEHICLES ═══ -->

          <!-- Tram on teal line -->
          <g class="vehicle tram-vehicle">
            <rect x="-10" y="-5" width="20" height="10" rx="3" fill="#0a9b8a"/>
            <rect x="-7" y="-3" width="5" height="5" rx="1" fill="rgba(242,250,240,0.5)"/>
            <rect x="2" y="-3" width="5" height="5" rx="1" fill="rgba(242,250,240,0.5)"/>
            <circle cx="-6" cy="5" r="2" fill="#0f1e12" opacity="0.6"/>
            <circle cx="6" cy="5" r="2" fill="#0f1e12" opacity="0.6"/>
          </g>

          <!-- Train on amber line -->
          <g class="vehicle train-vehicle">
            <rect x="-12" y="-5" width="24" height="10" rx="2.5" fill="#c8940a"/>
            <rect x="-9" y="-3" width="5" height="5" rx="1" fill="rgba(255,248,220,0.5)"/>
            <rect x="-1" y="-3" width="5" height="5" rx="1" fill="rgba(255,248,220,0.5)"/>
            <rect x="7" y="-3" width="3" height="5" rx="1" fill="rgba(255,248,220,0.5)"/>
            <circle cx="-8" cy="5" r="2" fill="#6b4800" opacity="0.5"/>
            <circle cx="8" cy="5" r="2" fill="#6b4800" opacity="0.5"/>
          </g>

          <!-- ═══ COMMUNITY MARKERS (heart icons at key stops) ═══ -->
          <g class="community-marker" style="--delay:4.2s">
            <circle cx="140" cy="210" r="22" fill="rgba(10,155,138,0.06)" stroke="rgba(10,155,138,0.15)" stroke-width="1"/>
          </g>

          <!-- ═══ LEGEND (bottom-left) ═══ -->
          <g class="legend" style="--delay:4.8s">
            <rect x="14" y="490" width="110" height="58" rx="6" fill="white" stroke="rgba(29,113,105,0.12)" stroke-width="1"/>
            <line x1="24" y1="505" x2="44" y2="505" stroke="#0a9b8a" stroke-width="3" stroke-linecap="round"/>
            <text x="50" y="509" font-family="system-ui,sans-serif" font-size="9" fill="#3a5a3e" font-weight="600">Tram</text>
            <line x1="24" y1="520" x2="44" y2="520" stroke="#c8940a" stroke-width="2.5" stroke-linecap="round"/>
            <text x="50" y="524" font-family="system-ui,sans-serif" font-size="9" fill="#3a5a3e" font-weight="600">Train</text>
            <line x1="24" y1="535" x2="44" y2="535" stroke="#5a8a3c" stroke-width="2" stroke-dasharray="5 3" stroke-linecap="round"/>
            <text x="50" y="539" font-family="system-ui,sans-serif" font-size="9" fill="#3a5a3e" font-weight="600">Bus</text>
          </g>

          <!-- Map title -->
          <text
            x="210" y="18"
            font-family="system-ui,sans-serif" font-size="10" font-weight="600"
            fill="rgba(10,155,138,0.5)" text-anchor="middle"
            letter-spacing="0.12em" class="map-title"
          >MELBOURNE COMMUNITY NETWORK</text>

        </svg>

        <!-- Stat pills (matching HomePage ed-stats style) -->
        <div class="stat-row">
          <div class="stat-item" style="animation-delay:0.3s">
            <span class="stat-num">1 in 5</span>
            <span class="stat-lbl">feel lonely in Australia</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item" style="animation-delay:0.55s">
            <span class="stat-num">150+</span>
            <span class="stat-lbl">local activities near you</span>
          </div>
        </div>
      </div>

      <!-- ══ RIGHT — login form ══════════════════════════════ -->
      <div class="form-col">
        <div class="form-inner">

          <!-- Brand -->
          <div class="brand">
            <div class="brand-logo">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/>
                <circle cx="12" cy="10" r="2.5"/>
              </svg>
            </div>
            <span class="brand-wordmark"><em>Connect</em>Local</span>
          </div>

          <!-- Heading -->
          <p class="form-eyebrow">Welcome back</p>
          <h1 class="form-headline">
            Your community<br>
            is <em>waiting for you.</em>
          </h1>
          <p class="form-sub">Enter your details to continue exploring ConnectLocal.</p>

          <!-- Error -->
          <Transition name="err-slide">
            <div v-if="errorMsg" class="err-banner" role="alert">
              <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              {{ errorMsg }}
            </div>
          </Transition>

          <!-- Username field -->
          <div class="field" :class="{ focused: focusField === 'u', filled: username }">
            <label class="field-lbl" for="username">Username</label>
            <div class="field-wrap">
              <svg class="field-icon" viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              <input
                id="username"
                v-model="username"
                type="text"
                class="field-input"
                placeholder="Enter your username"
                autocomplete="username"
                @focus="focusField = 'u'; errorMsg = ''"
                @blur="focusField = ''"
                @keyup.enter="$el.querySelector('#password').focus()"
              />
            </div>
            <div class="field-line"></div>
          </div>

          <!-- Password field -->
          <div class="field" :class="{ focused: focusField === 'p', filled: password }">
            <label class="field-lbl" for="password">Password</label>
            <div class="field-wrap">
              <svg class="field-icon" viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              <input
                id="password"
                v-model="password"
                :type="showPw ? 'text' : 'password'"
                class="field-input"
                placeholder="Enter your password"
                autocomplete="current-password"
                @focus="focusField = 'p'; errorMsg = ''"
                @blur="focusField = ''"
                @keyup.enter="handleLogin"
              />
              <button class="eye-btn" type="button" @click="showPw = !showPw" :aria-label="showPw ? 'Hide' : 'Show'">
                <svg v-if="!showPw" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
                  <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              </button>
            </div>
            <div class="field-line"></div>
          </div>


          <!-- Submit CTA — styled exactly like hero-cta -->
          <button
            class="submit-btn"
            :class="{ loading: isLoading, success: isSuccess }"
            :disabled="isLoading || isSuccess"
            @click="handleLogin"
          >
            <span v-if="isSuccess" class="btn-inner">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              Welcome!
            </span>
            <span v-else-if="isLoading" class="btn-inner">
              <span class="btn-spin"></span>
              Signing in…
            </span>
            <span v-else class="btn-inner">
              Continue to ConnectLocal
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M5 12h14M13 5l7 7-7 7"/>
              </svg>
            </span>
          </button>

        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, RouterLink } from 'vue-router'

const router = useRouter()

/* ── Mouse parallax ──────────────────────────────────────────── */
const mouse = ref({ x: 0, y: 0 })
function handleMouse(e) {
  mouse.value = {
    x: e.clientX - window.innerWidth  / 2,
    y: e.clientY - window.innerHeight / 2
  }
}

/* ── Form state ──────────────────────────────────────────────── */
const username   = ref('')
const password   = ref('')
const showPw     = ref(false)
const focusField = ref('')
const errorMsg   = ref('')
const isLoading  = ref(false)
const isSuccess  = ref(false)

const VALID_USER = 'connectlocal'
const VALID_PASS = 'community2024'

function autofill() {
  username.value = VALID_USER
  password.value = VALID_PASS
  errorMsg.value = ''
}

async function handleLogin() {
  if (isLoading.value || isSuccess.value) return
  errorMsg.value = ''

  if (!username.value.trim()) { errorMsg.value = 'Please enter your username.'; return }
  if (!password.value)         { errorMsg.value = 'Please enter your password.'; return }

  isLoading.value = true

  // Simulate a brief check
  await new Promise(r => setTimeout(r, 1100))

  if (
    username.value.trim().toLowerCase() === VALID_USER &&
    password.value === VALID_PASS
  ) {
    isSuccess.value = true
    await new Promise(r => setTimeout(r, 800))
    router.push('/home')
  } else {
    isLoading.value = false
    errorMsg.value  = 'Incorrect details. Try the demo credentials shown above.'
  }
}

function goHome() {
  router.push('/home')
}

onMounted(() => {})
onBeforeUnmount(() => {})
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* ── Root page — exactly matches HomePage ── */
.page {
  min-height: 100vh;
  background: #f2faf0;
  color: #1a2e1e;
  font-family: system-ui, sans-serif;
  overflow: hidden;
  position: relative;
}

/* ── Noise overlay (identical to HomePage) ── */
.noise {
  position: fixed; inset: 0; z-index: 1000; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  background-size: 180px; opacity: 0.45;
}

/* ── Orbs (identical to HomePage) ── */
.orb { position: fixed; border-radius: 50%; pointer-events: none; z-index: 0; filter: blur(80px); }
.orb-1 { width: 500px; height: 500px; background: rgba(90,180,110,0.2); top: -120px; left: -80px; animation: orb-drift 20s ease-in-out infinite alternate; }
.orb-2 { width: 400px; height: 400px; background: rgba(255,180,140,0.14); bottom: 10%; right: -80px; animation: orb-drift 26s ease-in-out infinite alternate-reverse; }
@keyframes orb-drift { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(50px,60px) scale(1.12)} }

/* ── Floating tags (identical to HomePage) ── */
.hero-tag {
  position: fixed; z-index: 10;
  display: inline-flex; align-items: center; gap: 8px;
  font-family: system-ui, sans-serif; font-size: 13px; font-weight: 600;
  color: #1d7169; letter-spacing: 0.05em;
  background: rgba(255,255,255,0.82); backdrop-filter: blur(10px);
  border: 1px solid rgba(29,113,105,0.18); padding: 8px 16px; border-radius: 999px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.06);
  pointer-events: none;
  transition: transform 0.5s cubic-bezier(0.22,1,0.36,1);
  animation: fade-up 0.8s both;
}
.tag-1 { top: 22%; left: 2%;  animation-delay: 1.4s; }
.tag-2 { top: 42%; left: 1.5%; animation-delay: 1.6s; }
.tag-3 { bottom: 22%; left: 2%; animation-delay: 1.8s; }

.tag-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #0a9b8a;
  animation: blink 2s ease-in-out infinite;
  flex-shrink: 0;
}
@keyframes blink { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(1.5)} }

/* ── Two-column layout ── */
.layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 100vh;
  position: relative;
  z-index: 2;
}

/* ══ LEFT — map column ══════════════════════════════════════════ */
.map-col {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 40px 40px;
  overflow: hidden;
}

/* Large faded bg word — exactly like HomePage hero-bg-text */
.bg-word {
  position: absolute;
  left: 50%; top: 50%;
  transform: translate(-50%, -50%);
  font-family: Georgia, serif;
  font-size: clamp(80px, 14vw, 160px);
  font-weight: 700; font-style: italic;
  color: rgba(10,155,138,0.055);
  white-space: nowrap; pointer-events: none;
  letter-spacing: -0.04em; user-select: none;
}

/* ── Map SVG ── */
.map-svg {
  width: 100%;
  max-width: 420px;
  height: auto;
  animation: fade-up 1s 0.3s both;
}

/* Route lines — draw-on animation */
.route {
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
}
.tram-line  { animation: draw-line 2.0s 0.4s ease-out forwards; }
.train-line { animation: draw-line 1.6s 0.8s ease-out forwards; }
.bus-line   { animation: draw-line 1.4s 1.2s ease-out forwards; }
.tram2-line { animation: draw-line 1.8s 1.0s ease-out forwards; }
.walk-line  { animation: draw-line 0.8s 2.0s ease-out forwards; }
@keyframes draw-line { to { stroke-dashoffset: 0; } }

/* Station dots — pop in sequence */
.station {
  opacity: 0;
  animation: pop-station 0.5s var(--delay, 2.5s) cubic-bezier(0.34,1.56,0.64,1) forwards;
}
@keyframes pop-station {
  0%   { opacity: 0; transform: scale(0); }
  60%  { transform: scale(1.2); }
  100% { opacity: 1; transform: scale(1); }
}

/* Station labels fade in after dot */
.stn-label {
  opacity: 0;
  animation: fade-in-label 0.4s calc(var(--delay, 2.5s) + 0.15s) ease forwards;
}
@keyframes fade-in-label { to { opacity: 1; } }

/* Pulse rings on major hubs */
.pulse {
  animation: pulse-ring 2.8s ease-in-out 3s infinite;
}
@keyframes pulse-ring {
  0%   { r: 7;  opacity: 0.7; }
  80%  { r: 18; opacity: 0; }
  100% { opacity: 0; }
}

/* Moving tram along teal route */
.tram-vehicle {
  offset-path: path("M 140 20 L 140 140 Q 140 210 210 210 L 210 420 Q 210 490 140 490 L 140 540");
  animation: move-tram 8s 3s linear infinite;
}
@keyframes move-tram {
  0%   { offset-distance: 0%; }
  100% { offset-distance: 100%; }
}

/* Moving train along amber route */
.train-vehicle {
  offset-path: path("M 20 100 L 140 140 L 280 140 L 380 80");
  animation: move-train 6s 4s linear infinite;
}
@keyframes move-train {
  0%   { offset-distance: 0%; }
  100% { offset-distance: 100%; }
}

/* Community marker ring fade in */
.community-marker {
  opacity: 0;
  animation: fade-in-label 0.6s var(--delay, 4.2s) ease forwards;
}

/* Legend + title */
.legend {
  opacity: 0;
  animation: fade-in-label 0.6s var(--delay, 4.8s) ease forwards;
}
.map-title {
  opacity: 0;
  animation: fade-in-label 0.5s 5s ease forwards;
}

/* ── Stat row (matching HomePage ed-stats) ── */
.stat-row {
  display: flex; align-items: center; gap: 24px;
  margin-top: 28px;
  animation: fade-up 0.8s 0.6s both;
}
.stat-item { display: flex; flex-direction: column; gap: 4px; }
.stat-num {
  font-family: Georgia, serif;
  font-size: clamp(22px, 3vw, 34px);
  font-weight: 700; color: #0a9b8a; line-height: 1;
}
.stat-lbl {
  font-family: system-ui, sans-serif;
  font-size: 13px; color: #6a8e6e; max-width: 120px; line-height: 1.4;
}
.stat-divider { width: 1px; height: 44px; background: rgba(29,113,105,0.2); }

/* ══ RIGHT — form column ════════════════════════════════════════ */
.form-col {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 52px;
  background: rgba(255,255,255,0.55);
  backdrop-filter: blur(12px);
  border-left: 1px solid rgba(29,113,105,0.1);
}

.form-inner {
  width: 100%;
  max-width: 400px;
  animation: fade-up 0.9s 0.2s both;
}

/* Brand — matches .nav-brand from HomePage */
.brand {
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 36px;
}
.brand-logo {
  width: 40px; height: 40px; border-radius: 50%;
  background: linear-gradient(135deg, #0a9b8a, #056b5e);
  color: white;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 6px 16px rgba(7,141,127,0.3);
}
.brand-wordmark { font-family: Georgia, serif; font-size: 22px; color: #1a2e1e; }
.brand-wordmark em { color: #0a9b8a; font-style: italic; }

/* Eyebrow — matches .hero-eyebrow */
.form-eyebrow {
  font-family: system-ui, sans-serif;
  font-size: 13px; font-weight: 700; letter-spacing: 0.1em;
  text-transform: uppercase; color: #0a9b8a;
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 16px;
}
.form-eyebrow::before { content: ''; display: block; width: 32px; height: 1px; background: #0a9b8a; }

/* Headline — matches .hero-headline */
.form-headline {
  font-family: Georgia, serif;
  font-size: clamp(30px, 4vw, 46px);
  font-weight: 700; line-height: 1.08; color: #0f1e12;
  margin-bottom: 14px;
}
.form-headline em { color: #0a9b8a; font-style: italic; }

/* Sub — matches .hero-sub p */
.form-sub {
  font-family: system-ui, sans-serif;
  font-size: 16px; line-height: 1.7; color: #4a6a4e;
  margin-bottom: 32px;
}

/* ── Error banner ── */
.err-banner {
  display: flex; align-items: center; gap: 10px;
  padding: 13px 16px; border-radius: 4px;
  background: #fff5f5;
  border: 1.5px solid rgba(185,28,28,0.18);
  color: #b91c1c;
  font-family: system-ui, sans-serif; font-size: 14px; font-weight: 600;
  margin-bottom: 20px;
}

/* Error slide transition */
.err-slide-enter-active { transition: all 0.3s cubic-bezier(0.22,1,0.36,1); }
.err-slide-leave-active { transition: all 0.2s ease; }
.err-slide-enter-from { opacity: 0; transform: translateY(-8px); }
.err-slide-leave-to  { opacity: 0; transform: translateY(-4px); }


.field { margin-bottom: 28px; position: relative; }

.field-lbl {
  display: block;
  font-family: system-ui, sans-serif;
  font-size: 11px; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: #6a8e6e;
  margin-bottom: 10px;
  transition: color 0.2s;
}
.field.focused .field-lbl { color: #0a9b8a; }

.field-wrap {
  display: flex; align-items: center; gap: 12px;
  padding-bottom: 12px;
}

.field-icon {
  color: #a8c8a8; flex-shrink: 0;
  transition: color 0.2s;
}
.field.focused .field-icon { color: #0a9b8a; }

.field-input {
  flex: 1; border: none; outline: none; background: transparent;
  font-family: system-ui, sans-serif;
  font-size: 17px; font-weight: 600; color: #0f1e12;
}
.field-input::placeholder { color: #b8d4b8; font-weight: 400; }

.eye-btn {
  background: none; border: none; cursor: pointer; padding: 2px; line-height: 0;
  color: #a8c8a8; transition: color 0.2s;
}
.eye-btn:hover { color: #0a9b8a; }

/* Animated underline — matches custom-select border style */
.field-line {
  height: 1.5px;
  background: rgba(29,113,105,0.2);
  position: relative;
  border-radius: 999px;
}
.field-line::after {
  content: '';
  position: absolute; inset: 0; left: 0;
  height: 100%;
  background: #0a9b8a;
  border-radius: 999px;
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s cubic-bezier(0.22,1,0.36,1);
}
.field.focused .field-line::after { transform: scaleX(1); }

/* ── Hint + autofill ── */
.hint-row {
  display: flex; align-items: center; justify-content: space-between;
  margin: -14px 0 28px;
}
.hint-text {
  font-family: system-ui, sans-serif;
  font-size: 12px; color: #8aaa8e; line-height: 1.5;
}
.hint-text strong { color: #0a9b8a; font-weight: 700; }

.autofill-btn {
  font-family: system-ui, sans-serif;
  font-size: 12px; font-weight: 700; color: #0a9b8a;
  background: rgba(10,155,138,0.07);
  border: 1.5px solid rgba(10,155,138,0.22);
  border-radius: 999px; padding: 5px 14px; cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.autofill-btn:hover { background: #0a9b8a; color: white; }

/* ── Submit CTA — styled exactly like .hero-cta from HomePage ── */
.submit-btn {
  width: 100%;
  display: inline-flex; align-items: center; justify-content: center; gap: 12px;
  font-family: system-ui, sans-serif;
  font-size: 16px; font-weight: 700;
  background: linear-gradient(135deg, #0a9b8a, #056b5e);
  color: white; border: none;
  padding: 18px 32px; border-radius: 4px;
  box-shadow: 0 16px 40px rgba(10,155,138,0.28);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s, background 0.3s;
  margin-bottom: 24px;
}
.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 22px 48px rgba(10,155,138,0.36);
}
.submit-btn:disabled { opacity: 0.8; cursor: not-allowed; transform: none; }
.submit-btn.success { background: linear-gradient(135deg, #1d7169, #0a9b8a); }

.btn-inner { display: flex; align-items: center; gap: 10px; }
.btn-spin {
  width: 18px; height: 18px;
  border: 2.5px solid rgba(255,255,255,0.3);
  border-top-color: white; border-radius: 50%;
  animation: spin 0.7s linear infinite; flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Submit arrow hover — matches .hero-cta svg */
.submit-btn svg { transition: transform 0.3s; }
.submit-btn:hover:not(:disabled) svg { transform: translateX(4px); }

/* ── Divider ── */
.divider-row {
  display: flex; align-items: center; gap: 14px;
  margin-bottom: 16px;
}
.divider-line { flex: 1; height: 1px; background: rgba(29,113,105,0.12); }
.divider-txt {
  font-family: system-ui, sans-serif;
  font-size: 12px; color: #8aaa8e;
}

/* ── Guest button — matches .nav-cta from HomePage ── */
.guest-btn {
  width: 100%;
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  font-family: system-ui, sans-serif;
  font-size: 14px; font-weight: 700;
  color: #0a9b8a; background: transparent;
  border: 1.5px solid #0a9b8a; border-radius: 999px;
  padding: 11px 22px; cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 28px;
}
.guest-btn:hover { background: #0a9b8a; color: white; }

/* ── Footer ── */
.form-footer {
  font-family: system-ui, sans-serif;
  font-size: 13px; color: #6a8e6e;
  text-align: center;
}
.footer-link {
  color: #0a9b8a; font-weight: 700;
  text-decoration: none; transition: opacity 0.2s;
}
.footer-link:hover { opacity: 0.7; }

/* ── Shared animations ── */
@keyframes fade-up {
  from { opacity: 0; transform: translateY(22px); }
  to   { opacity: 1; transform: none; }
}

/* ── Responsive ── */
@media (max-width: 980px) {
  .layout { grid-template-columns: 1fr; }
  .map-col { display: none; }
  .form-col {
    background: transparent;
    backdrop-filter: none;
    border-left: none;
    padding: 80px 28px 60px;
  }
  .hero-tag { display: none; }
}
</style>