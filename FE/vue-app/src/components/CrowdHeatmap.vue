<!-- src/components/CrowdHeatmap.vue — Pure canvas heatmap, no external libraries -->
<template>
  <div class="heatmap-outer">

    <!-- Hour axis labels -->
    <div class="axis-row">
      <div class="axis-day-spacer"></div>
      <div class="axis-hours">
        <span
          v-for="h in displayHours"
          :key="h"
          class="hour-tick"
          :class="{ 'hour-tick-peak': h === 12 }"
        >
          {{ formatHour(h) }}
        </span>
      </div>
    </div>

    <!-- Rows: one per day -->
    <div class="heatmap-rows">
      <div
        v-for="day in days"
        :key="day"
        class="heatmap-row"
      >
        <!-- Day label -->
        <div class="day-label">{{ day.slice(0, 3) }}</div>

        <!-- Cells -->
        <div class="cells-row">
          <div
            v-for="h in displayHours"
            :key="h"
            class="cell"
            :style="cellStyle(day, h)"
            :class="{
              'cell-selected': isSelected(day, h),
              'cell-best':     isBestCell(day, h),
            }"
            @mouseenter="onHover(day, h, $event)"
            @mouseleave="onLeave"
            @click="onSelect(day, h)"
          >
            <AppIcon name="star" :size="12" color="#fff" class="best-star-icon" />
          </div>
        </div>
      </div>
    </div>

    <!-- Gradient legend bar -->
    <div class="legend-row">
      <div class="axis-day-spacer"></div>
      <div class="legend-wrap">
        <span class="legend-label">Quietest</span>
        <div class="legend-bar"></div>
        <span class="legend-label">Busiest</span>
      </div>
    </div>

    <!-- Hover tooltip (absolutely positioned) -->
    <div
      v-if="tooltip.visible"
      class="heatmap-tooltip"
      :style="{ top: tooltip.y + 'px', left: tooltip.x + 'px' }"
    >
      <div class="tt-day">{{ tooltip.day }} · {{ formatHour(tooltip.hour) }}</div>
      <div class="tt-crowd" :class="`tt-${tooltip.level?.toLowerCase()}`">
        {{ tooltip.level }}
      </div>
      <div class="tt-count">~{{ tooltip.avg_count }} people/hr</div>
      <div class="tt-hint">Click to plan this visit</div>
    </div>

    <!-- Selected cell callout -->
    <div v-if="selected" class="selected-callout">
      <div class="callout-left">
        <AppIcon name="clock" :size="20" color="#0c8b7d" />
        <div class="callout-text">
          <strong>{{ selected.day }}, {{ formatHour(selected.hour) }}</strong>
          <span class="callout-count">~{{ selected.avg_count }} people/hr</span>
        </div>
      </div>
      <span class="callout-badge" :class="`crowd-${selected.level.toLowerCase()}`">
        {{ selected.level }}
      </span>
      <button class="callout-btn" @click="$emit('planVisit', selected)">
        Plan this visit →
      </button>
      <button class="callout-close" @click="selected = null">✕</button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AppIcon from './AppIcon.vue'

const props = defineProps({
  forecast:     { type: Object,  default: () => ({}) },
  forecastDays: { type: Array,   default: () => [] },
  quietestDay:  { type: Object,  default: null },
})

defineEmits(['planVisit'])

// ── Config ────────────────────────────────────────────────────────────────────
const displayHours = Array.from({ length: 13 }, (_, i) => i + 8)  // 8am–8pm
const days         = computed(() => props.forecastDays)

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatHour(h) {
  const ampm = h < 12 ? 'am' : 'pm'
  const h12  = h % 12 === 0 ? 12 : h % 12
  return `${h12}${ampm}`
}

function getCell(day, hour) {
  return props.forecast?.[day]?.[hour] ?? null
}

// Compute max count across visible cells for normalisation
const maxCount = computed(() => {
  let m = 1
  for (const day of days.value) {
    for (const h of displayHours) {
      const d = getCell(day, h)
      if (d && d.avg_count > m) m = d.avg_count
    }
  }
  return m
})

// ── Colour mapping ─────────────────────────────────────────────────────────────
// Sunrise palette: deep teal (quiet) → warm gold → coral (busy)
// Uses 5-stop gradient interpolation so cells feel natural, not banded
function countToColor(count) {
  const t = Math.min(count / maxCount.value, 1)   // 0 = quietest, 1 = busiest

  // 5 stops: teal → mint → gold → orange → coral
  const stops = [
    [12,  139, 125],   // 0.00 — teal     (quietest)
    [76,  175, 140],   // 0.25 — mint
    [245, 195,  40],   // 0.50 — gold
    [235, 130,  50],   // 0.75 — orange
    [220,  72,  60],   // 1.00 — coral    (busiest)
  ]

  const seg  = t * (stops.length - 1)
  const lo   = Math.floor(seg)
  const hi   = Math.min(lo + 1, stops.length - 1)
  const frac = seg - lo

  const [r1,g1,b1] = stops[lo]
  const [r2,g2,b2] = stops[hi]

  const r = Math.round(r1 + (r2 - r1) * frac)
  const g = Math.round(g1 + (g2 - g1) * frac)
  const b = Math.round(b1 + (b2 - b1) * frac)

  return { r, g, b }
}

function cellStyle(day, hour) {
  const d = getCell(day, hour)
  if (!d) return { background: '#e8e9f3' }

  const { r, g, b } = countToColor(d.avg_count)
  return {
    background: `rgb(${r},${g},${b})`,
    // Subtle inner shadow for depth
    boxShadow:  `inset 0 1px 0 rgba(255,255,255,0.18), inset 0 -1px 0 rgba(0,0,0,0.08)`,
  }
}

function isBestCell(day, hour) {
  return props.quietestDay?.day === day && props.quietestDay?.hour === hour
}

// ── Interaction ───────────────────────────────────────────────────────────────
const tooltip = ref({ visible: false, day: '', hour: 0, level: '', avg_count: 0, x: 0, y: 0 })
const selected = ref(null)

function onHover(day, hour, event) {
  const d = getCell(day, hour)
  if (!d) return
  const rect = event.currentTarget.getBoundingClientRect()
  const container = event.currentTarget.closest('.heatmap-outer').getBoundingClientRect()
  tooltip.value = {
    visible:   true,
    day,
    hour,
    level:     d.crowd_level,
    avg_count: Math.round(d.avg_count),
    x: rect.left - container.left + rect.width / 2 - 80,
    y: rect.top  - container.top  - 110,
  }
}

function onLeave() {
  tooltip.value.visible = false
}

function onSelect(day, hour) {
  const d = getCell(day, hour)
  if (!d) return
  if (isSelected(day, hour)) { selected.value = null; return }
  selected.value = { day, hour, level: d.crowd_level, avg_count: Math.round(d.avg_count) }
}

function isSelected(day, hour) {
  return selected.value?.day === day && selected.value?.hour === hour
}
</script>

<style scoped>
.heatmap-outer {
  position: relative;
  user-select: none;
}

/* ── Axis row ── */
.axis-row {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
}

.axis-day-spacer { width: 44px; flex-shrink: 0; }

.axis-hours {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(13, 1fr);
  gap: 3px;
}

.hour-tick {
  font-size: calc(10px * var(--font-scale));
  font-weight: 700;
  color: #9b9db8;
  text-align: center;
  white-space: nowrap;
}

.hour-tick-peak { color: #0c8b7d; font-weight: 800; }

/* ── Heatmap rows ── */
.heatmap-rows {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.heatmap-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.day-label {
  width: 44px;
  flex-shrink: 0;
  font-size: calc(13px * var(--font-scale));
  font-weight: 800;
  color: #2f3152;
  text-align: right;
  padding-right: 6px;
}

.cells-row {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(13, 1fr);
  gap: 3px;
}

/* ── Cells ── */
.cell {
  height: 36px;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.12s ease, box-shadow 0.12s ease;
}

.cell:hover {
  transform: scaleY(1.18) scaleX(1.04);
  z-index: 2;
  box-shadow: 0 4px 12px rgba(0,0,0,0.22) !important;
}

.cell-selected {
  outline: 3px solid #fff;
  outline-offset: -3px;
  z-index: 3;
  transform: scaleY(1.18) scaleX(1.04);
  box-shadow: 0 4px 16px rgba(0,0,0,0.28) !important;
}

.cell-best {
  outline: 2.5px solid #fff;
  outline-offset: -2px;
  z-index: 4;
}

.best-star-icon {
  font-size: 11px;
  color: #fff;
  text-shadow: 0 1px 3px rgba(0,0,0,0.4);
  line-height: 1;
}

/* ── Legend ── */
.legend-row {
  display: flex;
  align-items: center;
  margin-top: 10px;
}

.legend-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.legend-label {
  font-size: calc(11px * var(--font-scale));
  font-weight: 700;
  color: #9b9db8;
  white-space: nowrap;
  flex-shrink: 0;
}

.legend-bar {
  flex: 1;
  height: 10px;
  border-radius: 999px;
  background: linear-gradient(
    90deg,
    rgb(12,139,125)  0%,
    rgb(76,175,140)  25%,
    rgb(245,195,40)  50%,
    rgb(235,130,50)  75%,
    rgb(220,72,60)   100%
  );
}

/* ── Tooltip ── */
.heatmap-tooltip {
  position: absolute;
  width: 160px;
  background: #1a1a2e;
  border-radius: 12px;
  padding: 10px 14px;
  pointer-events: none;
  z-index: 100;
  box-shadow: 0 8px 24px rgba(0,0,0,0.28);
}

.heatmap-tooltip::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: #1a1a2e;
  border-bottom: none;
}

.tt-day {
  font-size: calc(12px * var(--font-scale));
  font-weight: 800;
  color: #f5c812;
  margin-bottom: 4px;
}

.tt-crowd {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: calc(11px * var(--font-scale));
  font-weight: 800;
  margin-bottom: 4px;
}

.tt-low      { background: rgba(12,139,125,0.3); color: #4bb6a8; }
.tt-moderate { background: rgba(245,180,18,0.3); color: #f5c040; }
.tt-high     { background: rgba(220,72,60,0.3);  color: #f08070; }
.tt-unknown  { background: rgba(160,162,180,0.3); color: #a0a2c0; }

.tt-count {
  font-size: calc(11px * var(--font-scale));
  color: #a0a2c0;
  font-weight: 600;
}

.tt-hint {
  font-size: calc(10px * var(--font-scale));
  color: #60628a;
  margin-top: 5px;
  font-style: italic;
}

/* ── Selected callout ── */
.selected-callout {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 16px;
  padding: 14px 18px;
  background: #fff;
  border: 2px solid #0c8b7d;
  border-radius: 14px;
  animation: slideIn 0.18s ease;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(-6px); }
  to   { opacity: 1; transform: translateY(0); }
}

.callout-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.callout-icon { font-size: 20px; flex-shrink: 0; }

.callout-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.callout-text strong {
  font-size: calc(15px * var(--font-scale));
  color: #2f3152;
}

.callout-count {
  font-size: calc(12px * var(--font-scale));
  color: #6b6d88;
  font-weight: 600;
}

.callout-badge {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: calc(12px * var(--font-scale));
  font-weight: 800;
  flex-shrink: 0;
}

.crowd-low      { background: #e8f8f5; color: #0a6e62; }
.crowd-moderate { background: #fff8e0; color: #8a6000; }
.crowd-high     { background: #ffeaea; color: #c84848; }
.crowd-unknown  { background: #f0f0f8; color: #6b6d88; }

.callout-btn {
  padding: 9px 16px;
  border: none;
  border-radius: 10px;
  background: #0c8b7d;
  color: #fff;
  font-family: 'Manrope', sans-serif;
  font-size: calc(13px * var(--font-scale));
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
  transition: background 0.15s;
}
.callout-btn:hover { background: #0a756a; }

.callout-close {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1.5px solid #e0e1ed;
  background: #fff;
  color: #9b9db8;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.12s;
}
.callout-close:hover { background: #ffeaea; color: #c84848; border-color: #c84848; }

@media (max-width: 700px) {
  .axis-day-spacer { width: 32px; }
  .day-label { width: 32px; font-size: calc(11px * var(--font-scale)); }
  .cell { height: 28px; border-radius: 4px; }
  .hour-tick { font-size: calc(8px * var(--font-scale)); }
  .selected-callout { flex-direction: column; align-items: flex-start; }
}
</style>