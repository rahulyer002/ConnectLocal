<!-- src/pages/BestTimePage.vue — Epic 4 Best Time setup screen -->
<template>
  <MainLayout>
    <div class="page">
      <LocationBar @locationChanged="loadAll" />

      <!-- Hero -->
      <div class="hero">
        <div class="hero-badge">☆ Personalised Timing Engine</div>
        <h1>When is the <em>best time</em><br />for you?</h1>
        <p class="hero-sub">
          Tell us how you are feeling and what you would like to do.
          We will find the perfect window in your day.
        </p>

        <div class="hero-circle c1"></div>
        <div class="hero-circle c2"></div>
      </div>

      <!-- No location prompt -->
      <div v-if="!store.locationReady" class="empty-state">
        <div class="empty-icon">📍</div>
        <h3>Set your location to get started</h3>
        <p>Use the bar above to enter your suburb or tap "Locate me".</p>
      </div>

      <template v-else>
        <!-- Setup panel -->
        <section class="setup-panel">
          <!-- Your Usual Routine -->
          <div class="routine-card">
            <h2 class="card-title">Your Usual Routine</h2>

            <div class="routine-row">
              <div class="routine-label">Wake up time</div>
              <div class="routine-options">
                <button
                  v-for="time in wakeOptions"
                  :key="time"
                  type="button"
                  class="pill-btn"
                  :class="{ active: routineProfile.wakeTime === time }"
                  @click="selectRoutineOption('wakeTime', time)"
                >
                  {{ time }}
                </button>
              </div>
            </div>

            <div class="routine-row">
              <div class="routine-label">Best energy</div>
              <div class="routine-options">
                <button
                  v-for="time in energyOptions"
                  :key="time"
                  type="button"
                  class="pill-btn"
                  :class="{ active: routineProfile.energyTime === time }"
                  @click="selectRoutineOption('energyTime', time)"
                >
                  {{ time }}
                </button>
              </div>
            </div>

            <div class="routine-row">
              <div class="routine-label">Outing goal</div>
              <div class="routine-options">
                <button
                  v-for="goal in outingOptions"
                  :key="goal"
                  type="button"
                  class="pill-btn"
                  :class="{ active: routineProfile.outingGoals.includes(goal) }"
                  @click="toggleOutingGoal(goal)"
                >
                  {{ goal }}
                </button>
              </div>
            </div>
          </div>

          <!-- Mood selection -->
          <div class="mood-section">
            <h2 class="mood-title">How are you feeling right now?</h2>

            <div class="mood-grid">
              <button
                v-for="mood in moodOptions"
                :key="mood.key"
                type="button"
                class="mood-option"
                :class="[mood.className, { active: selectedMood === mood.key }]"
                @click="selectMood(mood.key)"
              >
                <span class="mood-icon">{{ mood.icon }}</span>
                <span class="mood-label">{{ mood.label }}</span>
              </button>
            </div>
          </div>

          <!-- CTA buttons -->
          <div class="setup-actions">
            <button
              type="button"
              class="find-btn"
              @click="findBestMoment"
            >
              Find My Best Moment Today
            </button>

            <button
              type="button"
              class="week-btn"
              @click="$router.push('/best-time/week')"
            >
              See my full week forecast
            </button>
          </div>

          <!-- Mood recommendation text -->
          <div class="mood-recommendation">
            <strong>{{ moodRecommendation.title }}</strong>
            <p>{{ moodRecommendation.message }}</p>
          </div>
        </section>

        <!-- Best Moment Result UI -->
        <section
          v-if="showGoNowCard && goNowRecommendationReady"
          ref="bestMomentResult"
          class="best-moment-result"
        >
          <div class="best-moment-hero">
            <button type="button" class="result-back-btn" @click="closeBestMoment">
              ‹ Back
            </button>

            <p class="result-eyebrow">Your best moment today</p>
            <h2>Now is a great time<br />to head out</h2>
          </div>

          <div class="go-now-panel">
            <p class="go-now-panel-label">Go Now Recommendation</p>

            <p class="go-now-summary">
              {{ goNowSummary }}
            </p>

            <div class="go-now-row">
              <span>Crowd level</span>
              <strong class="status-pill status-green">{{ crowdStatusText }}</strong>
            </div>

            <div class="go-now-row">
              <span>Conditions</span>
              <strong class="status-pill status-yellow">{{ conditionStatusText }}</strong>
            </div>

            <div class="go-now-row">
              <span>Leave home by</span>
              <strong>{{ leaveHomeByText }}</strong>
            </div>

            <div class="go-now-row">
              <span>How to get there</span>
              <strong>{{ routeMethodText }}</strong>
            </div>
          </div>

          <button
            type="button"
            class="show-route-btn"
            @click="$router.push(goNowAction.path)"
          >
            Show me how to get there
          </button>

          <button
            type="button"
            class="forecast-instead-btn"
            @click="$router.push('/best-time/week')"
          >
            See my full week forecast instead
          </button>
        </section>

        <!-- If score is not good enough -->
        <section
          v-else-if="showGoNowCard && store.scoreResult"
          ref="bestMomentResult"
          class="wait-card"
        >
          <p class="wait-label">Timing check</p>
          <h2>A better window may be coming later</h2>
          <p>
            Your live score is not strong enough yet. Check the week forecast
            or try a quieter time later today.
          </p>
        </section>

        <!-- Live Score -->
        <section class="section">
          <div v-if="store.loadingScore" class="loading-row">
            <div class="spinner"></div>
            Loading live conditions…
          </div>

          <div v-else-if="store.scoreResult" class="score-panel">
            <div class="score-ring-wrap">
              <svg class="score-ring" viewBox="0 0 120 120">
                <circle class="ring-bg" cx="60" cy="60" r="50" />
                <circle
                  class="ring-fill"
                  cx="60"
                  cy="60"
                  r="50"
                  :stroke="gradeColor"
                  :stroke-dasharray="`${scoreArc} ${314 - scoreArc}`"
                  stroke-dashoffset="78"
                />
              </svg>

              <div class="score-label-wrap">
                <span class="score-num">
                  {{ Math.round(store.scoreResult.resonance_score) }}
                </span>
                <span class="score-grade" :style="{ color: gradeColor }">
                  {{ store.scoreResult.grade }}
                </span>
              </div>
            </div>

            <div class="breakdown">
              <p class="breakdown-title">What makes up your score right now</p>

              <div
                v-for="item in breakdownItems"
                :key="item.label"
                class="bar-row"
              >
                <span class="bar-label">{{ item.label }}</span>

                <div class="bar-track">
                  <div
                    class="bar-fill"
                    :style="{
                      width: `${(item.value / item.max) * 100}%`,
                      background: item.color
                    }"
                  ></div>
                </div>

                <span class="bar-pts">{{ item.value }}/{{ item.max }}</span>
              </div>

              <div v-if="store.scoreResult.weather" class="weather-strip">
                <div class="weather-chip">
                  🌡 {{ store.scoreResult.weather.temperature_c }}°C
                </div>
                <div class="weather-chip">
                  💨 {{ store.scoreResult.weather.wind_speed_kmh }} km/h
                </div>
                <div class="weather-chip">
                  💧 {{ store.scoreResult.weather.humidity_pct }}%
                </div>
                <div class="weather-chip">
                  🌫 PM2.5 {{ store.scoreResult.weather.pm25_ug_m3 }}
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Safety advice banner -->
        <div
          v-if="store.safetyConditions"
          class="advice-banner"
          :class="`verdict-${store.safetyConditions.conditions?.safety_verdict?.toLowerCase()}`"
        >
          <span class="advice-dot"></span>
          <div>
            <strong>{{ store.safetyConditions.conditions?.safety_verdict }} conditions</strong>
            — {{ store.safetyConditions.advice }}
          </div>
        </div>

        <!-- Quietest Times -->
        <section
          class="section"
          v-if="store.bestTimesResult?.best_times?.length"
        >
          <h2 class="section-title">🕐 Quietest times near you</h2>
          <p class="section-sub">
            Based on 2 years of City of Melbourne pedestrian sensor data.
          </p>

          <div class="quiet-list">
            <div
              v-for="(t, i) in store.bestTimesResult.best_times"
              :key="i"
              class="quiet-item"
              :class="{ 'quiet-best': i === 0 }"
            >
              <div class="quiet-rank">{{ i + 1 }}</div>

              <div class="quiet-info">
                <span class="quiet-day">{{ t.day_name }}</span>
                <span class="quiet-time">{{ t.hour_label }}</span>
              </div>

              <div class="quiet-right">
                <span
                  class="crowd-badge"
                  :class="`crowd-${t.crowd_level.toLowerCase()}`"
                >
                  {{ t.crowd_level }}
                </span>
                <span class="quiet-count">
                  {{ Math.round(t.avg_count) }} people/hr avg
                </span>
              </div>

              <span v-if="i === 0" class="best-tag">Best window</span>
            </div>
          </div>

          <p class="tip-text">{{ store.bestTimesResult.tip }}</p>
        </section>
      </template>
    </div>
  </MainLayout>
</template>

<script setup>
import { computed, watch, onMounted, ref, nextTick } from 'vue'
import MainLayout from '../layouts/MainLayout.vue'
import LocationBar from '../components/LocationBar.vue'
import { resonanceStore as store } from '../stores/resonanceStore'
import { useResonanceApi } from '../composables/useResonanceApi'

const {
  fetchScore,
  fetchSafety,
  fetchBestTimes,
  fetchGoNow,
} = useResonanceApi()

const showGoNowCard = ref(false)
const bestMomentResult = ref(null)
const goNowLiveResult = ref(null)

const wakeOptions = ['6 AM', '7 AM', '8 AM']
const energyOptions = ['Morning', 'Afternoon']
const outingOptions = ['Socialise', 'Walk', 'Relax']

const routineProfile = ref({
  wakeTime: '7 AM',
  energyTime: 'Morning',
  outingGoals: ['Socialise'],
})

const selectedMood = ref('happy')

const moodOptions = [
  { key: 'happy', label: 'Happy and ready', icon: '☺', className: 'mood-happy' },
  { key: 'meet', label: 'Want to meet people', icon: '♙', className: 'mood-meet' },
  { key: 'tired', label: 'Tired, need gentle', icon: '☾', className: 'mood-tired' },
  { key: 'fresh-air', label: 'Want some fresh air', icon: '☘', className: 'mood-fresh' },
]

const isRoutineComplete = computed(() => {
  return (
    routineProfile.value.wakeTime &&
    routineProfile.value.energyTime &&
    routineProfile.value.outingGoals.length > 0
  )
})

const preferredTimeText = computed(() => {
  if (routineProfile.value.energyTime === 'Morning') return 'a morning time'
  if (routineProfile.value.energyTime === 'Afternoon') return 'an afternoon time'
  return 'a quiet time'
})

const moodRecommendation = computed(() => {
  if (selectedMood.value === 'happy') {
    return {
      title: 'You may be ready for a more active outing.',
      message: `We suggest ${preferredTimeText.value} with good outdoor comfort and lower crowd levels.`,
    }
  }

  if (selectedMood.value === 'meet') {
    return {
      title: 'A welcoming social place may suit you today.',
      message: `We suggest ${preferredTimeText.value} at a library, community centre, or welcoming space.`,
    }
  }

  if (selectedMood.value === 'tired') {
    return {
      title: 'A gentle low-effort outing is a better match.',
      message: 'We suggest a quieter window and a short outing that does not feel too tiring.',
    }
  }

  return {
    title: 'Fresh air may be a good choice today.',
    message: `We suggest ${preferredTimeText.value} for a nearby outdoor space or gentle walk.`,
  }
})

const gradeColor = computed(() => {
  const g = store.scoreResult?.grade
  if (g === 'Excellent') return '#0a9e6e'
  if (g === 'Good') return '#0c8b7d'
  if (g === 'Fair') return '#e6a800'
  return '#c84848'
})

const scoreArc = computed(() => {
  const s = store.scoreResult?.resonance_score ?? 0
  return Math.round((s / 100) * 314)
})

const breakdownItems = computed(() => {
  const b = store.scoreResult?.breakdown
  if (!b) return []

  return [
    { label: 'Crowd level', value: b.crowd_score, max: 35, color: '#0c8b7d' },
    { label: 'Weather safety', value: b.weather_score, max: 35, color: '#2196a6' },
    { label: 'Comfort', value: b.comfort_score, max: 20, color: '#5c8a3c' },
    { label: 'Toilet access', value: b.toilet_score, max: 5, color: '#8b7d0c' },
    { label: 'Shade', value: b.shade_score, max: 5, color: '#6a5c2a' },
  ]
})

const isCurrentWindowGood = computed(() => {
  const grade = store.scoreResult?.grade
  return grade === 'Good' || grade === 'Excellent'
})

const goNowRecommendationReady = computed(() => {
  return (
    isRoutineComplete.value &&
    selectedMood.value &&
    store.scoreResult &&
    isCurrentWindowGood.value
  )
})

const bestGoNowSpot = computed(() => {
  return goNowLiveResult.value?.recommendations?.[0] ?? null
})

const goNowCrowdLevel = computed(() => {
  const apiCrowd = bestGoNowSpot.value?.crowd_level
  if (apiCrowd) return apiCrowd

  const crowdScore = store.scoreResult?.breakdown?.crowd_score
  if (crowdScore === undefined || crowdScore === null) return 'Moderate'
  if (crowdScore >= 24) return 'Low'
  if (crowdScore >= 14) return 'Moderate'
  return 'High'
})

const goNowLocation = computed(() => {
  if (bestGoNowSpot.value?.space_name) {
    return bestGoNowSpot.value.space_name
  }

  if (selectedMood.value === 'meet') return 'A welcoming community space nearby'
  if (selectedMood.value === 'tired') return 'A quiet nearby place for a short visit'
  if (selectedMood.value === 'fresh-air') return 'A nearby outdoor spot or park'

  return 'Best nearby spot from your area'
})

const goNowAction = computed(() => {
  if (bestGoNowSpot.value) {
    return {
      text: 'Find best nearby spot',
      path: '/best-time/result',
    }
  }

  if (selectedMood.value === 'meet') {
    return {
      text: 'Show nearby welcoming spaces',
      path: '/best-time/welcoming',
    }
  }

  if (selectedMood.value === 'tired') {
    return {
      text: 'See quietest times',
      path: '/best-time/week',
    }
  }

  return {
    text: 'Find best nearby spot',
    path: '/best-time/result',
  }
})

const crowdStatusText = computed(() => {
  const level = goNowCrowdLevel.value?.toLowerCase()

  if (level === 'low') return 'Quiet right now'
  if (level === 'moderate') return 'Moderate now'
  if (level === 'high') return 'Busy right now'

  return 'Moderate now'
})

const conditionStatusText = computed(() => {
  const weather =
    goNowLiveResult.value?.weather ??
    store.scoreResult?.weather

  if (!weather) return 'Comfortable'

  return `${weather.temperature_c}°C · ${weather.safety_verdict ?? 'Comfortable'}`
})

const leaveHomeByText = computed(() => {
  const leaveTime = new Date(Date.now() + 5 * 60 * 1000)

  return leaveTime.toLocaleTimeString([], {
    hour: 'numeric',
    minute: '2-digit',
  })
})

const routeMethodText = computed(() => {
  if (routineProfile.value.outingGoals.includes('Walk')) return 'Walking'
  if (selectedMood.value === 'meet') return 'Nearby community space'
  return 'Walking or public transport'
})

const goNowSummary = computed(() => {
  if (bestGoNowSpot.value?.why_recommended) {
    return `${goNowLocation.value}: ${bestGoNowSpot.value.why_recommended}`
  }

  const location = goNowLocation.value
  const weather = store.scoreResult?.weather
  const temperatureText = weather ? `${weather.temperature_c} degrees` : 'comfortable weather'

  if (selectedMood.value === 'meet') {
    return `${location} looks suitable now, ${temperatureText}, and it may be a good place to connect with others.`
  }

  if (selectedMood.value === 'tired') {
    return `${location} looks calm enough now, ${temperatureText}, and it may suit a short gentle outing.`
  }

  if (selectedMood.value === 'fresh-air') {
    return `${location} looks suitable now, ${temperatureText}, and it may be a good moment for fresh air.`
  }

  return `${location} looks suitable now, ${temperatureText}, and current conditions are good for a comfortable local outing.`
})

function selectRoutineOption(field, value) {
  routineProfile.value[field] = value
  saveRoutineProfile()
}

function toggleOutingGoal(goal) {
  if (routineProfile.value.outingGoals.includes(goal)) {
    routineProfile.value.outingGoals = routineProfile.value.outingGoals.filter(
      item => item !== goal
    )
  } else {
    routineProfile.value.outingGoals.push(goal)
  }

  saveRoutineProfile()
}

function saveRoutineProfile() {
  localStorage.setItem('e4RoutineProfile', JSON.stringify(routineProfile.value))
}

function selectMood(mood) {
  selectedMood.value = mood
  localStorage.setItem('e4SelectedMood', mood)
}

async function findBestMoment() {
  showGoNowCard.value = true

  if (store.locationReady) {
    const { userLat: lat, userLon: lon } = store

    try {
      goNowLiveResult.value = await fetchGoNow(lat, lon, 5)
    } catch (error) {
      console.error('Go now API failed:', error)
      goNowLiveResult.value = null
    }
  }

  await nextTick()

  bestMomentResult.value?.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })
}

async function closeBestMoment() {
  showGoNowCard.value = false

  await nextTick()

  document.querySelector('.setup-panel')?.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })
}

async function loadAll() {
  if (!store.locationReady) return

  const { userLat: lat, userLon: lon } = store

  store.loadingScore = true

  try {
    const [score, safety, bestTimes] = await Promise.all([
      fetchScore(lat, lon),
      fetchSafety(lat, lon),
      fetchBestTimes(lat, lon, 5),
    ])

    store.scoreResult = score
    store.safetyConditions = safety
    store.bestTimesResult = bestTimes
  } catch (error) {
    console.error('BestTimePage API failed:', error)

    store.scoreResult = null
    store.safetyConditions = null
    store.bestTimesResult = null
  } finally {
    store.loadingScore = false
  }
}

watch(() => store.locationReady, (ready) => {
  if (ready) loadAll()
})

watch(() => [store.userLat, store.userLon], () => {
  if (store.locationReady) loadAll()
})

onMounted(() => {
  const savedRoutine = localStorage.getItem('e4RoutineProfile')
  const savedMood = localStorage.getItem('e4SelectedMood')

  if (savedRoutine) {
    try {
      routineProfile.value = JSON.parse(savedRoutine)
    } catch (error) {
      localStorage.removeItem('e4RoutineProfile')
    }
  }

  if (savedMood) {
    selectedMood.value = savedMood
  }

  if (store.locationReady) loadAll()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f5fa;
}

/* Hero */
.hero {
  position: relative;
  overflow: hidden;
  padding: 48px 56px 54px;
  background: linear-gradient(135deg, #087867, #005843);
  color: #ffffff;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  padding: 8px 20px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
  font-size: calc(16px * var(--font-scale));
  font-weight: 800;
  margin-bottom: 28px;
}

.hero h1 {
  margin: 0 0 18px;
  max-width: 520px;
  font-family: 'Fraunces', Georgia, serif;
  font-size: calc(48px * var(--font-scale));
  font-weight: 800;
  line-height: 1.1;
}

.hero em {
  color: #ffc400;
  font-style: italic;
}

.hero-sub {
  margin: 0;
  max-width: 860px;
  font-size: calc(20px * var(--font-scale));
  line-height: 1.5;
  opacity: 0.9;
}

.hero-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}

.c1 {
  width: 220px;
  height: 220px;
  right: -40px;
  top: -50px;
}

.c2 {
  width: 150px;
  height: 150px;
  left: 28px;
  bottom: -70px;
}

/* Setup */
.setup-panel {
  margin: 30px 40px 0;
  padding: 0 0 28px;
  background: #ffffff;
  border-radius: 26px;
}

.routine-card {
  padding: 30px 34px 34px;
  border: 2px solid #cfcfe3;
  border-radius: 26px;
  background: #ffffff;
  box-shadow: 0 12px 26px rgba(0, 0, 0, 0.04);
}

.card-title,
.mood-title {
  margin: 0 0 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #d8d8ea;
  color: #606079;
  font-size: calc(17px * var(--font-scale));
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.routine-row {
  display: grid;
  grid-template-columns: 1fr 1.7fr;
  align-items: center;
  gap: 24px;
  margin-top: 18px;
}

.routine-label {
  color: #28283e;
  font-size: calc(21px * var(--font-scale));
  font-weight: 900;
}

.routine-options {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 12px;
}

.pill-btn {
  min-width: 86px;
  padding: 12px 22px;
  border: 3px solid #d2d2e4;
  border-radius: 999px;
  background: #ffffff;
  color: #5a5a72;
  font-size: calc(18px * var(--font-scale));
  font-weight: 900;
  cursor: pointer;
}

.pill-btn.active {
  background: #007866;
  border-color: #007866;
  color: #ffffff;
}

/* Mood */
.mood-section {
  margin-top: 30px;
}

.mood-title {
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 18px;
}

.mood-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.mood-option {
  min-height: 112px;
  padding: 22px;
  border-radius: 18px;
  border: 3px solid;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: calc(18px * var(--font-scale));
  font-weight: 900;
  cursor: pointer;
}

.mood-icon {
  font-size: 26px;
}

.mood-label {
  text-align: center;
}

.mood-happy {
  border-color: #ffbf00;
  background: #fff6d8;
  color: #8a6500;
}

.mood-meet {
  border-color: #007866;
  background: #e1f7f4;
  color: #006756;
}

.mood-tired {
  border-color: #007866;
  background: #e1f7f4;
  color: #006756;
}

.mood-fresh {
  border-color: #2b7f2c;
  background: #eaf7e8;
  color: #1f6d20;
}

.mood-option.active {
  box-shadow: inset 0 0 0 3px rgba(0, 0, 0, 0.05), 0 12px 24px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

/* Setup actions */
.setup-actions {
  display: flex;
  flex-direction: column;
  gap: 18px;
  margin-top: 28px;
}

.find-btn,
.week-btn {
  width: 100%;
  padding: 22px 24px;
  border-radius: 18px;
  font-size: calc(24px * var(--font-scale));
  font-weight: 900;
  cursor: pointer;
}

.find-btn {
  border: none;
  background: #007866;
  color: #ffffff;
  box-shadow: 0 12px 24px rgba(0, 120, 102, 0.18);
}

.week-btn {
  border: 3px solid #d2d2e4;
  background: #ffffff;
  color: #5a5a72;
}

/* Recommendation text */
.mood-recommendation {
  margin-top: 24px;
  padding: 18px 22px;
  border-left: 6px solid #007866;
  border-radius: 0 16px 16px 0;
  background: #eaf8f5;
}

.mood-recommendation strong {
  color: #006756;
  font-size: calc(16px * var(--font-scale));
}

.mood-recommendation p {
  margin: 8px 0 0;
  color: #34344d;
  font-size: calc(15px * var(--font-scale));
  line-height: 1.5;
}

/* Best Moment Result UI */
.best-moment-result {
  margin: 32px 40px 0;
  background: #ffffff;
  border-radius: 0 0 26px 26px;
  overflow: hidden;
  scroll-margin-top: 90px;
}

.best-moment-hero {
  padding: 34px 42px 42px;
  background: linear-gradient(135deg, #006b5b, #004b3d);
  color: #ffffff;
}

.result-back-btn {
  margin-bottom: 24px;
  padding: 9px 20px;
  border: none;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  font-size: calc(16px * var(--font-scale));
  font-weight: 900;
  cursor: pointer;
}

.result-back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.result-eyebrow {
  margin: 0 0 12px;
  color: rgba(255, 255, 255, 0.72);
  font-size: calc(14px * var(--font-scale));
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.best-moment-hero h2 {
  margin: 0;
  max-width: 560px;
  color: #ffc400;
  font-family: 'Fraunces', Georgia, serif;
  font-size: calc(42px * var(--font-scale));
  font-weight: 900;
  line-height: 1.15;
}

.go-now-panel {
  margin: 26px 28px 0;
  padding: 28px 32px;
  border-radius: 22px;
  background: linear-gradient(135deg, #007866, #005f4f);
  color: #ffffff;
  box-shadow: 0 12px 28px rgba(0, 80, 65, 0.18);
}

.go-now-panel-label {
  margin: 0 0 18px;
  color: #ffc400;
  font-size: calc(15px * var(--font-scale));
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.go-now-summary {
  margin: 0 0 28px;
  color: #ffc400;
  font-size: calc(21px * var(--font-scale));
  font-weight: 900;
  line-height: 1.45;
}

.go-now-row {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 20px;
  padding: 15px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.18);
}

.go-now-row span {
  color: rgba(255, 255, 255, 0.72);
  font-size: calc(17px * var(--font-scale));
  font-weight: 700;
}

.go-now-row strong {
  color: #ffffff;
  font-size: calc(17px * var(--font-scale));
  font-weight: 900;
  text-align: right;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 150px;
  padding: 8px 16px;
  border-radius: 999px;
  text-align: center;
}

.status-green {
  background: #e0fff7;
  color: #006b5b !important;
}

.status-yellow {
  background: #fff2b8;
  color: #8a6500 !important;
}

.show-route-btn {
  width: calc(100% - 56px);
  margin: 22px 28px 0;
  padding: 20px 24px;
  border: none;
  border-radius: 18px;
  background: #ffc400;
  color: #1d1d2f;
  font-size: calc(22px * var(--font-scale));
  font-weight: 900;
  cursor: pointer;
  box-shadow: 0 12px 24px rgba(255, 196, 0, 0.18);
}

.show-route-btn:hover {
  background: #f0b800;
  transform: translateY(-1px);
}

.forecast-instead-btn {
  width: calc(100% - 56px);
  margin: 18px 28px 28px;
  padding: 18px 24px;
  border: 3px solid #d2d2e4;
  border-radius: 18px;
  background: #ffffff;
  color: #5a5a72;
  font-size: calc(20px * var(--font-scale));
  font-weight: 900;
  cursor: pointer;
}

.forecast-instead-btn:hover {
  border-color: #007866;
  color: #007866;
}

/* Wait card */
.wait-card {
  margin: 32px 40px 0;
  padding: 28px 30px;
  background: #ffffff;
  border: 2px solid #d2d2e4;
  border-radius: 24px;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.06);
  scroll-margin-top: 90px;
}

.wait-label {
  margin: 0 0 8px;
  color: #6b6d88;
  font-size: calc(13px * var(--font-scale));
  font-weight: 900;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.wait-card h2 {
  margin: 0 0 10px;
  font-family: 'Fraunces', Georgia, serif;
  color: #2f3152;
  font-size: calc(30px * var(--font-scale));
}

.wait-card p {
  margin: 0;
  color: #6b6d88;
  font-size: calc(16px * var(--font-scale));
  line-height: 1.5;
}

/* Score */
.section {
  padding: 32px 40px;
  border-bottom: 1.5px solid #e8e9f3;
}

.loading-row {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #6b6d88;
  font-size: calc(16px * var(--font-scale));
  font-weight: 600;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #e0e1ed;
  border-top-color: #0c8b7d;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.score-panel {
  display: flex;
  gap: 40px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.score-ring-wrap {
  position: relative;
  width: 140px;
  height: 140px;
  flex-shrink: 0;
}

.score-ring {
  width: 140px;
  height: 140px;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: #e8e9f3;
  stroke-width: 12;
}

.ring-fill {
  fill: none;
  stroke-width: 12;
  stroke-linecap: round;
}

.score-label-wrap {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-num {
  font-size: calc(32px * var(--font-scale));
  font-weight: 900;
  color: #2f3152;
}

.score-grade {
  font-size: calc(13px * var(--font-scale));
  font-weight: 900;
}

.breakdown {
  flex: 1;
  min-width: 260px;
}

.breakdown-title {
  margin: 0 0 16px;
  font-size: calc(14px * var(--font-scale));
  font-weight: 800;
  color: #6b6d88;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.bar-label {
  width: 120px;
  font-size: calc(13px * var(--font-scale));
  font-weight: 800;
  color: #3c3c58;
}

.bar-track {
  flex: 1;
  height: 10px;
  background: #e8e9f3;
  border-radius: 999px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
}

.bar-pts {
  width: 44px;
  font-size: calc(12px * var(--font-scale));
  font-weight: 800;
  color: #6b6d88;
  text-align: right;
}

.weather-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.weather-chip {
  padding: 5px 12px;
  border-radius: 999px;
  background: #f0f0f8;
  color: #3c3c58;
  font-size: calc(13px * var(--font-scale));
  font-weight: 800;
}

/* Advice */
.advice-banner {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 40px;
  font-size: calc(15px * var(--font-scale));
}

.verdict-good {
  background: #e8f8f5;
  color: #0a6e62;
}

.verdict-caution {
  background: #fff8e0;
  color: #8a6000;
}

.verdict-poor {
  background: #ffeaea;
  color: #c84848;
}

.verdict-unknown {
  background: #f0f0f8;
  color: #6b6d88;
}

.advice-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: currentColor;
  margin-top: 4px;
}

/* Quiet list */
.section-title {
  margin: 0 0 6px;
  font-family: 'Fraunces', Georgia, serif;
  font-size: calc(24px * var(--font-scale));
  color: #2f3152;
}

.section-sub {
  margin: 0 0 20px;
  font-size: calc(14px * var(--font-scale));
  color: #6b6d88;
}

.quiet-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.quiet-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  background: #ffffff;
  border: 1.5px solid #e0e1ed;
  border-radius: 14px;
  position: relative;
}

.quiet-best {
  border-color: #0c8b7d;
  background: #f0faf8;
}

.quiet-rank {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e8e9f3;
  color: #3c3c58;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quiet-best .quiet-rank {
  background: #0c8b7d;
  color: #ffffff;
}

.quiet-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.quiet-day {
  font-size: calc(16px * var(--font-scale));
  font-weight: 900;
  color: #2f3152;
}

.quiet-time {
  font-size: calc(14px * var(--font-scale));
  color: #6b6d88;
  font-weight: 700;
}

.quiet-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.quiet-count {
  font-size: calc(12px * var(--font-scale));
  color: #9b9db8;
  font-weight: 700;
}

.crowd-badge {
  padding: 3px 10px;
  border-radius: 999px;
  font-size: calc(12px * var(--font-scale));
  font-weight: 800;
}

.crowd-low {
  background: #e8f8f5;
  color: #0a6e62;
}

.crowd-moderate {
  background: #fff8e0;
  color: #8a6000;
}

.crowd-high {
  background: #ffeaea;
  color: #c84848;
}

.best-tag {
  position: absolute;
  top: -10px;
  left: 20px;
  padding: 2px 10px;
  border-radius: 999px;
  background: #0c8b7d;
  color: #ffffff;
  font-size: calc(11px * var(--font-scale));
  font-weight: 900;
}

.tip-text {
  margin: 16px 0 0;
  font-size: calc(13px * var(--font-scale));
  color: #9b9db8;
  font-style: italic;
}

/* Empty */
.empty-state {
  text-align: center;
  padding: 72px 40px;
  color: #6b6d88;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

/* Responsive */
@media (max-width: 1100px) {
  .routine-row {
    grid-template-columns: 1fr;
  }

  .routine-options {
    justify-content: flex-start;
  }
}

@media (max-width: 900px) {
  .hero {
    padding: 38px 22px 44px;
  }

  .hero h1 {
    font-size: calc(34px * var(--font-scale));
  }

  .hero-sub {
    font-size: calc(16px * var(--font-scale));
  }

  .setup-panel,
  .best-moment-result,
  .wait-card {
    margin: 24px 18px 0;
  }

  .routine-card {
    padding: 24px 20px;
  }

  .mood-grid {
    grid-template-columns: 1fr;
  }

  .best-moment-hero {
    padding: 28px 24px 34px;
  }

  .best-moment-hero h2 {
    font-size: calc(32px * var(--font-scale));
  }

  .go-now-panel {
    margin: 20px 18px 0;
    padding: 24px 22px;
  }

  .go-now-summary {
    font-size: calc(18px * var(--font-scale));
  }

  .go-now-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .go-now-row strong {
    text-align: left;
  }

  .show-route-btn,
  .forecast-instead-btn {
    width: calc(100% - 36px);
    margin-left: 18px;
    margin-right: 18px;
  }

  .section {
    padding: 24px 20px;
  }

  .score-panel {
    flex-direction: column;
    align-items: center;
  }
}
</style>