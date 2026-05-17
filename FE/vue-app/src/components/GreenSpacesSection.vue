<template>
  <div class="green-spaces-section">
    <!-- Metric cards strip + park illustration -->
    <div class="metrics-strip">
      <div class="stat-card-big">
        <div class="stat-icon-big mint">
          <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M2 22c1.25-1.25 2.5-2.5 3.5-4C7 16 8 13.5 8 11c0-5.5 4.5-9 9-9 0 4.5-1 8-3.5 10.5S8.5 16 6 18c-1 1-2.5 2.5-4 4z"/>
          </svg>
        </div>
        <span class="stat-num-big">{{ totalSpacesCount }}</span>
        <span class="stat-label-big">Parks within 2km</span>
      </div>

      <div class="stat-card-big">
        <div class="stat-icon-big purple">
          <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="9" y="2" width="6" height="20" rx="1"/>
            <rect x="2" y="9" width="20" height="6" rx="1"/>
          </svg>
        </div>
        <span class="stat-num-big">{{ toiletParksCount }}</span>
        <span class="stat-label-big">With toilets nearby</span>
      </div>

      <div class="stat-card-big">
        <div class="stat-icon-big yellow">
          <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
        </div>
        <span class="stat-num-big">{{ topComfortScore }}</span>
        <span class="stat-label-big">Top comfort score</span>
      </div>
    </div>

    <!-- Title + animated park illustration -->
    <div class="green-header">
      <div class="green-title-block">
        <p class="green-eyebrow">Comfortable parks near you</p>
        <h3 class="green-headline">
          Green spaces<br><em>ranked &amp; filtered.</em>
        </h3>
        <p class="green-sub">
          Comfort score combines walkability, shade, and toilet access.
          Walkability is normalised against the best in your search area.
        </p>
      </div>

      <!-- Decorative park illustration with subtle motion -->
      <div class="park-illust" aria-hidden="true">
        <svg viewBox="0 0 280 180" xmlns="http://www.w3.org/2000/svg">
          <!-- sky -->
          <rect width="280" height="180" fill="#dff3df" rx="14"/>
          <!-- clouds -->
          <g class="park-clouds">
            <ellipse cx="70" cy="35" rx="16" ry="6" fill="#fff" opacity="0.85"/>
            <ellipse cx="200" cy="42" rx="20" ry="7" fill="#fff" opacity="0.78"/>
          </g>
          <!-- distant hill -->
          <path d="M0 130 Q70 95 140 115 T280 110 V180 H0 Z" fill="#86c186"/>
          <!-- nearer hill / path -->
          <path d="M0 145 Q90 120 180 138 T280 140 V180 H0 Z" fill="#a9d3a3"/>
          <!-- walking path -->
          <path d="M80 178 Q140 155 220 178" fill="none" stroke="#d9b984" stroke-width="6" stroke-linecap="round"/>
          <!-- bench -->
          <g transform="translate(125 142)">
            <rect x="0" y="0" width="30" height="2" rx="1" fill="#7a5a3a"/>
            <rect x="3" y="2" width="2" height="8" fill="#7a5a3a"/>
            <rect x="25" y="2" width="2" height="8" fill="#7a5a3a"/>
          </g>
          <!-- left tree -->
          <g class="park-tree park-tree-l">
            <rect x="45" y="105" width="4" height="22" fill="#7a5a3a"/>
            <circle cx="47" cy="100" r="18" fill="#4f9555"/>
            <circle cx="38" cy="105" r="12" fill="#4f9555"/>
            <circle cx="56" cy="103" r="13" fill="#5ea863"/>
          </g>
          <!-- right tree -->
          <g class="park-tree park-tree-r">
            <rect x="232" y="100" width="4" height="26" fill="#7a5a3a"/>
            <circle cx="234" cy="95" r="20" fill="#4f9555"/>
            <circle cx="225" cy="100" r="13" fill="#5ea863"/>
            <circle cx="244" cy="98" r="14" fill="#4f9555"/>
          </g>
          <!-- person walking -->
          <g class="park-person" transform="translate(165 132)">
            <circle cx="0" cy="0" r="4" fill="#1d7169"/>
            <rect x="-3" y="4" width="6" height="11" rx="2" fill="#2a8478"/>
            <line x1="-2" y1="15" x2="-4" y2="22" stroke="#2a4ab0" stroke-width="2.5" stroke-linecap="round"/>
            <line x1="2" y1="15" x2="4" y2="22" stroke="#2a4ab0" stroke-width="2.5" stroke-linecap="round"/>
          </g>
        </svg>
      </div>
    </div>

    <!-- Sort controls -->
    <div v-if="totalSpacesCount > 0" class="sort-controls-wrap">
      <div class="control-group">
        <span class="control-label">Sort by</span>
        <div class="pill-row">
          <button
            v-for="opt in sortOptions"
            :key="opt.value"
            type="button"
            class="filter-pill"
            :class="{ active: sortBy === opt.value }"
            @click="sortBy = opt.value"
          >
            <svg v-if="opt.icon" viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path :d="opt.icon"/></svg>
            {{ opt.label }}
          </button>
        </div>
      </div>
    </div>

    <p v-if="totalSpacesCount > 0" class="results-summary">
      Showing <strong>{{ visibleSpaces.length }}</strong>
      of <strong>{{ filteredSpaces.length }}</strong>
      parks · Sorted by <em>{{ activeSortLabel }}</em>
    </p>

    <!-- Loading state -->
    <div v-if="loading &amp;&amp; !spaces.length" class="mini-loading">
      <div class="mini-spin" aria-hidden="true"></div> Loading nearby parks…
    </div>

    <!-- Park cards grid -->
    <div v-else-if="filteredSpaces.length" class="spaces-grid">
      <article v-for="space in visibleSpaces" :key="space.space_id || space.space_name" class="space-card">
        <div class="space-card-head">
          <div class="space-icon">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M2 22c1.25-1.25 2.5-2.5 3.5-4C7 16 8 13.5 8 11c0-5.5 4.5-9 9-9 0 4.5-1 8-3.5 10.5S8.5 16 6 18c-1 1-2.5 2.5-4 4z"/>
            </svg>
          </div>
          <div class="space-titles">
            <h4 class="space-name">{{ space.space_name }}</h4>
            <p class="space-meta-line">
              <span class="meta-distance">
                <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>
                {{ space.distance_km?.toFixed(2) }} km
              </span>
              <span class="meta-sep">·</span>
              <span>{{ space.space_type || 'Leisure/Recreation' }}</span>
            </p>
          </div>
        </div>

        <div class="space-tags">
          <span v-if="space.has_toilet_nearby" class="toilet-pill yes">
            <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>
            Toilet
          </span>
          <span v-else class="toilet-pill no">No toilet</span>
          <span v-if="space.public_access" class="info-tag access">Public access</span>
        </div>

        <div class="metric-bars">
          <div class="metric-row">
            <span class="metric-label">Comfort</span>
            <div class="metric-track"><div class="metric-fill comfort" :class="comfortBarClass(space.comfort_score)" :style="{ width: `${space.comfort_score}%` }"></div></div>
            <span class="metric-num">{{ Math.round(space.comfort_score || 0) }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Walkability</span>
            <div class="metric-track"><div class="metric-fill walk" :style="{ width: `${walkPct(space.walkability_score)}%` }"></div></div>
            <span class="metric-num">{{ walkPct(space.walkability_score) }}</span>
          </div>
        </div>

        <p v-if="space.managed_by" class="managed-by-line">
          <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 21h18M5 21V7l8-4v18M19 21V11l-6-4"/></svg>
          Managed by {{ space.managed_by }}
        </p>

        <button type="button" class="directions-btn" @click="emit('plan-journey', space)">
          <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <polygon points="3 11 22 2 13 21 11 13 3 11"/>
          </svg>
          Get directions
          <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>
        </button>
      </article>
    </div>

    <div v-else-if="!loading" class="filter-empty">
      <p>No parks found within 2 km. Try a different location.</p>
    </div>

    <div v-if="canShowMore" class="show-more-wrap">
      <button type="button" class="show-more-btn" @click="showAll = !showAll">
        {{ showAll ? 'Show fewer parks' : `Show all ${filteredSpaces.length} parks` }}
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" :style="{ transform: showAll ? 'rotate(180deg)' : 'none' }">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  spaces:  { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})
const emit = defineEmits(['plan-journey'])

const showAll = ref(false)
const sortBy  = ref('comfort')

const sortOptions = [
  { value: 'comfort',     label: 'Comfort',     icon: 'M12 2v20M2 12h20' },
  { value: 'walkability', label: 'Walkability', icon: 'M3 12h18M3 6h18M3 18h18' },
  { value: 'distance',    label: 'Distance',    icon: 'M12 21s-7-4.5-7-11a7 7 0 0 1 14 0c0 6.5-7 11-7 11z' },
  { value: 'name',        label: 'Name',        icon: 'M4 6h16M4 12h16M4 18h12' },
]

const totalSpacesCount = computed(() => props.spaces.length)
const toiletParksCount = computed(() => props.spaces.filter(s => s.has_toilet_nearby).length)
const topComfortScore  = computed(() => {
  if (!props.spaces.length) return 0
  return Math.round(Math.max(...props.spaces.map(s => Number(s.comfort_score) || 0)))
})

const filteredSpaces = computed(() => {
  const list = [...props.spaces]
  switch (sortBy.value) {
    case 'walkability': list.sort((a,b) => (Number(b.walkability_score)||0) - (Number(a.walkability_score)||0)); break
    case 'distance':    list.sort((a,b) => (a.distance_km||Infinity) - (b.distance_km||Infinity)); break
    case 'name':        list.sort((a,b) => (a.space_name||'').localeCompare(b.space_name||'')); break
    case 'comfort':
    default:            list.sort((a,b) => (Number(b.comfort_score)||0) - (Number(a.comfort_score)||0))
  }
  return list
})

const DEFAULT_VISIBLE = 9
const visibleSpaces = computed(() => showAll.value ? filteredSpaces.value : filteredSpaces.value.slice(0, DEFAULT_VISIBLE))
const canShowMore   = computed(() => filteredSpaces.value.length > DEFAULT_VISIBLE)
const activeSortLabel = computed(() => sortOptions.find(o => o.value === sortBy.value)?.label.toLowerCase() || 'comfort')

function comfortBarClass(s) {
  if (s >= 70) return 'high'
  if (s >= 45) return 'mid'
  return 'low'
}

const maxWalkability = computed(() => {
  let m = 0
  for (const s of props.spaces) {
    const v = Number(s.walkability_score) || 0
    if (v > m) m = v
  }
  return m || 1
})
function walkPct(score) {
  const v = Number(score) || 0
  if (v <= 0) return 0
  return Math.max(2, Math.round((v / maxWalkability.value) * 100))
}
</script>

<style scoped>
.green-spaces-section { padding-top: 32px; }

/* ── Metrics strip ── */
.metrics-strip { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-bottom: 44px; }
.stat-card-big { background: white; border: 1px solid rgba(10,155,138,0.14); border-radius: 18px; padding: 26px 28px; display: flex; flex-direction: column; gap: 10px; min-height: 150px; transition: transform 0.3s, box-shadow 0.3s; }
.stat-card-big:hover { transform: translateY(-3px); box-shadow: 0 12px 28px rgba(10,155,138,0.1); }
.stat-icon-big { width: 56px; height: 56px; border-radius: 14px; display: flex; align-items: center; justify-content: center; }
.stat-icon-big.mint   { background: #d6f4e7; color: #1d7169; }
.stat-icon-big.purple { background: #e6dcff; color: #5b3fb6; }
.stat-icon-big.yellow { background: #fff3c2; color: #b88a00; }
.stat-num-big { font-family: Georgia, serif; font-size: 48px; font-weight: 700; color: #0a9b8a; line-height: 1; }
.stat-label-big { font-family: system-ui, sans-serif; font-size: 12px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; color: #1a2e1e; }

/* ── Header + illustration ── */
.green-header { display: grid; grid-template-columns: 1fr auto; gap: 40px; align-items: center; margin-bottom: 36px; }
.green-title-block { max-width: 640px; }
.green-eyebrow { font-family: system-ui, sans-serif; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #0a9b8a; margin-bottom: 12px; }
.green-headline { font-family: Georgia, serif; font-size: 38px; font-weight: 700; line-height: 1.06; color: #0f1e12; margin-bottom: 14px; }
.green-headline em { color: #0a9b8a; font-style: italic; }
.green-sub { font-family: system-ui, sans-serif; font-size: 15px; color: #4a6a4e; line-height: 1.6; }

.park-illust { width: 280px; flex-shrink: 0; border-radius: 14px; overflow: hidden; box-shadow: 0 8px 22px rgba(10,155,138,0.1); }
.park-illust svg { display: block; width: 100%; height: auto; }
.park-clouds ellipse { animation: cloud-drift 18s ease-in-out infinite alternate; }
.park-clouds ellipse:nth-child(2) { animation-delay: -6s; animation-duration: 22s; }
@keyframes cloud-drift { from { transform: translateX(0); } to { transform: translateX(8px); } }
.park-tree-l { transform-origin: 47px 127px; animation: tree-sway 5s ease-in-out infinite alternate; }
.park-tree-r { transform-origin: 234px 126px; animation: tree-sway 6.5s ease-in-out infinite alternate-reverse; }
@keyframes tree-sway { from { transform: rotate(-1.2deg); } to { transform: rotate(1.2deg); } }
.park-person { animation: person-bob 1.4s ease-in-out infinite alternate; }
@keyframes person-bob { from { transform: translate(165px, 132px); } to { transform: translate(168px, 130px); } }

/* ── Sort controls ── */
.sort-controls-wrap { display: flex; justify-content: center; margin-bottom: 18px; padding: 14px 22px; background: linear-gradient(180deg, #fafdf7 0%, #f4f9f0 100%); border-radius: 14px; border: 1px solid rgba(10,155,138,0.1); }
.control-group { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; justify-content: center; }
.control-label { font-family: system-ui, sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; color: #6a8e6e; }
.pill-row { display: flex; gap: 8px; flex-wrap: wrap; }
.filter-pill { display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; background: white; border: 1.5px solid rgba(10,155,138,0.16); border-radius: 999px; color: #4a6a4e; font-family: system-ui, sans-serif; font-size: 13px; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.filter-pill:hover { border-color: #0a9b8a; color: #0a9b8a; }
.filter-pill.active { background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; border-color: transparent; box-shadow: 0 4px 10px rgba(10,155,138,0.2); }

.results-summary { text-align: center; font-family: system-ui, sans-serif; font-size: 13px; color: #4a6a4e; margin-bottom: 28px; }
.results-summary strong { color: #0a9b8a; font-weight: 800; }
.results-summary em { font-style: italic; color: #1a2e1e; font-weight: 700; }

/* ── Park cards grid ── */
.spaces-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.space-card { background: white; border: 1px solid rgba(10,155,138,0.14); border-radius: 16px; padding: 22px; display: flex; flex-direction: column; gap: 14px; transition: transform 0.3s, box-shadow 0.3s; }
.space-card:hover { transform: translateY(-3px); box-shadow: 0 14px 32px rgba(10,155,138,0.12); }
.space-card-head { display: flex; align-items: flex-start; gap: 12px; }
.space-icon { width: 40px; height: 40px; border-radius: 10px; background: #d6f4e7; color: #1d7169; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.space-titles { flex: 1; min-width: 0; }
.space-name { font-family: Georgia, serif; font-size: 18px; font-weight: 700; color: #0f1e12; line-height: 1.2; margin: 0 0 4px; }
.space-meta-line { font-family: system-ui, sans-serif; font-size: 12px; color: #6a8e6e; font-weight: 600; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.meta-distance { display: inline-flex; align-items: center; gap: 4px; }
.meta-sep { opacity: 0.5; }
.space-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.toilet-pill { display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 999px; font-family: system-ui, sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; }
.toilet-pill.yes { background: #d6f4e7; color: #1d7169; }
.toilet-pill.no  { background: #f0f0f0; color: #6a6a6a; }
.info-tag.access { padding: 4px 10px; background: #e6dcff; color: #5b3fb6; border-radius: 999px; font-family: system-ui, sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; }

.metric-bars { display: flex; flex-direction: column; gap: 6px; }
.metric-row { display: flex; align-items: center; gap: 10px; }
.metric-label { width: 80px; font-family: system-ui, sans-serif; font-size: 11px; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; color: #6a8e6e; }
.metric-track { flex: 1; height: 8px; background: #eaf4ea; border-radius: 999px; overflow: hidden; }
.metric-fill { height: 100%; border-radius: 999px; transition: width 0.7s cubic-bezier(0.22,1,0.36,1); }
.metric-fill.comfort.high { background: linear-gradient(90deg, #0a9b8a, #1d7169); }
.metric-fill.comfort.mid  { background: linear-gradient(90deg, #b88a00, #d4a000); }
.metric-fill.comfort.low  { background: linear-gradient(90deg, #c87858, #a85040); }
.metric-fill.walk { background: linear-gradient(90deg, #5b3fb6, #7d5fd6); }
.metric-num { width: 32px; font-family: system-ui, sans-serif; font-size: 13px; font-weight: 800; color: #1a2e1e; text-align: right; }

.managed-by-line { display: flex; align-items: center; gap: 6px; font-family: system-ui, sans-serif; font-size: 11px; color: #6a8e6e; font-weight: 600; }

.directions-btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 11px 18px; background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; border: none; border-radius: 11px; font-family: system-ui, sans-serif; font-size: 13px; font-weight: 700; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; margin-top: 4px; }
.directions-btn:hover { transform: translateY(-2px); box-shadow: 0 10px 22px rgba(10,155,138,0.28); }
.dir-arrow { transition: transform 0.2s; }
.directions-btn:hover .dir-arrow { transform: translateX(2px); }

/* ── Show more / loading / empty ── */
.show-more-wrap { display: flex; justify-content: center; margin-top: 28px; }
.show-more-btn { display: inline-flex; align-items: center; gap: 8px; padding: 12px 24px; background: white; border: 1.5px solid rgba(10,155,138,0.22); color: #0a9b8a; border-radius: 999px; font-family: system-ui, sans-serif; font-size: 13px; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.show-more-btn:hover { background: #e4f5e0; border-color: #0a9b8a; }
.mini-loading { display: flex; align-items: center; justify-content: center; gap: 10px; padding: 40px 0; color: #4a6a4e; font-family: system-ui, sans-serif; font-size: 14px; }
.mini-spin { width: 18px; height: 18px; border-radius: 50%; border: 2.5px solid rgba(10,155,138,0.16); border-top-color: #0a9b8a; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.filter-empty { text-align: center; padding: 40px 20px; color: #4a6a4e; font-family: system-ui, sans-serif; font-size: 14px; background: #fafdf7; border-radius: 12px; }

@media (max-width: 1024px) {
  .metrics-strip { grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
  .stat-card-big { padding: 20px; min-height: 130px; }
  .stat-num-big { font-size: 38px; }
  .green-header { grid-template-columns: 1fr; }
  .park-illust { width: 100%; max-width: 320px; }
}
@media (max-width: 600px) {
  .metrics-strip { grid-template-columns: 1fr; }
  .green-headline { font-size: 30px; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
</style>
