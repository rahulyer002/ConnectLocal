<template>
  <div class="home-page">
    <header class="top-nav">
      <div class="brand">
        <div class="logo-circle">●</div>
        <div>
          <h1><span>Connect</span>Local</h1>
          <p>Real connections. Local places.</p>
        </div>
      </div>

      <nav class="nav-links">
        <RouterLink to="/home">Home</RouterLink>
        <RouterLink to="/discover">Events</RouterLink>
        <RouterLink to="/discover">Places</RouterLink>
        <RouterLink to="/about">About</RouterLink>
        <RouterLink to="/resources">Resources</RouterLink>
        <RouterLink to="/checkin" class="start-btn">Start Check-in</RouterLink>
      </nav>
    </header>

    <section class="home">
      <div class="home-text">
        <h2>
          You're not<br />
          alone in this.
        </h2>

        <p>
          People of all ages experience challenges with social connection and
          wellbeing.
        </p>
        <p>
          Small steps can help build a more connected life.
        </p>

        <RouterLink to="/checkin" class="explore-btn">
          Explore activities near you
        </RouterLink>
      </div>

      <div class="home-image">
        <img src="../assets/home.png" alt="Home illustration" />
      </div>
    </section>

    <section class="age-section">
      <div class="age-text">
        <h2>Understanding wellbeing across age groups</h2>
        <p>
          Around the country, people of every age experience periods of higher
          psychological distress. Select your age group to see how common this is
          and know you are not alone.
        </p>
      </div>

      <div class="age-panel">
        <label for="ageGroup">Select your age group</label>

        <select id="ageGroup" v-model="selectedAgeGroup">
          <option value="">Choose your age group...</option>
          <option
            v-for="item in distressData"
            :key="item.age_group"
            :value="item.age_group"
          >
            {{ formatAgeGroup(item.age_group) }}
          </option>
        </select>

        <p v-if="isLoading" class="loading-text">
          Loading wellbeing data...
        </p>

        <p v-if="loadError" class="error-text">
          {{ loadError }}
        </p>

        <div v-if="selectedRecord" class="age-result">
          <div class="age-result-content">
            <div class="age-result-text">
              <h3>
                Around {{ distressedCount }} in 10 people aged
                {{ formatAgeGroup(selectedRecord.age_group) }} experience higher
                levels of psychological distress.
              </h3>

              <p>
                This is about {{ selectedRecord.psychological_distress_percent }}%
                of this age group. You are not alone, and ConnectLocal can help
                you find welcoming local activities.
              </p>

              <p v-if="elderlyNote" class="elderly-note">
                {{ elderlyNote }}
              </p>

              <p class="source">
                Source: {{ sourceText }}
              </p>
            </div>

            <!-- 
            Image visualisation temporarily disabled.
            This part used to show 1.png, 2.png, 3.png, etc. based on the dropdown result.

            <div class="people-visual">
              <img
                :src="getPeopleImage(distressedCount)"
                alt="People visualisation"
              />
            </div>
            -->
          </div>
        </div>
      </div>
    </section>

    <section class="steps-section">
      <h2>Small steps can help</h2>
      <p>
        Being part of your local community and finding places to connect can
        improve wellbeing and reduce feelings of isolation.
      </p>

      <div class="step-grid">
        <div class="step-card">
          <div class="step-icon mint">⌖</div>
          <h3>Local places</h3>
          <p>Find nearby places that feel familiar and easy to reach.</p>
        </div>

        <div class="step-card">
          <div class="step-icon yellow">◒</div>
          <h3>Gentle activities</h3>
          <p>Explore simple activities that do not feel too stressful.</p>
        </div>

        <div class="step-card">
          <div class="step-icon pink">♿</div>
          <h3>Comfort focused</h3>
          <p>Consider access, comfort and ease before going out.</p>
        </div>

        <div class="step-card">
          <div class="step-icon purple">♡</div>
          <h3>Social connection</h3>
          <p>Take small steps to reconnect with people around you.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

const API_URL = 'https://connectlocal.duckdns.org/api/suburbs/psychological-distress'

const selectedAgeGroup = ref('')
const distressData = ref([])
const sourceText = ref('ABS National Health Survey')
const elderlyHighlight = ref(null)
const isLoading = ref(false)
const loadError = ref('')

const selectedRecord = computed(() => {
  return distressData.value.find(
    item => item.age_group === selectedAgeGroup.value
  )
})

const elderlyNote = computed(() => {
  if (!elderlyHighlight.value || !selectedRecord.value) return ''

  if (selectedRecord.value.age_group === elderlyHighlight.value.age_group) {
    return elderlyHighlight.value.note
  }

  return ''
})

const distressedCount = computed(() => {
  if (!selectedRecord.value) return 1

  const percent = Number(selectedRecord.value.psychological_distress_percent)
  const count = Math.round(percent / 10)

  return Math.min(10, Math.max(1, count))
})

// Image visualisation temporarily disabled.
// This function was used to load 1.png, 2.png, 3.png, etc.
// function getPeopleImage(count) {
//   return new URL(`../assets/${count}.png`, import.meta.url).href
// }

function formatAgeGroup(ageGroup) {
  if (ageGroup === '65+') return '65 years and over'
  return `${ageGroup} years`
}

async function fetchDistressData() {
  isLoading.value = true
  loadError.value = ''

  try {
    const response = await fetch(API_URL)

    if (!response.ok) {
      throw new Error('Failed to load data')
    }

    const result = await response.json()

    distressData.value = result.data || []
    elderlyHighlight.value = result.elderly_highlight || null

    if (result.source && result.note && result.year) {
      sourceText.value = `${result.source}, ${result.note}, ${result.year}`
    } else if (result.source && result.year) {
      sourceText.value = `${result.source}, ${result.year}`
    }
  } catch (error) {
    loadError.value = 'Unable to load wellbeing data right now.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchDistressData()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f7faf7;
  color: #2f2d42;
}

.top-nav {
  height: 92px;
  padding: 0 44px;
  background: #fff;
  border-bottom: 2px solid #d9d8e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo-circle {
  width: 52px;
  height: 52px;
  background: #078d7f;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.brand h1 {
  margin: 0;
  font-family: Georgia, serif;
  font-size: calc(28px * var(--font-scale));
  line-height: 1;
  color: #078d7f;
}

.brand h1 span {
  color: #1f2c1f;
}

.brand p {
  margin: 4px 0 0;
  font-size: calc(16px * var(--font-scale));
  font-weight: 700;
  color: #5f6075;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 28px;
}

.nav-links a {
  text-decoration: none;
  color: #4b4b61;
  font-size: calc(18px * var(--font-scale));
  font-weight: 800;
}

.nav-links .router-link-active {
  color: #1d7169;
  border-bottom: 3px solid #1d7169;
  padding-bottom: 8px;
}

.start-btn {
  border: 3px solid #1d7169;
  border-radius: 999px;
  padding: 12px 24px;
  color: #1d7169 !important;
  border-bottom: 3px solid #1d7169 !important;
}

.home {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 560px;
  border-bottom: 2px solid #d9d8e6;
}

.home-text {
  padding: 88px 68px;
  background: #f7fbf8;
}

.home-text h2 {
  margin: 0 0 28px;
  font-family: Georgia, serif;
  font-size: calc(64px * var(--font-scale));
  line-height: 1.08;
  color: #17341d;
}

.home-text p {
  margin: 0 0 14px;
  font-size: calc(24px * var(--font-scale));
  line-height: 1.5;
  color: #48564b;
}

.explore-btn {
  display: inline-block;
  margin-top: 28px;
  background: #008c7d;
  color: #fff;
  text-decoration: none;
  padding: 20px 34px;
  border-radius: 14px;
  font-size: calc(22px * var(--font-scale));
  font-weight: 800;
  box-shadow: 0 14px 28px rgba(0, 140, 125, 0.25);
}

.home-image {
  background: #d8efd2;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.home-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.age-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 70px;
  padding: 70px 56px;
  background: #fff;
  border-bottom: 2px solid #e1e2ea;
}

.age-text h2 {
  margin: 0 0 26px;
  font-family: Georgia, serif;
  font-size: calc(40px * var(--font-scale));
  line-height: 1.2;
}

.age-text p {
  margin: 0;
  font-size: calc(22px * var(--font-scale));
  line-height: 1.6;
  color: #5d5d75;
}

.age-panel label {
  display: block;
  margin-bottom: 10px;
  font-size: calc(20px * var(--font-scale));
  font-weight: 800;
  color: #5d5d75;
}

.age-panel select {
  width: 100%;
  padding: 18px 22px;
  border: 3px solid #1b8179;
  border-radius: 14px;
  background: #fff;
  font-size: calc(22px * var(--font-scale));
  font-weight: 800;
  color: #2f2d42;
}

.loading-text,
.error-text {
  margin-top: 14px;
  font-size: calc(16px * var(--font-scale));
  font-weight: 700;
}

.error-text {
  color: #b3261e;
}

.age-result {
  margin-top: 20px;
  padding: 26px 30px;
  border-left: 6px solid #1b8179;
  border-radius: 0 16px 16px 0;
  background: #eff8f6;
}

.age-result-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 28px;
  align-items: center;
}

.age-result h3 {
  margin: 0 0 12px;
  font-size: calc(22px * var(--font-scale));
}

.age-result p {
  margin: 0 0 10px;
  font-size: calc(18px * var(--font-scale));
  line-height: 1.6;
  color: #5d5d75;
}

.elderly-note {
  font-weight: 700;
  color: #1b8179;
}

.source {
  font-size: calc(15px * var(--font-scale)) !important;
}

/*
People visualisation style temporarily disabled.
Keep this here in case the image feature is added back later.

.people-visual {
  display: flex;
  align-items: center;
  justify-content: center;
}

.people-visual img {
  width: 220px;
  height: auto;
}
*/

.steps-section {
  padding: 72px 56px;
  background: #f7faf7;
  text-align: center;
}

.steps-section h2 {
  margin: 0 0 16px;
  font-family: Georgia, serif;
  font-size: calc(38px * var(--font-scale));
}

.steps-section > p {
  max-width: 780px;
  margin: 0 auto 44px;
  font-size: calc(22px * var(--font-scale));
  line-height: 1.6;
  color: #5d5d75;
}

.step-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 28px;
}

.step-card {
  background: #fff;
  border: 2px solid #dfe8df;
  border-radius: 18px;
  padding: 34px 24px;
}

.step-icon {
  width: 70px;
  height: 70px;
  margin: 0 auto 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: calc(32px * var(--font-scale));
}

.mint {
  background: #e3faf5;
}

.yellow {
  background: #fff8d8;
}

.pink {
  background: #fff0ed;
}

.purple {
  background: #eee5ff;
}

.step-card h3 {
  margin: 0 0 12px;
  font-size: calc(22px * var(--font-scale));
}

.step-card p {
  margin: 0;
  font-size: calc(18px * var(--font-scale));
  line-height: 1.5;
  color: #5d5d75;
}

@media (max-width: 1000px) {
  .top-nav {
    height: auto;
    padding: 22px;
    flex-direction: column;
    gap: 18px;
  }

  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
  }

  .home,
  .age-section {
    grid-template-columns: 1fr;
  }

  .home-text h2 {
    font-size: calc(46px * var(--font-scale));
  }

  .age-result-content {
    grid-template-columns: 1fr;
  }

  .step-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>