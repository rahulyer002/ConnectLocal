<!-- src/pages/BestTimeWeekPage.vue — Page 3: 7-Day Crowd Forecast + Best Window -->
<template>
  <MainLayout>
    <div class="page">
      <LocationBar @locationChanged="loadAll" />

      <!-- Hero -->
      <div class="week-hero">
        <button class="back-btn" @click="$router.back()">‹ Back</button>
        <p class="hero-eyebrow">YOUR 7-DAY RESONANCE FORECAST</p>
        <h1>Your best windows<br /><em>this week</em></h1>
        <p class="hero-sub">Based on 2 years of City of Melbourne pedestrian sensor data.</p>
        <div class="hero-circle c1"></div>
        <div class="hero-circle c2"></div>
      </div>

      <!-- No location -->
      <div v-if="!store.locationReady" class="empty-state">
        <div class="empty-icon">
          <AppIcon name="map-pin" :size="48" color="#9b9db8" />
        </div>
        <h3>Set your location to see your forecast</h3>
        <p>Use the bar above to enter your suburb or tap "Locate me".</p>
      </div>

      <template v-else>
        <!-- Loading -->
        <div v-if="store.loadingForecast" class="loading-state">
          <div class="spinner"></div>
          <p>Building your week forecast…</p>
        </div>

        <template v-else-if="store.forecastResult">
          <!-- Best Window Banner -->
          <div class="best-window-banner">
            <div class="bw-left">
              <p class="bw-label">BEST WINDOW THIS WEEK</p>
              <p class="bw-text">{{ bestWindowText }}</p>
            </div>

            <button class="bw-btn" @click="$router.push('/best-time/result')">
              Find best spots →
            </button>
          </div>

          <!-- Best Window Summary Card -->
          <section class="section" v-if="bestForecastRow">
            <div class="best-summary-card">
              <div class="best-summary-main">
                <p class="summary-label">Best Window This Week</p>
                <h2>{{ bestForecastRow.day }}, {{ formatHour(bestForecastRow.hour) }}</h2>
                <p class="summary-sub">
                  This is the strongest recommended time based on lower crowd level
                  and your weekly resonance forecast.
                </p>
              </div>

              <div class="summary-grid">
                <div class="summary-item">
                  <span>Suggested location</span>
                  <strong>{{ suggestedLocation }}</strong>
                </div>

                <div class="summary-item">
                  <span>Comfort note</span>
                  <strong>{{ comfortNote }}</strong>
                </div>

                <div class="summary-item">
                  <span>Suggested activity</span>
                  <strong>{{ suggestedActivity }}</strong>
                </div>

                <div class="summary-item">
                  <span>Forecast strength</span>
                  <strong>{{ bestForecastRow.strength }}% · Best</strong>
                </div>
              </div>
            </div>
          </section>

          <!-- 7-Day Horizontal Forecast -->
          <section class="section" v-if="weeklyForecastRows.length">
            <h2 class="section-title">
              <AppIcon name="bar-chart" :size="22" color="#2f3152" class="title-icon" />
              7-day resonance forecast
            </h2>

            <p class="section-sub">
              Each bar shows the strongest recommended time for that day. Longer bars
              mean a better match for a calm and comfortable outing.
            </p>

            <div class="forecast-list">
              <div
                v-for="row in weeklyForecastRows"
                :key="row.day"
                class="forecast-row"
                :class="{ 'forecast-best': row.isBest }"
              >
                <div class="forecast-day-block">
                  <span class="forecast-day">{{ row.day }}</span>
                  <span class="forecast-time">{{ formatHour(row.hour) }}</span>
                </div>

                <div class="forecast-bar-area">
                  <div class="forecast-bar-track">
                    <div
                      class="forecast-bar-fill"
                      :class="{ 'forecast-bar-best': row.isBest }"
                      :style="{ width: `${row.strength}%` }"
                    ></div>
                  </div>
                </div>

                <div class="forecast-meta">
                  <span class="forecast-strength">{{ row.strength }}%</span>
                  <span v-if="row.isBest" class="best-pill">Best</span>
                </div>
              </div>
            </div>
          </section>

          <!-- 7-Day Heatmap -->
          <section class="section">
            <h2 class="section-title">
              <AppIcon name="calendar" :size="22" color="#2f3152" class="title-icon" />
              Crowd heatmap — this week
            </h2>

            <p class="section-sub">
              Darker green = quieter. Tap any cell to see details.
              Only showing 8am – 8pm.
            </p>

            <div class="heatmap-wrap">
              <!-- Hour labels row -->
              <div class="heatmap-grid">
                <div class="day-col-label"></div>
                <div
                  v-for="h in displayHours"
                  :key="h"
                  class="hour-label"
                >
                  {{ formatHour(h) }}
                </div>
              </div>

              <!-- One row per day -->
              <div
                v-for="day in forecastDays"
                :key="day"
                class="heatmap-grid"
              >
                <div class="day-label">{{ day.slice(0, 3) }}</div>

                <div
                  v-for="h in displayHours"
                  :key="h"
                  class="heat-cell"
                  :class="getCellClass(day, h)"
                  :title="`${day} ${formatHour(h)} — ${getCellLevel(day, h)}`"
                  @click="selectCell(day, h)"
                >
                  <span v-if="isSelectedCell(day, h)" class="cell-dot"></span>
                </div>
              </div>

              <!-- Legend -->
              <div class="heatmap-legend">
                <span class="legend-item legend-low">Quiet</span>
                <span class="legend-item legend-moderate">Moderate</span>
                <span class="legend-item legend-high">Busy</span>
              </div>
            </div>

            <!-- Selected cell detail -->
            <div v-if="selectedCell" class="cell-detail">
              <AppIcon name="clock" :size="22" color="#0c8b7d" />

              <div class="cell-detail-text">
                <strong>{{ selectedCell.day }}, {{ formatHour(selectedCell.hour) }}</strong>
                <span class="crowd-badge" :class="`crowd-${selectedCell.level.toLowerCase()}`">
                  {{ selectedCell.level }}
                </span>
                <span class="cell-count">~{{ selectedCell.avg_count }} people/hr avg</span>
              </div>

              <button class="plan-cell-btn" @click="$router.push('/best-time/result')">
                Plan this visit →
              </button>
            </div>
          </section>

          <!-- Quietest Day Summary -->
          <section class="section">
            <h2 class="section-title">
              <AppIcon name="trophy" :size="22" color="#2f3152" class="title-icon" />
              Quietest day this week
            </h2>

            <div class="quiet-day-card" v-if="quietestDay">
              <div class="qd-left">
                <span class="qd-day">{{ quietestDay.day }}</span>
                <span class="qd-time">Best from {{ formatHour(quietestDay.hour) }}</span>
              </div>

              <div class="qd-right">
                <span class="crowd-badge crowd-low">Low crowd</span>
                <span class="qd-count">~{{ quietestDay.avg_count }} people/hr</span>
              </div>
            </div>

            <p class="data-note">{{ store.forecastResult.data_note }}</p>
          </section>

          <!-- Green Spaces -->
          <section class="section" v-if="store.greenSpaces.length">
            <h2 class="section-title">
              <AppIcon name="leaf" :size="22" color="#2f3152" class="title-icon" />
              Comfortable parks near you
            </h2>

            <p class="section-sub">Ranked by comfort score — walkability, shade, and toilet access.</p>

            <div class="spaces-list">
              <div
                v-for="space in store.greenSpaces"
                :key="space.space_id"
                class="space-card"
              >
                <div class="space-header">
                  <div class="space-icon-wrap">
                    <AppIcon
                      :name="space.has_toilet_nearby ? 'leaf' : 'star'"
                      :size="20"
                      :color="space.has_toilet_nearby ? '#0c8b7d' : '#e6a800'"
                    />
                  </div>

                  <div class="space-info">
                    <h3 class="space-name">{{ space.space_name }}</h3>
                    <p class="space-meta">
                      {{ space.distance_km?.toFixed(1) }} km · {{ space.category }}
                    </p>
                  </div>

                  <div class="comfort-score-wrap">
                    <span class="comfort-num">{{ Math.round(space.comfort_score) }}</span>
                    <span class="comfort-label">comfort</span>
                  </div>
                </div>

                <!-- Comfort bar -->
                <div class="comfort-bar-track">
                  <div
                    class="comfort-bar-fill"
                    :style="{ width: `${space.comfort_score}%` }"
                    :class="comfortBarClass(space.comfort_score)"
                  ></div>
                </div>

                <!-- Tags -->
                <div class="space-tags">
                  <span v-if="space.has_toilet_nearby" class="space-tag tag-toilet">
                    <AppIcon name="check-circle" :size="13" color="#2a4ab0" class="tag-icon" />
                    Accessible toilet nearby
                  </span>

                  <span v-else class="space-tag tag-no-toilet">
                    <AppIcon name="alert-triangle" :size="13" color="#8a4000" class="tag-icon" />
                    No toilet within walking distance
                  </span>

                  <span v-if="space.walkability_score > 70" class="space-tag tag-walk">
                    <AppIcon name="navigation" :size="13" color="#0a6e62" class="tag-icon" />
                    Good walkability
                  </span>

                  <span v-if="space.public_access !== false" class="space-tag tag-access">
                    <AppIcon name="check" :size="13" color="#3a6a10" class="tag-icon" />
                    Free public access
                  </span>
                </div>
              </div>
            </div>
          </section>

          <!-- Loading spaces -->
          <div v-else-if="store.loadingSpaces" class="section loading-row">
            <div class="spinner"></div> Loading nearby parks…
          </div>
        </template>

        <!-- No forecast data -->
        <div v-else class="empty-state">
          <div class="empty-icon">
            <AppIcon name="bar-chart" :size="48" color="#9b9db8" />
          </div>
          <h3>No forecast data available</h3>
          <p>No pedestrian sensors found near this location. Try a suburb closer to Melbourne CBD.</p>
        </div>

        <!-- Bottom nav -->
        <div class="bottom-nav">
          <button class="nav-btn" @click="$router.push('/best-time')">
            ← Live score
          </button>

          <button class="nav-btn nav-btn-primary" @click="$router.push('/best-time/result')">
            Best spots now →
          </button>

          <button class="nav-btn" @click="$router.push('/best-time/welcoming')">
            <AppIcon name="heart" :size="14" color="#0c8b7d" class="nav-icon" />
            Welcoming spaces
          </button>
        </div>
      </template>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import MainLayout from '../layouts/MainLayout.vue'
import LocationBar from '../components/LocationBar.vue'
import AppIcon from '../components/AppIcon.vue'
import { resonanceStore as store } from '../stores/resonanceStore'
import { useResonanceApi } from '../composables/useResonanceApi'

const { fetchForecast, fetchGreenSpaces } = useResonanceApi()

// Hours to display in heatmap: 8am to 8pm
const displayHours = Array.from({ length: 13 }, (_, i) => i + 8)

// AC 4.3 requires this display order
const dayDisplayOrder = [
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday',
  'Monday',
]

const forecastDays = computed(() => store.forecastResult?.forecast_days ?? [])

const orderedForecastDays = computed(() => {
  const days = store.forecastResult?.forecast_days ?? []
  const orderedDays = dayDisplayOrder.filter(day => days.includes(day))
  const otherDays = days.filter(day => !dayDisplayOrder.includes(day))

  return [...orderedDays, ...otherDays]
})

// Selected cell state
const selectedCell = ref(null)

const savedRoutineProfile = ref({
  wakeTime: '',
  energyTime: '',
  outingGoals: [],
})

const savedMood = ref('')

function formatHour(h) {
  const ampm = h < 12 ? 'am' : 'pm'
  const h12 = h % 12 === 0 ? 12 : h % 12
  return `${h12}${ampm}`
}

function getHourData(day, hour) {
  return store.forecastResult?.forecast?.[day]?.[hour] ?? null
}

function getCellLevel(day, hour) {
  return getHourData(day, hour)?.crowd_level ?? 'Unknown'
}

function getCellClass(day, hour) {
  const level = getCellLevel(day, hour).toLowerCase()
  return `cell-${level}`
}

function isSelectedCell(day, hour) {
  return selectedCell.value?.day === day && selectedCell.value?.hour === hour
}

function selectCell(day, hour) {
  const data = getHourData(day, hour)

  if (!data) return

  if (isSelectedCell(day, hour)) {
    selectedCell.value = null
    return
  }

  selectedCell.value = {
    day,
    hour,
    level: data.crowd_level,
    avg_count: Math.round(data.avg_count),
  }
}

function getBestHourForDay(day) {
  const forecast = store.forecastResult?.forecast?.[day]

  if (!forecast) return null

  let best = null

  for (const h of displayHours) {
    const data = forecast[h]

    if (!data) continue

    const avgCount = Number(data.avg_count)

    if (!best || avgCount < best.avg_count) {
      best = {
        day,
        hour: h,
        avg_count: Math.round(avgCount),
        level: data.crowd_level ?? 'Unknown',
      }
    }
  }

  return best
}

const dailyBestWindows = computed(() => {
  return orderedForecastDays.value
    .map(day => getBestHourForDay(day))
    .filter(Boolean)
})

const bestBaseWindow = computed(() => {
  if (!dailyBestWindows.value.length) return null

  return dailyBestWindows.value.reduce((best, current) => {
    if (!best) return current
    return current.avg_count < best.avg_count ? current : best
  }, null)
})

const weeklyForecastRows = computed(() => {
  const rows = dailyBestWindows.value

  if (!rows.length) return []

  const counts = rows.map(row => row.avg_count)
  const minCount = Math.min(...counts)
  const maxCount = Math.max(...counts)
  const range = maxCount - minCount

  return rows.map(row => {
    let strength = range === 0
      ? 80
      : Math.round(45 + ((maxCount - row.avg_count) / range) * 55)

    const isBest =
      bestBaseWindow.value &&
      row.day === bestBaseWindow.value.day &&
      row.hour === bestBaseWindow.value.hour

    if (isBest) {
      strength = 100
    }

    return {
      ...row,
      strength,
      isBest,
    }
  })
})

const bestForecastRow = computed(() => {
  return weeklyForecastRows.value.find(row => row.isBest) ?? null
})

// Find quietest hour across all days
const quietestDay = computed(() => {
  const forecast = store.forecastResult?.forecast

  if (!forecast) return null

  let best = null

  for (const day of (store.forecastResult.forecast_days ?? [])) {
    for (const h of displayHours) {
      const d = forecast[day]?.[h]

      if (!d) continue

      if (!best || d.avg_count < best.avg_count) {
        best = {
          day,
          hour: h,
          avg_count: Math.round(d.avg_count),
        }
      }
    }
  }

  return best
})

const bestWindowText = computed(() => {
  if (!bestForecastRow.value) return 'Calculating your best window…'

  return `${bestForecastRow.value.day} at ${formatHour(bestForecastRow.value.hour)} is your strongest window — ideal for a peaceful outing.`
})

const suggestedLocation = computed(() => {
  if (store.greenSpaces?.length) {
    return store.greenSpaces[0].space_name
  }

  return 'A nearby park or welcoming open space'
})

const comfortNote = computed(() => {
  if (!bestForecastRow.value) {
    return 'Comfort conditions will be checked once the forecast loads.'
  }

  if (bestForecastRow.value.level === 'Low') {
    return 'Lower crowd level and calmer conditions.'
  }

  if (bestForecastRow.value.level === 'Moderate') {
    return 'Moderate crowd level with a manageable outing window.'
  }

  return 'This is the best available window, but the area may still feel busy.'
})

const suggestedActivity = computed(() => {
  const goals = savedRoutineProfile.value.outingGoals ?? []

  if (savedMood.value === 'meet' || goals.includes('Socialise')) {
    return 'Visit a welcoming space or try a light community activity.'
  }

  if (savedMood.value === 'tired' || goals.includes('Relax')) {
    return 'Take a short, low-effort outing or sit in a calm outdoor area.'
  }

  if (savedMood.value === 'fresh-air' || goals.includes('Walk')) {
    return 'Take a gentle walk or fresh air break.'
  }

  return 'Try a gentle local outing that feels comfortable and easy.'
})

function comfortBarClass(score) {
  if (score >= 70) return 'bar-high'
  if (score >= 45) return 'bar-mid'
  return 'bar-low'
}

function loadSavedPreferences() {
  const routine = localStorage.getItem('e4RoutineProfile')
  const mood = localStorage.getItem('e4SelectedMood')

  if (routine) {
    try {
      savedRoutineProfile.value = JSON.parse(routine)
    } catch (error) {
      localStorage.removeItem('e4RoutineProfile')
    }
  }

  if (mood) {
    savedMood.value = mood
  }
}

async function loadAll() {
  if (!store.locationReady) return

  const { userLat: lat, userLon: lon } = store

  store.loadingForecast = true
  store.loadingSpaces = true
  selectedCell.value = null

  try {
    const [forecast, spaces] = await Promise.all([
      fetchForecast(lat, lon, 5),
      fetchGreenSpaces(lat, lon, 5, null, 6),
    ])

    store.forecastResult = forecast
    store.greenSpaces = Array.isArray(spaces) ? spaces : []
  } catch (error) {
    console.error('Best time weekly forecast failed:', error)

    store.forecastResult = null
    store.greenSpaces = []
  } finally {
    store.loadingForecast = false
    store.loadingSpaces = false
  }
}

watch(() => store.locationReady, (ready) => {
  if (ready) loadAll()
})

watch(() => [store.userLat, store.userLon], () => {
  if (store.locationReady) loadAll()
})

onMounted(() => {
  loadSavedPreferences()

  if (store.locationReady) loadAll()
})
</script>

<style scoped>
.page { min-height: 100vh; background: #f5f5fa; }

/* Hero */
.week-hero {
  position: relative; overflow: hidden;
  padding: 40px 48px 44px;
  background: linear-gradient(135deg, #0c8b7d, #0a6e62);
  color: #fff;
}

.back-btn {
  display: inline-flex; align-items: center; gap: 6px;
  margin-bottom: 20px; padding: 8px 16px;
  border-radius: 999px; border: none;
  background: rgba(255,255,255,0.18); color: #fff;
  font-size: calc(14px * var(--font-scale)); font-weight: 700;
  cursor: pointer; transition: background 0.15s;
}

.back-btn:hover { background: rgba(255,255,255,0.28); }

.hero-eyebrow {
  margin: 0 0 10px; font-size: calc(12px * var(--font-scale));
  font-weight: 800; letter-spacing: 0.1em; opacity: 0.8;
}

.week-hero h1 {
  margin: 0 0 12px; font-family: 'Fraunces', serif;
  font-size: calc(42px * var(--font-scale)); font-weight: 700; line-height: 1.15;
}

.week-hero em { color: #f5c812; font-style: italic; }

.hero-sub { margin: 0; font-size: calc(14px * var(--font-scale)); opacity: 0.82; }

.hero-circle { position: absolute; border-radius: 50%; background: rgba(255,255,255,0.09); }

.c1 { width: 220px; height: 220px; right: -40px; top: -40px; }

.c2 { width: 140px; height: 140px; right: 150px; bottom: -60px; }

/* States */
.empty-state { text-align: center; padding: 72px 40px; color: #6b6d88; }

.empty-icon { font-size: 48px; margin-bottom: 16px; }

.empty-state h3 { margin: 0 0 10px; font-size: calc(22px * var(--font-scale)); color: #2f3152; }

.empty-state p { margin: 0; font-size: calc(16px * var(--font-scale)); }

.loading-state {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; min-height: 40vh; gap: 16px;
  color: #6b6d88; font-size: calc(16px * var(--font-scale)); font-weight: 600;
}

.loading-row {
  display: flex; align-items: center; gap: 12px;
  color: #6b6d88; font-size: calc(15px * var(--font-scale)); font-weight: 600;
}

.spinner {
  width: 36px; height: 36px;
  border: 4px solid #e0e1ed; border-top-color: #0c8b7d;
  border-radius: 50%; animation: spin 0.8s linear infinite; flex-shrink: 0;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Best window banner */
.best-window-banner {
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; flex-wrap: wrap;
  margin: 0; padding: 20px 40px;
  background: #0c6b60; color: #fff;
}

.bw-label {
  margin: 0 0 6px; font-size: calc(11px * var(--font-scale));
  font-weight: 800; letter-spacing: 0.1em; color: rgba(255,255,255,0.7);
}

.bw-text { margin: 0; font-size: calc(16px * var(--font-scale)); font-weight: 700; color: #f5c812; }

.bw-btn {
  padding: 12px 22px; border: none; border-radius: 12px;
  background: #f5c812; color: #1a1200;
  font-family: 'Manrope', sans-serif;
  font-size: calc(14px * var(--font-scale)); font-weight: 800;
  cursor: pointer; white-space: nowrap; flex-shrink: 0;
  transition: background 0.15s;
}

.bw-btn:hover { background: #e6b800; }

/* Section */
.section { padding: 28px 40px; border-bottom: 1.5px solid #e8e9f3; }

.section-title {
  margin: 0 0 6px; font-family: 'Fraunces', serif;
  font-size: calc(22px * var(--font-scale)); color: #2f3152;
}

.section-sub { margin: 0 0 20px; font-size: calc(13px * var(--font-scale)); color: #6b6d88; }

/* Best summary card */
.best-summary-card {
  padding: 26px 28px;
  background: #fff;
  border: 2px solid #0c8b7d;
  border-radius: 20px;
  box-shadow: 0 12px 26px rgba(12, 139, 125, 0.1);
}

.summary-label {
  margin: 0 0 8px;
  font-size: calc(11px * var(--font-scale));
  font-weight: 800;
  letter-spacing: 0.1em;
  color: #0c8b7d;
  text-transform: uppercase;
}

.best-summary-main h2 {
  margin: 0 0 8px;
  font-family: 'Fraunces', serif;
  font-size: calc(30px * var(--font-scale));
  color: #2f3152;
}

.summary-sub {
  margin: 0 0 20px;
  color: #6b6d88;
  font-size: calc(14px * var(--font-scale));
  line-height: 1.5;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.summary-item {
  padding: 16px;
  border-radius: 16px;
  background: #f0faf8;
}

.summary-item span {
  display: block;
  margin-bottom: 8px;
  font-size: calc(11px * var(--font-scale));
  font-weight: 800;
  color: #6b6d88;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.summary-item strong {
  color: #2f3152;
  font-size: calc(14px * var(--font-scale));
  line-height: 1.4;
}

/* Weekly forecast bars */
.forecast-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.forecast-row {
  display: grid;
  grid-template-columns: 140px 1fr 120px;
  align-items: center;
  gap: 18px;
  padding: 16px 18px;
  background: #fff;
  border: 1.5px solid #e0e1ed;
  border-radius: 16px;
}

.forecast-best {
  border-color: #0c8b7d;
  background: #f0faf8;
}

.forecast-day-block {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.forecast-day {
  font-weight: 800;
  color: #2f3152;
  font-size: calc(15px * var(--font-scale));
}

.forecast-time {
  font-weight: 700;
  color: #6b6d88;
  font-size: calc(13px * var(--font-scale));
}

.forecast-bar-area {
  width: 100%;
}

.forecast-bar-track {
  height: 18px;
  background: #e8e9f3;
  border-radius: 999px;
  overflow: hidden;
}

.forecast-bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #55b7aa, #0c8b7d);
  transition: width 0.45s ease;
}

.forecast-bar-best {
  background: linear-gradient(90deg, #0c8b7d, #f5c812);
}

.forecast-meta {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
}

.forecast-strength {
  color: #6b6d88;
  font-weight: 800;
  font-size: calc(13px * var(--font-scale));
}

.best-pill {
  padding: 4px 10px;
  border-radius: 999px;
  background: #f5c812;
  color: #1a1200;
  font-size: calc(11px * var(--font-scale));
  font-weight: 900;
}

/* Heatmap */
.heatmap-wrap { overflow-x: auto; }

.heatmap-grid {
  display: grid;
  grid-template-columns: 44px repeat(13, 1fr);
  gap: 3px;
  min-width: 480px;
  margin-bottom: 3px;
}

.day-col-label { width: 44px; }

.hour-label {
  font-size: calc(10px * var(--font-scale));
  font-weight: 700; color: #9b9db8;
  text-align: center; padding: 2px 0;
}

.day-label {
  font-size: calc(13px * var(--font-scale));
  font-weight: 800; color: #2f3152;
  display: flex; align-items: center;
  padding-right: 6px;
}

.heat-cell {
  height: 32px; border-radius: 6px;
  cursor: pointer; position: relative;
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.1s, opacity 0.1s;
}

.heat-cell:hover { transform: scale(1.12); opacity: 0.9; }

.cell-low { background: #0c8b7d; }

.cell-moderate { background: #f5c812; }

.cell-high { background: #e05c4a; }

.cell-unknown { background: #e8e9f3; }

.cell-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #fff; box-shadow: 0 0 0 2px rgba(0,0,0,0.25);
}

.heatmap-legend {
  display: flex; gap: 16px; margin-top: 12px;
}

.legend-item {
  display: flex; align-items: center; gap: 7px;
  font-size: calc(12px * var(--font-scale)); font-weight: 700; color: #3c3c58;
}

.legend-item::before {
  content: ''; width: 16px; height: 16px;
  border-radius: 4px; display: block;
}

.legend-low::before { background: #0c8b7d; }

.legend-moderate::before { background: #f5c812; }

.legend-high::before { background: #e05c4a; }

/* Selected cell detail */
.cell-detail {
  display: flex; align-items: center; gap: 14px;
  margin-top: 16px; padding: 14px 18px;
  background: #fff; border: 1.5px solid #0c8b7d;
  border-radius: 14px; flex-wrap: wrap;
}

.cell-detail-text {
  display: flex; align-items: center; gap: 10px;
  flex: 1; flex-wrap: wrap;
  font-size: calc(14px * var(--font-scale)); font-weight: 700; color: #2f3152;
}

.cell-count { font-size: calc(13px * var(--font-scale)); color: #6b6d88; font-weight: 600; }

.plan-cell-btn {
  padding: 9px 18px; border: none; border-radius: 10px;
  background: #0c8b7d; color: #fff;
  font-family: 'Manrope', sans-serif;
  font-size: calc(13px * var(--font-scale)); font-weight: 700;
  cursor: pointer; white-space: nowrap; flex-shrink: 0;
}

.plan-cell-btn:hover { background: #0a756a; }

/* Crowd badges */
.crowd-badge { padding: 3px 10px; border-radius: 999px; font-size: calc(12px * var(--font-scale)); font-weight: 700; }

.crowd-low { background: #e8f8f5; color: #0a6e62; }

.crowd-moderate { background: #fff8e0; color: #8a6000; }

.crowd-high { background: #ffeaea; color: #c84848; }

/* Quietest day card */
.quiet-day-card {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 24px; background: #fff;
  border: 1.5px solid #0c8b7d; border-radius: 16px;
  margin-bottom: 14px; flex-wrap: wrap; gap: 12px;
}

.qd-left { display: flex; flex-direction: column; gap: 4px; }

.qd-day { font-family: 'Fraunces', serif; font-size: calc(26px * var(--font-scale)); font-weight: 700; color: #2f3152; }

.qd-time { font-size: calc(14px * var(--font-scale)); color: #6b6d88; font-weight: 600; }

.qd-right { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }

.qd-count { font-size: calc(13px * var(--font-scale)); color: #9b9db8; font-weight: 600; }

.data-note { margin: 0; font-size: calc(12px * var(--font-scale)); color: #b0b2c8; font-style: italic; }

/* Green spaces */
.spaces-list { display: flex; flex-direction: column; gap: 14px; }

.space-card {
  background: #fff; border: 1.5px solid #e0e1ed;
  border-radius: 16px; padding: 20px 24px;
  display: flex; flex-direction: column; gap: 12px;
}

.space-header { display: flex; align-items: flex-start; gap: 14px; }

.space-icon-wrap {
  width: 44px; height: 44px; border-radius: 12px;
  background: #e8f8f5; display: flex;
  align-items: center; justify-content: center;
  font-size: 20px; flex-shrink: 0;
}

.space-info { flex: 1; }

.space-name { margin: 0 0 4px; font-size: calc(17px * var(--font-scale)); font-weight: 800; color: #2f3152; }

.space-meta { margin: 0; font-size: calc(13px * var(--font-scale)); color: #6b6d88; font-weight: 600; }

.comfort-score-wrap { display: flex; flex-direction: column; align-items: center; gap: 2px; flex-shrink: 0; }

.comfort-num { font-size: calc(28px * var(--font-scale)); font-weight: 800; color: #0c8b7d; line-height: 1; }

.comfort-label { font-size: calc(10px * var(--font-scale)); color: #9b9db8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }

.comfort-bar-track { height: 8px; background: #e8e9f3; border-radius: 999px; overflow: hidden; }

.comfort-bar-fill { height: 100%; border-radius: 999px; transition: width 0.5s ease; }

.bar-high { background: linear-gradient(90deg, #0c8b7d, #4bb6a8); }

.bar-mid { background: linear-gradient(90deg, #e6a800, #f5c812); }

.bar-low { background: #e05c4a; }

.space-tags { display: flex; flex-wrap: wrap; gap: 8px; }

.space-tag {
  padding: 4px 12px; border-radius: 999px;
  font-size: calc(12px * var(--font-scale)); font-weight: 700;
}

.tag-toilet { background: #e8f0ff; color: #2a4ab0; }

.tag-no-toilet { background: #fff3e8; color: #8a4000; }

.tag-walk { background: #e8f8f5; color: #0a6e62; }

.tag-access { background: #f0f8e8; color: #3a6a10; }

/* Bottom nav */
.bottom-nav { display: flex; gap: 10px; flex-wrap: wrap; padding: 24px 40px 40px; }

.nav-btn {
  flex: 1; min-width: 140px; padding: 14px 16px;
  border: 2px solid #d8d9e8; border-radius: 14px;
  background: #fff; color: #3c3c58;
  font-family: 'Manrope', sans-serif;
  font-size: calc(14px * var(--font-scale)); font-weight: 700;
  cursor: pointer; transition: all 0.15s ease; text-align: center;
}

.nav-btn:hover { border-color: #0c8b7d; color: #0c8b7d; }

.nav-btn-primary { background: #0c8b7d; color: #fff; border-color: #0c8b7d; }

.nav-btn-primary:hover { background: #0a756a; color: #fff; }

@media (max-width: 900px) {
  .week-hero { padding: 32px 20px; }

  .week-hero h1 { font-size: calc(30px * var(--font-scale)); }

  .section { padding: 22px 16px; }

  .best-window-banner { padding: 16px 20px; }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .forecast-row {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .forecast-meta {
    justify-content: flex-start;
  }

  .bottom-nav { padding: 20px 16px 36px; }

  .heatmap-grid { grid-template-columns: 36px repeat(13, 1fr); }

  .heat-cell { height: 26px; }
}
</style>