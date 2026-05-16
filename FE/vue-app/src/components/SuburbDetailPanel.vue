<template>
  <div class="panel-root">
    <!-- ── EMPTY STATE ─────────────────────────────────────── -->
    <div v-if="!suburbId" class="state empty-state">
      <div class="empty-art" aria-hidden="true">
        <svg viewBox="0 0 200 140" width="180" height="126">
          <circle cx="100" cy="80" r="46" fill="#e1f5ee" />
          <circle cx="100" cy="80" r="46" fill="none" stroke="#5DCAA5" stroke-width="2" stroke-dasharray="4 3"/>
          <circle cx="100" cy="80" r="6" fill="#0F6E56"/>
          <path d="M40 70 Q70 30 100 50 T160 60" stroke="#5DCAA5" stroke-width="2" fill="none" stroke-linecap="round"/>
          <circle cx="40" cy="70" r="3" fill="#0F6E56"/>
          <circle cx="100" cy="50" r="3" fill="#0F6E56"/>
          <circle cx="160" cy="60" r="3" fill="#0F6E56"/>
        </svg>
      </div>
      <h2 class="empty-title">Discover Melbourne</h2>
      <p class="empty-msg">
        Tap any suburb on the map to see how welcoming it is for older
        Melburnians.
      </p>
      <div v-if="topSuburbs.length" class="empty-quick">
        <p class="empty-quick-label">Start with one of these</p>
        <div class="empty-chips">
          <button
            v-for="s in topSuburbs.slice(0, 4)"
            :key="s.suburb_id"
            class="empty-chip"
            type="button"
            @click="$emit('select-suburb', s.suburb_id)"
          >
            <span class="empty-chip-name">{{ s.suburb_name }}</span>
            <span class="empty-chip-score">{{ Math.round(s.outing_score) }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ── ERROR STATE ─────────────────────────────────────── -->
    <div v-else-if="error && !isLoading" class="state error-state">
      <span class="err-ic" aria-hidden="true">⚠</span>
      <h3 class="err-title">Couldn't load this suburb</h3>
      <p class="err-msg">{{ error.message || 'Something went wrong.' }}</p>
      <button class="err-retry" type="button" @click="run()">Try again</button>
    </div>

    <!-- ── LOADING STATE ───────────────────────────────────── -->
    <div v-else-if="isLoading && !inference" class="state loading-state">
      <SkeletonBox width="60%" height="26px" />
      <SkeletonBox width="40%" height="14px" />
      <div style="margin: 20px auto"><SkeletonBox width="160px" height="160px" radius="80px" /></div>
      <SkeletonBox width="80%" height="14px" />
      <SkeletonBox width="100%" height="60px" />
      <SkeletonBox width="100%" height="48px" />
      <SkeletonBox width="100%" height="120px" />
    </div>

    <!-- ── LOADED CONTENT ─────────────────────────────────── -->
    <div v-else-if="inference" class="panel-content">
      <!-- Header (fixed) -->
      <header class="head">
        <div class="head-text">
          <h2 class="head-name">{{ inference.suburb_name || displayName }}</h2>
          <p class="head-meta">
            <span v-if="inference.persona" class="head-persona">{{ inference.persona }}</span>
            <span v-if="inference.counts?.dist_to_cbd_km != null" class="head-dist">
              {{ inference.counts.dist_to_cbd_km }} km from CBD
            </span>
          </p>
        </div>
        <button class="head-close" type="button" aria-label="Close" @click="$emit('close')">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </button>
      </header>

      <!-- Scrollable body -->
      <div class="body" ref="bodyEl">

        <!-- HERO RING -->
        <section class="hero">
          <div class="hero-ring" :style="{ width: HERO_RING_SIZE + 'px', height: HERO_RING_SIZE + 'px' }">
            <svg :viewBox="`0 0 ${HERO_RING_SIZE} ${HERO_RING_SIZE}`" :width="HERO_RING_SIZE" :height="HERO_RING_SIZE">
              <circle
                :cx="HERO_RING_SIZE / 2"
                :cy="HERO_RING_SIZE / 2"
                :r="heroRadius"
                fill="none"
                stroke="#E1F5EE"
                :stroke-width="HERO_STROKE"
              />
              <circle
                :cx="HERO_RING_SIZE / 2"
                :cy="HERO_RING_SIZE / 2"
                :r="heroRadius"
                fill="none"
                :stroke="ringColor(inference.outing_score)"
                :stroke-width="HERO_STROKE"
                stroke-linecap="round"
                :stroke-dasharray="heroCircumference"
                :stroke-dashoffset="animated ? heroOffset : heroCircumference"
                :transform="`rotate(-90 ${HERO_RING_SIZE / 2} ${HERO_RING_SIZE / 2})`"
                class="ring-progress"
              />
            </svg>
            <div class="hero-center">
              <span class="hero-num">{{ Math.round(inference.outing_score || 0) }}</span>
              <span class="hero-suf">out of 100</span>
            </div>
          </div>
          <div class="hero-caption">
            <p class="hero-label">Connection score</p>
            <span class="hero-band" :class="scoreClass">{{ scoreBand }}</span>
          </div>
        </section>

        <!-- NARRATIVE -->
        <p v-if="narrative" class="narrative">{{ narrative }}</p>

        <!-- PROFILE BARS -->
        <section class="block">
          <h3 class="block-title">Profile</h3>
          <div class="bars">
            <div class="bar-row">
              <p class="bar-label">Residents aged 65+</p>
              <p class="bar-value">{{ formatNum(inference.counts?.elderly_total) }}</p>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: animated ? barWidth(inference.counts?.elderly_total, 3000) : '0%' }">
                  <span class="bar-thumb" aria-hidden="true"></span>
                </div>
              </div>
            </div>

            <div class="bar-row">
              <p class="bar-label">Share of suburb</p>
              <p class="bar-value">{{ formatNum(inference.counts?.elderly_pct, 1) }}%</p>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: animated ? barWidth(inference.counts?.elderly_pct, 25) : '0%' }">
                  <span class="bar-thumb" aria-hidden="true"></span>
                </div>
              </div>
            </div>

            <div class="bar-row">
              <p class="bar-label">Distance from CBD</p>
              <p class="bar-value">{{ inference.counts?.dist_to_cbd_km ?? '—' }} km</p>
              <div class="bar-track">
                <div class="bar-fill bar-fill-inverse" :style="{ width: animated ? barWidth(inference.counts?.dist_to_cbd_km, 40) : '0%' }">
                  <span class="bar-thumb" aria-hidden="true"></span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- TABS (sticky) -->
        <nav class="tabs" role="tablist" aria-label="Detail sections">
          <button
            v-for="t in TABS"
            :key="t.key"
            type="button"
            role="tab"
            :aria-selected="activeTab === t.key"
            :class="['tab', { active: activeTab === t.key }]"
            @click="activeTab = t.key"
          >
            {{ t.label }}
          </button>
          <span class="tab-indicator" :style="indicatorStyle" aria-hidden="true"></span>
        </nav>

        <!-- TAB CONTENT -->
        <div class="tab-content">
          <transition name="tab-fade" mode="out-in">

            <!-- SCORE BREAKDOWN -->
            <div v-if="activeTab === 'breakdown'" key="breakdown" class="tab-pane">
              <div class="rings-grid">
                <div
                  v-for="(row, i) in subScoreRows"
                  :key="row.key"
                  class="ring-cell"
                  :style="{ animationDelay: (i * 30) + 'ms' }"
                >
                  <div class="cell-ring" :style="{ width: SMALL_RING_SIZE + 'px', height: SMALL_RING_SIZE + 'px' }">
                    <svg :viewBox="`0 0 ${SMALL_RING_SIZE} ${SMALL_RING_SIZE}`" :width="SMALL_RING_SIZE" :height="SMALL_RING_SIZE">
                      <circle
                        :cx="SMALL_RING_SIZE / 2"
                        :cy="SMALL_RING_SIZE / 2"
                        :r="smallRadius"
                        fill="none"
                        stroke="#E1F5EE"
                        :stroke-width="SMALL_STROKE"
                      />
                      <circle
                        :cx="SMALL_RING_SIZE / 2"
                        :cy="SMALL_RING_SIZE / 2"
                        :r="smallRadius"
                        fill="none"
                        :stroke="ringColor(row.value)"
                        :stroke-width="SMALL_STROKE"
                        stroke-linecap="round"
                        :stroke-dasharray="smallCircumference"
                        :stroke-dashoffset="animated ? smallOffset(row.value) : smallCircumference"
                        :transform="`rotate(-90 ${SMALL_RING_SIZE / 2} ${SMALL_RING_SIZE / 2})`"
                        class="ring-progress"
                        :style="{ transitionDelay: (i * 30 + 60) + 'ms' }"
                      />
                    </svg>
                    <div class="cell-center">
                      <span class="cell-num">{{ Math.round(row.value) }}</span>
                    </div>
                  </div>
                  <p class="cell-label">{{ row.label }}</p>
                </div>
              </div>

              <div v-if="hasGap" class="gap-card">
                <span class="gap-ic" aria-hidden="true">ⓘ</span>
                <p>
                  Limited amenity data here ({{ Math.round(inference.data_completeness_pct) }}% coverage).
                  Demographics and live conditions still work.
                </p>
              </div>
            </div>

            <!-- PLACES -->
            <div v-else-if="activeTab === 'places'" key="places" class="tab-pane">
              <div class="companion-card">
                <span class="companion-ic" aria-hidden="true">
                  <svg viewBox="0 0 24 24" width="22" height="22" stroke="#0F6E56" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                </span>
                <div class="companion-body">
                  <p class="companion-num">
                    <strong>{{ formatNum(inference.counts?.elderly_total || 0) }}</strong>
                    neighbours aged 65+
                  </p>
                  <p v-if="inference.counts?.elderly_pct" class="companion-sub">
                    Roughly 1 in {{ peopleRatio }} people you'll see locally
                  </p>
                </div>
              </div>

              <div class="tile-grid">
                <div class="tile tile-welcoming">
                  <span class="tile-ic" aria-hidden="true">
                    <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M5 21V8l7-4 7 4v13M9 21v-6h6v6"/></svg>
                  </span>
                  <p class="tile-num">{{ inference.counts?.welcoming_spaces ?? '—' }}</p>
                  <p class="tile-label">Welcoming spaces</p>
                </div>
                <div class="tile tile-cafe">
                  <span class="tile-ic" aria-hidden="true">
                    <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M17 8h1a3 3 0 0 1 0 6h-1M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/></svg>
                  </span>
                  <p class="tile-num">{{ inference.counts?.wc_social_count ?? '—' }}</p>
                  <p class="tile-label">Accessible cafés</p>
                </div>
                <div class="tile tile-park">
                  <span class="tile-ic" aria-hidden="true">
                    <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2 6 8a6 6 0 1 0 12 0Z M12 8v14"/></svg>
                  </span>
                  <p class="tile-num">{{ inference.counts?.green_space_count ?? '—' }}</p>
                  <p class="tile-label">Parks & green</p>
                </div>
                <div class="tile tile-events">
                  <span class="tile-ic" aria-hidden="true">
                    <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4M16 3v4M3 11h18"/></svg>
                  </span>
                  <p class="tile-num">{{ eventsCount }}</p>
                  <p class="tile-label">Events nearby</p>
                </div>
              </div>

              <div v-if="peers.length" class="peers">
                <h4 class="peers-title">Similar suburbs</h4>
                <div class="peer-list">
                  <button
                    v-for="p in peers"
                    :key="p.suburb_id"
                    type="button"
                    class="peer-row"
                    @click="$emit('select-suburb', p.suburb_id)"
                  >
                    <div class="peer-mini-ring" aria-hidden="true">
                      <svg viewBox="0 0 36 36" width="36" height="36">
                        <circle cx="18" cy="18" r="14" fill="none" stroke="#E1F5EE" stroke-width="3"/>
                        <circle cx="18" cy="18" r="14" fill="none"
                          :stroke="ringColor(p.outing_score || 0)"
                          stroke-width="3"
                          stroke-linecap="round"
                          stroke-dasharray="87.96"
                          :stroke-dashoffset="87.96 * (1 - Math.max(0, Math.min(100, Number(p.outing_score || 0))) / 100)"
                          transform="rotate(-90 18 18)"
                        />
                      </svg>
                      <span class="peer-mini-num">{{ Math.round(p.outing_score || 0) }}</span>
                    </div>
                    <div class="peer-meta">
                      <p class="peer-name">{{ p.suburb_name }}</p>
                      <p class="peer-reason">{{ p.reason }}</p>
                    </div>
                    <svg viewBox="0 0 24 24" width="14" height="14" class="peer-chev" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- COMFORT -->
            <div v-else-if="activeTab === 'comfort'" key="comfort" class="tab-pane">
              <div class="now-banner" :class="`now-${nowState}`">
                <span class="now-ic" aria-hidden="true">
                  <svg v-if="nowState === 'safe'" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01"/></svg>
                  <svg v-else-if="nowState === 'caution'" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0M12 9v4M12 17h.01"/></svg>
                  <svg v-else viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>
                </span>
                <div class="now-body">
                  <p class="now-title">{{ nowTitle }}</p>
                  <p class="now-sub">{{ nowSub }}</p>
                </div>
                <span v-if="snapshotApi.isLoading?.value" class="now-loading" aria-hidden="true"></span>
              </div>

              <div class="stat-grid">
                <div class="stat">
                  <p class="stat-num">{{ inference.counts?.stop_modes ?? '—' }}</p>
                  <p class="stat-lbl">Transit modes</p>
                </div>
                <div class="stat">
                  <p class="stat-num">{{ inference.counts?.stop_count ?? '—' }}</p>
                  <p class="stat-lbl">Stops nearby</p>
                </div>
                <div class="stat">
                  <p class="stat-num">{{ inference.counts?.bench_count ?? '—' }}</p>
                  <p class="stat-lbl">Rest benches</p>
                </div>
                <div class="stat">
                  <p class="stat-num">{{ inference.counts?.toilet_count ?? '—' }}</p>
                  <p class="stat-lbl">Accessible toilets</p>
                </div>
              </div>

              <div v-if="wcStopRatio" class="wc-bar">
                <div class="wc-bar-head">
                  <span class="wc-bar-label">Wheelchair-friendly stops</span>
                  <span class="wc-bar-value">{{ wcStopRatio.wc }} of {{ wcStopRatio.total }}</span>
                </div>
                <div class="bar-track">
                  <div class="bar-fill" :style="{ width: animated ? wcStopRatio.pct + '%' : '0%' }">
                    <span class="bar-thumb" aria-hidden="true"></span>
                  </div>
                </div>
                <p class="wc-bar-caption">{{ wcStopRatio.note }}</p>
              </div>
            </div>

          </transition>
        </div>
      </div>

      <!-- Action bar (fixed) -->
      <footer class="action-bar">
        <button class="action-btn" type="button" @click="$emit('find-events')">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4M16 3v4M3 11h18"/></svg>
          Events
        </button>
        <button class="action-btn" type="button" @click="$emit('plan-journey')">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="6" cy="19" r="3"/><circle cx="18" cy="5" r="3"/><path d="M6 16V9a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4"/></svg>
          Journey
        </button>
        <button class="action-btn action-primary" type="button" @click="$emit('view-on-map')">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12 22 7-7-7-7-7 7 7 7Z M5 15 12 8l7 7"/></svg>
          View on map
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import SkeletonBox from './SkeletonBox.vue'
import { useSuburbInference } from '../composables/useSuburbInference'
import { useApi, jsonFetcher } from '../composables/useApi'

const props = defineProps({
  suburbId:    { type: [Number, null], default: null },
  displayName: { type: String, default: '' },
  topSuburbs:  { type: Array,  default: () => [] },
})

defineEmits(['close', 'select-suburb', 'find-events', 'plan-journey', 'view-on-map'])

const BASE = import.meta.env.VITE_API_BASE_URL
  || import.meta.env.VITE_ACTIVITIES_API_URL
  || 'https://connectlocal.duckdns.org'

const HERO_RING_SIZE  = 160
const HERO_STROKE     = 12
const SMALL_RING_SIZE = 76
const SMALL_STROKE    = 6

const TABS = [
  { key: 'breakdown', label: 'Score' },
  { key: 'places',    label: 'Places' },
  { key: 'comfort',   label: 'Comfort' },
]

const SUB_SCORE_DEFS = [
  { key: 'rest',      label: 'Rest stops' },
  { key: 'relief',    label: 'Toilets' },
  { key: 'amenities', label: 'Amenities' },
  { key: 'shade',     label: 'Tree shade' },
  { key: 'transit',   label: 'Transit' },
  { key: 'social',    label: 'Social' },
]

const suburbIdRef = computed(() => props.suburbId)
const { data: inference, error, isLoading, run } = useSuburbInference(suburbIdRef)

const snapshotApi = useApi(async (signal) => {
  if (!props.suburbId) return null
  return jsonFetcher(`${BASE}/api/suburbs/${props.suburbId}/snapshot`, { signal })
}, { autoRetry: 1, timeoutMs: 12_000 })

const activeTab = ref('breakdown')
const animated  = ref(false)
const bodyEl    = ref(null)

watch(() => props.suburbId, async (id) => {
  if (id == null) return
  animated.value = false
  activeTab.value = 'breakdown'
  if (bodyEl.value) bodyEl.value.scrollTop = 0
  await run()
  await snapshotApi.run()
  await nextTick()
  setTimeout(() => { animated.value = true }, 50)
}, { immediate: true })

// ── Ring geometry ─────────────────────────────────────────────
const heroRadius        = computed(() => (HERO_RING_SIZE - HERO_STROKE) / 2)
const heroCircumference = computed(() => 2 * Math.PI * heroRadius.value)
const heroOffset        = computed(() => {
  const v = Math.max(0, Math.min(100, Number(inference.value?.outing_score || 0)))
  return heroCircumference.value * (1 - v / 100)
})

const smallRadius        = computed(() => (SMALL_RING_SIZE - SMALL_STROKE) / 2)
const smallCircumference = computed(() => 2 * Math.PI * smallRadius.value)
function smallOffset(value) {
  const v = Math.max(0, Math.min(100, Number(value || 0)))
  return smallCircumference.value * (1 - v / 100)
}

function ringColor(value) {
  const v = Number(value || 0)
  if (v >= 75) return '#0F6E56'
  if (v >= 50) return '#1D9E75'
  if (v >= 25) return '#D97706'
  return '#DC2626'
}

function barWidth(value, max) {
  if (value == null || isNaN(value)) return '0%'
  const v = Math.max(0, Math.min(1, Number(value) / max))
  return (v * 100).toFixed(1) + '%'
}

// ── Computed content ─────────────────────────────────────────
const subScoreRows = computed(() => {
  const sc = inference.value?.scores || {}
  return SUB_SCORE_DEFS.map(d => ({
    ...d,
    value: Math.max(0, Math.min(100, Number(sc[d.key] || 0))),
  }))
})

const narrative = computed(() => {
  if (!inference.value) return ''
  const strengths = inference.value.strengths || []
  const gaps      = inference.value.gaps      || []
  const score     = Math.round(inference.value.outing_score || 0)
  let s = ''
  if (score >= 75)      s = 'A strong suburb for staying connected as you age.'
  else if (score >= 50) s = 'A solid spot with good options for staying connected.'
  else if (score >= 25) s = 'Some basics are here, but a few gaps to be aware of.'
  else                  s = 'Limited amenities for outings — neighbouring suburbs may offer more.'
  if (strengths.length) s += ` Particularly strong on ${strengths.slice(0, 2).join(' and ')}.`
  if (gaps.length)      s += ` Watch for: ${gaps.slice(0, 2).join(', ')}.`
  return s
})

const scoreBand = computed(() => {
  const s = inference.value?.outing_score || 0
  if (s >= 75) return 'Strong'
  if (s >= 50) return 'Good'
  if (s >= 25) return 'Limited'
  return 'Sparse'
})
const scoreClass = computed(() => `band-${scoreBand.value.toLowerCase()}`)

const peers = computed(() => inference.value?.peer_suburbs || [])

const peopleRatio = computed(() => {
  const pct = inference.value?.counts?.elderly_pct
  if (!pct || pct <= 0) return '—'
  return Math.max(2, Math.round(100 / pct))
})

const wcStopRatio = computed(() => {
  const total = inference.value?.counts?.stop_count
  const wc    = inference.value?.counts?.wc_stop_count
  if (!total) return null
  const pct = wc ? Math.round((wc / total) * 100) : 0
  let note = ''
  if (pct >= 60)      note = 'Well served — most stops have step-free access.'
  else if (pct >= 25) note = 'Reasonable coverage. Check your specific stop.'
  else                note = 'A known gap — many stops are not step-free.'
  return { wc, total, pct, note }
})

const eventsCount = computed(() => {
  const s = snapshotApi.data?.value
  const ev = s?.events?.events || s?.events || []
  return Array.isArray(ev) ? ev.length : (s?.events_count ?? '—')
})

const nowState = computed(() => {
  const s = snapshotApi.data?.value
  const safety = s?.safety?.verdict || s?.safety_verdict
  if (safety === 'Good' || safety === 'good')        return 'safe'
  if (safety === 'Caution' || safety === 'caution')  return 'caution'
  if (safety === 'Poor' || safety === 'poor')        return 'poor'
  return 'unknown'
})

const nowTitle = computed(() => {
  const s = snapshotApi.data?.value
  if (!s) return 'Loading current conditions…'
  const crowd  = s?.crowd?.level || s?.crowd_level
  const temp   = s?.weather?.temperature_c ?? s?.weather?.temp
  const cond   = s?.weather?.summary || s?.weather?.description
  const safe   = s?.safety?.verdict || 'Unknown'
  const parts = []
  if (crowd)  parts.push(String(crowd).toLowerCase())
  if (temp != null) parts.push(`${Math.round(temp)}°C${cond ? ', ' + cond.toLowerCase() : ''}`)
  if (safe)   parts.push(`${String(safe).toLowerCase()} to go`)
  return parts.length ? `Right now: ${parts.join(' · ')}` : 'Conditions unavailable.'
})

const nowSub = computed(() => {
  const ns = nowState.value
  if (ns === 'safe')    return 'Good time for a short, gentle outing.'
  if (ns === 'caution') return 'Take it easy — bring water and watch the heat.'
  if (ns === 'poor')    return 'Maybe stay in today. Try again later.'
  return 'Weather feed loading…'
})

const hasGap = computed(() => {
  const c = inference.value?.data_completeness_pct
  return c != null && c < 50
})

const indicatorStyle = computed(() => {
  const idx = TABS.findIndex(t => t.key === activeTab.value)
  const left = (idx / TABS.length) * 100
  const width = 100 / TABS.length
  return { left: `${left}%`, width: `${width}%` }
})

function formatNum(n, decimals = 0) {
  if (n == null || isNaN(n)) return '—'
  if (decimals === 0) return Number(n).toLocaleString()
  return Number(n).toFixed(decimals)
}
</script>

<style scoped>
/* ================================================================== */
/*  PANEL ROOT — robust flex column                                   */
/* ================================================================== */
.panel-root {
  --teal:       #0F6E56;
  --teal-deep:  #04342C;
  --teal-soft:  #E1F5EE;
  --mint:       #F2FAF0;
  --ink:        #0f1e12;
  --ink-2:      #2d3e30;
  --muted:      #6a7e6d;
  --line:       #ECF3EC;
  --line-2:     #DEEAE0;
  --surface:    #FFFFFF;

  /* Critical: explicit height + flex + overflow:hidden so the
     scrollable .body inside knows when to scroll */
  height: 100%;
  width: 100%;
  background: var(--surface);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 18px;
  border: 1px solid var(--line);
}

/* Every direct child fills the panel — required for scroll to work */
.state, .panel-content {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ================================================================== */
/*  STATES (empty / error / loading)                                  */
/* ================================================================== */
.empty-state {
  align-items: center;
  justify-content: center;
  padding: 40px 28px;
  gap: 14px;
  text-align: center;
  overflow-y: auto;
}
.empty-art { margin-bottom: 4px; opacity: 0.95; }
.empty-title {
  font-family: Georgia, serif;
  margin: 0;
  font-size: calc(22px * var(--font-scale));
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.01em;
}
.empty-msg {
  margin: 0;
  max-width: 280px;
  font-size: calc(14px * var(--font-scale));
  line-height: 1.6;
  color: var(--muted);
}
.empty-quick { margin-top: 8px; width: 100%; max-width: 320px; }
.empty-quick-label {
  margin: 0 0 10px;
  font-size: calc(11px * var(--font-scale));
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  font-weight: 600;
}
.empty-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
}
.empty-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: var(--mint);
  border: 1px solid var(--line);
  border-radius: 999px;
  cursor: pointer;
  font-family: inherit;
  font-size: calc(13px * var(--font-scale));
  transition: all 0.15s;
}
.empty-chip:hover { border-color: #5DCAA5; background: var(--teal-soft); }
.empty-chip-name { color: var(--ink); font-weight: 500; }
.empty-chip-score {
  font-family: Georgia, serif;
  font-weight: 700;
  color: var(--teal);
  font-size: calc(14px * var(--font-scale));
}

.loading-state {
  padding: 24px 24px 80px;
  gap: 14px;
  align-items: center;
}

.error-state {
  align-items: center;
  justify-content: center;
  padding: 40px 28px;
  gap: 12px;
  text-align: center;
}
.err-ic { font-size: 36px; color: #B07919; line-height: 1; }
.err-title {
  font-family: Georgia, serif;
  margin: 0;
  font-size: calc(18px * var(--font-scale));
  color: var(--ink);
  font-weight: 700;
}
.err-msg {
  margin: 0;
  max-width: 300px;
  font-size: calc(13px * var(--font-scale));
  line-height: 1.55;
  color: var(--muted);
}
.err-retry {
  margin-top: 6px;
  padding: 8px 18px;
  background: transparent;
  border: 1.5px solid var(--teal);
  border-radius: 999px;
  color: var(--teal);
  font-weight: 700;
  font-family: inherit;
  font-size: calc(13px * var(--font-scale));
  cursor: pointer;
  transition: all 0.15s;
}
.err-retry:hover { background: var(--teal); color: #fff; }

/* ================================================================== */
/*  LOADED CONTENT                                                    */
/* ================================================================== */
/* .panel-content already gets flex:1, min-height:0, overflow:hidden from .state */

.head {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 22px 24px 18px;
  background: var(--surface);
  border-bottom: 1px solid var(--line);
  flex: 0 0 auto;          /* never shrinks */
}
.head-text { flex: 1; min-width: 0; }
.head-name {
  font-family: Georgia, serif;
  margin: 0 0 4px;
  font-size: calc(24px * var(--font-scale));
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.015em;
  line-height: 1.15;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.head-meta {
  margin: 0;
  font-size: calc(12px * var(--font-scale));
  color: var(--muted);
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.head-persona {
  display: inline-block;
  padding: 2px 10px;
  background: var(--mint);
  border-radius: 999px;
  font-weight: 600;
  color: var(--teal);
}
.head-close {
  width: 32px;
  height: 32px;
  background: var(--mint);
  border: 1px solid var(--line);
  border-radius: 50%;
  color: var(--muted);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.15s;
}
.head-close:hover {
  background: var(--teal);
  border-color: var(--teal);
  color: #ffffff;
}

/* ───── SCROLLABLE BODY ─────────────────────────────────── */
.body {
  flex: 1 1 auto;       /* fills remaining space */
  min-height: 0;        /* CRITICAL — lets flex child shrink */
  overflow-y: auto;     /* scroll inside */
  overflow-x: hidden;
  padding: 24px 24px 16px;
  scrollbar-width: thin;
  -webkit-overflow-scrolling: touch;
}
.body::-webkit-scrollbar { width: 6px; }
.body::-webkit-scrollbar-thumb { background: var(--line-2); border-radius: 3px; }

/* ================================================================== */
/*  HERO RING                                                         */
/* ================================================================== */
.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.hero-ring { position: relative; display: inline-block; }
.hero-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}
.hero-num {
  font-family: Georgia, serif;
  font-size: calc(48px * var(--font-scale));
  font-weight: 700;
  color: var(--ink);
  line-height: 1;
  letter-spacing: -0.02em;
}
.hero-suf {
  margin-top: 4px;
  font-size: calc(11px * var(--font-scale));
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 600;
}
.hero-caption { display: flex; align-items: center; gap: 10px; }
.hero-label {
  margin: 0;
  font-size: calc(13px * var(--font-scale));
  color: var(--muted);
  font-weight: 500;
}
.hero-band {
  padding: 3px 12px;
  border-radius: 999px;
  font-size: calc(12px * var(--font-scale));
  font-weight: 600;
}
.band-strong   { background: #C9EFDF; color: #04342C; }
.band-good     { background: #E1F5EE; color: #0F6E56; }
.band-limited  { background: #FEF0DD; color: #855414; }
.band-sparse   { background: #FBE5E5; color: #7A2828; }

/* Ring animation — faster (0.5s instead of 1.1s) */
.ring-progress {
  transition: stroke-dashoffset 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
@media (prefers-reduced-motion: reduce) {
  .ring-progress { transition: none; }
}

/* ================================================================== */
/*  NARRATIVE                                                         */
/* ================================================================== */
.narrative {
  margin: 0 0 24px;
  padding: 14px 16px;
  background: var(--mint);
  border-radius: 12px;
  font-size: calc(14px * var(--font-scale));
  line-height: 1.65;
  color: var(--ink-2);
}

/* ================================================================== */
/*  BLOCK / SECTION                                                   */
/* ================================================================== */
.block { margin-bottom: 24px; }
.block-title {
  font-family: Georgia, serif;
  margin: 0 0 12px;
  font-size: calc(15px * var(--font-scale));
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.01em;
}

/* ================================================================== */
/*  LINE BARS — faster (0.4s)                                         */
/* ================================================================== */
.bars { display: flex; flex-direction: column; gap: 14px; }
.bar-row {
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto auto;
  gap: 4px 12px;
  align-items: center;
}
.bar-label {
  margin: 0;
  font-size: calc(13px * var(--font-scale));
  color: var(--ink-2);
  font-weight: 500;
  grid-column: 1;
  grid-row: 1;
}
.bar-value {
  margin: 0;
  font-family: Georgia, serif;
  font-size: calc(15px * var(--font-scale));
  font-weight: 700;
  color: var(--teal);
  grid-column: 2;
  grid-row: 1;
}
.bar-track {
  grid-column: 1 / -1;
  grid-row: 2;
  position: relative;
  height: 8px;
  background: var(--line);
  border-radius: 4px;
  overflow: visible;
}
.bar-fill {
  position: absolute;
  inset: 0 auto 0 0;
  height: 100%;
  background: linear-gradient(90deg, #5DCAA5 0%, #0F6E56 100%);
  border-radius: 4px;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.bar-fill-inverse {
  background: linear-gradient(90deg, #0F6E56 0%, #5DCAA5 100%);
}
.bar-thumb {
  position: absolute;
  top: 50%;
  right: -6px;
  transform: translate(0, -50%);
  width: 14px;
  height: 14px;
  background: #FFFFFF;
  border: 3px solid #0F6E56;
  border-radius: 50%;
  box-shadow: 0 1px 4px rgba(15, 110, 86, 0.2);
}
@media (prefers-reduced-motion: reduce) { .bar-fill { transition: none; } }

/* ================================================================== */
/*  TABS                                                              */
/* ================================================================== */
.tabs {
  position: sticky;
  top: 0;
  z-index: 2;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  background: var(--surface);
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  margin: 0 -24px 16px;
  padding: 0 24px;
}
.tab {
  padding: 14px 0;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: calc(13px * var(--font-scale));
  color: var(--muted);
  font-weight: 600;
  font-family: inherit;
  transition: color 0.2s;
}
.tab:hover { color: var(--teal); }
.tab.active { color: var(--teal-deep); }
.tab-indicator {
  position: absolute;
  bottom: -1px;
  height: 2.5px;
  background: var(--teal);
  border-radius: 2px 2px 0 0;
  transition: left 0.25s cubic-bezier(0.4, 0, 0.2, 1), width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
}
@media (prefers-reduced-motion: reduce) { .tab-indicator { transition: none; } }

.tab-content { min-height: 200px; }
.tab-pane { display: flex; flex-direction: column; gap: 18px; }

.tab-fade-enter-active, .tab-fade-leave-active {
  transition: opacity 0.15s, transform 0.15s;
}
.tab-fade-enter-from { opacity: 0; transform: translateY(4px); }
.tab-fade-leave-to   { opacity: 0; transform: translateY(-4px); }

/* ================================================================== */
/*  SCORE BREAKDOWN — Ring grid — faster fade-in (0.3s, 30ms stagger) */
/* ================================================================== */
.rings-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px 8px;
  padding: 8px 0;
}
.ring-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  animation: cell-fade-in 0.3s cubic-bezier(0.4, 0, 0.2, 1) both;
}
@keyframes cell-fade-in {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
@media (prefers-reduced-motion: reduce) {
  .ring-cell { animation: none; }
}
.cell-ring { position: relative; display: inline-block; }
.cell-center {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}
.cell-num {
  font-family: Georgia, serif;
  font-size: calc(20px * var(--font-scale));
  font-weight: 700;
  color: var(--ink);
}
.cell-label {
  margin: 0;
  font-size: calc(11px * var(--font-scale));
  color: var(--muted);
  text-align: center;
  font-weight: 500;
}

.gap-card {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  background: #FEF5E7;
  border: 1px solid #F3D7A8;
  border-radius: 10px;
}
.gap-card p {
  margin: 0;
  font-size: calc(12px * var(--font-scale));
  line-height: 1.55;
  color: #4A2E10;
}
.gap-ic { font-size: 17px; color: #B07919; line-height: 1; flex-shrink: 0; }

/* ================================================================== */
/*  PLACES tab                                                        */
/* ================================================================== */
.companion-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--teal-soft);
  border-radius: 14px;
  border: 1px solid var(--line-2);
}
.companion-ic {
  width: 40px;
  height: 40px;
  background: #ffffff;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.companion-num {
  margin: 0;
  font-size: calc(13px * var(--font-scale));
  color: var(--ink-2);
  line-height: 1.4;
}
.companion-num strong {
  font-family: Georgia, serif;
  font-size: calc(20px * var(--font-scale));
  font-weight: 700;
  color: var(--teal);
  margin-right: 4px;
}
.companion-sub {
  margin: 2px 0 0;
  font-size: calc(12px * var(--font-scale));
  color: var(--teal);
}

.tile-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}
.tile {
  background: var(--mint);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 14px;
  transition: transform 0.15s, border-color 0.15s;
}
.tile:hover { transform: translateY(-1px); border-color: #5DCAA5; }
.tile-ic {
  display: inline-flex;
  width: 32px;
  height: 32px;
  border-radius: 9px;
  align-items: center;
  justify-content: center;
  margin-bottom: 6px;
}
.tile-welcoming .tile-ic { background: #E1F5EE; color: #0F6E56; }
.tile-cafe      .tile-ic { background: #FEEBD2; color: #EE8B27; }
.tile-park      .tile-ic { background: #E5F0D6; color: #5B9420; }
.tile-events    .tile-ic { background: #E1ECF7; color: #2D7BD4; }

.tile-num {
  font-family: Georgia, serif;
  margin: 0;
  font-size: calc(24px * var(--font-scale));
  font-weight: 700;
  color: var(--ink);
  line-height: 1;
  letter-spacing: -0.01em;
}
.tile-label {
  margin: 3px 0 0;
  font-size: calc(12px * var(--font-scale));
  color: var(--muted);
}

.peers { margin-top: 4px; }
.peers-title {
  font-family: Georgia, serif;
  margin: 0 0 8px;
  font-size: calc(14px * var(--font-scale));
  font-weight: 700;
  color: var(--ink);
}
.peer-list { display: flex; flex-direction: column; gap: 4px; }
.peer-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  cursor: pointer;
  text-align: left;
  font: inherit;
  color: inherit;
  transition: all 0.15s;
}
.peer-row:hover {
  border-color: #5DCAA5;
  background: var(--mint);
}
.peer-mini-ring {
  position: relative;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}
.peer-mini-num {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: Georgia, serif;
  font-size: calc(11px * var(--font-scale));
  font-weight: 700;
  color: var(--ink);
}
.peer-meta { flex: 1; min-width: 0; }
.peer-name {
  margin: 0;
  font-size: calc(13px * var(--font-scale));
  font-weight: 600;
  color: var(--ink);
}
.peer-reason {
  margin: 1px 0 0;
  font-size: calc(11px * var(--font-scale));
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.peer-chev { color: var(--muted); flex-shrink: 0; }

/* ================================================================== */
/*  COMFORT tab                                                       */
/* ================================================================== */
.now-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 14px;
  position: relative;
}
.now-safe    { background: #D8F0DC; color: #173404; }
.now-caution { background: #FDF0D2; color: #6B4D0C; }
.now-poor    { background: #FBE1E1; color: #7A2828; }
.now-unknown { background: var(--mint); color: var(--muted); }

.now-ic { flex-shrink: 0; line-height: 1; color: currentColor; }
.now-body { flex: 1; min-width: 0; }
.now-title { margin: 0; font-weight: 600; font-size: calc(13px * var(--font-scale)); color: currentColor; }
.now-sub { margin: 2px 0 0; font-size: calc(11px * var(--font-scale)); color: currentColor; opacity: 0.85; }
.now-loading {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(0, 0, 0, 0.15);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) { .now-loading { animation: none; } }

.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}
.stat {
  background: var(--mint);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 14px;
  text-align: center;
}
.stat-num {
  font-family: Georgia, serif;
  margin: 0;
  font-size: calc(22px * var(--font-scale));
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.01em;
  line-height: 1.1;
}
.stat-lbl {
  margin: 4px 0 0;
  font-size: calc(11px * var(--font-scale));
  color: var(--muted);
}

.wc-bar {
  padding: 14px 16px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
}
.wc-bar-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 10px;
}
.wc-bar-label {
  font-size: calc(12px * var(--font-scale));
  color: var(--ink-2);
  font-weight: 500;
}
.wc-bar-value {
  font-family: Georgia, serif;
  font-size: calc(14px * var(--font-scale));
  font-weight: 700;
  color: var(--teal);
}
.wc-bar-caption {
  margin: 10px 0 0;
  font-size: calc(11px * var(--font-scale));
  color: var(--muted);
  line-height: 1.5;
}

/* ================================================================== */
/*  ACTION BAR (fixed bottom)                                         */
/* ================================================================== */
.action-bar {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  padding: 14px 18px;
  background: var(--surface);
  border-top: 1px solid var(--line);
  flex: 0 0 auto;       /* never shrinks */
}
.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 11px 10px;
  background: var(--mint);
  color: var(--teal-deep);
  border: 1px solid var(--line);
  border-radius: 11px;
  font-size: calc(12px * var(--font-scale));
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
}
.action-btn:hover {
  background: var(--teal-soft);
  border-color: #5DCAA5;
}
.action-primary {
  background: var(--teal);
  color: #ffffff;
  border-color: var(--teal);
}
.action-primary:hover {
  background: var(--teal-deep);
  border-color: var(--teal-deep);
}

/* ================================================================== */
/*  RESPONSIVE                                                        */
/* ================================================================== */
@media (max-width: 640px) {
  .head { padding: 18px 18px 14px; }
  .head-name { font-size: calc(22px * var(--font-scale)); }
  .body { padding: 18px 18px 12px; }
  .tabs { margin: 0 -18px 14px; padding: 0 18px; }
  .hero-num { font-size: calc(42px * var(--font-scale)); }
  .rings-grid { gap: 14px 4px; }
  .action-bar { padding: 12px 16px; }
  .action-btn { padding: 10px 8px; font-size: calc(11px * var(--font-scale)); }
}
</style>
