<template>
  <div class="crowd-day-chart">
    <!-- Day selector pills -->
    <div class="day-pills" role="tablist" aria-label="Choose a day">
      <button
        v-for="d in dayOptions"
        :key="d.value"
        type="button"
        role="tab"
        :aria-selected="selectedDay === d.value"
        class="day-pill"
        :class="{ active: selectedDay === d.value }"
        @click="selectedDay = d.value"
      >{{ d.short }}</button>
    </div>

    <!-- Bar chart -->
    <div class="chart-wrap">
      <div class="chart-axis">
        <span class="axis-num">{{ Math.round(maxValue) }}</span>
        <span class="axis-num">{{ Math.round(maxValue / 2) }}</span>
        <span class="axis-num">0</span>
        <span class="axis-unit">people/hr</span>
      </div>
      <div class="chart-bars">
        <button
          v-for="h in hours"
          :key="h"
          type="button"
          class="bar-col"
          :class="{ active: activeHour === h }"
          @mouseenter="hovered = h"
          @mouseleave="hovered = null"
          @click="pinHour(h)"
          :aria-label="`${formatHour(h)}: ${cellFor(h)?.crowd_level || 'no data'}`"
        >
          <span class="bar-fill" :style="barStyle(h)"></span>
          <span class="bar-tick">{{ formatHourShort(h) }}</span>
        </button>
      </div>
    </div>

    <!-- Detail row when a bar is hovered or pinned -->
    <transition name="fade">
      <div v-if="activeCell" class="cell-detail" :key="`${selectedDay}-${activeCell.hour}`">
        <div class="cell-time">
          <span class="cell-day">{{ selectedDayLabel }}</span>
          <span class="cell-hour">{{ formatHour(activeCell.hour) }}</span>
        </div>
        <div class="cell-stat">
          <span class="cell-pip" :class="`crowd-${(activeCell.crowd_level || 'unknown').toLowerCase()}`">
            {{ activeCell.crowd_level || 'No data' }}
          </span>
          <span class="cell-count">~{{ Math.round(activeCell.avg_count) }} people/hr</span>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  forecast: { type: Object, default: () => ({}) },
})

const hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
const dayOptions = [
  { value: 'Monday',    short: 'Mon' },
  { value: 'Tuesday',   short: 'Tue' },
  { value: 'Wednesday', short: 'Wed' },
  { value: 'Thursday',  short: 'Thu' },
  { value: 'Friday',    short: 'Fri' },
  { value: 'Saturday',  short: 'Sat' },
  { value: 'Sunday',    short: 'Sun' },
]

// Pick the quietest day as initial selection (most useful insight)
const quietestDay = computed(() => {
  let best = null, bestAvg = Infinity
  for (const d of dayOptions) {
    const arr = props.forecast?.[d.value]
    if (!Array.isArray(arr) || !arr.length) continue
    const avg = arr.reduce((s, x) => s + (Number(x.avg_count) || 0), 0) / arr.length
    if (avg < bestAvg) { bestAvg = avg; best = d.value }
  }
  return best || 'Sunday'
})

const selectedDay = ref(quietestDay.value)
watch(quietestDay, (v) => {
  // If selectedDay still has no data (initial load), snap to quietest day once data arrives
  const cur = props.forecast?.[selectedDay.value]
  if (!Array.isArray(cur) || !cur.length) selectedDay.value = v
})

const selectedDayLabel = computed(() =>
  dayOptions.find(d => d.value === selectedDay.value)?.value || selectedDay.value
)

const hovered = ref(null)
const pinned = ref(null)
const activeHour = computed(() => hovered.value ?? pinned.value)
const activeCell = computed(() => activeHour.value != null ? cellFor(activeHour.value) : null)

function pinHour(h) {
  if (pinned.value === h) pinned.value = null
  else pinned.value = h
}

function cellFor(hour) {
  const list = props.forecast?.[selectedDay.value] || []
  return list.find(x => x.hour === hour) || null
}

const maxValue = computed(() => {
  let m = 0
  for (const day of Object.values(props.forecast || {})) {
    if (!Array.isArray(day)) continue
    for (const cell of day) {
      const v = Number(cell.avg_count) || 0
      if (v > m) m = v
    }
  }
  return Math.max(100, Math.ceil(m / 100) * 100)
})

function barStyle(h) {
  const cell = cellFor(h)
  if (!cell || cell.avg_count == null) return { height: '4%', background: '#e4ece4' }
  const pct = Math.max(4, (cell.avg_count / maxValue.value) * 100)
  const c = cell.avg_count
  let bg
  if (c < 50)        bg = 'linear-gradient(180deg, #5cae7a, #2d8f6f)'
  else if (c < 100)  bg = 'linear-gradient(180deg, #8fc878, #5cae7a)'
  else if (c < 200)  bg = 'linear-gradient(180deg, #c5c476, #8fc878)'
  else if (c < 350)  bg = 'linear-gradient(180deg, #d8a060, #c5c476)'
  else if (c < 500)  bg = 'linear-gradient(180deg, #d8a060, #c87858)'
  else if (c < 700)  bg = 'linear-gradient(180deg, #c87858, #a85040)'
  else               bg = 'linear-gradient(180deg, #a85040, #8a3a30)'
  return { height: `${pct}%`, background: bg }
}

function formatHour(h) {
  if (h === 0) return '12:00 AM'
  if (h === 12) return '12:00 PM'
  return h < 12 ? `${h}:00 AM` : `${h - 12}:00 PM`
}
function formatHourShort(h) {
  if (h === 0) return '12a'
  if (h === 12) return '12p'
  return h < 12 ? `${h}a` : `${h - 12}p`
}
</script>

<style scoped>
.crowd-day-chart { width: 100%; }

.day-pills { display: flex; gap: 6px; margin-bottom: 18px; flex-wrap: wrap; }
.day-pill {
  padding: 8px 14px; background: white; border: 1px solid rgba(29,113,105,0.16); border-radius: 999px;
  color: #4a6a4e; font-family: system-ui,sans-serif; font-size: 12px; font-weight: 700;
  letter-spacing: 0.04em; cursor: pointer; transition: all 0.2s;
}
.day-pill:hover { color: #0a9b8a; border-color: rgba(10,155,138,0.36); }
.day-pill.active { background: linear-gradient(135deg, #0a9b8a, #056b5e); color: white; border-color: transparent; box-shadow: 0 6px 14px rgba(10,155,138,0.28); }

.chart-wrap { display: flex; gap: 12px; height: 220px; align-items: stretch; }
.chart-axis {
  display: flex; flex-direction: column; justify-content: space-between; align-items: flex-end;
  padding: 4px 0 22px;
  font-family: system-ui,sans-serif; font-size: 10px; font-weight: 700;
  color: #8aaa8e; letter-spacing: 0.04em;
}
.axis-num { line-height: 1; }
.axis-unit { color: #6a8e6e; font-size: 9px; text-transform: uppercase; transform: translateY(8px); }

.chart-bars {
  flex: 1; display: grid; grid-template-columns: repeat(13, 1fr); gap: 4px;
  align-items: end;
}
.bar-col {
  position: relative; display: flex; flex-direction: column; align-items: center; justify-content: flex-end;
  height: 100%; padding: 0; background: transparent; border: none; cursor: pointer;
}
.bar-fill {
  display: block; width: 100%; min-height: 4px;
  border-radius: 6px 6px 2px 2px;
  transition: height 0.5s cubic-bezier(0.22,1,0.36,1), filter 0.2s, transform 0.2s;
}
.bar-col:hover .bar-fill { transform: scaleY(1.04); filter: brightness(1.06); }
.bar-col.active .bar-fill { outline: 2px solid #0f1e12; outline-offset: 2px; }
.bar-tick {
  margin-top: 6px; font-family: system-ui,sans-serif; font-size: 10px; font-weight: 700;
  color: #8aaa8e; letter-spacing: 0.02em;
}

.cell-detail {
  margin-top: 14px; display: flex; align-items: center; justify-content: space-between; gap: 14px;
  padding: 14px 18px; background: white; border: 1px solid rgba(29,113,105,0.18); border-radius: 14px;
}
.cell-time { display: flex; flex-direction: column; gap: 2px; }
.cell-day { font-family: Georgia,serif; font-weight: 700; color: #0f1e12; font-size: 17px; }
.cell-hour { font-family: system-ui,sans-serif; font-size: 13px; color: #6a8e6e; font-weight: 600; }
.cell-stat { display: flex; align-items: center; gap: 10px; }
.cell-pip { padding: 4px 12px; border-radius: 999px; font-family: system-ui,sans-serif; font-size: 12px; font-weight: 800; letter-spacing: 0.03em; text-transform: uppercase; }
.cell-pip.crowd-low      { background: #d6f4e7; color: #1d7169; }
.cell-pip.crowd-moderate { background: #fff3c2; color: #8a6000; }
.cell-pip.crowd-high     { background: #ffded5; color: #c44a2c; }
.cell-pip.crowd-unknown  { background: #f0f0f8; color: #6a8e6e; }
.cell-count { font-family: system-ui,sans-serif; font-size: 13px; color: #4a6a4e; font-weight: 600; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s, transform 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(4px); }

@media (max-width: 600px) {
  .chart-wrap { height: 180px; }
  .cell-detail { flex-direction: column; align-items: flex-start; gap: 8px; }
  .bar-tick { font-size: 9px; }
}
</style>
