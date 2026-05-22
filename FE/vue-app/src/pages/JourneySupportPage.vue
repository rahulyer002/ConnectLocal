<template>
  <MainLayout>
    <div class="journey-page" :class="['phase-' + phase]">
    <div class="noise" aria-hidden="true"></div>
    <div class="orb orb-1" aria-hidden="true"></div>
    <div class="orb orb-2" aria-hidden="true"></div>

    <!-- ─── MAIN CANVAS: full-bleed map + floating panels ─── -->
    <main class="journey-canvas">
      <!-- Google Map container -->
      <div ref="mapEl" class="map-canvas" aria-label="Interactive journey map"></div>

      <!-- Map loading -->
      <transition name="overlay-fade">
        <div v-if="!mapReady && !mapError" class="map-overlay loading-overlay">
          <div class="loading-orb">
            <div class="loading-ring"></div>
            <div class="loading-pin">📍</div>
          </div>
          <h2>Preparing your map…</h2>
          <p>Loading streets, transit, and 3D buildings.</p>
        </div>
      </transition>

      <!-- Map error -->
      <transition name="overlay-fade">
        <div v-if="mapError" class="map-overlay error-overlay">
          <div class="error-card">
            <div class="error-icon">⚠️</div>
            <h2>Map unavailable</h2>
            <p class="error-msg">{{ mapError }}</p>
            <details class="error-help">
              <summary>How to fix this</summary>
              <div class="error-help-body">
                <p>Add to your <code>.env</code> in the project root:</p>
                <pre>VITE_GOOGLE_MAPS_API_KEY=your_api_key_here
                  VITE_GOOGLE_MAPS_MAP_ID=your_map_id_here</pre>
                <p>The Map ID is optional but unlocks <strong>3D buildings + tilt</strong>. Get one in the Google Cloud Console under <em>Maps Management → Map Styles</em>.</p>
                <p>Restart <code>npm run dev</code> after editing.</p>
              </div>
            </details>
          </div>
        </div>
      </transition>

      <!-- ─── TOP TOOLBAR: layer toggles (visible in all phases) ───
      <transition name="toolbar-slide">
        <div v-show="mapReady" class="float-toolbar">
          <button
            v-for="l in layerDefs"
            :key="l.id"
            class="toolbar-pill"
            :class="{ active: layerState[l.id] }"
            @click="toggleLayer(l.id)"
            :aria-pressed="layerState[l.id]"
          >
            <span class="pill-icon" :style="{ background: l.color, color: l.fg }">{{ l.icon }}</span>
            <span class="pill-label">{{ l.label }}</span>
            <span v-if="layerLoading[l.id]" class="pill-spinner"></span>
            <span v-else-if="layerState[l.id] && layerData[l.id].length" class="pill-count">{{ layerData[l.id].length }}</span>
          </button>
        </div>
      </transition> -->

      <!-- Right-side floating controls -->
      <div v-show="mapReady" class="float-controls">
        <button class="ctrl-btn" @click="recenter" title="Recenter">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>
          </svg>
        </button>
        <button v-if="canUse3D" class="ctrl-btn ctrl-3d" :class="{ active: tilted3D }" @click="toggle3D" :title="tilted3D ? 'Flatten to 2D' : 'Tilt to 3D'">
          <span class="threed-label">{{ tilted3D ? '2D' : '3D' }}</span>
        </button>
        <button class="ctrl-btn ctrl-zoom" @click="zoomIn" title="Zoom in">＋</button>
        <button class="ctrl-btn ctrl-zoom" @click="zoomOut" title="Zoom out">−</button>
      </div>

      <!-- ─── ASIDE PANEL ─── -->
      <aside class="float-panel" :class="['panel-' + phase, { collapsed: panelCollapsed }]">
        <button class="panel-collapse" @click="panelCollapsed = !panelCollapsed" :title="panelCollapsed ? 'Expand' : 'Collapse'">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <polyline :points="panelCollapsed ? '9 18 15 12 9 6' : '15 18 9 12 15 6'"/>
          </svg>
        </button>

        <!-- ═══ PHASE: PLAN ═══ -->
        <div v-if="phase === 'plan'" class="phase-plan-content">
          <div class="plan-hero">
            <span class="plan-eyebrow">Journey Planner</span>
            <h1>Get there<br/>comfortably.</h1>
            <p>Plan a route with toilets, rest stops, and accessibility info along the way.</p>
          </div>

          <div class="plan-form">
            <!-- FROM row -->
            <div class="form-row" :class="{ focused: fromFocused }">
              <div class="form-pin pin-from">
                <span class="pin-dot pin-dot-from"></span>
              </div>
              <div class="form-input-wrap">
                <label class="form-label">From</label>
                <input
                  v-model="fromText"
                  type="text"
                  class="form-input"
                  placeholder="Suburb, address, place name…"
                  @input="onFromInput"
                  @focus="onFromFocus"
                  @blur="onFromBlur"
                  ref="fromInputEl"
                />
              </div>
              <button class="form-locate" :class="{ loading: isLocating }" @click="locateMe" :disabled="isLocating" title="Use my current location">
                <span v-if="!isLocating">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <circle cx="12" cy="12" r="3"/>
                    <path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>
                  </svg>
                </span>
                <span v-else class="mini-spinner"></span>
              </button>
              <div
                v-if="fromFocused && fromText.trim().length >= 2 && (fromSuggestions.length || fromSearchError)"
                class="form-dropdown"
              >
                <p v-if="fromSearchError" class="dropdown-error" role="alert">{{ fromSearchError }}</p>
                <button
                  v-for="(s, i) in fromSuggestions"
                  :key="s.id || i"
                  class="dropdown-item"
                  @mousedown.prevent="pickFromSuggestion(s)"
                >
                  <span class="suggest-icon">📍</span>
                  <span class="suggest-name">
                    <strong>{{ s.name || s.suburb_name }}</strong>
                    <small v-if="s.address">{{ s.address }}</small>
                  </span>
                </button>
              </div>
            </div>

            <!-- Swap button between rows -->
            <div class="form-swap-rail">
              <button class="form-swap-btn" :disabled="!canSwap" @click="swapEndpoints" title="Swap from and to">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <path d="M7 4v16M3 8l4-4 4 4"/>
                  <path d="M17 20V4M21 16l-4 4-4-4"/>
                </svg>
              </button>
            </div>

            <!-- TO row -->
            <div class="form-row" :class="{ focused: toFocused }">
              <div class="form-pin pin-to">
                <span class="pin-dot pin-dot-to"></span>
              </div>
              <div class="form-input-wrap">
                <label class="form-label">To</label>
                <input
                  v-model="toText"
                  type="text"
                  class="form-input"
                  placeholder="A suburb, café, park, address — anywhere"
                  @input="onToInput"
                  @focus="onToFocus"
                  @blur="onToBlur"
                  ref="toInputEl"
                />
              </div>
              <div
                v-if="toFocused && toText.trim().length >= 2 && (toSuggestions.length || toSearchError)"
                class="form-dropdown"
              >
                <p v-if="toSearchError" class="dropdown-error" role="alert">{{ toSearchError }}</p>
                <button
                  v-for="(s, i) in toSuggestions"
                  :key="s.id || i"
                  class="dropdown-item"
                  @mousedown.prevent="pickToSuggestion(s)"
                >
                  <span class="suggest-icon">📍</span>
                  <span class="suggest-name">
                    <strong>{{ s.name || s.suburb_name }}</strong>
                    <small v-if="s.address">{{ s.address }}</small>
                  </span>
                </button>
              </div>
            </div>

            <!-- ── When row + inline picker popup ── -->
            <div class="when-wrap" ref="whenWrapEl">
              <div class="form-row when-row" :class="{ focused: whenPickerOpen }" @click="toggleWhenPicker">
                <div class="form-pin pin-when">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <circle cx="12" cy="12" r="9"/>
                    <path d="M12 7v5l3 2"/>
                  </svg>
                </div>
                <div class="form-input-wrap">
                  <label class="form-label">When</label>
                  <p class="form-input when-value">{{ whenBarText }}</p>
                </div>
                <svg class="when-chevron" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <polyline points="6 9 12 15 18 9"/>
                </svg>
              </div>

              <!-- Popup — anchored under the bar, NOT a full overlay -->
              <transition name="when-pop">
                <div
                  v-if="whenPickerOpen"
                  class="when-pop"
                  role="dialog"
                  aria-label="Choose departure time"
                  @click.stop
                >
                  <header class="when-pop-head">
                    <h3 class="when-pop-title">When are you travelling?</h3>
                    <button type="button" class="when-pop-close" @click="closeWhenPicker" aria-label="Close">
                      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <path d="M18 6 6 18M6 6l12 12"/>
                      </svg>
                    </button>
                  </header>

                  <!-- Mode toggle -->
                  <div class="time-mode-toggle" role="tablist" aria-label="Departure mode">
                    <button
                      type="button"
                      role="tab"
                      class="time-mode"
                      :class="{ active: timeMode === 'now' }"
                      :aria-selected="timeMode === 'now'"
                      @click="pickLeaveNow"
                    >
                      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <circle cx="12" cy="12" r="9"/>
                        <path d="M12 7v5l3 2"/>
                      </svg>
                      Leave now
                    </button>
                    <button
                      type="button"
                      role="tab"
                      class="time-mode"
                      :class="{ active: timeMode === 'arrive' }"
                      :aria-selected="timeMode === 'arrive'"
                      @click="setTimeMode('arrive')"
                    >
                      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <rect x="3" y="4" width="18" height="17" rx="2"/>
                        <path d="M16 2v4M8 2v4M3 10h18"/>
                      </svg>
                      Arrive by a time
                    </button>
                  </div>

                  <!-- Day + time chips -->
                  <div v-if="timeMode === 'arrive'" class="time-picker-card">
                    <div class="time-picker-section">
                      <p class="time-picker-label">Day</p>
                      <div class="time-chip-row">
                        <button
                          v-for="d in dayChoices"
                          :key="d.iso"
                          type="button"
                          class="time-chip"
                          :class="{ active: d.iso === selectedDay }"
                          @click="selectedDay = d.iso"
                        >
                          <span class="chip-top">{{ d.short }}</span>
                          <span class="chip-bottom">{{ d.sub }}</span>
                        </button>
                      </div>
                    </div>

                    <div class="time-picker-section">
                      <p class="time-picker-label">Time</p>
                      <div class="time-chip-grid">
                        <button
                          v-for="h in hourChoices"
                          :key="h.value"
                          type="button"
                          class="time-chip time-chip-hour"
                          :class="{ active: h.value === selectedHour }"
                          @click="pickArriveHour(h.value)"
                        >
                          {{ h.label }}
                        </button>
                      </div>
                    </div>

                    <p v-if="arriveByHumanLabel" class="time-picker-summary">
                      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <path d="M20 6 9 17l-5-5"/>
                      </svg>
                      Arriving <strong>{{ arriveByHumanLabel }}</strong>
                    </p>
                  </div>

                  <button
                    type="button"
                    class="when-pop-done"
                    :disabled="timeMode === 'arrive' && !arriveByHumanLabel"
                    @click="closeWhenPicker"
                  >
                    Done
                  </button>
                </div>
              </transition>
            </div>

            <button class="form-submit" :disabled="!canSearch || isSearching" @click="findRoute">
              <span v-if="isSearching" class="mini-spinner light"></span>
              <span v-else>Find my route</span>
              <svg v-if="!isSearching" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <line x1="5" y1="12" x2="19" y2="12"/>
                <polyline points="12 5 19 12 12 19"/>
              </svg>
            </button>

            <p v-if="searchError" class="search-error" role="alert">{{ searchError }}</p>
          </div>

          <!-- Recents -->
          <div v-if="recentDestinations.length" class="plan-section">
            <h3 class="plan-section-title">Recent journeys</h3>
            <div class="recents-list">
              <button v-for="(r, i) in recentDestinations" :key="i" class="recent-pill" @click="useRecent(r)">
                <span class="recent-icon">↗</span>
                <span class="recent-name">{{ r.name }}</span>
              </button>
            </div>
          </div>

          <!-- Tips / what's new -->
          <div class="plan-tips">
            <div class="tip-card">
              <div class="tip-icon" style="background:#fce8d4;color:#a85a1f">🚻</div>
              <div>
                <strong>Toilets along the way</strong>
                <p>Public toilets near every stop on your route.</p>
              </div>
            </div>
            <div class="tip-card">
              <div class="tip-icon" style="background:#dff3dc;color:#286c2a">🌳</div>
              <div>
                <strong>Green rest stops</strong>
                <p>Parks &amp; benches show up next to your route.</p>
              </div>
            </div>
            <div class="tip-card">
              <div class="tip-icon" style="background:#dceafd;color:#1d4ed8">♿</div>
              <div>
                <strong>Accessibility-first</strong>
                <p>Step-free transit and lift access on each stop.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- ═══ PHASE: ROUTES ═══ -->
        <div v-else-if="phase === 'routes'" class="phase-routes-content">
          <div class="routes-header">
            <button class="header-back" @click="returnToPlan" title="Edit journey">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <div class="routes-header-text">
              <span class="routes-eyebrow">{{ routes.length }} {{ routes.length === 1 ? 'route' : 'routes' }} found</span>
              <h2>{{ truncate(fromText, 26) }} <span class="arrow">→</span> {{ truncate(toText, 26) }}</h2>
            </div>
          </div>

          <div v-if="leaveByText" class="leave-callout">
            <div class="callout-icon">⏰</div>
            <div class="callout-body">
              <strong>Leave by {{ leaveByText }}</strong>
              <p>To arrive at <span>{{ arriveAtText }}</span></p>
            </div>
          </div>

          <div class="routes-list">
            <button
              v-for="(r, idx) in routes"
              :key="idx"
              class="route-card"
              :class="{ selected: idx === selectedRouteIdx }"
              @click="selectRoute(idx)"
            >
              <div class="route-card-top">
                <span v-if="idx === 0" class="badge badge-comfort">Most comfortable</span>
                <span v-else-if="idx === routes.length - 1 && routes.length > 1" class="badge badge-fast">Fastest</span>
                <span v-else class="badge badge-alt">Alternative {{ idx }}</span>
                <span class="route-time">{{ r.duration_text }}</span>
              </div>
              <div class="route-meta">
                <span>Leave {{ r.leave_by_text }}</span>
                <span class="dot-sep">·</span>
                <span>Arrive {{ r.arrive_at_text }}</span>
              </div>
              <div class="route-legs">
                <template v-for="(leg, j) in r.leg_pills" :key="j">
                  <span class="leg-pill" :class="`leg-${leg.kind}`">
                    <span class="leg-icon">{{ leg.icon }}</span>
                    <span v-if="leg.label" class="leg-label">{{ leg.label }}</span>
                  </span>
                  <span v-if="j < r.leg_pills.length - 1" class="leg-arrow">›</span>
                </template>
              </div>
              <div v-if="r.transfers > 0" class="route-transfers">
                {{ r.transfers }} {{ r.transfers === 1 ? 'transfer' : 'transfers' }}
              </div>
            </button>
          </div>

          <div v-if="selectedRoute" class="route-actions">
            <button class="action-secondary" @click="returnToPlan">Adjust trip</button>
            <button class="action-primary" @click="startNavigation">
              Start journey
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
          </div>
        </div>

        <!-- ═══ PHASE: NAVIGATE ═══ -->
        <div v-else-if="phase === 'navigate'" class="phase-navigate-content">
          <div class="nav-header">
            <button class="header-back" @click="exitToRoutes" title="Back to routes">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <div class="nav-header-text">
              <span class="nav-progress-text">Step {{ currentStepIdx + 1 }} of {{ steps.length }}</span>
              <h2 v-if="selectedRoute">Arrive {{ selectedRoute.arrive_at_text }}</h2>
            </div>
          </div>

          <div class="nav-progress-bar">
            <div class="nav-progress-fill" :style="{ width: navProgress + '%' }"></div>
          </div>

          <div v-if="currentStep" class="current-step" :class="`tone-${currentStep.kind}`" :key="currentStepIdx">
            <div class="step-icon-big" v-html="currentStep.iconSvg"></div>
            <div class="step-body">
              <span class="step-kind-label">{{ currentStep.kindLabel }}</span>
              <h3>{{ currentStep.title }}</h3>
              <p v-if="currentStep.detail" class="step-detail">{{ currentStep.detail }}</p>
              <div v-if="currentStep.flags?.length" class="step-flags">
                <span v-for="f in currentStep.flags" :key="f.label" class="step-flag">
                  <span>{{ f.icon }}</span> {{ f.label }}
                </span>
              </div>
            </div>
          </div>

          <div class="nav-controls">
            <button class="nav-prev" :disabled="currentStepIdx === 0" @click="prevStep">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="15 18 9 12 15 6"/></svg>
              Previous
            </button>
            <button v-if="currentStepIdx < steps.length - 1" class="nav-next" @click="nextStep">
              Next step
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9 18 15 12 9 6"/></svg>
            </button>
            <button v-else class="nav-finish" @click="finishJourney">
              Finish journey ✓
            </button>
          </div>

          <details class="all-steps" :open="false">
            <summary>All {{ steps.length }} steps</summary>
            <ol class="steps-list">
              <li v-for="(s, idx) in steps" :key="idx" :class="{ done: idx < currentStepIdx, current: idx === currentStepIdx }" @click="jumpToStep(idx)">
                <span class="step-num">{{ idx + 1 }}</span>
                <div class="step-li-body">
                  <strong>{{ s.title }}</strong>
                  <small v-if="s.detail">{{ s.detail }}</small>
                </div>
                <span class="step-li-icon" v-html="s.iconSmallSvg"></span>
              </li>
            </ol>
          </details>
        </div>
      </aside>

      <!-- ─── BOTTOM BAR (navigate only): comfort stats ─── -->
      <transition name="slide-up">
        <div v-if="phase === 'navigate' && selectedRoute" class="float-bottom">
          <div class="bottom-stat">
            <span class="stat-label">Total</span>
            <span class="stat-value">{{ selectedRoute.duration_text }}</span>
          </div>
          <div class="bottom-stat">
            <span class="stat-label">Walking</span>
            <span class="stat-value">{{ totalWalkText }}</span>
          </div>
          <div class="bottom-stat">
            <span class="stat-label">Transfers</span>
            <span class="stat-value">{{ selectedRoute.transfers }}</span>
          </div>
          <button class="bottom-end" @click="finishJourney">End journey</button>
        </div>
      </transition>
    </main>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import { uiStore } from '../stores/uiStore'
import { resonanceStore } from '../stores/resonanceStore'
import { useJourneyApi, searchSuburbs, decodePolyline, extractPath } from '../composables/useJourneyApi'
// import { useNominatimSearch } from '../composables/useNominatimSearch'

const route = useRoute()
const router = useRouter()
const api = useJourneyApi()

// ─── Env config ───
const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''
const GOOGLE_MAPS_MAP_ID = import.meta.env.VITE_GOOGLE_MAPS_MAP_ID || 'DEMO_MAP_ID'
const RECENT_KEY = 'connectlocal-journey-recent'
const MELBOURNE_FALLBACK = { lat: -37.8136, lng: 144.9631 }

// ─── Page state ───
const phase = ref('plan') // 'plan' | 'routes' | 'navigate'
const panelCollapsed = ref(false)

// ─── Map state ───
const mapEl = ref(null)
const map = ref(null)
const mapReady = ref(false)
const mapError = ref('')
const tilted3D = ref(false)
const canUse3D = computed(() => !!GOOGLE_MAPS_MAP_ID && GOOGLE_MAPS_MAP_ID !== '')

// Live map objects (raw, not reactive — Vue + GMaps don't mix well)
let userMarker = null
let destMarker = null
let routePolylines = []
let stepHighlightMarker = null
let infoWindow = null

// ─── Form state ───
const fromText = ref('')
const fromLat = ref(null)
const fromLon = ref(null)
const fromInputEl = ref(null)
const fromFocused = ref(false)
const fromSuggestions = ref([])
const fromSearchError = ref('')  // v8: shown in dropdown when search fails or no matches
let fromDebounce = null

const toText = ref('')
const toLat = ref(null)
const toLon = ref(null)
const toInputEl = ref(null)
const toFocused = ref(false)
const toSuggestions = ref([])
const toSearchError = ref('')    // v8: shown in dropdown when search fails or no matches
let toDebounce = null
const arriveByInputEl = ref(null)

// v8: Google-Maps-style place search backed by OpenStreetMap Nominatim.
// Returns normalised results: { id, name, address, lat, lon, kind }
async function nominatimSearch(text) {
  const p = new URLSearchParams({
    q: text,
    format: 'jsonv2',
    addressdetails: '1',
    limit: '8',
    countrycodes: 'au',
    'accept-language': 'en',
    viewbox: '144.55,-37.40,145.85,-38.45',  // Melbourne bbox — soft bias
    bounded: '0',
  })
  const r = await fetch(`https://nominatim.openstreetmap.org/search?${p}`)
  if (!r.ok) throw new Error(`Search failed (${r.status})`)
  const items = await r.json()
  if (!Array.isArray(items)) return []
  return items.reduce((out, it) => {
    const lat = Number(it?.lat), lon = Number(it?.lon)
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) return out
    const a = it?.address || {}
    let name = a.amenity || a.shop || a.building || a.tourism
    if (!name && a.house_number) name = `${a.house_number} ${a.road || ''}`.trim()
    if (!name) name = a.road || a.suburb || a.town || a.city || a.locality
                    || a.neighbourhood || it.name || (it.display_name || '').split(',')[0]
    if (!name) return out
    out.push({ id: String(it.place_id), name: String(name).trim(), address: it.display_name || '', lat, lon })
    return out
  }, [])
}

const arriveBy = ref('')
const isLocating = ref(false)
const isSearching = ref(false)
const searchError = ref('')

// ─── v9: Custom date/time picker state ─────────────────────────────────
// Replaces the native datetime-local input which looked browser-specific
// and inconsistent. Uses team-branded chip controls instead.
const timeMode    = ref('now')      // 'now' | 'arrive'
const selectedDay = ref('')         // ISO date 'YYYY-MM-DD'
const selectedHour = ref(null)      // 0–23 (matches user's 24h clock)

// Build 'YYYY-MM-DD' from a Date using LOCAL components.
// toISOString() converts to UTC first, which in Melbourne (UTC+10/+11) shifts
// the date back one day for local-midnight Dates. That caused the picker to
// show "today" while actually meaning yesterday.
function localIsoDate(d) {
  const y  = d.getFullYear()
  const m  = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${dd}`
}

// Next 7 days as choosable chips. First two get friendly labels.
const dayChoices = computed(() => {
  const days = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const DOW = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
  for (let i = 0; i < 7; i++) {
    const d = new Date(today)
    d.setDate(today.getDate() + i)
    const iso = localIsoDate(d)
    const short = i === 0 ? 'Today' : i === 1 ? 'Tomorrow' : DOW[d.getDay()]
    const sub   = i < 2 ? `${DOW[d.getDay()]} ${d.getDate()}` : `${d.getDate()} ${d.toLocaleString('en-AU', { month: 'short' })}`
    days.push({ iso, short, sub })
  }
  return days
})

// 5 AM through 10 PM in 1-hour steps — practical hours people travel
const hourChoices = computed(() => {
  const list = []
  for (let h = 5; h <= 22; h++) {
    let label
    if (h === 0)        label = '12 AM'
    else if (h === 12)  label = '12 PM'
    else if (h < 12)    label = `${h} AM`
    else                label = `${h - 12} PM`
    list.push({ value: h, label })
  }
  return list
})

// Switching modes resets sensible defaults
function setTimeMode(mode) {
  timeMode.value = mode
  if (mode === 'now') {
    selectedDay.value  = ''
    selectedHour.value = null
  } else {
    // Default to today + next sensible hour
    if (!selectedDay.value) selectedDay.value = localIsoDate(new Date())
    if (selectedHour.value == null) {
      const next = new Date()
      next.setMinutes(0); next.setSeconds(0); next.setMilliseconds(0)
      next.setHours(next.getHours() + 1)
      const h = next.getHours()
      // Clamp to our chip range so the highlighted chip is always visible
      selectedHour.value = Math.min(22, Math.max(5, h))
    }
  }
}

// arriveBy stays the source of truth that the rest of the page uses.
// When the user changes day/hour, we recompute it. When timeMode is 'now',
// arriveBy is empty (which the existing search code already treats as "now").
watch([timeMode, selectedDay, selectedHour], () => {
  if (timeMode.value !== 'arrive' || !selectedDay.value || selectedHour.value == null) {
    arriveBy.value = ''
    return
  }
  // Build a local datetime string in the same shape datetime-local used,
  // so the existing `new Date(arriveBy.value).toISOString()` call still works.
  const hh = String(selectedHour.value).padStart(2, '0')
  arriveBy.value = `${selectedDay.value}T${hh}:00`
})

// Human-friendly summary shown under the chip grid
const arriveByHumanLabel = computed(() => {
  if (timeMode.value !== 'arrive' || !arriveBy.value) return ''
  const d = new Date(arriveBy.value)
  if (isNaN(d.getTime())) return ''
  const today = new Date(); today.setHours(0, 0, 0, 0)
  const that = new Date(d); that.setHours(0, 0, 0, 0)
  const diffDays = Math.round((that - today) / 86400000)
  let dayPart = ''
  if (diffDays === 0)      dayPart = 'today'
  else if (diffDays === 1) dayPart = 'tomorrow'
  else                     dayPart = d.toLocaleDateString('en-AU', { weekday: 'long', day: 'numeric', month: 'short' })
  const h = d.getHours()
  let timePart
  if (h === 0)        timePart = '12 AM'
  else if (h === 12)  timePart = '12 PM'
  else if (h < 12)    timePart = `${h} AM`
  else                timePart = `${h - 12} PM`
  return `${dayPart} at ${timePart}`
})

// ─── When-bar overlay state ───
const whenPickerOpen = ref(false)
const whenWrapEl = ref(null)
const nowTick = ref(Date.now())   // refreshes the "Leave now" label live
let nowTickTimer = null

// Live-updating text for the "Leave now" mode: shows current day + hour
const leaveNowText = computed(() => {
  // depend on nowTick so this recomputes every minute
  void nowTick.value
  const d = new Date()
  const today = new Date(); today.setHours(0, 0, 0, 0)
  const that = new Date(d); that.setHours(0, 0, 0, 0)
  const diffDays = Math.round((that - today) / 86400000)
  let dayPart
  if (diffDays === 0)      dayPart = 'today'
  else if (diffDays === 1) dayPart = 'tomorrow'
  else                     dayPart = d.toLocaleDateString('en-AU', { weekday: 'long', day: 'numeric', month: 'short' })
  const h = d.getHours()
  const m = String(d.getMinutes()).padStart(2, '0')
  let hh
  if (h === 0)        hh = `12:${m} AM`
  else if (h === 12)  hh = `12:${m} PM`
  else if (h < 12)    hh = `${h}:${m} AM`
  else                hh = `${h - 12}:${m} PM`
  return `Leave now · ${dayPart} at ${hh}`
})

// What the WHEN bar shows
const whenBarText = computed(() => {
  if (timeMode.value === 'arrive' && arriveByHumanLabel.value) {
    return `Arrive by ${arriveByHumanLabel.value}`
  }
  return leaveNowText.value
})

function openWhenPicker() {
  whenPickerOpen.value = true
}

function closeWhenPicker() {
  whenPickerOpen.value = false
}

function toggleWhenPicker() {
  whenPickerOpen.value = !whenPickerOpen.value
}

// Wrap setTimeMode('now') so the picker closes when the user taps Leave now
function pickLeaveNow() {
  setTimeMode('now')
  closeWhenPicker()
}

// Wrap hour selection so the picker closes after a complete pick (day + hour set)
function pickArriveHour(value) {
  selectedHour.value = value
  // Only close if both a day and hour are now chosen — leaves room for the
  // user to change their mind on the day before closing.
  if (selectedDay.value && value != null) {
    setTimeout(() => closeWhenPicker(), 180)
  }
}

const recentDestinations = ref(loadRecents())

// ─── Routes / steps state ───
const routes = ref([])
const selectedRouteIdx = ref(0)
const selectedRoute = computed(() => routes.value[selectedRouteIdx.value] || null)
const steps = computed(() => selectedRoute.value?.steps || [])
const currentStepIdx = ref(0)
const currentStep = computed(() => steps.value[currentStepIdx.value] || null)
const navProgress = computed(() => {
  if (!steps.value.length) return 0
  return Math.round(((currentStepIdx.value + 1) / steps.value.length) * 100)
})

const leaveByText = computed(() => selectedRoute.value?.leave_by_text || '')
const arriveAtText = computed(() => selectedRoute.value?.arrive_at_text || '')
const totalWalkText = computed(() => {
  const r = selectedRoute.value
  if (!r) return '—'
  if (r.walk_minutes != null) return `${r.walk_minutes} min`
  return '—'
})

// ─── Computed gates ───
const canSwap = computed(() => fromLat.value != null && toLat.value != null)
const canSearch = computed(() => fromLat.value != null && fromLon.value != null && toLat.value != null && toLon.value != null)

// ─── Helpers ───
function truncate(s, n) {
  if (!s) return ''
  return s.length > n ? s.slice(0, n - 1) + '…' : s
}

function loadRecents() {
  try {
    const raw = localStorage.getItem(RECENT_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed.slice(0, 4) : []
  } catch { return [] }
}

function saveRecent(entry) {
  try {
    const existing = loadRecents().filter(r => r.name !== entry.name)
    const next = [entry, ...existing].slice(0, 4)
    localStorage.setItem(RECENT_KEY, JSON.stringify(next))
    recentDestinations.value = next
  } catch {}
}

function fmtTime(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    if (isNaN(d.getTime())) return iso
    return d.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
  } catch { return iso }
}

// ═════════ GOOGLE MAPS LOADER (FIXED) ═════════
// Uses the official callback pattern so importLibrary is guaranteed
// to be fully wired up before we call it — eliminating the race condition
// that caused "importLibrary is not a function" on first load.
function loadGoogleMaps(key) {
  // Already fully loaded — nothing to do
  if (window.google?.maps?.importLibrary) return Promise.resolve()

  if (!key) return Promise.reject(new Error('No Google Maps API key configured.'))

  const SCRIPT_ID = 'gmaps-loader-script'

  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error('Map loading timed out. Check your API key and network connection.'))
    }, 15000)

    // The callback Google calls AFTER importLibrary is fully initialised
    window.__onGoogleMapsLoaded = () => {
      clearTimeout(timeout)
      resolve()
    }

    // Script already injected (e.g. hot-reload) — poll until callback fires
    if (document.getElementById(SCRIPT_ID)) {
      const tick = setInterval(() => {
        if (window.google?.maps?.importLibrary) {
          clearInterval(tick)
          clearTimeout(timeout)
          resolve()
        }
      }, 80)
      return
    }

    // Inject the Maps script with the callback parameter.
    // Google calls window.__onGoogleMapsLoaded ONLY after importLibrary is ready,
    // which is later than onload — that was the root cause of the original bug.
    const s = document.createElement('script')
    s.id = SCRIPT_ID
    s.async = true
    s.defer = true
    s.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(key)}&v=weekly&libraries=geometry,marker,places&loading=async&callback=__onGoogleMapsLoaded`
    s.onerror = () => {
      clearTimeout(timeout)
      reject(new Error('Failed to load Google Maps. Check your API key and that the Maps JavaScript API is enabled.'))
    }
    document.head.appendChild(s)
  })
}

async function initMap() {
  if (!GOOGLE_MAPS_API_KEY) {
    mapError.value = 'No Google Maps API key configured. The page works, but the map is hidden.'
    return
  }
  try {
    await loadGoogleMaps(GOOGLE_MAPS_API_KEY)
    const { Map } = await window.google.maps.importLibrary('maps')

    const center = (resonanceStore.userLat && resonanceStore.userLon)
      ? { lat: resonanceStore.userLat, lng: resonanceStore.userLon }
      : MELBOURNE_FALLBACK

    const opts = {
      center,
      zoom: 13,
      disableDefaultUI: true,
      gestureHandling: 'greedy',
      clickableIcons: false,
      mapId: GOOGLE_MAPS_MAP_ID,
      backgroundColor: '#eef5e8'
    }

    map.value = new Map(mapEl.value, opts)
    infoWindow = new window.google.maps.InfoWindow({ pixelOffset: new window.google.maps.Size(0, -8) })
    mapReady.value = true

    if (resonanceStore.userLat && resonanceStore.userLon) {
      placeUserMarker(resonanceStore.userLat, resonanceStore.userLon)
    }

    await applyQueryState()
  } catch (e) {
    console.error('[Journey] Map init failed:', e)
    mapError.value = e.message || 'Could not load the map.'
  }
}

// ═════════ MARKER HELPERS ═════════
async function getMarkerLib() {
  return await window.google.maps.importLibrary('marker')
}

function makePinHTML({ icon, color = '#0a9b8a', label = '', size = 'md' }) {
  const div = document.createElement('div')
  div.className = `cl-pin cl-pin-${size}`
  div.innerHTML = `
    <div class="cl-pin-bubble" style="background:${color}">
      <span class="cl-pin-icon">${icon}</span>
    </div>
    ${label ? `<span class="cl-pin-label">${label}</span>` : ''}
    <div class="cl-pin-tail" style="background:${color}"></div>
  `
  return div
}

async function placeUserMarker(lat, lng) {
  if (!map.value) return
  const { AdvancedMarkerElement } = await getMarkerLib()
  if (userMarker) userMarker.map = null
  userMarker = new AdvancedMarkerElement({
    position: { lat, lng },
    map: map.value,
    content: makePinHTML({ icon: '👤', color: '#0a9b8a', label: 'You', size: 'lg' }),
    zIndex: 1000
  })
}

async function placeDestMarker(lat, lng, name = '') {
  if (!map.value) return
  const { AdvancedMarkerElement } = await getMarkerLib()
  if (destMarker) destMarker.map = null
  destMarker = new AdvancedMarkerElement({
    position: { lat, lng },
    map: map.value,
    content: makePinHTML({ icon: '🎯', color: '#ee6c4d', label: name || 'Destination', size: 'lg' }),
    zIndex: 999
  })
}

// ═════════ ROUTE RENDERING ═════════
function clearRoutePolylines() {
  for (const p of routePolylines) p.setMap(null)
  routePolylines = []
}

let currentStepLines = []
function clearCurrentStepHighlight() {
  for (const l of currentStepLines) l.setMap(null)
  currentStepLines = []
}

function renderCurrentStepHighlight() {
  clearCurrentStepHighlight()
  if (phase.value !== 'navigate') return
  if (!map.value || !currentStep.value) return
  const path = currentStep.value.path
  if (!path?.length || path.length < 2) return

  const color = legColor(currentStep.value.kind)
  const halo = new window.google.maps.Polyline({
    path,
    strokeColor: '#ffffff',
    strokeOpacity: 1,
    strokeWeight: 14,
    zIndex: 80,
    map: map.value
  })
  const line = new window.google.maps.Polyline({
    path,
    strokeColor: color,
    strokeOpacity: 1,
    strokeWeight: 8,
    zIndex: 81,
    map: map.value
  })
  currentStepLines.push(halo, line)
}

function renderRoutesOnMap() {
  if (!map.value) return
  clearRoutePolylines()
  clearCurrentStepHighlight()
  if (!routes.value.length) return

  const bounds = new window.google.maps.LatLngBounds()

  routes.value.forEach((r, idx) => {
    const isSelected = idx === selectedRouteIdx.value
    const path = r.full_path
    if (!path?.length || path.length < 2) return

    const halo = new window.google.maps.Polyline({
      path,
      strokeColor: '#ffffff',
      strokeOpacity: isSelected ? 0.95 : 0.5,
      strokeWeight: isSelected ? 9 : 6,
      zIndex: isSelected ? 10 : 5,
      map: map.value
    })
    routePolylines.push(halo)

    const legs = r.legs_geometry?.length ? r.legs_geometry : [{ kind: r.leg_pills?.[0]?.kind || 'walk', path }]
    legs.forEach(leg => {
      if (!leg.path?.length || leg.path.length < 2) return
      const isWalk = leg.kind === 'walk' || leg.kind === 'bike'
      const color = isSelected ? legColor(leg.kind) : '#9ca3af'

      const opts = {
        path: leg.path,
        strokeColor: color,
        strokeOpacity: isWalk ? 0 : (isSelected ? 0.95 : 0.55),
        strokeWeight: isSelected ? 5 : 3.5,
        zIndex: isSelected ? 11 : 6,
        map: map.value
      }
      if (isWalk) {
        opts.icons = [{
          icon: {
            path: 'M 0,-1 0,1',
            strokeOpacity: isSelected ? 0.95 : 0.55,
            strokeColor: color,
            scale: isSelected ? 4 : 3
          },
          offset: '0',
          repeat: '14px'
        }]
      }
      const line = new window.google.maps.Polyline(opts)
      routePolylines.push(line)
    })

    if (isSelected) {
      path.forEach(p => bounds.extend(new window.google.maps.LatLng(p.lat, p.lng)))
    }
  })

  if (!bounds.isEmpty()) {
    map.value.fitBounds(bounds, { top: 100, bottom: 100, left: 480, right: 100 })
  }

  if (phase.value === 'navigate') {
    renderCurrentStepHighlight()
  }
}

function legColor(kind) {
  switch (kind) {
    case 'walk':  return '#0a9b8a'
    case 'bike':  return '#0e8d7e'
    case 'bus':   return '#f59e0b'
    case 'tram':  return '#0ea5b7'
    case 'train': return '#ef4444'
    default:      return '#0a9b8a'
  }
}

// ═════════ MAP CONTROLS ═════════
function recenter() {
  if (!map.value) return
  if (resonanceStore.userLat && resonanceStore.userLon) {
    map.value.panTo({ lat: resonanceStore.userLat, lng: resonanceStore.userLon })
    map.value.setZoom(15)
  } else if (selectedRoute.value?.full_path?.length) {
    const bounds = new window.google.maps.LatLngBounds()
    selectedRoute.value.full_path.forEach(p => bounds.extend(new window.google.maps.LatLng(p.lat, p.lng)))
    map.value.fitBounds(bounds, { top: 80, bottom: 80, left: 480, right: 80 })
  } else {
    map.value.panTo(MELBOURNE_FALLBACK)
    map.value.setZoom(13)
  }
}

function toggle3D() {
  if (!map.value || !canUse3D.value) return
  tilted3D.value = !tilted3D.value
  if (tilted3D.value) {
    map.value.setTilt(67.5)
    map.value.setHeading(20)
    if (map.value.getZoom() < 16) map.value.setZoom(16)
  } else {
    map.value.setTilt(0)
    map.value.setHeading(0)
  }
}

function zoomIn() {
  if (!map.value) return
  map.value.setZoom((map.value.getZoom() || 13) + 1)
}
function zoomOut() {
  if (!map.value) return
  map.value.setZoom((map.value.getZoom() || 13) - 1)
}

// ═════════ FORM / AUTOCOMPLETE ═════════
// v8: Switched from internal suburb list to Nominatim — supports any place
// (houses, buildings, addresses, toilets, parks, landmarks) across Australia,
// not just our hand-curated Melbourne suburbs.
async function onFromInput() {
  fromLat.value = null; fromLon.value = null
  if (fromDebounce) clearTimeout(fromDebounce)
  const text = fromText.value.trim()
  if (!text || text.length < 2) {
    fromSuggestions.value = []
    fromSearchError.value = ''
    return
  }
  fromDebounce = setTimeout(async () => {
    try {
      const items = await nominatimSearch(text)
      fromSuggestions.value = items
      fromSearchError.value = items.length ? '' : `No places match "${text}". Try a different search.`
    } catch (e) {
      fromSuggestions.value = []
      fromSearchError.value = "Couldn't search right now. Please try again."
    }
  }, 280)
}

function onFromFocus() { fromFocused.value = true }
function onFromBlur() { setTimeout(() => { fromFocused.value = false }, 180) }

function pickFromSuggestion(s) {
  fromText.value = s.name || s.suburb_name
  fromLat.value = s.lat ?? s.centroid_lat ?? s.latitude
  fromLon.value = s.lon ?? s.centroid_lng ?? s.lng ?? s.longitude
  fromSuggestions.value = []
  fromSearchError.value = ''
  fromFocused.value = false
  if (mapReady.value && fromLat.value != null) {
    placeUserMarker(fromLat.value, fromLon.value)
    map.value?.panTo({ lat: fromLat.value, lng: fromLon.value })
  }
}

function clearFrom() {
  fromText.value = ''; fromLat.value = null; fromLon.value = null
  fromSuggestions.value = []; fromSearchError.value = ''
}

async function onToInput() {
  toLat.value = null; toLon.value = null
  if (toDebounce) clearTimeout(toDebounce)
  const text = toText.value.trim()
  if (!text || text.length < 2) {
    toSuggestions.value = []
    toSearchError.value = ''
    return
  }
  toDebounce = setTimeout(async () => {
    try {
      const items = await nominatimSearch(text)
      toSuggestions.value = items
      toSearchError.value = items.length ? '' : `No places match "${text}". Try a different search.`
    } catch (e) {
      toSuggestions.value = []
      toSearchError.value = "Couldn't search right now. Please try again."
    }
  }, 280)
}

function onToFocus() { toFocused.value = true }
function onToBlur() { setTimeout(() => { toFocused.value = false }, 180) }

function pickToSuggestion(s) {
  toText.value = s.name || s.suburb_name
  toLat.value = s.lat ?? s.centroid_lat ?? s.latitude
  toLon.value = s.lon ?? s.centroid_lng ?? s.lng ?? s.longitude
  toSuggestions.value = []
  toSearchError.value = ''
  toFocused.value = false
  if (mapReady.value && toLat.value != null) {
    placeDestMarker(toLat.value, toLon.value, toText.value)
  }
}

function clearTo() {
  toText.value = ''; toLat.value = null; toLon.value = null
  toSuggestions.value = []; toSearchError.value = ''
}

function swapEndpoints() {
  if (!canSwap.value) return
  const t = { text: fromText.value, lat: fromLat.value, lon: fromLon.value }
  fromText.value = toText.value; fromLat.value = toLat.value; fromLon.value = toLon.value
  toText.value = t.text; toLat.value = t.lat; toLon.value = t.lon
  if (fromLat.value != null) placeUserMarker(fromLat.value, fromLon.value)
  if (toLat.value != null) placeDestMarker(toLat.value, toLon.value, toText.value)
}

async function locateMe() {
  if (!navigator.geolocation) {
    searchError.value = 'Your browser does not support location services.'
    return
  }
  isLocating.value = true
  searchError.value = ''
  try {
    const pos = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 })
    })
    fromLat.value = pos.coords.latitude
    fromLon.value = pos.coords.longitude
    fromText.value = 'My current location'
    resonanceStore.setLocation?.(fromLat.value, fromLon.value, 'My current location')
    if (mapReady.value) {
      placeUserMarker(fromLat.value, fromLon.value)
      map.value?.panTo({ lat: fromLat.value, lng: fromLon.value })
      map.value?.setZoom(15)
    }
  } catch (e) {
    searchError.value = e?.message || 'Could not access your location. Please type your starting point.'
  } finally {
    isLocating.value = false
  }
}

function useRecent(r) {
  toText.value = r.name
  toLat.value = r.lat
  toLon.value = r.lon
  if (mapReady.value && r.lat != null) placeDestMarker(r.lat, r.lon, r.name)
}

// ═════════ SEARCH ROUTES ═════════
async function findRoute() {
  if (!canSearch.value) {
    searchError.value = 'Please pick both a starting point and a destination.'
    return
  }
  isSearching.value = true
  searchError.value = ''
  try {
    const params = {
      from_lat: fromLat.value,
      from_lon: fromLon.value,
      to_lat: toLat.value,
      to_lon: toLon.value
    }
    if (arriveBy.value) params.arrive_by = new Date(arriveBy.value).toISOString()

    const res = await api.fetchRoutes(params)
    const rawRoutes = res?.routes || res?.alternatives || (Array.isArray(res) ? res : null) || (res ? [res] : [])
    if (!rawRoutes.length) {
      searchError.value = 'No routes found between those points. Try adjusting your start, destination, or time.'
      isSearching.value = false
      return
    }
    routes.value = rawRoutes.map(parseSingleRoute).filter(Boolean)
    if (!routes.value.length) {
      searchError.value = 'Could not parse the routes returned. Please try again.'
      isSearching.value = false
      return
    }
    selectedRouteIdx.value = 0

    saveRecent({ name: toText.value, lat: toLat.value, lon: toLon.value })

    phase.value = 'routes'

    await nextTick()
    const wp = routes.value[0]?.waypoints
    const oc = wp?.origin_coords
    const dc = wp?.destination_coords
    const startLat = (oc?.lat ?? oc?.latitude) ?? fromLat.value
    const startLng = (oc?.lon ?? oc?.lng ?? oc?.longitude) ?? fromLon.value
    const endLat = (dc?.lat ?? dc?.latitude) ?? toLat.value
    const endLng = (dc?.lon ?? dc?.lng ?? dc?.longitude) ?? toLon.value

    if (startLat != null) placeUserMarker(startLat, startLng)
    if (endLat != null) placeDestMarker(endLat, endLng, toText.value)
    renderRoutesOnMap()
  } catch (e) {
    console.error('[Journey] Route search failed:', e)
    searchError.value = e?.message || 'Could not search for routes. Please try again.'
  } finally {
    isSearching.value = false
  }
}

function returnToPlan() {
  phase.value = 'plan'
  clearRoutePolylines()
  clearCurrentStepHighlight()
}

function selectRoute(idx) {
  if (idx === selectedRouteIdx.value) return
  selectedRouteIdx.value = idx
  currentStepIdx.value = 0
  renderRoutesOnMap()
}

function startNavigation() {
  if (!selectedRoute.value) return
  phase.value = 'navigate'
  currentStepIdx.value = 0
  panelCollapsed.value = false
  nextTick(() => {
    renderCurrentStepHighlight()
    focusStepOnMap(steps.value[0])
    if (canUse3D.value && !tilted3D.value) {
      toggle3D()
    }
  })
}

function exitToRoutes() {
  phase.value = 'routes'
  if (tilted3D.value) toggle3D()
  clearCurrentStepHighlight()
  renderRoutesOnMap()
}

function finishJourney() {
  phase.value = 'plan'
  if (tilted3D.value) toggle3D()
  clearRoutePolylines()
  clearCurrentStepHighlight()
  routes.value = []
  selectedRouteIdx.value = 0
  currentStepIdx.value = 0
}

// ═════════ STEP NAVIGATION ═════════
function nextStep() {
  if (currentStepIdx.value < steps.value.length - 1) {
    currentStepIdx.value++
    focusStepOnMap(steps.value[currentStepIdx.value])
  }
}

function prevStep() {
  if (currentStepIdx.value > 0) {
    currentStepIdx.value--
    focusStepOnMap(steps.value[currentStepIdx.value])
  }
}

function jumpToStep(idx) {
  currentStepIdx.value = idx
  focusStepOnMap(steps.value[idx])
}

function focusStepOnMap(step) {
  if (!map.value || !step) return
  renderCurrentStepHighlight()

  const path = step.path
  if (path?.length >= 2) {
    const bounds = new window.google.maps.LatLngBounds()
    path.forEach(p => bounds.extend(new window.google.maps.LatLng(p.lat, p.lng)))
    if (tilted3D.value) {
      const mid = path[Math.floor(path.length / 2)]
      map.value.panTo({ lat: mid.lat, lng: mid.lng })
      if (map.value.getZoom() < 17) map.value.setZoom(18)
    } else {
      map.value.fitBounds(bounds, { top: 80, bottom: 220, left: 480, right: 80, maxZoom: 18 })
    }
  } else if (step.start) {
    map.value.panTo({ lat: step.start.lat, lng: step.start.lng })
    if (map.value.getZoom() < 16) map.value.setZoom(17)
  }
}

// ═════════ ROUTE PARSING ═════════
function parseGeometry(g) {
  if (!g) return []
  if (g.type === 'LineString' && Array.isArray(g.coordinates)) {
    return g.coordinates.map(c => ({ lat: Number(c[1]), lng: Number(c[0]) }))
  }
  if (typeof g === 'string') return decodePolyline(g)
  if (typeof g.points === 'string') return decodePolyline(g.points)
  if (typeof g.polyline === 'string') return decodePolyline(g.polyline)
  if (Array.isArray(g)) {
    return g.map(p => Array.isArray(p) ? { lat: Number(p[0]), lng: Number(p[1]) } : p)
  }
  return []
}

function parseSingleRoute(r) {
  if (!r) return null

  const durationMin = r.total_duration_mins
    ?? (r.total_duration_secs ? Math.round(r.total_duration_secs / 60) : null)
    ?? r.duration_min ?? r.duration_minutes ?? null
  const durationText = r.total_duration_label
    || (durationMin != null ? `${durationMin} min` : '—')

  const distanceText = r.total_distance_label || ''

  const departureIso = r.departure_time || r.departure || null
  const leaveByIso = r.leave_by || r.leave_home_by || departureIso
  const arriveAtIso = r.arrival_time || r.arrive_at || null

  const transfers = r.transfers ?? r.num_transfers ?? 0

  const totalWalkM = r.total_walk_m ?? null
  let walkMinutes = r.walking_minutes ?? r.walk_minutes ?? null
  if (walkMinutes == null && totalWalkM) {
    walkMinutes = Math.max(1, Math.round(totalWalkM / 80))
  }
  const walkText = r.total_walk_label
    || (totalWalkM ? `${totalWalkM} m` : (walkMinutes ? `${walkMinutes} min` : '—'))

  const fullPath = parseGeometry(r.geometry)

  const flatSubSteps = []
  const topSteps = Array.isArray(r.steps) ? r.steps : []
  for (const top of topSteps) {
    const parentMode = top.travel_mode || top.mode || 'walking'
    const subs = Array.isArray(top.sub_steps) && top.sub_steps.length
      ? top.sub_steps
      : [top]
    for (const sub of subs) {
      flatSubSteps.push({
        ...sub,
        parent_mode: parentMode,
        instruction: sub.instruction || top.instruction || ''
      })
    }
  }

  const totalSubDist = flatSubSteps.reduce((s, x) => s + (x.distance_m || 0), 0)
  let cumDist = 0

  const steps = flatSubSteps.map((sub, idx) => {
    const startRatio = totalSubDist
      ? (cumDist / totalSubDist)
      : (idx / Math.max(1, flatSubSteps.length))
    cumDist += (sub.distance_m || 0)
    const endRatio = totalSubDist
      ? (cumDist / totalSubDist)
      : ((idx + 1) / Math.max(1, flatSubSteps.length))

    let stepPath = []
    if (fullPath.length > 1) {
      const startIdx = Math.max(0, Math.floor(startRatio * (fullPath.length - 1)))
      const endIdx = Math.min(fullPath.length - 1, Math.ceil(endRatio * (fullPath.length - 1)))
      stepPath = fullPath.slice(startIdx, endIdx + 1)
      if (stepPath.length < 2 && fullPath[startIdx + 1]) stepPath = [fullPath[startIdx], fullPath[startIdx + 1]]
    }

    const kind = classifyMode(sub.parent_mode || sub.travel_mode || 'walking')

    return {
      kind,
      kindLabel: kindLabel(kind),
      title: stripHtml(sub.instruction || sub.text || 'Continue'),
      detail: [sub.distance_label, sub.duration_label].filter(Boolean).join(' · '),
      duration_min: sub.duration_secs ? Math.round(sub.duration_secs / 60) : null,
      flags: [],
      iconSvg: kindIconSvg(kind),
      iconSmallSvg: kindIconSvgSmall(kind),
      path: stepPath,
      start: stepPath[0] || null,
      end: stepPath[stepPath.length - 1] || null,
      routeLabel: ''
    }
  })

  const legPills = (Array.isArray(r.legs_summary) ? r.legs_summary : []).map(leg => {
    const kind = classifyMode(leg.type || leg.mode || 'walking')
    return {
      kind,
      icon: kindIcon(kind),
      label: leg.duration_label || leg.distance_label || leg.label || ''
    }
  })
  if (!legPills.length && steps.length) {
    const seenKinds = new Set()
    for (const s of steps) {
      if (s.kind === 'arrive' || seenKinds.has(s.kind)) continue
      seenKinds.add(s.kind)
      legPills.push({ kind: s.kind, icon: kindIcon(s.kind), label: '' })
    }
  }

  const legsGeometry = []
  if (fullPath.length) {
    const dominantKind = legPills[0]?.kind || 'walk'
    legsGeometry.push({ kind: dominantKind, path: fullPath })
  }

  const destCoords = r.waypoints?.destination_coords
  const destName = r.waypoints?.destination
  if (destCoords) {
    const dLat = destCoords.lat ?? destCoords.latitude
    const dLng = destCoords.lon ?? destCoords.lng ?? destCoords.longitude
    if (dLat != null && dLng != null) {
      steps.push({
        kind: 'arrive',
        kindLabel: 'Arrive',
        title: destName ? `Arrive at ${destName.split(',')[0]}` : `You've arrived${toText.value ? ' at ' + toText.value : ''}`,
        detail: arriveAtIso ? `Arrive ${fmtTime(arriveAtIso)}` : (destName || null),
        iconSvg: kindIconSvg('arrive'),
        iconSmallSvg: kindIconSvgSmall('arrive'),
        flags: [],
        path: [],
        start: { lat: dLat, lng: dLng },
        end: { lat: dLat, lng: dLng },
        routeLabel: ''
      })
    }
  } else if (steps.length && toLat.value != null) {
    steps.push({
      kind: 'arrive',
      kindLabel: 'Arrive',
      title: `Arrive at ${toText.value || 'destination'}`,
      detail: arriveAtIso ? `Arrive ${fmtTime(arriveAtIso)}` : null,
      iconSvg: kindIconSvg('arrive'),
      iconSmallSvg: kindIconSvgSmall('arrive'),
      flags: [],
      path: [],
      start: { lat: toLat.value, lng: toLon.value },
      end: { lat: toLat.value, lng: toLon.value },
      routeLabel: ''
    })
  }

  return {
    duration_min: durationMin,
    duration_text: durationText,
    distance_text: distanceText,
    leave_by_iso: leaveByIso,
    leave_by_text: fmtTime(leaveByIso) || 'now',
    arrive_at_iso: arriveAtIso,
    arrive_at_text: fmtTime(arriveAtIso) || (durationMin != null ? `in ${durationMin} min` : ''),
    transfers,
    walk_minutes: walkMinutes,
    walk_text: walkText,
    summary: r.summary || '',
    recommendation_label: r.recommendation_label || (r.recommended ? 'Most comfortable' : ''),
    warnings: Array.isArray(r.warnings) ? r.warnings : [],
    steps,
    legs_geometry: legsGeometry,
    leg_pills: legPills,
    full_path: fullPath,
    waypoints: r.waypoints || null
  }
}

function classifyMode(travelMode, td) {
  const m = String(travelMode || '').toUpperCase().trim()
  if (m === 'WALKING' || m === 'WALK' || m === 'FOOT') return 'walk'
  if (m === 'BICYCLING' || m === 'BIKE' || m === 'CYCLING' || m === 'CYCLE') return 'bike'
  if (m === 'TRAIN' || m === 'RAIL' || m === 'METRO' || m === 'SUBWAY' || m === 'HEAVY_RAIL') return 'train'
  if (m === 'TRAM' || m === 'LIGHT_RAIL' || m === 'STREETCAR') return 'tram'
  if (m === 'BUS' || m === 'COACH') return 'bus'
  const v = (td?.line?.vehicle?.type || td?.vehicle_type || td?.mode || td?.type || '').toString().toUpperCase()
  if (v.includes('TRAIN') || v.includes('RAIL') || v.includes('METRO') || v.includes('SUBWAY') || v.includes('HEAVY')) return 'train'
  if (v.includes('TRAM') || v.includes('LIGHT') || v.includes('STREETCAR')) return 'tram'
  if (v.includes('BUS')) return 'bus'
  if (m === 'TRANSIT') return 'bus'
  return 'walk'
}

function stripHtml(s) {
  if (!s) return ''
  return String(s).replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').trim()
}

function kindIcon(kind) {
  switch (kind) {
    case 'walk': return '🚶'
    case 'bike': return '🚴'
    case 'bus': return '🚌'
    case 'tram': return '🚊'
    case 'train': return '🚆'
    case 'arrive': return '🎯'
    default: return '➡️'
  }
}

function kindLabel(kind) {
  switch (kind) {
    case 'walk': return 'Walk'
    case 'bike': return 'Cycle'
    case 'bus': return 'Take the bus'
    case 'tram': return 'Take the tram'
    case 'train': return 'Take the train'
    case 'arrive': return 'Arrive'
    default: return 'Travel'
  }
}

function kindIconSvg(kind) {
  const svgWrap = (path) => `<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${path}</svg>`
  switch (kind) {
    case 'walk': return svgWrap('<circle cx="12" cy="4" r="2"/><path d="M9 22l1-7 3-3 4 3-1-5-3-3-3 2-3 5"/>')
    case 'bike': return svgWrap('<circle cx="6" cy="17" r="3.5"/><circle cx="18" cy="17" r="3.5"/><path d="M6 17l4-9h4l4 9M14 4l2 4"/>')
    case 'bus': return svgWrap('<rect x="4" y="4" width="16" height="14" rx="2"/><path d="M4 11h16"/><circle cx="8" cy="18" r="1.5"/><circle cx="16" cy="18" r="1.5"/>')
    case 'tram': return svgWrap('<rect x="5" y="3" width="14" height="14" rx="2"/><path d="M5 10h14M9 17l-2 4M15 17l2 4"/>')
    case 'train': return svgWrap('<rect x="5" y="3" width="14" height="14" rx="3"/><circle cx="9" cy="11" r="1.4"/><circle cx="15" cy="11" r="1.4"/><path d="M9 17l-2 4M15 17l2 4M5 8h14"/>')
    case 'arrive': return svgWrap('<path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>')
    default: return svgWrap('<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>')
  }
}

function kindIconSvgSmall(kind) {
  return kindIconSvg(kind).replace('width="28"', 'width="18"').replace('height="28"', 'height="18"')
}

// ═════════ URL QUERY HANDLING ═════════
async function applyQueryState() {
  const q = route.query || {}

  if (q.from_lat && q.from_lon) {
    fromLat.value = parseFloat(q.from_lat); fromLon.value = parseFloat(q.from_lon)
    fromText.value = q.from_name || 'Custom location'
  } else if (resonanceStore.userLat && resonanceStore.userLon && resonanceStore.locationReady) {
    fromLat.value = resonanceStore.userLat
    fromLon.value = resonanceStore.userLon
    fromText.value = resonanceStore.locationLabel || 'My current location'
  }

  if (q.dest_lat && q.dest_lon) {
    toLat.value = parseFloat(q.dest_lat); toLon.value = parseFloat(q.dest_lon)
    toText.value = q.dest_name || 'Destination'
  } else if (q.destination || q.to_name || q.place) {
    const dest = q.destination || q.to_name || q.place
    toText.value = dest
    try {
      const res = await searchSuburbs(dest, 1)
      const first = (res?.suburbs || res || [])[0]
      if (first) {
        toLat.value = first.centroid_lat ?? first.lat
        toLon.value = first.centroid_lng ?? first.lng
      }
    } catch {}
  } else if (q.to_lat && q.to_lon) {
    toLat.value = parseFloat(q.to_lat); toLon.value = parseFloat(q.to_lon)
    toText.value = q.to_name || q.place || 'Destination'
  }

  if (q.arrive_by) {
    // Chatbot may pass either a full ISO string or 'HH:MM' (today's HH:MM).
    let iso = q.arrive_by
    if (/^\d{1,2}:\d{2}$/.test(iso)) {
      // 'HH:MM' → treat as today (local-time date, not UTC)
      const today = localIsoDate(new Date())
      iso = `${today}T${iso.padStart(5, '0')}:00`
    }
    const d = new Date(iso)
    if (!isNaN(d.getTime())) {
      timeMode.value     = 'arrive'
      selectedDay.value  = localIsoDate(d)
      selectedHour.value = d.getHours()
      // The watcher will set arriveBy.value to the normalised string
    }
  }

  if (mapReady.value) {
    if (fromLat.value != null) await placeUserMarker(fromLat.value, fromLon.value)
    if (toLat.value != null) await placeDestMarker(toLat.value, toLon.value, toText.value)
    if (fromLat.value != null && toLat.value != null) {
      const bounds = new window.google.maps.LatLngBounds()
      bounds.extend(new window.google.maps.LatLng(fromLat.value, fromLon.value))
      bounds.extend(new window.google.maps.LatLng(toLat.value, toLon.value))
      map.value.fitBounds(bounds, { top: 100, bottom: 100, left: 480, right: 100 })
    }
  }

  if (q.auto === '1' && canSearch.value) {
    setTimeout(() => findRoute(), 200)
  }
}

// ═════════ LIFECYCLE ═════════
function onWhenKey(e) {
  if (e.key === 'Escape' && whenPickerOpen.value) closeWhenPicker()
}

function onWhenOutside(e) {
  if (!whenPickerOpen.value) return
  const wrap = whenWrapEl.value
  if (wrap && !wrap.contains(e.target)) closeWhenPicker()
}

onMounted(async () => {
  await nextTick()
  await initMap()
  // Refresh the "Leave now" label every 30s so the displayed time stays current
  nowTickTimer = setInterval(() => { nowTick.value = Date.now() }, 30000)
  window.addEventListener('keydown', onWhenKey)
  // Use capture so we catch clicks before any v-if removes the target
  document.addEventListener('mousedown', onWhenOutside, true)
  document.addEventListener('touchstart', onWhenOutside, true)
})

onBeforeUnmount(() => {
  if (userMarker) userMarker.map = null
  if (destMarker) destMarker.map = null
  if (stepHighlightMarker) stepHighlightMarker.map = null
  clearRoutePolylines()
  clearCurrentStepHighlight()
  if (infoWindow) infoWindow.close()
  // Clean up the global callback to avoid leaks on hot-reload
  delete window.__onGoogleMapsLoaded
  if (nowTickTimer) clearInterval(nowTickTimer)
  window.removeEventListener('keydown', onWhenKey)
  document.removeEventListener('mousedown', onWhenOutside, true)
  document.removeEventListener('touchstart', onWhenOutside, true)
})

watch(selectedRouteIdx, () => {
  if (phase.value !== 'plan') renderRoutesOnMap()
})
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.journey-page {
  position: relative;
  background: #f2faf0;
  color: #1a2e1e;
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  overflow: hidden;
}

/* ─── Ambient ─── */
.noise {
  position: fixed; inset: 0; pointer-events: none; z-index: 1;
  opacity: 0.025;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)'/%3E%3C/svg%3E");
}
.orb { position: fixed; border-radius: 50%; filter: blur(90px); opacity: 0.32; z-index: 1; pointer-events: none; }
.orb-1 { width: 480px; height: 480px; background: #b8e8c8; top: -180px; right: -120px; }
.orb-2 { width: 400px; height: 400px; background: #c5e4d4; bottom: -160px; left: -120px; }

/* ─── Main canvas ─── */
.journey-canvas {
  position: relative;
  width: 100%;
  height: calc(100vh - 64px);
}

.map-canvas {
  position: absolute;
  inset: 0;
  background: #eef5e8;
  z-index: 2;
}

/* ─── Map overlays (loading / error) ─── */
.map-overlay {
  position: absolute;
  inset: 0;
  z-index: 30;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #f2faf0 0%, #e8f5e3 100%);
  text-align: center; padding: 40px;
}
.loading-orb {
  position: relative; width: 100px; height: 100px; margin-bottom: 24px;
}
.loading-ring {
  position: absolute; inset: 0; border-radius: 50%;
  border: 3px solid rgba(10, 155, 138, 0.15);
  border-top-color: #0a9b8a;
  animation: spin 1s linear infinite;
}
.loading-pin {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  font-size: 36px; animation: pulse 1.6s ease-in-out infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.12); } }
.loading-overlay h2 { font-family: Georgia, serif; font-size: 30px; color: #0f1e12; margin-bottom: 8px; }
.loading-overlay p { color: #4a6a4e; font-size: 16px; }

.error-overlay { background: linear-gradient(135deg, #fff7ed, #fef3e2); }
.error-card {
  max-width: 520px; padding: 40px;
  background: white; border-radius: 22px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(29, 113, 105, 0.1);
}
.error-icon { font-size: 50px; margin-bottom: 12px; }
.error-card h2 { font-family: Georgia, serif; font-size: 26px; margin-bottom: 8px; color: #0f1e12; }
.error-msg { color: #b45309; font-weight: 600; margin-bottom: 20px; }
.error-help { text-align: left; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; }
.error-help summary { cursor: pointer; font-weight: 700; color: #0f1e12; }
.error-help-body { padding-top: 14px; }
.error-help-body p { font-size: 14px; color: #4a6a4e; margin-bottom: 10px; }
.error-help code { background: #e5e7eb; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
.error-help pre {
  background: #1a2e1e; color: #d1fae5; padding: 12px 14px; border-radius: 8px;
  font-size: 13px; overflow-x: auto; margin: 8px 0;
}

.overlay-fade-enter-active, .overlay-fade-leave-active { transition: opacity 0.4s; }
.overlay-fade-enter-from, .overlay-fade-leave-to { opacity: 0; }

/* ─── Floating map controls (right side) ─── */
.float-controls {
  position: absolute; top: 32px; right: 24px; z-index: 20;
  display: flex; flex-direction: column; gap: 6px;
  background: rgba(255,255,255,0.85); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  padding: 6px; border-radius: 14px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.08), 0 0 0 1px rgba(29,113,105,0.08);
}
.ctrl-btn {
  width: 38px; height: 38px; display: flex; align-items: center; justify-content: center;
  border: none; background: transparent; border-radius: 10px; cursor: pointer;
  color: #3a5a3e; font-size: 18px; font-weight: 700;
  transition: background 0.18s, color 0.18s, transform 0.15s;
}
.ctrl-btn:hover { background: rgba(10, 155, 138, 0.1); color: #0a9b8a; }
.ctrl-btn.active {
  background: #0a9b8a; color: white;
  box-shadow: 0 4px 10px rgba(10, 155, 138, 0.3);
}
.threed-label { font-size: 13px; font-weight: 800; letter-spacing: 0.5px; }

/* ─── Floating side panel (left) ─── */
.float-panel {
  position: absolute; top: 25px; left: 24px;
  width: 420px; max-width: calc(100vw - 48px);
  max-height: calc(100vh - 108px);
  z-index: 25;
  background: rgba(255,255,255,0.85); backdrop-filter: blur(24px) saturate(180%); -webkit-backdrop-filter: blur(24px) saturate(180%);
  border-radius: 22px; padding: 24px;
  box-shadow: 0 14px 40px rgba(0,0,0,0.10), 0 0 0 1px rgba(29,113,105,0.08);
  overflow-y: auto; overflow-x: hidden;
  transition: transform 0.45s cubic-bezier(0.22, 1, 0.36, 1), max-height 0.45s, padding 0.3s;
  scrollbar-width: thin;
}
.float-panel::-webkit-scrollbar { width: 6px; }
.float-panel::-webkit-scrollbar-thumb { background: rgba(10, 155, 138, 0.2); border-radius: 3px; }
.float-panel.collapsed { transform: translateX(calc(-100% + 32px)); }
.panel-collapse {
  position: absolute; top: 50%; right: -14px; transform: translateY(-50%);
  width: 28px; height: 56px;
  background: white; border: 1px solid rgba(29, 113, 105, 0.12);
  border-radius: 0 14px 14px 0;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  color: #3a5a3e;
  box-shadow: 6px 0 16px rgba(0,0,0,0.05);
  z-index: 1;
  transition: background 0.18s, color 0.18s;
}
.panel-collapse:hover { background: #0a9b8a; color: white; }

/* ─── PHASE: PLAN ─── */
.phase-plan-content { animation: fadeUp 0.4s ease-out; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

.plan-hero { margin-bottom: 24px; }
.plan-eyebrow {
  display: inline-block; padding: 6px 14px;
  background: linear-gradient(135deg, rgba(10,155,138,0.12), rgba(8,132,120,0.18));
  color: #066258; border-radius: 999px;
  font-size: 11.5px; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase;
  margin-bottom: 14px;
}
.plan-hero h1 {
  font-family: Georgia, serif; font-size: 40px; line-height: 1.05;
  color: #0f1e12; margin-bottom: 10px; letter-spacing: -0.02em;
}
.plan-hero p { color: #4a6a4e; font-size: 15.5px; line-height: 1.5; }

.plan-form {
  background: white;
  border: 1px solid rgba(29, 113, 105, 0.1);
  border-radius: 18px; padding: 18px; margin-bottom: 20px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.04);
}

.form-row {
  position: relative; display: flex; align-items: center; gap: 12px;
  background: #f7faf7; border: 1.5px solid #e5ede2;
  border-radius: 14px; padding: 8px 8px 8px 14px;
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
  min-height: 60px;
}
.form-row.focused {
  border-color: #0a9b8a; background: white;
  box-shadow: 0 0 0 4px rgba(10, 155, 138, 0.1);
}
.form-row + .form-row { margin-top: 0; }
.time-block { margin-top: 12px; display: flex; flex-direction: column; gap: 10px; }
.form-row-time { margin-top: 0; }

.form-pin {
  flex-shrink: 0; width: 24px; display: flex; align-items: center; justify-content: center;
}
.pin-dot {
  width: 12px; height: 12px; border-radius: 50%; display: block;
}
.pin-dot-from { background: #0a9b8a; box-shadow: 0 0 0 3px rgba(10,155,138,0.2); }
.pin-dot-to { background: #ee6c4d; box-shadow: 0 0 0 3px rgba(238,108,77,0.2); }
.pin-time { font-size: 17px; }

.form-input-wrap { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 1px; }
.form-label {
  font-size: 11px; font-weight: 700; letter-spacing: 0.6px; text-transform: uppercase;
  color: #6b8470; line-height: 1;
}
.form-input {
  width: 100%; border: none; background: transparent;
  padding: 0; font-size: 15px; font-weight: 500; color: #0f1e12;
  font-family: inherit; outline: none; line-height: 1.3;
}
.form-input::placeholder { color: #9eaba0; font-weight: 400; }
/* ═══════════════════════════════════════════════════════════════════════
   v9: TEAM-BRANDED date/time picker
   Replaces the native datetime-local + ad-hoc pill UI with consistent
   chip-based controls that match the rest of the journey planner.
   ═══════════════════════════════════════════════════════════════════════ */

/* Segmented toggle — Leave now / Arrive by */
.time-mode-toggle {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding: 4px;
  background: #f3f7f4;
  border: 1px solid rgba(29, 113, 105, 0.1);
  border-radius: 14px;
}
.time-mode {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 11px 14px;
  border: 1px solid transparent;
  background: transparent;
  border-radius: 10px;
  font-family: system-ui, sans-serif;
  font-size: 14.5px;
  font-weight: 700;
  color: #3a5a3e;
  cursor: pointer;
  transition: all 0.18s;
}
.time-mode:hover {
  color: #0a9b8a;
}
.time-mode.active {
  background: white;
  color: #066258;
  border-color: rgba(10, 155, 138, 0.2);
  box-shadow: 0 2px 6px rgba(10, 155, 138, 0.12);
}
.time-mode svg { flex-shrink: 0; }

/* Card that contains the day + time picker */
.time-picker-card {
  margin-top: 12px;
  padding: 16px;
  background: white;
  border: 1px solid rgba(29, 113, 105, 0.12);
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.time-picker-section { display: flex; flex-direction: column; gap: 8px; }
.time-picker-label {
  margin: 0;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: #6a8e6e;
  text-transform: uppercase;
}

/* Horizontal scrollable day row */
.time-chip-row {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  /* Soft scrollbar */
  scrollbar-width: thin;
  scrollbar-color: rgba(29, 113, 105, 0.25) transparent;
}
.time-chip-row::-webkit-scrollbar { height: 5px; }
.time-chip-row::-webkit-scrollbar-thumb { background: rgba(29, 113, 105, 0.25); border-radius: 3px; }

/* Grid for hour chips */
.time-chip-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 8px;
}
@media (max-width: 480px) {
  .time-chip-grid { grid-template-columns: repeat(4, 1fr); }
}

/* Individual chip — used for both day and hour */
.time-chip {
  flex-shrink: 0;
  min-width: 72px;
  padding: 10px 12px;
  background: white;
  border: 1.5px solid #e5ede2;
  border-radius: 10px;
  font-family: system-ui, sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #1a2e1e;
  cursor: pointer;
  transition: all 0.15s;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  line-height: 1.2;
}
.time-chip:hover {
  border-color: #0a9b8a;
  color: #0a9b8a;
  background: rgba(10, 155, 138, 0.04);
}
.time-chip.active {
  background: linear-gradient(135deg, #0a9b8a, #066258);
  border-color: #0a9b8a;
  color: white;
  box-shadow: 0 4px 12px rgba(10, 155, 138, 0.32);
}
.time-chip.active .chip-bottom { color: rgba(255, 255, 255, 0.85); }
.time-chip:focus-visible {
  outline: 3px solid rgba(10, 155, 138, 0.35);
  outline-offset: 2px;
}
.chip-top { font-size: 14px; font-weight: 700; }
.chip-bottom { font-size: 11px; color: #6a8e6e; font-weight: 500; }

.time-chip-hour {
  min-width: 0;
  padding: 12px 8px;
  font-size: 14.5px;
  font-weight: 700;
}

/* Human-friendly confirmation line */
.time-picker-summary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  padding: 10px 14px;
  background: rgba(10, 155, 138, 0.08);
  border-radius: 10px;
  font-size: 14px;
  color: #066258;
  font-family: system-ui, sans-serif;
}
.time-picker-summary svg { color: #0a9b8a; flex-shrink: 0; }
.time-picker-summary strong { font-weight: 700; }

/* ═══════════════════════════════════════════════════════════════════════
   WHEN bar + anchored popup picker
   ═══════════════════════════════════════════════════════════════════════ */
.when-wrap { position: relative; margin-top: 12px; }

.when-row { cursor: pointer; user-select: none; }
.when-row:hover {
  border-color: rgba(10, 155, 138, 0.4);
  background: white;
}
.when-row.focused {
  border-color: #0a9b8a;
  background: white;
  box-shadow: 0 0 0 4px rgba(10, 155, 138, 0.1);
}
.pin-when {
  color: #0a9b8a;
  display: flex; align-items: center; justify-content: center;
}
.when-value {
  margin: 0;
  font-size: 15px;
  font-weight: 500;
  color: #0f1e12;
  line-height: 1.3;
}
.when-chevron {
  color: #6b8470;
  flex-shrink: 0;
  margin-right: 8px;
  transition: transform 0.2s;
}
.when-row.focused .when-chevron { transform: rotate(180deg); color: #0a9b8a; }

/* Anchored popup — sits directly under the bar */
.when-pop {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  z-index: 30;
  background: white;
  border: 1px solid rgba(29, 113, 105, 0.14);
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.16), 0 4px 12px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.when-pop-head {
  display: flex; align-items: center; justify-content: space-between;
  gap: 10px;
}
.when-pop-title {
  font-family: Georgia, serif;
  font-size: 17px;
  color: #0f1e12;
  margin: 0;
  line-height: 1.2;
}
.when-pop-close {
  width: 28px; height: 28px;
  border: none; background: rgba(0, 0, 0, 0.05);
  border-radius: 50%; cursor: pointer; color: #3a5a3e;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.15s, color 0.15s;
  flex-shrink: 0;
}
.when-pop-close:hover { background: rgba(10, 155, 138, 0.12); color: #066258; }

.when-pop-done {
  padding: 11px 16px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #0a9b8a, #066258);
  color: white;
  font-family: system-ui, sans-serif;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(10, 155, 138, 0.28);
  transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s;
}
.when-pop-done:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(10, 155, 138, 0.38);
}
.when-pop-done:disabled { opacity: 0.5; cursor: not-allowed; }

/* Popup enter/leave transition */
.when-pop-enter-active,
.when-pop-leave-active {
  transition: opacity 0.18s ease, transform 0.18s cubic-bezier(0.22, 1, 0.36, 1);
  transform-origin: top center;
}
.when-pop-enter-from,
.when-pop-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.98);
}

.form-locate {
  width: 38px; height: 38px;
  border: none; background: rgba(10, 155, 138, 0.1); color: #0a9b8a;
  border-radius: 10px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.18s, transform 0.15s;
}
.form-locate:hover { background: rgba(10, 155, 138, 0.2); }
.form-locate:disabled { opacity: 0.5; cursor: wait; }

.form-clear {
  width: 24px; height: 24px; border: none; background: rgba(0,0,0,0.05);
  border-radius: 50%; cursor: pointer; color: #6b8470;
  font-size: 16px; line-height: 1;
}
.form-clear:hover { background: rgba(0,0,0,0.1); color: #0f1e12; }

.form-dropdown {
  position: absolute; top: calc(100% + 6px); left: 0; right: 0; z-index: 10;
  background: white; border: 1px solid rgba(29, 113, 105, 0.12);
  border-radius: 14px; padding: 6px;
  box-shadow: 0 12px 28px rgba(0,0,0,0.12);
  max-height: 280px; overflow-y: auto;
}
.dropdown-item {
  display: flex; align-items: center; gap: 12px;
  width: 100%; padding: 10px 12px;
  border: none; background: transparent;
  border-radius: 9px; cursor: pointer; text-align: left;
  transition: background 0.15s;
}
.dropdown-item:hover { background: rgba(10, 155, 138, 0.08); }
.suggest-icon { font-size: 16px; }
.suggest-name { display: flex; flex-direction: column; gap: 2px; min-width: 0; flex: 1; }
.suggest-name strong { font-size: 14.5px; color: #0f1e12; font-weight: 600; }
.suggest-name small {
  font-size: 12px; color: #6b8470;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.dropdown-error {
  margin: 0;
  padding: 12px 14px;
  font-size: 13.5px;
  color: #b3502a;
  font-weight: 500;
  font-family: system-ui, sans-serif;
}

.form-swap-rail {
  display: flex; justify-content: center; padding: 4px 0;
  position: relative;
}
.form-swap-rail::before {
  content: ''; position: absolute; left: 22px; top: 0; bottom: 0; width: 2px;
  background: repeating-linear-gradient(to bottom, #d3dccd 0 4px, transparent 4px 8px);
  border-radius: 1px;
}
.form-swap-btn {
  width: 28px; height: 28px;
  border: 1px solid rgba(29, 113, 105, 0.15);
  background: white; color: #3a5a3e;
  border-radius: 50%; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.18s, color 0.18s, transform 0.2s;
  position: relative; z-index: 1;
}
.form-swap-btn:hover:not(:disabled) {
  background: #0a9b8a; color: white; transform: rotate(180deg);
}
.form-swap-btn:disabled { opacity: 0.45; cursor: not-allowed; }

.form-submit {
  width: 100%; margin-top: 16px;
  display: flex; align-items: center; justify-content: center; gap: 10px;
  padding: 14px 20px;
  border: none; border-radius: 14px;
  background: linear-gradient(135deg, #0a9b8a, #066258);
  color: white; font-size: 15.5px; font-weight: 700;
  cursor: pointer;
  box-shadow: 0 8px 22px rgba(10, 155, 138, 0.35);
  transition: transform 0.18s, box-shadow 0.18s, opacity 0.18s;
}
.form-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 11px 26px rgba(10, 155, 138, 0.42);
}
.form-submit:disabled { opacity: 0.55; cursor: not-allowed; }

.search-error {
  margin-top: 12px; padding: 10px 12px;
  background: #fef2f2; border: 1px solid #fecaca;
  border-radius: 10px; color: #b91c1c;
  font-size: 13.5px; font-weight: 500;
}

.mini-spinner {
  display: inline-block; width: 16px; height: 16px;
  border: 2px solid rgba(0,0,0,0.15); border-top-color: currentColor;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
.mini-spinner.light { border-color: rgba(255,255,255,0.3); border-top-color: white; }

.plan-section { margin-bottom: 22px; }
.plan-section-title {
  font-size: 12px; font-weight: 700; letter-spacing: 1px;
  text-transform: uppercase; color: #6b8470;
  margin-bottom: 10px;
}
.recents-list { display: flex; flex-wrap: wrap; gap: 8px; }
.recent-pill {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 9px 14px;
  background: white; border: 1px solid rgba(29, 113, 105, 0.15);
  border-radius: 999px; cursor: pointer;
  font-size: 13px; font-weight: 600; color: #1a2e1e;
  transition: all 0.18s;
}
.recent-pill:hover { background: #0a9b8a; color: white; border-color: #0a9b8a; transform: translateY(-1px); }
.recent-icon { font-size: 13px; opacity: 0.7; }
.recent-pill:hover .recent-icon { opacity: 1; }

.plan-tips { display: flex; flex-direction: column; gap: 10px; }
.tip-card {
  display: flex; align-items: flex-start; gap: 12px;
  background: white; border: 1px solid rgba(29, 113, 105, 0.08);
  border-radius: 14px; padding: 14px;
}
.tip-icon {
  flex-shrink: 0; width: 38px; height: 38px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 10px; font-size: 18px;
}
.tip-card strong { display: block; font-size: 14px; color: #0f1e12; margin-bottom: 2px; }
.tip-card p { font-size: 13px; color: #4a6a4e; line-height: 1.4; }

/* ─── PHASE: ROUTES ─── */
.phase-routes-content { animation: fadeUp 0.4s ease-out; }
.routes-header {
  display: flex; align-items: center; gap: 14px; margin-bottom: 18px;
  padding-bottom: 16px; border-bottom: 1px solid rgba(29, 113, 105, 0.08);
}
.header-back {
  width: 36px; height: 36px;
  border: 1px solid rgba(29, 113, 105, 0.15);
  background: white; color: #3a5a3e;
  border-radius: 10px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  transition: all 0.18s;
}
.header-back:hover { background: #0a9b8a; color: white; border-color: #0a9b8a; }
.routes-header-text { min-width: 0; flex: 1; }
.routes-eyebrow {
  font-size: 11.5px; font-weight: 700; letter-spacing: 1px;
  text-transform: uppercase; color: #0a9b8a;
}
.routes-header-text h2 {
  font-family: Georgia, serif; font-size: 20px;
  color: #0f1e12; line-height: 1.25; margin-top: 4px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.routes-header-text h2 .arrow { color: #0a9b8a; margin: 0 4px; }

.leave-callout {
  display: flex; align-items: center; gap: 12px;
  background: linear-gradient(135deg, #ee6c4d, #d44827);
  color: white; border-radius: 14px; padding: 14px 16px;
  margin-bottom: 16px;
  box-shadow: 0 8px 22px rgba(238, 108, 77, 0.3);
}
.callout-icon { font-size: 22px; flex-shrink: 0; }
.callout-body strong { display: block; font-size: 16px; font-weight: 700; }
.callout-body p { font-size: 13px; opacity: 0.9; margin-top: 2px; }
.callout-body p span { font-weight: 700; }

.routes-list { display: flex; flex-direction: column; gap: 10px; margin-bottom: 18px; }
.route-card {
  width: 100%; text-align: left;
  background: white; border: 2px solid rgba(29, 113, 105, 0.1);
  border-radius: 16px; padding: 14px 16px;
  cursor: pointer;
  transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
}
.route-card:hover {
  border-color: rgba(10, 155, 138, 0.4); transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(0,0,0,0.06);
}
.route-card.selected {
  border-color: #0a9b8a;
  box-shadow: 0 8px 22px rgba(10, 155, 138, 0.18);
}

.route-card-top {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 6px;
}
.badge {
  display: inline-block; padding: 4px 10px;
  border-radius: 999px; font-size: 11px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.6px;
}
.badge-comfort { background: #ddf2ed; color: #066258; }
.badge-fast { background: #fde7d4; color: #b14b1f; }
.badge-alt { background: #ecf2e9; color: #4a6a4e; }
.route-time {
  font-family: Georgia, serif; font-size: 18px; font-weight: 700;
  color: #0f1e12;
}
.route-meta {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; color: #4a6a4e; margin-bottom: 10px;
}
.dot-sep { opacity: 0.4; }

.route-legs {
  display: flex; flex-wrap: wrap; align-items: center; gap: 4px;
  margin-bottom: 6px;
}
.leg-pill {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 12px; font-weight: 600;
}
.leg-pill .leg-icon { font-size: 13px; }
.leg-walk { background: #ecf2e9; color: #4a6a4e; }
.leg-bike { background: #e3eee3; color: #3a5a3e; }
.leg-bus { background: #fde7c4; color: #a85a1f; }
.leg-tram { background: #d3eef2; color: #0e6d7e; }
.leg-train { background: #fde2e2; color: #c1272d; }
.leg-arrow { color: #c0cdc1; font-size: 16px; font-weight: 600; }
.route-transfers {
  font-size: 12.5px; color: #6b8470; font-weight: 500;
}

.route-actions {
  position: sticky; bottom: -24px;
  display: flex; gap: 10px; padding: 14px 0;
  background: linear-gradient(to bottom, transparent, rgba(255,255,255,0.95) 30%);
}
.action-secondary, .action-primary {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 13px 18px;
  border: none; border-radius: 12px; cursor: pointer;
  font-size: 14.5px; font-weight: 700;
  transition: transform 0.18s, box-shadow 0.18s;
}
.action-secondary {
  flex: 1; background: white; color: #3a5a3e;
  border: 1.5px solid rgba(29, 113, 105, 0.15);
}
.action-secondary:hover { background: rgba(10, 155, 138, 0.06); border-color: #0a9b8a; color: #0a9b8a; }
.action-primary {
  flex: 1.5;
  background: linear-gradient(135deg, #0a9b8a, #066258);
  color: white;
  box-shadow: 0 6px 18px rgba(10, 155, 138, 0.32);
}
.action-primary:hover { transform: translateY(-1px); box-shadow: 0 9px 22px rgba(10, 155, 138, 0.42); }

/* ─── PHASE: NAVIGATE ─── */
.phase-navigate-content { animation: fadeUp 0.4s ease-out; }
.nav-header {
  display: flex; align-items: center; gap: 14px; margin-bottom: 14px;
}
.nav-header-text { flex: 1; min-width: 0; }
.nav-progress-text {
  font-size: 11.5px; font-weight: 700; letter-spacing: 1px;
  text-transform: uppercase; color: #0a9b8a;
}
.nav-header-text h2 {
  font-family: Georgia, serif; font-size: 22px; line-height: 1.25;
  color: #0f1e12; margin-top: 4px;
}

.nav-progress-bar {
  height: 4px; background: rgba(10, 155, 138, 0.1);
  border-radius: 2px; overflow: hidden; margin-bottom: 18px;
}
.nav-progress-fill {
  height: 100%; background: linear-gradient(90deg, #0a9b8a, #ee6c4d);
  border-radius: 2px;
  transition: width 0.5s cubic-bezier(0.22, 1, 0.36, 1);
}

.current-step {
  display: flex; align-items: flex-start; gap: 14px;
  padding: 18px;
  border-radius: 16px;
  margin-bottom: 16px;
  animation: stepIn 0.4s ease-out;
}
@keyframes stepIn { from { opacity: 0; transform: translateX(-12px); } to { opacity: 1; transform: translateX(0); } }
.current-step.tone-walk { background: linear-gradient(135deg, #f0f7ed, #e1efdc); }
.current-step.tone-bike { background: linear-gradient(135deg, #ecf4e8, #d8e9d2); }
.current-step.tone-bus { background: linear-gradient(135deg, #fdf2dc, #fbe4ba); }
.current-step.tone-tram { background: linear-gradient(135deg, #d8eef3, #bce0e8); }
.current-step.tone-train { background: linear-gradient(135deg, #fde2e2, #fbcfcf); }
.current-step.tone-arrive { background: linear-gradient(135deg, #fde0d3, #fac0a8); color: #5b1d0a; }
.step-icon-big {
  flex-shrink: 0; width: 52px; height: 52px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 14px;
  color: #0f1e12;
}
.current-step.tone-arrive .step-icon-big { color: #5b1d0a; }
.step-body { flex: 1; min-width: 0; }
.step-kind-label {
  display: inline-block;
  font-size: 11px; font-weight: 700; letter-spacing: 0.8px;
  text-transform: uppercase; color: rgba(15, 30, 18, 0.6);
  margin-bottom: 4px;
}
.step-body h3 {
  font-family: Georgia, serif; font-size: 18px; line-height: 1.3;
  color: #0f1e12; margin-bottom: 4px;
}
.step-detail { font-size: 14px; color: #3a5a3e; line-height: 1.45; }
.step-flags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.step-flag {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 9px;
  background: rgba(255,255,255,0.65);
  border-radius: 999px;
  font-size: 11.5px; font-weight: 600; color: #0f1e12;
}

.nav-controls { display: flex; gap: 10px; margin-bottom: 16px; }
.nav-prev, .nav-next, .nav-finish {
  flex: 1;
  display: flex; align-items: center; justify-content: center; gap: 7px;
  padding: 12px 16px;
  border: none; border-radius: 12px; cursor: pointer;
  font-size: 14px; font-weight: 700;
  transition: all 0.18s;
}
.nav-prev {
  background: white; color: #3a5a3e;
  border: 1.5px solid rgba(29, 113, 105, 0.15);
}
.nav-prev:hover:not(:disabled) { background: rgba(10, 155, 138, 0.06); border-color: #0a9b8a; color: #0a9b8a; }
.nav-prev:disabled { opacity: 0.4; cursor: not-allowed; }
.nav-next {
  background: linear-gradient(135deg, #0a9b8a, #066258);
  color: white;
  box-shadow: 0 5px 14px rgba(10, 155, 138, 0.32);
}
.nav-next:hover { transform: translateY(-1px); box-shadow: 0 8px 18px rgba(10, 155, 138, 0.42); }
.nav-finish {
  background: linear-gradient(135deg, #ee6c4d, #d44827);
  color: white;
  box-shadow: 0 5px 14px rgba(238, 108, 77, 0.32);
}
.nav-finish:hover { transform: translateY(-1px); }

.all-steps {
  background: white; border: 1px solid rgba(29, 113, 105, 0.08);
  border-radius: 12px; padding: 12px;
}
.all-steps summary {
  cursor: pointer; font-weight: 700; font-size: 13.5px;
  color: #3a5a3e; user-select: none;
}
.steps-list {
  list-style: none; margin-top: 12px;
  display: flex; flex-direction: column; gap: 4px;
}
.steps-list li {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 10px;
  border-radius: 9px; cursor: pointer;
  transition: background 0.18s;
}
.steps-list li:hover { background: rgba(10, 155, 138, 0.06); }
.steps-list li.current { background: rgba(10, 155, 138, 0.1); }
.steps-list li.done { opacity: 0.5; }
.step-num {
  width: 22px; height: 22px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: rgba(10, 155, 138, 0.12); color: #0a9b8a;
  border-radius: 50%; font-size: 11.5px; font-weight: 800;
}
.steps-list li.current .step-num { background: #0a9b8a; color: white; }
.step-li-body { flex: 1; min-width: 0; }
.step-li-body strong { display: block; font-size: 13.5px; color: #0f1e12; line-height: 1.3; }
.step-li-body small { font-size: 12px; color: #6b8470; }
.step-li-icon { color: #6b8470; flex-shrink: 0; }
.steps-list li.current .step-li-icon { color: #0a9b8a; }

/* ─── Bottom bar (navigate) ─── */
.float-bottom {
  position: absolute; bottom: 24px; left: 50%; transform: translateX(calc(-50% + 220px));
  z-index: 20;
  display: flex; gap: 18px; align-items: center;
  background: rgba(15, 30, 18, 0.92); color: white;
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  padding: 12px 20px; border-radius: 999px;
  box-shadow: 0 14px 38px rgba(0,0,0,0.25);
}
.bottom-stat { display: flex; flex-direction: column; align-items: center; min-width: 64px; }
.stat-label { font-size: 10.5px; opacity: 0.6; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 700; }
.stat-value { font-family: Georgia, serif; font-size: 18px; font-weight: 700; margin-top: 1px; }
.bottom-end {
  margin-left: 6px; padding: 9px 18px;
  border: none; border-radius: 999px;
  background: #ee6c4d; color: white;
  font-size: 13px; font-weight: 700; cursor: pointer;
  transition: background 0.18s, transform 0.15s;
}
.bottom-end:hover { background: #d44827; transform: translateY(-1px); }

.slide-up-enter-active, .slide-up-leave-active { transition: transform 0.45s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.3s; }
.slide-up-enter-from, .slide-up-leave-to { transform: translate(calc(-50% + 220px), 28px); opacity: 0; }

/* ─── Responsive ─── */
@media (max-width: 1024px) {
  .float-panel { width: 380px; left: 16px; top: 86px; }
  .float-bottom { transform: translateX(calc(-50% + 198px)); }
  .slide-up-enter-from, .slide-up-leave-to { transform: translate(calc(-50% + 198px), 28px); opacity: 0; }
}

@media (max-width: 760px) {
  .float-panel {
    width: calc(100vw - 24px);
    left: 12px; right: 12px;
    top: auto; bottom: 12px;
    max-height: 60vh;
    padding: 18px;
    border-radius: 18px 18px 14px 14px;
  }
  .float-panel.collapsed { transform: translateY(calc(100% - 56px)); }
  .panel-collapse {
    top: 6px; left: 50%; right: auto;
    transform: translateX(-50%);
    width: 56px; height: 28px;
    border-radius: 14px 14px 0 0;
    box-shadow: 0 -4px 12px rgba(0,0,0,0.05);
  }
  .panel-collapse svg { transform: rotate(90deg); }
  .float-toolbar {
    top: 32px; left: 12px; right: 12px; transform: none;
    max-width: none; justify-content: flex-start;
  }
  .toolbar-slide-enter-from, .toolbar-slide-leave-to { transform: translateY(-28px); opacity: 0; }
  .float-controls { top: 138px; right: 12px; }
  .float-bottom { left: 12px; right: 12px; transform: none; bottom: 12px; }
  .slide-up-enter-from, .slide-up-leave-to { transform: translateY(28px); opacity: 0; }
  .plan-hero h1 { font-size: 32px; }
}
</style>

<!-- Global styles for Google Maps marker HTML (cannot be scoped) -->
<style>
.cl-pin {
  position: relative;
  display: flex; flex-direction: column; align-items: center;
  pointer-events: auto;
  font-family: system-ui, -apple-system, sans-serif;
}
.cl-pin-bubble {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px;
  border-radius: 50% 50% 50% 4px;
  transform: rotate(-45deg);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25), 0 0 0 2px white;
  transition: transform 0.2s, box-shadow 0.2s;
}
.cl-pin-bubble:hover {
  transform: rotate(-45deg) scale(1.1);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3), 0 0 0 2px white;
}
.cl-pin-icon {
  transform: rotate(45deg);
  font-size: 15px;
  line-height: 1;
}
.cl-pin-tail { display: none; }
.cl-pin-label {
  position: absolute; top: -22px; left: 50%; transform: translateX(-50%);
  background: rgba(15, 30, 18, 0.92); color: white;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 11px; font-weight: 700;
  white-space: nowrap;
  box-shadow: 0 4px 10px rgba(0,0,0,0.18);
  letter-spacing: 0.3px;
}
.cl-pin-lg .cl-pin-bubble { width: 40px; height: 40px; }
.cl-pin-lg .cl-pin-icon { font-size: 18px; }
.cl-pin-sm .cl-pin-bubble { width: 26px; height: 26px; }
.cl-pin-sm .cl-pin-icon { font-size: 12px; }

/* Info window */
.cl-info {
  display: flex; gap: 10px;
  padding: 6px 4px 6px 0;
  font-family: system-ui, -apple-system, sans-serif;
  max-width: 240px;
}
.cl-info-icon {
  flex-shrink: 0; width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 10px; font-size: 18px;
}
.cl-info-body { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.cl-info-body strong { font-size: 14px; color: #0f1e12; }
.cl-info-body small { font-size: 12px; color: #4a6a4e; }
.cl-info-tag {
  display: inline-block; margin-top: 4px;
  background: #ddf2ed; color: #066258;
  padding: 2px 7px; border-radius: 6px;
  font-size: 11px; font-weight: 700;
  width: fit-content;
}
</style>